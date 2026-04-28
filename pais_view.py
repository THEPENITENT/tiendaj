# pais_view.py — Pantalla CRUD de la tabla pais (abuela, sin FK)
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_form_panel, make_topbar, make_entry, make_boton,
                     make_treeview, make_status, set_status)
from pais_dao import PaisDAO


class PaisView:
    """
    Pantalla de mantenimiento de la tabla pais.
    - idpais:      VARCHAR(6)  → máx 6 chars
    - nombre_pais: VARCHAR(50) → máx 50 chars, NOT NULL
    Hijos: estados
    """

    def __init__(self, ventana, usuario, puesto, cb_volver):
        self.ventana   = ventana
        self.usuario   = usuario
        self.puesto    = puesto
        self.cb_volver = cb_volver
        self.dao       = PaisDAO()
        self._construir()

    def _construir(self):
        self.ventana.geometry("820x640")
        make_topbar(self.ventana)

        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        # Header
        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="🌎", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Países",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Tabla abuela · Sin llaves foráneas",
                     font=("Segoe UI", 10), text_color=GRAY_TEXT).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        self._form(body)
        self._grid(body)
        self._refrescar()
        self.ent_id.focus_set()

    # ── Formulario ────────────────────────────────────────────────────────────
    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)

        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, width=280)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        # ID — VARCHAR(6)
        ctk.CTkLabel(form, text="ID PAÍS  (máx. 6)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 3))
        self.ent_id = make_entry(self.ventana, form, "Ej. MX", max_chars=6)
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        # Nombre — VARCHAR(50) NOT NULL
        ctk.CTkLabel(form, text="NOMBRE DEL PAÍS  (máx. 50, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=2, column=0, sticky="w", padx=18, pady=(14, 3))
        self.ent_nombre = make_entry(self.ventana, form, "Ej. México", max_chars=50)
        self.ent_nombre.grid(row=3, column=0, sticky="ew", padx=18)

        ctk.CTkFrame(form, height=14, fg_color="transparent").grid(row=4, column=0)

        # Botones
        btns = ctk.CTkFrame(ba, fg_color="transparent")
        btns.pack(fill="x")
        acciones = [
            ("Alta",    GREEN,    self._alta,    0, 0),
            ("Cambios", PURPLE,   self._cambios, 0, 1),
            ("Baja",    RED,      self._baja,    1, 0),
            ("Limpiar", "#374151",self._limpiar, 1, 1),
        ]
        for txt, color, cmd, r, c in acciones:
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

    # ── Grid ──────────────────────────────────────────────────────────────────
    def _grid(self, parent):
        right = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                             border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="REGISTROS EN BD",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=16, pady=(12, 6))
        self.tree = make_treeview(right,
                                  columnas=["ID", "Nombre del País"],
                                  anchos=[80, 320])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _s(self, msg, color=CYAN):
        set_status(self.lbl_status, msg, color)

    def _limpiar(self):
        self.ent_id.delete(0, "end")
        self.ent_nombre.delete(0, "end")
        self._s("")
        self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children():
                self.tree.delete(r)
            for r in self.dao.obtener_todos():
                self.tree.insert("", "end", values=(r[0], r[1] or ""))
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], "values")
        self.ent_id.delete(0, "end");     self.ent_id.insert(0, v[0])
        self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, v[1])
        self._s(f"  Registro '{v[0]}' cargado.", GRAY_TEXT)

    def _buscar(self):
        id_ = self.ent_id.get().strip()
        if not id_:
            return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_nombre.delete(0, "end")
                self.ent_nombre.insert(0, row[1] or "")
                self._s(f"✔  País '{id_}' encontrado.", CYAN)
            else:
                self.ent_nombre.delete(0, "end")
                self._s(f"  ID '{id_}' disponible para alta.", GRAY_TEXT)
        except Exception as e:
            self._s(f"✖  {e}", RED)

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def _alta(self):
        id_    = self.ent_id.get().strip()
        nombre = self.ent_nombre.get().strip()
        if not id_:
            self._s("⚠  El ID es obligatorio (NOT NULL).", RED)
            self.ent_id.focus_set(); return
        if not nombre:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED)
            self.ent_nombre.focus_set(); return
        try:
            if self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' ya existe. No se duplica la PK.", RED)
                self.ent_id.focus_set(); return
            self.dao.insertar(id_, nombre)
            self._s(f"✔  País '{id_}' guardado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _cambios(self):
        id_    = self.ent_id.get().strip()
        nombre = self.ent_nombre.get().strip()
        if not id_:
            self._s("⚠  El ID es obligatorio.", RED)
            self.ent_id.focus_set(); return
        if not nombre:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED)
            self.ent_nombre.focus_set(); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe en la BD.", RED); return
            self.dao.actualizar(id_, nombre)
            self._s(f"✔  País '{id_}' actualizado.", GREEN)
            self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _baja(self):
        id_ = self.ent_id.get().strip()
        if not id_:
            self._s("⚠  Escribe o selecciona un ID.", RED)
            self.ent_id.focus_set(); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s(f"✖  No se puede eliminar '{id_}': tiene estados asociados (tiene hijos).", RED)
                return
            if not messagebox.askyesno("Confirmar baja",
                                       f"¿Eliminar el país '{id_}'?\nEsta acción no se puede deshacer."):
                return
            self.dao.eliminar(id_)
            self._s(f"✔  País '{id_}' eliminado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)
