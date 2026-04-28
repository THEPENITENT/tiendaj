# cliente_view.py — CRUD de Clientes con scroll y validaciones
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_topbar, make_entry, make_boton, make_treeview,
                     make_status, set_status, make_combo, get_combo_value,
                     set_combo_by_id, make_form_panel)
from cliente_dao import ClienteDAO


class ClienteView:
    def __init__(self, ventana, usuario, puesto, cb_volver):
        self.ventana   = ventana; self.usuario = usuario
        self.puesto    = puesto;  self.cb_volver = cb_volver
        self.dao = ClienteDAO();  self._calles = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("1000x680")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="👤", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Clientes",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Hijo de Calle · Padre de ventas, teléfonos, correos",
                     font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        try:
            self._calles = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_calles()}
        except: self._calles = {}

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID CLIENTE  (automático)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Auto")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        ctk.CTkLabel(form, text="CALLE  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=2, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_calle = make_combo(form, self._calles)
        self.cb_calle.grid(row=3, column=0, sticky="ew", padx=18)

        for lbl, attr, ph, mx, r in [
            ("NOMBRE  (máx. 50)",            "ent_nom", "Nombre",          50,  4),
            ("APELLIDO PATERNO  (máx. 50)",   "ent_ap",  "Ap. Paterno",     50,  6),
            ("APELLIDO MATERNO  (máx. 50)",   "ent_am",  "Ap. Materno",     50,  8),
        ]:
            ctk.CTkLabel(form, text=lbl, font=("Segoe UI",10,"bold"),
                         text_color=GRAY_TEXT).grid(row=r, column=0, sticky="w", padx=18, pady=(12,3))
            e = make_entry(self.ventana, form, ph, max_chars=mx)
            e.grid(row=r+1, column=0, sticky="ew", padx=18, pady=(0, 2 if r<8 else 16))
            setattr(self, attr, e)

        ctk.CTkLabel(sf, text="VER TABLAS HIJAS", font=("Segoe UI",9,"bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=4, pady=(14,4))
        for txt, cmd in [
            ("💰  Ventas",    self._ver_ventas),
            ("📞  Teléfonos", self._ver_telefonos),
            ("📧  Correos",   self._ver_correos),
        ]:
            ctk.CTkButton(sf, text=txt, height=32, fg_color=BG_INPUT, text_color=CYAN,
                          font=("Segoe UI",10,"bold"), corner_radius=6,
                          command=cmd).pack(fill="x", padx=4, pady=2)

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
            columnas=["ID","Calle","Nombre","Ap. Paterno","Ap. Materno","Registro"],
            anchos=[50,120,120,120,120,90])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _limpiar(self):
        for a in ["ent_id","ent_nom","ent_ap","ent_am"]:
            getattr(self, a).delete(0,"end")
        if self._calles: self.cb_calle.set(list(self._calles.keys())[0])
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                self.tree.insert("","end", values=(r[0],r[2],r[3] or "",r[4] or "",r[5] or "",str(r[6])[:10] if r[6] else ""))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        try:
            row = self.dao.buscar_por_id(int(v[0]))
            if row:
                self.ent_id.delete(0,"end"); self.ent_id.insert(0, row[0])
                set_combo_by_id(self.cb_calle, self._calles, row[1])
                self.ent_nom.delete(0,"end"); self.ent_nom.insert(0, row[2] or "")
                self.ent_ap.delete(0,"end");  self.ent_ap.insert(0, row[3] or "")
                self.ent_am.delete(0,"end");  self.ent_am.insert(0, row[4] or "")
                self._s(f"  Cliente '{row[0]}' cargado.", GRAY_TEXT)
        except: pass

    def _buscar(self):
        txt = self.ent_id.get().strip()
        if not txt: return
        try: id_ = int(txt)
        except: self._s("⚠  ID debe ser número.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                set_combo_by_id(self.cb_calle, self._calles, row[1])
                self.ent_nom.delete(0,"end"); self.ent_nom.insert(0, row[2] or "")
                self.ent_ap.delete(0,"end");  self.ent_ap.insert(0, row[3] or "")
                self.ent_am.delete(0,"end");  self.ent_am.insert(0, row[4] or "")
                self._s(f"✔  Cliente '{id_}' encontrado.", CYAN)
            else: self._s(f"⚠  No existe el cliente '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _validar(self):
        id_calle = get_combo_value(self.cb_calle, self._calles)
        if not id_calle:
            self._s("⚠  Selecciona una calle (FK obligatoria).", RED); return None
        return id_calle, self.ent_nom.get().strip(), self.ent_ap.get().strip(), self.ent_am.get().strip()

    def _alta(self):
        d = self._validar()
        if d is None: return
        try:
            self.dao.insertar(*d)
            self._s("✔  Cliente dado de alta.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        d = self._validar()
        if d is None: return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Cliente '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, *d)
            self._s(f"✔  Cliente '{id_}' actualizado.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Cliente '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s("✖  No se puede eliminar: tiene ventas, teléfonos o correos asociados.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar cliente '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Cliente '{id_}' eliminado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _vid(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona un cliente del grid.", RED); return None
        try: return int(txt)
        except: self._s("⚠  ID inválido.", RED); return None

    def _ver_ventas(self):
        id_ = self._vid()
        if id_ is None: return
        from venta_view import VentaView
        self.ventana._limpiar()
        VentaView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro_cliente=id_)

    def _ver_telefonos(self):
        id_ = self._vid()
        if id_ is None: return
        from contacto_views import TelefonoView
        self.ventana._limpiar()
        TelefonoView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro=("cliente", id_))

    def _ver_correos(self):
        id_ = self._vid()
        if id_ is None: return
        from contacto_views import CorreoView
        self.ventana._limpiar()
        CorreoView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro=("cliente", id_))
