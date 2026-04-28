# detalle_venta_view.py — CRUD Detalle_Ventas con scroll + validaciones
# 3 FKs: Ventas, Videojuego, inventarios
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_topbar, make_entry, make_boton, make_treeview,
                     make_status, set_status, make_combo, get_combo_value,
                     set_combo_by_id, make_form_panel)
from detalle_venta_dao import DetalleVentaDAO


class DetalleVentaView:
    def __init__(self, ventana, usuario, puesto, cb_volver,
                 filtro_venta=None, filtro_videojuego=None):
        self.ventana    = ventana; self.usuario = usuario
        self.puesto     = puesto;  self.cb_volver = cb_volver
        self.filtro_v   = filtro_venta
        self.filtro_vid = filtro_videojuego
        self.dao = DetalleVentaDAO()
        self._ventas = {}; self._videojuegos = {}; self._inventarios = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("1020x700")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="📋", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        if self.filtro_v:    sub = f"Filtrado por venta: {self.filtro_v}"
        elif self.filtro_vid: sub = f"Filtrado por videojuego: {self.filtro_vid}"
        else: sub = "Hijo de Ventas, Videojuego e Inventarios · Sin tablas hijas"
        ctk.CTkLabel(ttl, text="Detalles de Venta",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text=sub, font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        # Cargar combos
        try:
            ventas_raw = self.dao.obtener_ventas()
            self._ventas = {}
            for r in ventas_raw:
                fecha_str = str(r[1])[:10] if r[1] is not None else "sin fecha"
                self._ventas[f"{r[0]} ({fecha_str})"] = r[0]

            vid_raw = self.dao.obtener_videojuegos()
            self._videojuegos = {}
            for r in vid_raw:
                titulo = r[1] if r[1] else "(sin título)"
                self._videojuegos[f"{r[0]} - {titulo}"] = r[0]

            inv_raw = self.dao.obtener_inventarios()
            self._inventarios = {}
            for r in inv_raw:
                # r = (idinventario, nombre_inventario, nombre_sucursal, plat_nombre, stock)
                nom  = r[1] if r[1] else "(sin nombre)"
                suc  = r[2] if r[2] else "?"
                plat = r[3] if r[3] else "?"
                stk  = r[4] if r[4] is not None else 0
                self._inventarios[f"{r[0]} - {nom} | {suc}/{plat} (stock:{stk})"] = r[0]
        except Exception as e:
            print(f"[detalle_venta_view] Error cargando combos: {e}")

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID DETALLE  (automático)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Auto")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        # FK Venta
        ctk.CTkLabel(form, text="VENTA  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=2, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_v = make_combo(form, self._ventas)
        self.cb_v.grid(row=3, column=0, sticky="ew", padx=18)
        if self.filtro_v is not None:
            set_combo_by_id(self.cb_v, self._ventas, self.filtro_v)

        # FK Videojuego
        ctk.CTkLabel(form, text="VIDEOJUEGO  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=4, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_vid = make_combo(form, self._videojuegos)
        self.cb_vid.grid(row=5, column=0, sticky="ew", padx=18)
        if self.filtro_vid is not None:
            set_combo_by_id(self.cb_vid, self._videojuegos, self.filtro_vid)

        # FK Inventarios (NUEVO)
        ctk.CTkLabel(form, text="INVENTARIO  (FK obligatoria · de qué bodega/sucursal)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=6, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_inv = make_combo(form, self._inventarios)
        self.cb_inv.grid(row=7, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="CANTIDAD  (NOT NULL, entero > 0 — CHECK)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=8, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_cant = make_entry(self.ventana, form, "Ej. 2", max_chars=10)
        self.ent_cant.grid(row=9, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="PRECIO UNITARIO  (NOT NULL, decimal > 0 — CHECK)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=10, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_precio = make_entry(self.ventana, form, "Ej. 999.99", max_chars=12)
        self.ent_precio.grid(row=11, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="Subtotal = cantidad × precio  (calculado automático)",
                     font=("Segoe UI",9), text_color=AMBER
                     ).grid(row=12, column=0, sticky="w", padx=18, pady=(8,16))

        g = ctk.CTkFrame(ba, fg_color="transparent"); g.pack(fill="x")
        for txt, color, cmd, r, c in [
            ("Alta", GREEN, self._alta, 0, 0), ("Cambios", PURPLE, self._cambios, 0, 1),
            ("Baja", RED, self._baja, 1, 0),   ("Limpiar", "#374151", self._limpiar, 1, 1),
        ]:
            make_boton(g, txt, cmd, color=color).grid(row=r, column=c, padx=4, pady=3)
        ctk.CTkButton(ba, text="← Volver", height=34, fg_color="transparent",
                      border_width=1, border_color=BORDER, text_color=GRAY_TEXT,
                      hover_color=BG_CARD, corner_radius=8, font=("Segoe UI",11),
                      command=self.cb_volver).pack(fill="x", pady=(4,0))
        self.lbl_status = make_status(ba)

    def _grid(self, parent):
        right = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                             border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="REGISTROS EN BD",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).pack(anchor="w", padx=16, pady=(12,6))
        self.tree = make_treeview(right,
            columnas=["ID","Venta","Videojuego","Inventario","Cant.","P. Unit","Subtotal"],
            anchos=[40,55,180,180,55,90,100])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _limpiar(self):
        for e in [self.ent_id, self.ent_cant, self.ent_precio]: e.delete(0,"end")
        if self._ventas:      self.cb_v.set(list(self._ventas.keys())[0])
        if self._videojuegos: self.cb_vid.set(list(self._videojuegos.keys())[0])
        if self._inventarios: self.cb_inv.set(list(self._inventarios.keys())[0])
        # Si vinimos filtrados, mantener el padre seleccionado
        if self.filtro_v   is not None: set_combo_by_id(self.cb_v,   self._ventas,      self.filtro_v)
        if self.filtro_vid is not None: set_combo_by_id(self.cb_vid, self._videojuegos, self.filtro_vid)
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                # r = (idDetalle, idVenta, idVid, Titulo, idInv, nombre_inv, Cant, Precio, Subtotal)
                if self.filtro_v   and r[1] != self.filtro_v:   continue
                if self.filtro_vid and r[2] != self.filtro_vid: continue
                titulo = r[3] if r[3] else "(sin título)"
                inv    = r[5] if r[5] else "(sin nombre)"
                cant   = r[6] if r[6] is not None else 0
                precio = r[7] if r[7] is not None else 0
                subt   = r[8] if r[8] is not None else 0
                self.tree.insert("", "end",
                                 values=(r[0], r[1], f"{r[2]} - {titulo}",
                                         f"{r[4]} - {inv}", cant,
                                         f"${precio:,.2f}", f"${subt:,.2f}"))
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        try:
            row = self.dao.buscar_por_id(int(v[0]))
            if row:
                # row = (idDetalle, idVenta, idVid, idInv, Cant, Precio, Subt)
                self.ent_id.delete(0,"end");     self.ent_id.insert(0, row[0])
                set_combo_by_id(self.cb_v,   self._ventas,      row[1])
                set_combo_by_id(self.cb_vid, self._videojuegos, row[2])
                set_combo_by_id(self.cb_inv, self._inventarios, row[3])
                self.ent_cant.delete(0,"end");   self.ent_cant.insert(0, str(row[4]))
                self.ent_precio.delete(0,"end"); self.ent_precio.insert(0, str(row[5]))
                self._s(f"  Detalle '{row[0]}' cargado.", GRAY_TEXT)
        except: pass

    def _buscar(self):
        txt = self.ent_id.get().strip()
        if not txt: return
        try: id_ = int(txt)
        except: self._s("⚠  ID debe ser número.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                set_combo_by_id(self.cb_v,   self._ventas,      row[1])
                set_combo_by_id(self.cb_vid, self._videojuegos, row[2])
                set_combo_by_id(self.cb_inv, self._inventarios, row[3])
                self.ent_cant.delete(0,"end");   self.ent_cant.insert(0, str(row[4]))
                self.ent_precio.delete(0,"end"); self.ent_precio.insert(0, str(row[5]))
                self._s(f"✔  Detalle '{id_}' encontrado.", CYAN)
            else: self._s(f"⚠  No existe el detalle '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _validar(self):
        id_v   = get_combo_value(self.cb_v,   self._ventas)
        id_vid = get_combo_value(self.cb_vid, self._videojuegos)
        id_inv = get_combo_value(self.cb_inv, self._inventarios)
        ctxt   = self.ent_cant.get().strip()
        ptxt   = self.ent_precio.get().strip()
        if not id_v:   self._s("⚠  Selecciona una venta (FK obligatoria).", RED); return None
        if not id_vid: self._s("⚠  Selecciona un videojuego (FK obligatoria).", RED); return None
        if not id_inv:
            self._s("⚠  Selecciona un inventario. Si la lista está vacía, primero debes "
                    "registrar inventarios con stock > 0.", RED); return None
        if not ctxt:   self._s("⚠  Cantidad obligatoria (NOT NULL).", RED); self.ent_cant.focus_set(); return None
        if not ptxt:   self._s("⚠  Precio obligatorio (NOT NULL).", RED); self.ent_precio.focus_set(); return None
        try: cant = int(ctxt)
        except: self._s("⚠  Cantidad debe ser entero.", RED); return None
        if cant <= 0:  self._s("⚠  Cantidad debe ser > 0 (CHECK constraint).", RED); return None
        try: precio = float(ptxt)
        except: self._s("⚠  Precio debe ser decimal.", RED); return None
        if precio <= 0: self._s("⚠  Precio debe ser > 0 (CHECK constraint).", RED); return None
        return id_v, id_vid, id_inv, cant, precio

    def _alta(self):
        d = self._validar()
        if d is None: return
        try:
            self.dao.insertar(*d)
            sub = d[3] * d[4]
            self._s(f"✔  Detalle guardado. Subtotal: ${sub:,.2f}", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        d = self._validar()
        if d is None: return
        try:
            id_ = int(txt)
            if not self.dao.existe(id_): self._s(f"⚠  Detalle '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, *d)
            self._s(f"✔  Detalle '{id_}' actualizado.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Detalle '{id_}' no existe.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar detalle '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Detalle '{id_}' eliminado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)
