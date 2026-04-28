# plataforma_view.py — CRUD Plataforma con scroll + validaciones
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_topbar, make_entry, make_boton, make_treeview,
                     make_status, set_status, make_combo, get_combo_value,
                     set_combo_by_id, make_form_panel)
from plataforma_dao import PlataformaDAO


class PlataformaView:
    def __init__(self, ventana, usuario, puesto, cb_volver, id_videojuego=None):
        self.ventana   = ventana; self.usuario = usuario
        self.puesto    = puesto;  self.cb_volver = cb_volver
        self.id_vid    = id_videojuego
        self.dao = PlataformaDAO(); self._videojuegos = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("920x660")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="🕹", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        sub = f"Filtrado por videojuego: {self.id_vid}" if self.id_vid else "Hijo de Videojuego · Padre de inventarios"
        ctk.CTkLabel(ttl, text="Mantenimiento de Plataformas",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text=sub, font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        try:
            self._videojuegos = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_videojuegos()}
        except: self._videojuegos = {}

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID PLATAFORMA  (PK manual, NOT NULL, máx. 50)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Ej. PS5_001", max_chars=50)
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        ctk.CTkLabel(form, text="VIDEOJUEGO  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=2, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_vid = make_combo(form, self._videojuegos)
        self.cb_vid.grid(row=3, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="NOMBRE  (máx. 50, opcional)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=4, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_nombre = make_entry(self.ventana, form, "Ej. PlayStation 5", max_chars=50)
        self.ent_nombre.grid(row=5, column=0, sticky="ew", padx=18, pady=(0,16))

        ctk.CTkLabel(sf, text="VER TABLAS HIJAS", font=("Segoe UI",9,"bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=4, pady=(14,4))
        ctk.CTkButton(sf, text="📦  Inventarios", height=32,
                      fg_color=BG_INPUT, text_color=CYAN,
                      font=("Segoe UI",10,"bold"), corner_radius=6,
                      command=self._ver_inventarios).pack(fill="x", padx=4, pady=2)

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
            columnas=["ID Plataforma","Videojuego","Nombre"],
            anchos=[150,120,220])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _limpiar(self):
        self.ent_id.delete(0,"end"); self.ent_nombre.delete(0,"end")
        if self._videojuegos: self.cb_vid.set(list(self._videojuegos.keys())[0])
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            if self.id_vid:
                rows = self.dao.obtener_por_videojuego(self.id_vid)
                for r in rows:
                    self.tree.insert("","end", values=(r[0], r[1], r[2] or ""))
            else:
                from conexion import obtener_conexion
                con = obtener_conexion(); cur = con.cursor()
                cur.execute("SELECT idPlataforma, Videojuego_idVideojuego, Nombre FROM Plataforma ORDER BY idPlataforma")
                for r in cur.fetchall():
                    self.tree.insert("","end", values=(r[0], r[1], r[2] or ""))
                con.close()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        self.ent_id.delete(0,"end");     self.ent_id.insert(0, v[0])
        set_combo_by_id(self.cb_vid, self._videojuegos, v[1])
        self.ent_nombre.delete(0,"end"); self.ent_nombre.insert(0, v[2])
        self._s(f"  Plataforma '{v[0]}' cargada.", GRAY_TEXT)

    def _buscar(self):
        id_ = self.ent_id.get().strip()
        if not id_: return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                set_combo_by_id(self.cb_vid, self._videojuegos, row[1])
                self.ent_nombre.delete(0,"end"); self.ent_nombre.insert(0, row[2] or "")
                self._s(f"✔  Plataforma '{id_}' encontrada.", CYAN)
            else: self._s(f"  ID '{id_}' disponible para alta.", GRAY_TEXT)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _validar(self):
        id_ = self.ent_id.get().strip()
        id_vid = get_combo_value(self.cb_vid, self._videojuegos)
        if not id_:    self._s("⚠  ID de plataforma obligatorio (PK).", RED); self.ent_id.focus_set(); return None
        if not id_vid: self._s("⚠  Selecciona un videojuego (FK obligatoria).", RED); return None
        return id_, id_vid, self.ent_nombre.get().strip()

    def _alta(self):
        d = self._validar()
        if d is None: return
        try:
            if self.dao.existe(d[0]):
                self._s(f"⚠  El ID '{d[0]}' ya existe (PK duplicada).", RED); self.ent_id.focus_set(); return
            self.dao.insertar(*d)
            self._s(f"✔  Plataforma '{d[0]}' dada de alta.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        d = self._validar()
        if d is None: return
        try:
            if not self.dao.existe(d[0]): self._s(f"⚠  ID '{d[0]}' no existe.", RED); return
            self.dao.actualizar(*d)
            self._s(f"✔  Plataforma '{d[0]}' actualizada.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        id_ = self.ent_id.get().strip()
        if not id_: self._s("⚠  Selecciona del grid.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s("✖  No se puede eliminar: la plataforma tiene inventarios asociados.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar plataforma '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Plataforma '{id_}' eliminada.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _ver_inventarios(self):
        id_ = self.ent_id.get().strip()
        if not id_: self._s("⚠  Selecciona una plataforma del grid.", RED); return
        from inventario_view import InventarioView
        self.ventana._limpiar()
        InventarioView(self.ventana, self.usuario, self.puesto, self.cb_volver, filtro_plataforma=id_)
