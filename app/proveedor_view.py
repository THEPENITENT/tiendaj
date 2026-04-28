# proveedor_view.py — Pantalla CRUD de la tabla proveedores (abuela, sin FK)
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_form_panel, make_topbar, make_entry, make_boton,
                     make_treeview, make_status, set_status)
from proveedor_dao import ProveedorDAO


class ProveedorView:
    """
    Pantalla de mantenimiento de la tabla proveedores.
    - id_proveedor:   INT IDENTITY → solo lectura (auto)
    - nombre:         VARCHAR(100) NOT NULL
    - rfc:            VARCHAR(13)  UNIQUE NULL
    - apellido_paterno: VARCHAR(50) NULL
    - apellido_materno: VARCHAR(50) NULL
    """

    def __init__(self, ventana, usuario, puesto, cb_volver):
        self.ventana   = ventana
        self.usuario   = usuario
        self.puesto    = puesto
        self.cb_volver = cb_volver
        self.dao       = ProveedorDAO()
        self._construir()

    def _construir(self):
        self.ventana.geometry("960x680")
        make_topbar(self.ventana)

        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="🏭", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Proveedores",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Tabla abuela · Sin llaves foráneas  ·  ID generado automáticamente",
                     font=("Segoe UI", 10), text_color=GRAY_TEXT).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        self._form(body)
        self._grid(body)
        self._refrescar()
        self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)

        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, width=290)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        # ID — solo lectura, IDENTITY auto
        ctk.CTkLabel(form, text="ID PROVEEDOR  (automático)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 3))
        self.ent_id = make_entry(self.ventana, form, "Se genera automáticamente")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        # Buscar por ID al salir del campo
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        # Nombre — VARCHAR(100) NOT NULL
        ctk.CTkLabel(form, text="NOMBRE  (máx. 100, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=2, column=0, sticky="w", padx=18, pady=(12, 3))
        self.ent_nombre = make_entry(self.ventana, form, "Nombre de la empresa", max_chars=100)
        self.ent_nombre.grid(row=3, column=0, sticky="ew", padx=18)

        # RFC — VARCHAR(13) UNIQUE
        ctk.CTkLabel(form, text="RFC  (máx. 13, único)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=4, column=0, sticky="w", padx=18, pady=(12, 3))
        self.ent_rfc = make_entry(self.ventana, form, "Ej. XAXX010101000", max_chars=13)
        self.ent_rfc.grid(row=5, column=0, sticky="ew", padx=18)

        # Apellido Paterno — VARCHAR(50)
        ctk.CTkLabel(form, text="APELLIDO PATERNO  (máx. 50)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=6, column=0, sticky="w", padx=18, pady=(12, 3))
        self.ent_ap = make_entry(self.ventana, form, "Apellido paterno", max_chars=50)
        self.ent_ap.grid(row=7, column=0, sticky="ew", padx=18)

        # Apellido Materno — VARCHAR(50)
        ctk.CTkLabel(form, text="APELLIDO MATERNO  (máx. 50)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=8, column=0, sticky="w", padx=18, pady=(12, 3))
        self.ent_am = make_entry(self.ventana, form, "Apellido materno", max_chars=50)
        self.ent_am.grid(row=9, column=0, sticky="ew", padx=18)

        ctk.CTkFrame(form, height=14, fg_color="transparent").grid(row=10, column=0)

        # Botones de tablas hijas: telefono, Correos
        hijos_frame = ctk.CTkFrame(form, fg_color="transparent")
        hijos_frame.grid(row=11, column=0, padx=18, pady=(0, 14), sticky="ew")
        for txt, cmd in [
            ("📞  Teléfonos",  self._ver_telefonos),
            ("📧  Correos",    self._ver_correos),
        ]:
            ctk.CTkButton(hijos_frame, text=txt, height=30,
                          fg_color=BG_INPUT, text_color=CYAN,
                          font=("Segoe UI", 10, "bold"), corner_radius=6,
                          command=cmd).pack(fill="x", pady=2)

        # Botones
        btns = ctk.CTkFrame(ba, fg_color="transparent")
        btns.pack(fill="x")
        for txt, color, cmd, r, c in [
            ("Alta",    GREEN,    self._alta,    0, 0),
            ("Cambios", PURPLE,   self._cambios, 0, 1),
            ("Baja",    RED,      self._baja,    1, 0),
            ("Limpiar", "#374151",self._limpiar, 1, 1),
        ]:
            make_boton(btns, txt, cmd, color=color).grid(row=r, column=c, padx=4, pady=4)

        ctk.CTkButton(
            ba, text="← Volver",
            height=34, fg_color="transparent",
            border_width=1, border_color=BORDER,
            text_color=GRAY_TEXT, hover_color=BG_CARD,
            corner_radius=8, font=("Segoe UI", 11),
            command=self.cb_volver
        ).pack(fill="x", pady=(10, 0))

        self.lbl_status = make_status(ba)

    def _grid(self, parent):
        right = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                             border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="REGISTROS EN BD",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=16, pady=(12, 6))
        self.tree = make_treeview(
            right,
            columnas=["ID", "Nombre", "RFC", "Ap. Paterno", "Ap. Materno"],
            anchos=[50, 180, 110, 120, 120]
        )
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, msg, color=CYAN):
        set_status(self.lbl_status, msg, color)

    def _limpiar(self):
        for e in [self.ent_id, self.ent_nombre, self.ent_rfc, self.ent_ap, self.ent_am]:
            e.delete(0, "end")
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                self.tree.insert("", "end", values=(r[0], r[1], r[2] or "", r[3] or "", r[4] or ""))
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self.ent_id.delete(0, "end");     self.ent_id.insert(0, v[0])
        self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, v[1])
        self.ent_rfc.delete(0, "end");    self.ent_rfc.insert(0, v[2])
        self.ent_ap.delete(0, "end");     self.ent_ap.insert(0, v[3])
        self.ent_am.delete(0, "end");     self.ent_am.insert(0, v[4])
        self._s(f"  Proveedor ID '{v[0]}' cargado.", GRAY_TEXT)

    def _buscar(self):
        id_txt = self.ent_id.get().strip()
        if not id_txt: return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  El ID debe ser un número entero.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, row[1] or "")
                self.ent_rfc.delete(0, "end");    self.ent_rfc.insert(0, row[2] or "")
                self.ent_ap.delete(0, "end");     self.ent_ap.insert(0, row[3] or "")
                self.ent_am.delete(0, "end");     self.ent_am.insert(0, row[4] or "")
                self._s(f"✔  Proveedor ID '{id_}' encontrado.", CYAN)
            else:
                self._s(f"⚠  No existe ningún proveedor con ID '{id_}'.", AMBER)
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _alta(self):
        nombre = self.ent_nombre.get().strip()
        rfc    = self.ent_rfc.get().strip()
        ap     = self.ent_ap.get().strip()
        am     = self.ent_am.get().strip()

        if not nombre:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED)
            self.ent_nombre.focus_set(); return

        # RFC único si se proporcionó
        if rfc and self.dao.rfc_duplicado(rfc):
            self._s(f"⚠  El RFC '{rfc}' ya está registrado (UNIQUE).", RED)
            self.ent_rfc.focus_set(); return
        try:
            self.dao.insertar(nombre, rfc, ap, am)
            self._s(f"✔  Proveedor '{nombre}' guardado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _cambios(self):
        id_txt = self.ent_id.get().strip()
        nombre = self.ent_nombre.get().strip()
        rfc    = self.ent_rfc.get().strip()
        ap     = self.ent_ap.get().strip()
        am     = self.ent_am.get().strip()

        if not id_txt:
            self._s("⚠  Selecciona un proveedor del grid para modificar.", RED); return
        if not nombre:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED)
            self.ent_nombre.focus_set(); return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  ID inválido.", RED); return

        if rfc and self.dao.rfc_duplicado(rfc, excluir_id=id_):
            self._s(f"⚠  El RFC '{rfc}' ya pertenece a otro proveedor (UNIQUE).", RED)
            self.ent_rfc.focus_set(); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, nombre, rfc, ap, am)
            self._s(f"✔  Proveedor ID '{id_}' actualizado.", GREEN)
            self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _baja(self):
        id_txt = self.ent_id.get().strip()
        if not id_txt:
            self._s("⚠  Selecciona un proveedor del grid para eliminar.", RED); return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s(f"✖  No se puede eliminar: el proveedor tiene teléfonos o correos asociados.", RED)
                return
            if not messagebox.askyesno("Confirmar baja",
                                       f"¿Eliminar al proveedor ID '{id_}'?\nEsta acción no se puede deshacer."):
                return
            self.dao.eliminar(id_)
            self._s(f"✔  Proveedor ID '{id_}' eliminado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    # ── Botones de hijos ─────────────────────────────────────────────────────
    def _validar_id(self):
        id_ = self.ent_id.get().strip()
        if not id_: self._s("⚠  Selecciona un proveedor.", RED); return None
        try: return int(id_)
        except: self._s("⚠  ID inválido.", RED); return None

    def _ver_telefonos(self):
        id_ = self._validar_id()
        if id_ is None: return
        from contacto_views import TelefonoView
        self.ventana._limpiar()
        TelefonoView(self.ventana, self.usuario, self.puesto, self.cb_volver,
                     filtro=("proveedor", id_))

    def _ver_correos(self):
        id_ = self._validar_id()
        if id_ is None: return
        from contacto_views import CorreoView
        self.ventana._limpiar()
        CorreoView(self.ventana, self.usuario, self.puesto, self.cb_volver,
                   filtro=("proveedor", id_))
