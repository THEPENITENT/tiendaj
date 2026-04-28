# inventario_view.py — CRUD inventarios (DOS FK) con scroll + validaciones CHECK
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import (make_topbar, make_entry, make_boton, make_treeview,
                     make_status, set_status, make_combo, get_combo_value,
                     set_combo_by_id, make_form_panel)
from inventario_dao import InventarioDAO


class InventarioView:
    def __init__(self, ventana, usuario, puesto, cb_volver,
                 filtro_sucursal=None, filtro_plataforma=None):
        self.ventana     = ventana; self.usuario = usuario
        self.puesto      = puesto;  self.cb_volver = cb_volver
        self.filtro_suc  = filtro_sucursal
        self.filtro_plat = filtro_plataforma
        self.dao = InventarioDAO()
        self._plataformas = {}; self._sucursales = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("980x660")
        make_topbar(self.ventana)
        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent"); hdr.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(hdr, text="📦", font=("Segoe UI",20)).pack(side="left", padx=(0,8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent"); ttl.pack(side="left")
        if self.filtro_suc:   sub = f"Filtrado por sucursal: {self.filtro_suc}"
        elif self.filtro_plat: sub = f"Filtrado por plataforma: {self.filtro_plat}"
        else: sub = "Hijo de Plataforma y Sucursal · Sin tablas hijas"
        ctk.CTkLabel(ttl, text="Mantenimiento de Inventarios",
                     font=("Segoe UI",15,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text=sub, font=("Segoe UI",10), text_color=CYAN).pack(anchor="w")
        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1); body.rowconfigure(0, weight=1)

        try:
            self._plataformas = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_plataformas()}
            self._sucursales  = {f"{r[0]} - {r[1]}": r[0] for r in self.dao.obtener_sucursales()}
        except: pass

        self._form(body); self._grid(body); self._refrescar(); self.ent_id.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)
        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=4, pady=4); form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID INVENTARIO  (automático)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=0, column=0, sticky="w", padx=18, pady=(16,3))
        self.ent_id = make_entry(self.ventana, form, "Auto")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        ctk.CTkLabel(form, text="PLATAFORMA  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=2, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_plat = make_combo(form, self._plataformas)
        self.cb_plat.grid(row=3, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="SUCURSAL  (FK obligatoria)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=4, column=0, sticky="w", padx=18, pady=(12,3))
        self.cb_suc = make_combo(form, self._sucursales)
        self.cb_suc.grid(row=5, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="NOMBRE INVENTARIO  (máx. 50, opcional)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=6, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_nombre = make_entry(self.ventana, form, "Ej. Bodega A", max_chars=50)
        self.ent_nombre.grid(row=7, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="STOCK  (NOT NULL, entero ≥ 0 — CHECK constraint)",
                     font=("Segoe UI",10,"bold"), text_color=GRAY_TEXT
                     ).grid(row=8, column=0, sticky="w", padx=18, pady=(12,3))
        self.ent_stock = make_entry(self.ventana, form, "Ej. 50", max_chars=10)
        self.ent_stock.grid(row=9, column=0, sticky="ew", padx=18, pady=(0,16))

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
            columnas=["ID","Plataforma","Sucursal","Nombre","Stock"],
            anchos=[40,140,140,180,70])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, m, c=CYAN): set_status(self.lbl_status, m, c)

    def _limpiar(self):
        for e in [self.ent_id, self.ent_nombre, self.ent_stock]: e.delete(0,"end")
        if self._plataformas: self.cb_plat.set(list(self._plataformas.keys())[0])
        if self._sucursales:  self.cb_suc.set(list(self._sucursales.keys())[0])
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                if self.filtro_suc  and r[3] != self.filtro_suc:  continue
                if self.filtro_plat and r[1] != self.filtro_plat: continue
                self.tree.insert("","end", values=(r[0], r[2], r[4], r[5] or "", r[6]))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0],"values")
        try:
            row = self.dao.buscar_por_id(int(v[0]))
            if row:
                self.ent_id.delete(0,"end");     self.ent_id.insert(0, row[0])
                set_combo_by_id(self.cb_plat, self._plataformas, row[1])
                set_combo_by_id(self.cb_suc,  self._sucursales,  row[2])
                self.ent_nombre.delete(0,"end"); self.ent_nombre.insert(0, row[3] or "")
                self.ent_stock.delete(0,"end");  self.ent_stock.insert(0, str(row[4]))
                self._s(f"  Inventario '{row[0]}' cargado.", GRAY_TEXT)
        except: pass

    def _buscar(self):
        txt = self.ent_id.get().strip()
        if not txt: return
        try: id_ = int(txt)
        except: self._s("⚠  ID debe ser número.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                set_combo_by_id(self.cb_plat, self._plataformas, row[1])
                set_combo_by_id(self.cb_suc,  self._sucursales,  row[2])
                self.ent_nombre.delete(0,"end"); self.ent_nombre.insert(0, row[3] or "")
                self.ent_stock.delete(0,"end");  self.ent_stock.insert(0, str(row[4]))
                self._s(f"✔  Inventario '{id_}' encontrado.", CYAN)
            else: self._s(f"⚠  No existe el inventario '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _validar(self):
        id_plat = get_combo_value(self.cb_plat, self._plataformas)
        id_suc  = get_combo_value(self.cb_suc,  self._sucursales)
        nom     = self.ent_nombre.get().strip()
        stxt    = self.ent_stock.get().strip()
        if not id_plat: self._s("⚠  Selecciona una plataforma (FK obligatoria).", RED); return None
        if not id_suc:  self._s("⚠  Selecciona una sucursal (FK obligatoria).", RED); return None
        if not stxt:    self._s("⚠  Stock obligatorio (NOT NULL).", RED); self.ent_stock.focus_set(); return None
        try: stock = int(stxt)
        except: self._s("⚠  Stock debe ser un número entero.", RED); self.ent_stock.focus_set(); return None
        if stock < 0:   self._s("⚠  Stock no puede ser negativo (CHECK constraint: stock ≥ 0).", RED); return None
        return id_plat, id_suc, nom, stock

    def _alta(self):
        d = self._validar()
        if d is None: return
        try:
            self.dao.insertar(*d)
            self._s("✔  Inventario guardado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        d = self._validar()
        if d is None: return
        try:
            id_ = int(txt)
            if not self.dao.existe(id_): self._s(f"⚠  Inventario '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, *d)
            self._s(f"✔  Inventario '{id_}' actualizado.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        txt = self.ent_id.get().strip()
        if not txt: self._s("⚠  Selecciona del grid.", RED); return
        try: id_ = int(txt)
        except: self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_): self._s(f"⚠  Inventario '{id_}' no existe.", RED); return
            if not messagebox.askyesno("Confirmar", f"¿Eliminar inventario '{id_}'?"): return
            self.dao.eliminar(id_)
            self._s(f"✔  Inventario '{id_}' eliminado.", GREEN); self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)
