# geo_views.py — Vistas de la cadena geográfica: estados, ciudad, colonia, calle
# Todas usan el mismo patrón de ClasificacionView / PaisView
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import make_form_panel, make_topbar, make_entry, make_boton, make_treeview, make_status, set_status
from geo_dao import EstadosDAO, CiudadDAO, ColoniaDAO, CalleDAO


# ── Helper para combo FK ──────────────────────────────────────────────────────
def _make_combo(parent, valores_dict, placeholder):
    """
    Crea un CTkOptionMenu con los valores de la FK.
    valores_dict: { 'ID - Nombre': id_real }
    Retorna (option_menu, dict_reverse)
    """
    opciones = list(valores_dict.keys())
    combo = ctk.CTkOptionMenu(
        parent,
        values=opciones if opciones else ["(sin registros)"],
        fg_color=BG_INPUT,
        button_color=PURPLE,
        button_hover_color=PURPLE_LT,
        dropdown_fg_color=BG_CARD,
        dropdown_hover_color=BORDER,
        text_color=WHITE,
        font=("Segoe UI", 12),
        height=40,
    )
    combo.set(placeholder if not opciones else opciones[0])
    return combo


# ═══════════════════════════════════════════════════════════════════════════════
class EstadosView:
    """
    CRUD de estados (hijo de pais).
    - idestados:     VARCHAR(6)  PK
    - pais_idpais:   VARCHAR(6)  FK (combo)
    - estadosnombre: VARCHAR(50) NOT NULL
    """

    def __init__(self, ventana, usuario, puesto, cb_volver):
        self.ventana   = ventana
        self.usuario   = usuario
        self.puesto    = puesto
        self.cb_volver = cb_volver
        self.dao       = EstadosDAO()
        self._paises   = {}   # { 'MX - México': 'MX' }
        self._construir()

    def _construir(self):
        self.ventana.geometry("900x660")
        make_topbar(self.ventana)

        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="🗺", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Estados",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Hijo de País · FK: pais_idpais",
                     font=("Segoe UI", 10), text_color=CYAN).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        self._cargar_paises()
        self._form(body)
        self._grid(body)
        self._refrescar()
        self.ent_id.focus_set()

    def _cargar_paises(self):
        try:
            rows = self.dao.obtener_paises()
            self._paises = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        except:
            self._paises = {}

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)

        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, width=290)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        # ID estado — VARCHAR(6)
        ctk.CTkLabel(form, text="ID ESTADO  (máx. 6)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 3))
        self.ent_id = make_entry(self.ventana, form, "Ej. NL", max_chars=6)
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        # País (FK) — combo
        ctk.CTkLabel(form, text="PAÍS  (FK obligatoria)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=2, column=0, sticky="w", padx=18, pady=(14, 3))
        self.combo_pais = _make_combo(form, self._paises, "Selecciona un país")
        self.combo_pais.grid(row=3, column=0, sticky="ew", padx=18)

        # Nombre estado — VARCHAR(50) NOT NULL
        ctk.CTkLabel(form, text="NOMBRE ESTADO  (máx. 50, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=4, column=0, sticky="w", padx=18, pady=(14, 3))
        self.ent_nombre = make_entry(self.ventana, form, "Ej. Nuevo León", max_chars=50)
        self.ent_nombre.grid(row=5, column=0, sticky="ew", padx=18)

        ctk.CTkFrame(form, height=14, fg_color="transparent").grid(row=6, column=0)

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
        self.tree = make_treeview(right,
                                  columnas=["ID", "ID País", "País", "Nombre Estado"],
                                  anchos=[80, 70, 130, 200])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, msg, color=CYAN): set_status(self.lbl_status, msg, color)

    def _limpiar(self):
        self.ent_id.delete(0, "end"); self.ent_nombre.delete(0, "end")
        if self._paises: self.combo_pais.set(list(self._paises.keys())[0])
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3]))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self.ent_id.delete(0, "end");     self.ent_id.insert(0, v[0])
        self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, v[3])
        # Ajustar combo al país del registro
        key = next((k for k, val in self._paises.items() if val == v[1]), None)
        if key: self.combo_pais.set(key)
        self._s(f"  Estado '{v[0]}' cargado.", GRAY_TEXT)

    def _buscar(self):
        id_ = self.ent_id.get().strip()
        if not id_: return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, row[2] or "")
                key = next((k for k, v in self._paises.items() if v == row[1]), None)
                if key: self.combo_pais.set(key)
                self._s(f"✔  Estado '{id_}' encontrado.", CYAN)
            else:
                self.ent_nombre.delete(0, "end")
                self._s(f"  ID '{id_}' disponible para alta.", GRAY_TEXT)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _get_pais(self):
        sel = self.combo_pais.get()
        return self._paises.get(sel)

    def _alta(self):
        id_ = self.ent_id.get().strip(); nom = self.ent_nombre.get().strip()
        id_pais = self._get_pais()
        if not id_:
            self._s("⚠  El ID es obligatorio.", RED); self.ent_id.focus_set(); return
        if not id_pais:
            self._s("⚠  Selecciona un país (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED); self.ent_nombre.focus_set(); return
        try:
            if self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' ya existe. No se duplica la PK.", RED)
                self.ent_id.focus_set(); return
            self.dao.insertar(id_, id_pais, nom)
            self._s(f"✔  Estado '{id_}' guardado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        id_ = self.ent_id.get().strip(); nom = self.ent_nombre.get().strip()
        id_pais = self._get_pais()
        if not id_:
            self._s("⚠  El ID es obligatorio.", RED); self.ent_id.focus_set(); return
        if not id_pais:
            self._s("⚠  Selecciona un país (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio.", RED); self.ent_nombre.focus_set(); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, id_pais, nom)
            self._s(f"✔  Estado '{id_}' actualizado.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        id_ = self.ent_id.get().strip()
        if not id_:
            self._s("⚠  Selecciona o escribe un ID.", RED); self.ent_id.focus_set(); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s(f"✖  No se puede eliminar '{id_}': tiene ciudades asociadas (tiene hijos).", RED); return
            if not messagebox.askyesno("Confirmar baja",
                                       f"¿Eliminar estado '{id_}'?\nEsta acción no se puede deshacer."):
                return
            self.dao.eliminar(id_)
            self._s(f"✔  Estado '{id_}' eliminado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)


# ═══════════════════════════════════════════════════════════════════════════════
class CiudadView:
    """
    CRUD de ciudad (hijo de estados).
    - idciudad:          INT IDENTITY PK (auto)
    - estados_idestados: VARCHAR(6) FK (combo)
    - nombre_ciudad:     VARCHAR(50) NOT NULL
    """

    def __init__(self, ventana, usuario, puesto, cb_volver):
        self.ventana   = ventana
        self.usuario   = usuario
        self.puesto    = puesto
        self.cb_volver = cb_volver
        self.dao       = CiudadDAO()
        self._estados  = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("900x660")
        make_topbar(self.ventana)

        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="🏙", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Ciudades",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Hijo de Estado · FK: estados_idestados",
                     font=("Segoe UI", 10), text_color=CYAN).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        self._cargar_estados()
        self._form(body)
        self._grid(body)
        self._refrescar()
        self.ent_id.focus_set()

    def _cargar_estados(self):
        try:
            rows = self.dao.obtener_estados()
            self._estados = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        except:
            self._estados = {}

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)

        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, width=290)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        # ID — IDENTITY, buscar
        ctk.CTkLabel(form, text="ID CIUDAD  (automático)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 3))
        self.ent_id = make_entry(self.ventana, form, "Se genera automáticamente")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        # Estado (FK)
        ctk.CTkLabel(form, text="ESTADO  (FK obligatoria)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=2, column=0, sticky="w", padx=18, pady=(14, 3))
        self.combo_estado = _make_combo(form, self._estados, "Selecciona un estado")
        self.combo_estado.grid(row=3, column=0, sticky="ew", padx=18)

        # Nombre ciudad — VARCHAR(50) NOT NULL
        ctk.CTkLabel(form, text="NOMBRE CIUDAD  (máx. 50, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=4, column=0, sticky="w", padx=18, pady=(14, 3))
        self.ent_nombre = make_entry(self.ventana, form, "Ej. Monterrey", max_chars=50)
        self.ent_nombre.grid(row=5, column=0, sticky="ew", padx=18)

        ctk.CTkFrame(form, height=14, fg_color="transparent").grid(row=6, column=0)

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
        self.tree = make_treeview(right,
                                  columnas=["ID", "ID Estado", "Estado", "Nombre Ciudad"],
                                  anchos=[60, 80, 150, 200])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, msg, color=CYAN): set_status(self.lbl_status, msg, color)

    def _limpiar(self):
        self.ent_id.delete(0, "end"); self.ent_nombre.delete(0, "end")
        if self._estados: self.combo_estado.set(list(self._estados.keys())[0])
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3]))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self.ent_id.delete(0, "end");     self.ent_id.insert(0, v[0])
        self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, v[3])
        key = next((k for k, val in self._estados.items() if val == v[1]), None)
        if key: self.combo_estado.set(key)
        self._s(f"  Ciudad ID '{v[0]}' cargada.", GRAY_TEXT)

    def _buscar(self):
        id_txt = self.ent_id.get().strip()
        if not id_txt: return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  El ID debe ser un número.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, row[2] or "")
                key = next((k for k, v in self._estados.items() if v == row[1]), None)
                if key: self.combo_estado.set(key)
                self._s(f"✔  Ciudad ID '{id_}' encontrada.", CYAN)
            else:
                self._s(f"⚠  No existe ciudad con ID '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _get_estado(self):
        return self._estados.get(self.combo_estado.get())

    def _alta(self):
        nom = self.ent_nombre.get().strip(); id_est = self._get_estado()
        if not id_est:
            self._s("⚠  Selecciona un estado (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED); self.ent_nombre.focus_set(); return
        try:
            self.dao.insertar(id_est, nom)
            self._s(f"✔  Ciudad '{nom}' guardada.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        id_txt = self.ent_id.get().strip(); nom = self.ent_nombre.get().strip()
        id_est = self._get_estado()
        if not id_txt:
            self._s("⚠  Selecciona una ciudad del grid.", RED); return
        if not id_est:
            self._s("⚠  Selecciona un estado (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio.", RED); self.ent_nombre.focus_set(); return
        try:
            id_ = int(id_txt)
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, id_est, nom)
            self._s(f"✔  Ciudad ID '{id_}' actualizada.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        id_txt = self.ent_id.get().strip()
        if not id_txt:
            self._s("⚠  Selecciona una ciudad del grid.", RED); return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s(f"✖  No se puede eliminar: tiene colonias asociadas (tiene hijos).", RED); return
            if not messagebox.askyesno("Confirmar baja",
                                       f"¿Eliminar ciudad ID '{id_}'?\nEsta acción no se puede deshacer."):
                return
            self.dao.eliminar(id_)
            self._s(f"✔  Ciudad ID '{id_}' eliminada.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)


# ═══════════════════════════════════════════════════════════════════════════════
class ColoniaView:
    """
    CRUD de colonia (hijo de ciudad).
    - idcolonia:       VARCHAR(10) PK
    - ciudad_idciudad: INT FK (combo)
    - nombrecolonia:   VARCHAR(50) NOT NULL
    """

    def __init__(self, ventana, usuario, puesto, cb_volver):
        self.ventana   = ventana
        self.usuario   = usuario
        self.puesto    = puesto
        self.cb_volver = cb_volver
        self.dao       = ColoniaDAO()
        self._ciudades = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("900x660")
        make_topbar(self.ventana)

        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="🏘", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Colonias",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Hijo de Ciudad · FK: ciudad_idciudad",
                     font=("Segoe UI", 10), text_color=CYAN).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        self._cargar_ciudades()
        self._form(body)
        self._grid(body)
        self._refrescar()
        self.ent_id.focus_set()

    def _cargar_ciudades(self):
        try:
            rows = self.dao.obtener_ciudades()
            self._ciudades = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        except:
            self._ciudades = {}

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)

        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, width=290)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID COLONIA  (máx. 10)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 3))
        self.ent_id = make_entry(self.ventana, form, "Ej. 64000", max_chars=10)
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        ctk.CTkLabel(form, text="CIUDAD  (FK obligatoria)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=2, column=0, sticky="w", padx=18, pady=(14, 3))
        self.combo_ciudad = _make_combo(form, self._ciudades, "Selecciona una ciudad")
        self.combo_ciudad.grid(row=3, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="NOMBRE COLONIA  (máx. 50, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=4, column=0, sticky="w", padx=18, pady=(14, 3))
        self.ent_nombre = make_entry(self.ventana, form, "Ej. Centro", max_chars=50)
        self.ent_nombre.grid(row=5, column=0, sticky="ew", padx=18)

        ctk.CTkFrame(form, height=14, fg_color="transparent").grid(row=6, column=0)

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
        self.tree = make_treeview(right,
                                  columnas=["ID", "ID Ciudad", "Ciudad", "Nombre Colonia"],
                                  anchos=[90, 70, 140, 190])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, msg, color=CYAN): set_status(self.lbl_status, msg, color)

    def _limpiar(self):
        self.ent_id.delete(0, "end"); self.ent_nombre.delete(0, "end")
        if self._ciudades: self.combo_ciudad.set(list(self._ciudades.keys())[0])
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3]))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self.ent_id.delete(0, "end");     self.ent_id.insert(0, v[0])
        self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, v[3])
        key = next((k for k, val in self._ciudades.items() if str(val) == str(v[1])), None)
        if key: self.combo_ciudad.set(key)
        self._s(f"  Colonia '{v[0]}' cargada.", GRAY_TEXT)

    def _buscar(self):
        id_ = self.ent_id.get().strip()
        if not id_: return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, row[2] or "")
                key = next((k for k, v in self._ciudades.items() if str(v) == str(row[1])), None)
                if key: self.combo_ciudad.set(key)
                self._s(f"✔  Colonia '{id_}' encontrada.", CYAN)
            else:
                self.ent_nombre.delete(0, "end")
                self._s(f"  ID '{id_}' disponible para alta.", GRAY_TEXT)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _get_ciudad(self):
        return self._ciudades.get(self.combo_ciudad.get())

    def _alta(self):
        id_ = self.ent_id.get().strip(); nom = self.ent_nombre.get().strip()
        id_ciudad = self._get_ciudad()
        if not id_:
            self._s("⚠  El ID es obligatorio.", RED); self.ent_id.focus_set(); return
        if not id_ciudad:
            self._s("⚠  Selecciona una ciudad (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED); self.ent_nombre.focus_set(); return
        try:
            if self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' ya existe. No se duplica la PK.", RED)
                self.ent_id.focus_set(); return
            self.dao.insertar(id_, id_ciudad, nom)
            self._s(f"✔  Colonia '{id_}' guardada.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        id_ = self.ent_id.get().strip(); nom = self.ent_nombre.get().strip()
        id_ciudad = self._get_ciudad()
        if not id_:
            self._s("⚠  El ID es obligatorio.", RED); self.ent_id.focus_set(); return
        if not id_ciudad:
            self._s("⚠  Selecciona una ciudad (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio.", RED); self.ent_nombre.focus_set(); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, id_ciudad, nom)
            self._s(f"✔  Colonia '{id_}' actualizada.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        id_ = self.ent_id.get().strip()
        if not id_:
            self._s("⚠  Selecciona o escribe un ID.", RED); self.ent_id.focus_set(); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s(f"✖  No se puede eliminar '{id_}': tiene calles asociadas (tiene hijos).", RED); return
            if not messagebox.askyesno("Confirmar baja",
                                       f"¿Eliminar colonia '{id_}'?\nEsta acción no se puede deshacer."):
                return
            self.dao.eliminar(id_)
            self._s(f"✔  Colonia '{id_}' eliminada.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)


# ═══════════════════════════════════════════════════════════════════════════════
class CalleView:
    """
    CRUD de calle (hijo de colonia, fin de la cadena geográfica).
    - idcalle:           INT IDENTITY PK (auto)
    - colonia_idcolonia: VARCHAR(10) FK (combo)
    - nombrecalle:       VARCHAR(100) NOT NULL
    """

    def __init__(self, ventana, usuario, puesto, cb_volver):
        self.ventana   = ventana
        self.usuario   = usuario
        self.puesto    = puesto
        self.cb_volver = cb_volver
        self.dao       = CalleDAO()
        self._colonias = {}
        self._construir()

    def _construir(self):
        self.ventana.geometry("900x660")
        make_topbar(self.ventana)

        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="🛣", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Calles",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Hijo de Colonia · FK: colonia_idcolonia",
                     font=("Segoe UI", 10), text_color=CYAN).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        self._cargar_colonias()
        self._form(body)
        self._grid(body)
        self._refrescar()
        self.ent_id.focus_set()

    def _cargar_colonias(self):
        try:
            rows = self.dao.obtener_colonias()
            self._colonias = {f"{r[0]} - {r[1]}": r[0] for r in rows}
        except:
            self._colonias = {}

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)

        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, width=290)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="ID CALLE  (automático)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 3))
        self.ent_id = make_entry(self.ventana, form, "Se genera automáticamente")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        ctk.CTkLabel(form, text="COLONIA  (FK obligatoria)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=2, column=0, sticky="w", padx=18, pady=(14, 3))
        self.combo_colonia = _make_combo(form, self._colonias, "Selecciona una colonia")
        self.combo_colonia.grid(row=3, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(form, text="NOMBRE CALLE  (máx. 100, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=4, column=0, sticky="w", padx=18, pady=(14, 3))
        self.ent_nombre = make_entry(self.ventana, form, "Ej. Av. Constitución", max_chars=100)
        self.ent_nombre.grid(row=5, column=0, sticky="ew", padx=18)

        ctk.CTkFrame(form, height=14, fg_color="transparent").grid(row=6, column=0)

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
        self.tree = make_treeview(right,
                                  columnas=["ID", "ID Colonia", "Colonia", "Nombre Calle"],
                                  anchos=[60, 90, 150, 200])
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, msg, color=CYAN): set_status(self.lbl_status, msg, color)

    def _limpiar(self):
        self.ent_id.delete(0, "end"); self.ent_nombre.delete(0, "end")
        if self._colonias: self.combo_colonia.set(list(self._colonias.keys())[0])
        self._s(""); self.ent_id.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_todos():
                self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3]))
        except Exception as e: self._s(f"✖  {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self.ent_id.delete(0, "end");     self.ent_id.insert(0, v[0])
        self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, v[3])
        key = next((k for k, val in self._colonias.items() if str(val) == str(v[1])), None)
        if key: self.combo_colonia.set(key)
        self._s(f"  Calle ID '{v[0]}' cargada.", GRAY_TEXT)

    def _buscar(self):
        id_txt = self.ent_id.get().strip()
        if not id_txt: return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  El ID debe ser un número.", RED); return
        try:
            row = self.dao.buscar_por_id(id_)
            if row:
                self.ent_nombre.delete(0, "end"); self.ent_nombre.insert(0, row[2] or "")
                key = next((k for k, v in self._colonias.items() if str(v) == str(row[1])), None)
                if key: self.combo_colonia.set(key)
                self._s(f"✔  Calle ID '{id_}' encontrada.", CYAN)
            else:
                self._s(f"⚠  No existe calle con ID '{id_}'.", AMBER)
        except Exception as e: self._s(f"✖  {e}", RED)

    def _get_colonia(self):
        return self._colonias.get(self.combo_colonia.get())

    def _alta(self):
        nom = self.ent_nombre.get().strip(); id_col = self._get_colonia()
        if not id_col:
            self._s("⚠  Selecciona una colonia (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio (NOT NULL).", RED); self.ent_nombre.focus_set(); return
        try:
            self.dao.insertar(id_col, nom)
            self._s(f"✔  Calle '{nom}' guardada.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _cambios(self):
        id_txt = self.ent_id.get().strip(); nom = self.ent_nombre.get().strip()
        id_col = self._get_colonia()
        if not id_txt:
            self._s("⚠  Selecciona una calle del grid.", RED); return
        if not id_col:
            self._s("⚠  Selecciona una colonia (FK obligatoria).", RED); return
        if not nom:
            self._s("⚠  El nombre es obligatorio.", RED); self.ent_nombre.focus_set(); return
        try:
            id_ = int(id_txt)
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, id_col, nom)
            self._s(f"✔  Calle ID '{id_}' actualizada.", GREEN); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)

    def _baja(self):
        id_txt = self.ent_id.get().strip()
        if not id_txt:
            self._s("⚠  Selecciona una calle del grid.", RED); return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.existe(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s(f"✖  No se puede eliminar: la calle está en uso (sucursales, clientes o empleados).", RED)
                return
            if not messagebox.askyesno("Confirmar baja",
                                       f"¿Eliminar calle ID '{id_}'?\nEsta acción no se puede deshacer."):
                return
            self.dao.eliminar(id_)
            self._s(f"✔  Calle ID '{id_}' eliminada.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e: self._s(f"✖  {e}", RED)
