# venta_view.py — CRUD Ventas (TRES FK) con scroll + validaciones
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from colores import *
from widgets import (make_topbar, make_entry, make_boton, make_treeview,
                     make_status, set_status, make_combo, get_combo_value,
                     set_combo_by_id, make_form_panel)
from venta_dao import VentaDAO


class VentaView:
    def __init__(self, ventana, usuario, puesto, cb_volver,
                 filtro_sucursal=None, filtro_empleado=None, filtro_cliente=None):
        self.ventana    = ventana; self.usuario = usuario
        self.puesto     = puesto;  self.cb_volver = cb_volver
        self.filtro_suc = filtro_sucursal
        self.filtro_emp = filtro_empleado
        self.filtro_cli = filtro_cliente
        self.dao = VentaDAO()
        self._sucursales = {}; self._empleados = {}; self._clientes = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("1050x700")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="💰", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        if self.filtro_suc: sub = f"Filtrado por sucursal: {self.filtro_suc}"
        elif self.filtro_emp: sub = f"Filtrado por empleado: {self.filtro_emp}"
        elif self.filtro_cli: sub = f"Filtrado por cliente: {self.filtro_cli}"
        else: sub = "Hijo de Sucursal, Empleado y Cliente · Padre de Detalle_Ventas"
        ctk.CTkLabel(ttl, text="Mantenimiento de Ventas",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text=sub, font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        try:
            self._sucursales = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_sucursales()}
            self._empleados  = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_empleados()}
            self._clientes   = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_clientes()}
        except: pass

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID VENTA  (automático)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Auto")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        for lbl, attr, dic, r in [
            ("SUCURSAL  (FK obligatoria)", "cb_suc", self._sucursales, 2),
            ("EMPLEADO  (FK obligatoria)", "cb_emp", self._empleados,  4),
            ("CLIENTE   (FK obligatoria)", "cb_cli", self._clientes,   6),
        ]:
            ctk.CTkLabel(form, text=lbl, font=("Segoe UI",10,"bold"),
                         text_color=GRAY_TEXT).grid(row=r, column=0, sticky="w", padx=18, pady=(12,3))
            cb = make_combo(form, dic)
            cb.grid(row=r+1, column=0, sticky="ew", padx=18)
            setattr(self, attr, cb)

        # --- FECHA DE VENTA con switch automática/manual ---
        fecha_hdr = ctk.CTkFrame(form, fg_color="transparent")
        fecha_hdr.grid(row=8, column=0, sticky="ew", padx=18, pady=(12, 3))
        fecha_hdr.columnconfigure(0, weight=1)

        ctk.CTkLabel(fecha_hdr, text="FECHA DE VENTA",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w")

        self.sw_auto = ctk.CTkSwitch(
            fecha_hdr, text="Automática", command=self._toggle_fecha_auto,
            fg_color=BORDER, progress_color=CYAN,
            button_color=WHITE, button_hover_color=CYAN,
            font=("Segoe UI", 10), text_color=GRAY_TEXT,
            switch_width=36, switch_height=18)
        self.sw_auto.grid(row=0, column=1, sticky="e")
        self.sw_auto.select()  # arranca en automática

        self.ent_fecha = ctk.CTkEntry(
            form, height=40, fg_color=BG_INPUT, border_color=BORDER,
            border_width=1, corner_radius=8, font=("Segoe UI", 13),
            text_color=WHITE,
            placeholder_text="AAAA-MM-DD HH:MM:SS")
        self.ent_fecha.grid(row=9, column=0, sticky="ew", padx=18)
        self._toggle_fecha_auto()  # aplicar estado inicial

        ctk.CTkLabel(form, text="TOTAL  (NOT NULL, decimal ≥ 0)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=10, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_total = make_entry(self.ventana, form, "Ej. 1500.50", max_chars=12)
        self.ent_total.grid(row=11, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="MÉTODO DE PAGO  (CHECK constraint)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=12, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_metodo = ctk.CTkOptionMenu(
            form, values=["Efectivo","Tarjeta","Transferencia"],
            fg_color=BG_INPUT, button_color=PURPLE, button_hover_color=PURPLE_LT,
            dropdown_fg_color=BG_CARD, text_color=WHITE, font=("Segoe UI",12), height=40)
        self.cb_metodo.set("Efectivo")
        self.cb_metodo.grid(row=13, column=0, sticky="ew", padx=18, pady=(0,16))

        ctk.CTkLabel(sf, text="VER TABLAS HIJAS", font=("Segoe UI",9,"bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=4, pady=(14,4))
        ctk.CTkButton(sf, text="📋  Detalle de Venta", height=32,
                      fg_color=BG_INPUT, text_color=CYAN,
                      font=("Segoe UI",10,"bold"), corner_radius=6,
                      command=self._ver_detalle).pack(fill="x", padx=4, pady=2)

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
            columnas=["ID","Sucursal","Empleado","Cliente","Fecha","Total","Pago"],
            anchos=[40,120,120,120,130,90,100])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _toggle_fecha_auto(self):
        """Cambia entre modo automático (campo bloqueado, fecha actual)
        y modo manual (campo editable, usuario escribe la fecha)."""
        if self.sw_auto.get() == 1:
            # Modo automático: muestra fecha/hora actual y bloquea
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.ent_fecha.configure(state="normal")
            self.ent_fecha.delete(0, "end")
            self.ent_fecha.insert(0, ahora)
            self.ent_fecha.configure(state="disabled", text_color=GRAY_TEXT)
        else:
            # Modo manual: deja editar
            self.ent_fecha.configure(state="normal", text_color=WHITE)
            self.ent_fecha.focus_set()

    def _set_fecha_existente(self, fecha_db):
        """Cuando se carga una venta existente, mostrar su fecha real.
        Apaga el switch automático para no machacarla."""
        self.sw_auto.deselect()
        self.ent_fecha.configure(state="normal", text_color=WHITE)
        self.ent_fecha.delete(0, "end")
        self.ent_fecha.insert(0, str(fecha_db)[:19] if fecha_db else "")

    def _limpiar(self):
        for e in [self.ent_id, self.ent_total]: e.delete(0,"end")
        if self._sucursales: self.cb_suc.set(list(self._sucursales.keys())[0])
        if self._empleados:  self.cb_emp.set(list(self._empleados.keys())[0])
        if self._clientes:   self.cb_cli.set(list(self._clientes.keys())[0])
        self.cb_metodo.set("Efectivo")
        self.sw_auto.select()       # vuelve a automática
        self._toggle_fecha_auto()   # actualiza el campo
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                if self.filtro_suc and r[1] != self.filtro_suc: continue
                if self.filtro_emp and r[3] != self.filtro_emp: continue
                if self.filtro_cli and r[5] != self.filtro_cli: continue
                fecha = str(r[7])[:16] if r[7] else ""
                total = r[8] if r[8] is not None else 0
                metodo = r[9] if r[9] else "—"
                self.tree.insert("", "end",
                                 values=(r[0], r[2], r[4], r[6], fecha,
                                         f"${total:,.2f}", metodo))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        try:
            row = self.dao.buscar_por_id(int(v[0]))
            if row:
                self.ent_id.delete(0,"end");    self.ent_id.insert(0, row[0])
                set_combo_by_id(self.cb_suc, self._sucursales, row[1])
                set_combo_by_id(self.cb_emp, self._empleados,  row[2])
                set_combo_by_id(self.cb_cli, self._clientes,   row[3])
                self._set_fecha_existente(row[4])
                self.ent_total.delete(0,"end"); self.ent_total.insert(0, str(row[5]))
                self.cb_metodo.set(row[6])
                self._s(f"  Venta '{row[0]}' cargada.", GRAY_TEXT)
        except: pass

    def _buscar(self):
        txt = self.ent_id.get().strip()
        if not txt: return
        try: id_ = int(txt)
        except: self._s("⚠  ID debe ser número.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                set_combo_by_id(self.cb_suc, self._sucursales, row[1])
                set_combo_by_id(self.cb_emp, self._empleados,  row[2])
                set_combo_by_id(self.cb_cli, self._clientes,   row[3])
                self._set_fecha_existente(row[4])
                self.ent_total.delete(0,"end"); self.ent_total.insert(0, str(row[5]))
                self.cb_metodo.set(row[6])
                self._s(f"✔  Venta '{id_}' encontrada.", CYAN)
            else: self._s(f"⚠  No existe la venta '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _resolver_fecha(self):
        """Devuelve un objeto datetime para insertar, o None si hay error.
        - Modo auto: usa datetime.now()
        - Modo manual: parsea el texto del entry. Acepta varios formatos."""
        if self.sw_auto.get() == 1:
            return datetime.now()

        txt = self.ent_fecha.get().strip()
        if not txt:
            self._s("⚠  En modo manual debes escribir la fecha.", RED)
            self.ent_fecha.focus_set(); return None

        # Formatos aceptados, en orden de preferencia
        formatos = ["%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d",
                    "%d/%m/%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M",
                    "%d/%m/%Y"]
        for fmt in formatos:
            try:
                return datetime.strptime(txt, fmt)
            except ValueError:
                continue

        self._s("⚠  Formato de fecha inválido. Usa AAAA-MM-DD HH:MM:SS", RED)
        self.ent_fecha.focus_set()
        return None

    def _validar(self):
        id_suc = get_combo_value(self.cb_suc, self._sucursales)
        id_emp = get_combo_value(self.cb_emp, self._empleados)
        id_cli = get_combo_value(self.cb_cli, self._clientes)
        ttxt   = self.ent_total.get().strip()
        if not id_suc: self._s("⚠  Selecciona una sucursal (FK obligatoria).", RED); return None
        if not id_emp: self._s("⚠  Selecciona un empleado (FK obligatoria).", RED); return None
        if not id_cli: self._s("⚠  Selecciona un cliente (FK obligatoria).", RED); return None
        if not ttxt:   self._s("⚠  Total obligatorio (NOT NULL).", RED); self.ent_total.focus_set(); return None
        try: total = float(ttxt)
        except: self._s("⚠  Total debe ser número decimal.", RED); return None
        if total < 0:  self._s("⚠  Total no puede ser negativo.", RED); return None

        fecha = self._resolver_fecha()
        if fecha is None: return None

        return id_suc, id_emp, id_cli, fecha, total, self.cb_metodo.get()

    def _alta(self):
        d = self._validar()
        if d is None: return
        try:
            self.dao.insertar(*d)
            self._s("✔  Venta registrada.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        d = self._validar()
        if d is None: return
        try:
            id_ = int(txt)
            if not self.dao.existe(id_): self._s(f"⚠  Venta '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, *d)
            self._s(f"✔  Venta '{id_}' actualizada.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Venta '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s("✖  No se puede eliminar: la venta tiene detalles asociados.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar venta '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Venta '{id_}' eliminada.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _ver_detalle(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona una venta del grid primero.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        from detalle_venta_view import DetalleVentaView
        self.ventana._limpiar()
        DetalleVentaView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro_venta=id_)
