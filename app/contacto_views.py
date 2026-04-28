# contacto_views.py — TelefonoView y CorreoView con scroll + validaciones
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_topbar, make_entry, make_boton, make_treeview,
                     make_status, set_status, make_form_panel)
from contacto_dao import TelefonoDAO, CorreoDAO


class TelefonoView:
    """filtro = ('proveedor'|'empleado'|'sucursal'|'cliente', id) — opcional"""
    def __init__(self, ventana, usuario, puesto, cb_volver, filtro=None):
        self.ventana   = ventana; self.usuario = usuario
        self.puesto    = puesto;  self.cb_volver = cb_volver
        self.filtro    = filtro;  self.dao = TelefonoDAO()
        self._construir()

    def _construir(self):
        self.ventana.geometry("820x620")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="📞", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        sub = f"Filtrado por {self.filtro[0]}: {self.filtro[1]}" if self.filtro \
              else "Hijo de proveedores/empleados/sucursales/clientes"
        ctk.CTkLabel(ttl, text="Mantenimiento de Teléfonos",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text=sub, font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID TELÉFONO  (automático)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Auto")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())

        ctk.CTkLabel(form, text="NÚMERO  (NOT NULL, máx. 20)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=2, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_num = make_entry(self.ventana, form, "Ej. 8181234567", max_chars=20)
        self.ent_num.grid(row=3, column=0, sticky="ew", padx=18, pady=(0,4))

        if self.filtro:
            ctk.CTkLabel(form, text=f"ASOCIADO A: {self.filtro[0].upper()} ID {self.filtro[1]}",
                         font=("Segoe UI",10,"bold"), text_color=CYAN
                         ).grid(row=4, column=0, sticky="w", padx=18, pady=(12,16))
        else:
            ctk.CTkLabel(form, text="⚠  Alta solo disponible desde el padre\n(proveedor, empleado, sucursal o cliente)",
                         font=("Segoe UI",9), text_color=AMBER
                         ).grid(row=4, column=0, sticky="w", padx=18, pady=(8,16))

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
        ctk.CTkLabel(right, text="REGISTROS", font=("Segoe UI",10,"bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=16, pady=(12,6))
        self.tree = make_treeview(right,
            columnas=["ID","Número","Prov","Emp","Suc","Cli"],
            anchos=[60,160,60,60,60,60])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _limpiar(self):
        self.ent_id.delete(0,"end"); self.ent_num.delete(0,"end")
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            if self.filtro:
                for r in self.dao.obtener_por_filtro(*self.filtro):
                    self.tree.insert("","end", values=(r[0], r[1], "-", "-", "-", "-"))
            else:
                for r in self.dao.obtener_todos():
                    self.tree.insert("","end",
                                     values=(r[0], r[1], r[2] or "", r[3] or "", r[4] or "", r[5] or ""))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        self.ent_id.delete(0,"end");  self.ent_id.insert(0, v[0])
        self.ent_num.delete(0,"end"); self.ent_num.insert(0, v[1])
        self._s(f"  Teléfono '{v[0]}' cargado.", GRAY_TEXT)

    def _buscar(self):
        txt = self.ent_id.get().strip()
        if not txt: return
        try: id_ = int(txt)
        except: return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_num.delete(0,"end"); self.ent_num.insert(0, row[1])
                self._s(f"✔  Teléfono '{id_}' encontrado.", CYAN)
            else: self._s(f"⚠  No existe el teléfono '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _ids_padre(self):
        if not self.filtro: return None, None, None, None
        tipo, id_ = self.filtro
        return (id_ if tipo=="proveedor" else None,
                id_ if tipo=="empleado"  else None,
                id_ if tipo=="sucursal"  else None,
                id_ if tipo=="cliente"   else None)

    def _alta(self):
        num = self.ent_num.get().strip()
        if not num: self._s("⚠  Número obligatorio (NOT NULL).", RED); self.ent_num.focus_set(); return
        if not self.filtro:
            self._s("⚠  Alta solo disponible desde el padre (sucursal/empleado/cliente/proveedor).", RED); return
        try:
            self.dao.insertar(num, *self._ids_padre())
            self._s("✔  Teléfono guardado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        txt = self.ent_id.get().strip();  num = self.ent_num.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        if not num: self._s("⚠  Número obligatorio.", RED); return
        try:
            id_ = int(txt)
            if not self.dao.existe(id_): self._s(f"⚠  Teléfono '{id_}' no existe.", RED); return
            row = self.dao.buscar_por_id(id_)
            self.dao.actualizar(id_, num, row[2], row[3], row[4], row[5])
            self._s(f"✔  Teléfono '{id_}' actualizado.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Teléfono '{id_}' no existe.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar teléfono '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Teléfono '{id_}' eliminado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)


class CorreoView:
    """filtro = ('proveedor'|'empleado'|'sucursal'|'cliente', id) — opcional"""
    def __init__(self, ventana, usuario, puesto, cb_volver, filtro=None):
        self.ventana   = ventana; self.usuario = usuario
        self.puesto    = puesto;  self.cb_volver = cb_volver
        self.filtro    = filtro;  self.dao = CorreoDAO()
        self._construir()

    def _construir(self):
        self.ventana.geometry("820x620")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="📧", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        sub = f"Filtrado por {self.filtro[0]}: {self.filtro[1]}" if self.filtro \
              else "Hijo de proveedores/empleados/sucursales/clientes"
        ctk.CTkLabel(ttl, text="Mantenimiento de Correos",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text=sub, font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID CORREO  (automático)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Auto")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())

        ctk.CTkLabel(form, text="CORREO ELECTRÓNICO  (NOT NULL, máx. 100)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=2, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_correo = make_entry(self.ventana, form, "ejemplo@correo.com", max_chars=100)
        self.ent_correo.grid(row=3, column=0, sticky="ew", padx=18, pady=(0,4))

        if self.filtro:
            ctk.CTkLabel(form, text=f"ASOCIADO A: {self.filtro[0].upper()} ID {self.filtro[1]}",
                         font=("Segoe UI",10,"bold"), text_color=CYAN
                         ).grid(row=4, column=0, sticky="w", padx=18, pady=(12,16))
        else:
            ctk.CTkLabel(form, text="⚠  Alta solo disponible desde el padre\n(proveedor, empleado, sucursal o cliente)",
                         font=("Segoe UI",9), text_color=AMBER
                         ).grid(row=4, column=0, sticky="w", padx=18, pady=(8,16))

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
        ctk.CTkLabel(right, text="REGISTROS", font=("Segoe UI",10,"bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=16, pady=(12,6))
        self.tree = make_treeview(right,
            columnas=["ID","Correo","Cli","Suc","Emp","Prov"],
            anchos=[60,200,50,50,50,50])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _limpiar(self):
        self.ent_id.delete(0,"end"); self.ent_correo.delete(0,"end")
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            if self.filtro:
                for r in self.dao.obtener_por_filtro(*self.filtro):
                    self.tree.insert("","end", values=(r[0], r[1], "-", "-", "-", "-"))
            else:
                for r in self.dao.obtener_todos():
                    self.tree.insert("","end",
                                     values=(r[0], r[1], r[2] or "", r[3] or "", r[4] or "", r[5] or ""))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        self.ent_id.delete(0,"end");     self.ent_id.insert(0, v[0])
        self.ent_correo.delete(0,"end"); self.ent_correo.insert(0, v[1])
        self._s(f"  Correo '{v[0]}' cargado.", GRAY_TEXT)

    def _buscar(self):
        txt = self.ent_id.get().strip()
        if not txt: return
        try: id_ = int(txt)
        except: return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_correo.delete(0,"end"); self.ent_correo.insert(0, row[1])
                self._s(f"✔  Correo '{id_}' encontrado.", CYAN)
            else: self._s(f"⚠  No existe el correo '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _ids_padre(self):
        if not self.filtro: return None, None, None, None
        tipo, id_ = self.filtro
        return (id_ if tipo=="cliente"   else None,
                id_ if tipo=="sucursal"  else None,
                id_ if tipo=="empleado"  else None,
                id_ if tipo=="proveedor" else None)

    def _alta(self):
        c = self.ent_correo.get().strip()
        if not c: self._s("⚠  Correo obligatorio (NOT NULL).", RED); return
        if not self.filtro:
            self._s("⚠  Alta solo disponible desde el padre.", RED); return
        try:
            self.dao.insertar(c, *self._ids_padre())
            self._s("✔  Correo guardado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        txt = self.ent_id.get().strip();  c = self.ent_correo.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        if not c:   self._s("⚠  Correo obligatorio.", RED); return
        try:
            id_ = int(txt)
            if not self.dao.existe(id_): self._s(f"⚠  Correo '{id_}' no existe.", RED); return
            row = self.dao.buscar_por_id(id_)
            self.dao.actualizar(id_, c, row[2], row[3], row[4], row[5])
            self._s(f"✔  Correo '{id_}' actualizado.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Correo '{id_}' no existe.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar correo '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Correo '{id_}' eliminado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)
