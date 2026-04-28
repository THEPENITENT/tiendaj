# empleado_view.py — CRUD de empleados con scroll + validaciones completas
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_topbar, make_entry, make_boton, make_treeview,
                     make_status, set_status, make_combo, get_combo_value,
                     set_combo_by_id, make_form_panel)
from empleado_dao import EmpleadoDAO


class EmpleadoView:
    def __init__(self, ventana, usuario, puesto, cb_volver, filtro_sucursal=None):
        self.ventana   = ventana; self.usuario = usuario
        self.puesto    = puesto;  self.cb_volver = cb_volver
        self.filtro_suc = filtro_sucursal
        self.dao = EmpleadoDAO()
        self._calles = {}; self._sucursales = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("1100x720")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="👨‍💼", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        sub = f"Filtrado por sucursal: {self.filtro_suc}" if self.filtro_suc else "Hijo de Calle y Sucursal · Padre de ventas, teléfonos, correos"
        ctk.CTkLabel(ttl, text="Mantenimiento de Empleados",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text=sub, font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        try:
            self._calles     = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_calles()}
            self._sucursales = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_sucursales()}
        except: pass

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        # ID
        ctk.CTkLabel(form, text="ID EMPLEADO  (automático)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Auto")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        # Combos FK
        ctk.CTkLabel(form, text="CALLE  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=2, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_calle = make_combo(form, self._calles)
        self.cb_calle.grid(row=3, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="SUCURSAL  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=4, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_suc = make_combo(form, self._sucursales)
        self.cb_suc.grid(row=5, column=0, sticky="ew", padx=18)

        # Campos texto (puesto se maneja aparte como OptionMenu)
        campos = [
            ("NOMBRE  (NOT NULL, máx. 50)",           "ent_nombre", "Nombre",          50,  False, 6),
            ("APELLIDO PATERNO  (NOT NULL, máx. 50)", "ent_ap",     "Ap. Paterno",     50,  False, 8),
            ("APELLIDO MATERNO  (NOT NULL, máx. 50)", "ent_am",     "Ap. Materno",     50,  False, 10),
            ("CURP  (UNIQUE, exactamente 18 chars)",  "ent_curp",   "18 caracteres",   18,  False, 12),
            ("RFC  (UNIQUE, 12-13 chars)",            "ent_rfc",    "12 o 13 chars",   13,  False, 14),
        ]
        for lbl, attr, ph, mx, pw, r in campos:
            ctk.CTkLabel(form, text=lbl, font=("Segoe UI",10,"bold"),
                         text_color=GRAY_TEXT).grid(row=r, column=0, sticky="w", padx=18, pady=(12,3))
            e = make_entry(self.ventana, form, ph, max_chars=mx, show="•" if pw else None)
            e.grid(row=r+1, column=0, sticky="ew", padx=18, pady=(0,2))
            setattr(self, attr, e)

        # PUESTO como OptionMenu (CHECK constraint en BD)
        ctk.CTkLabel(form, text="PUESTO  (NOT NULL · CHECK constraint)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=16, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_puesto = ctk.CTkOptionMenu(
            form, values=["Administrador", "Dueño", "Gerente", "Cajero"],
            fg_color=BG_INPUT, button_color=PURPLE, button_hover_color=PURPLE_LT,
            dropdown_fg_color=BG_CARD, text_color=WHITE, font=("Segoe UI",12), height=40)
        self.cb_puesto.set("Cajero")
        self.cb_puesto.grid(row=17, column=0, sticky="ew", padx=18, pady=(0,2))

        # CONTRASEÑA
        ctk.CTkLabel(form, text="CONTRASEÑA  (máx. 100)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=18, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_pass = make_entry(self.ventana, form, "Contraseña", max_chars=100, show="•")
        self.ent_pass.grid(row=19, column=0, sticky="ew", padx=18, pady=(0,16))

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
            columnas=["ID","Sucursal","Nombre","Ap. P","Ap. M","CURP","RFC","Puesto"],
            anchos=[40,110,110,90,90,130,100,100])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _limpiar(self):
        for a in ["ent_id","ent_nombre","ent_ap","ent_am","ent_curp","ent_rfc","ent_pass"]:
            getattr(self, a).delete(0,"end")
        if self._calles:     self.cb_calle.set(list(self._calles.keys())[0])
        if self._sucursales: self.cb_suc.set(list(self._sucursales.keys())[0])
        self.cb_puesto.set("Cajero")
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                if self.filtro_suc and r[1] != self.filtro_suc: continue
                self.tree.insert("","end", values=(r[0],r[2],r[5],r[6],r[7],r[8],r[9],r[10]))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        try:
            row = self.dao.buscar_por_id(int(v[0]))
            if row:
                self.ent_id.delete(0,"end");     self.ent_id.insert(0, row[0])
                set_combo_by_id(self.cb_calle,  self._calles,     row[1])
                set_combo_by_id(self.cb_suc,    self._sucursales, row[2])
                self.ent_nombre.delete(0,"end"); self.ent_nombre.insert(0, row[3])
                self.ent_ap.delete(0,"end");     self.ent_ap.insert(0, row[4])
                self.ent_am.delete(0,"end");     self.ent_am.insert(0, row[5])
                self.ent_curp.delete(0,"end");   self.ent_curp.insert(0, row[6])
                self.ent_rfc.delete(0,"end");    self.ent_rfc.insert(0, row[7])
                self.cb_puesto.set(row[8] if row[8] else "Cajero")
                self.ent_pass.delete(0,"end");   self.ent_pass.insert(0, row[9] or "")
                self._s(f"  Empleado '{row[0]}' cargado.", GRAY_TEXT)
        except: pass

    def _buscar(self):
        txt = self.ent_id.get().strip()
        if not txt: return
        try: id_ = int(txt)
        except: self._s("⚠  ID debe ser número.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                set_combo_by_id(self.cb_calle,  self._calles,     row[1])
                set_combo_by_id(self.cb_suc,    self._sucursales, row[2])
                self.ent_nombre.delete(0,"end"); self.ent_nombre.insert(0, row[3])
                self.ent_ap.delete(0,"end");     self.ent_ap.insert(0, row[4])
                self.ent_am.delete(0,"end");     self.ent_am.insert(0, row[5])
                self.ent_curp.delete(0,"end");   self.ent_curp.insert(0, row[6])
                self.ent_rfc.delete(0,"end");    self.ent_rfc.insert(0, row[7])
                self.cb_puesto.set(row[8] if row[8] else "Cajero")
                self.ent_pass.delete(0,"end");   self.ent_pass.insert(0, row[9] or "")
                self._s(f"✔  Empleado '{id_}' encontrado.", CYAN)
            else: self._s(f"⚠  No existe el empleado '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _validar(self, excluir_id=None):
        id_calle = get_combo_value(self.cb_calle, self._calles)
        id_suc   = get_combo_value(self.cb_suc,   self._sucursales)
        nom    = self.ent_nombre.get().strip()
        ap     = self.ent_ap.get().strip()
        am     = self.ent_am.get().strip()
        curp   = self.ent_curp.get().strip().upper()
        rfc    = self.ent_rfc.get().strip().upper()
        puesto = self.cb_puesto.get()
        pwd    = self.ent_pass.get().strip()

        if not id_calle: self._s("⚠  Selecciona una calle (FK obligatoria).", RED); return None
        if not id_suc:   self._s("⚠  Selecciona una sucursal (FK obligatoria).", RED); return None
        if not nom:      self._s("⚠  Nombre obligatorio (NOT NULL).", RED); self.ent_nombre.focus_set(); return None
        if not ap:       self._s("⚠  Apellido paterno obligatorio (NOT NULL).", RED); self.ent_ap.focus_set(); return None
        if not am:       self._s("⚠  Apellido materno obligatorio (NOT NULL).", RED); self.ent_am.focus_set(); return None
        if not curp or len(curp) != 18:
            self._s("⚠  CURP debe tener exactamente 18 caracteres (UNIQUE).", RED)
            self.ent_curp.focus_set(); return None
        if not rfc or len(rfc) not in (12, 13):
            self._s("⚠  RFC debe tener 12 o 13 caracteres (UNIQUE).", RED)
            self.ent_rfc.focus_set(); return None
        if not puesto:   self._s("⚠  Puesto obligatorio.", RED); return None

        # UNIQUE checks
        if self.dao.curp_duplicado(curp, excluir_id):
            self._s(f"⚠  El CURP '{curp}' ya pertenece a otro empleado (UNIQUE).", RED); return None
        if self.dao.rfc_duplicado(rfc, excluir_id):
            self._s(f"⚠  El RFC '{rfc}' ya pertenece a otro empleado (UNIQUE).", RED); return None

        return id_calle, id_suc, nom, ap, am, curp, rfc, puesto, pwd

    def _alta(self):
        d = self._validar()
        if d is None: return
        try:
            self.dao.insertar(*d)
            self._s(f"✔  Empleado '{d[2]}' dado de alta.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        d = self._validar(excluir_id=id_)
        if d is None: return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Empleado '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, *d)
            self._s(f"✔  Empleado '{id_}' actualizado.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Empleado '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s("✖  No se puede eliminar: tiene ventas, teléfonos o correos asociados.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar empleado '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Empleado '{id_}' eliminado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _vid(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona un empleado del grid primero.", RED); return None
        try: return int(txt)
        except: self._s("⚠  ID inválido.", RED); return None

    def _ver_ventas(self):
        id_ = self._vid()
        if id_ is None: return
        from venta_view import VentaView
        self.ventana._limpiar()
        VentaView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro_empleado=id_)

    def _ver_telefonos(self):
        id_ = self._vid()
        if id_ is None: return
        from contacto_views import TelefonoView
        self.ventana._limpiar()
        TelefonoView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro=("empleado", id_))

    def _ver_correos(self):
        id_ = self._vid()
        if id_ is None: return
        from contacto_views import CorreoView
        self.ventana._limpiar()
        CorreoView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro=("empleado", id_))
