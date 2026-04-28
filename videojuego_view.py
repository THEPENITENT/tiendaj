# videojuego_view.py — CRUD de Videojuego (hijo de clasificacion)
import customtkinter as ctk
from tkinter import messagebox
from colores import *
from widgets import make_form_panel, make_topbar, make_entry, make_boton, make_treeview, make_status, set_status
from videojuego_dao import VideojuegoDAO


class VideojuegoView:
    """
    Pantalla CRUD de la tabla Videojuego.
    - idVideojuego:                INT IDENTITY (auto)
    - clasificacion_idclasificacion: VARCHAR(5) FK → mostrado como referencia
    - Titulo:                      VARCHAR(150) NOT NULL
    - Precio:                      DECIMAL(10,2) NOT NULL, > 0
    - FechaLanzamiento:            DATE NULL
    Hijos: Plataforma (próximamente)
    Volver: regresa a ClasificacionView con la clasificación padre
    """

    def __init__(self, ventana, usuario, puesto, cb_volver, id_clasificacion):
        self.ventana   = ventana
        self.usuario   = usuario
        self.puesto    = puesto
        self.cb_volver = cb_volver        # regresa al menú principal
        self.id_clas   = id_clasificacion
        self.dao       = VideojuegoDAO()
        self._construir()

    def _construir(self):
        self.ventana.geometry("960x680")
        make_topbar(self.ventana)

        wrap = ctk.CTkFrame(self.ventana, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=16)

        # Header
        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="🎮", font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Mantenimiento de Videojuegos",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl,
                     text=f"Hijo de Clasificación · FK: {self.id_clas}",
                     font=("Segoe UI", 10), text_color=CYAN).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        body = ctk.CTkFrame(wrap, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        self._form(body)
        self._grid(body)
        self._refrescar()
        self.ent_titulo.focus_set()

    def _form(self, parent):
        left, sf, ba = make_form_panel(parent)

        form = ctk.CTkFrame(sf, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color=BORDER, width=290)
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        # ID — IDENTITY, solo lectura
        ctk.CTkLabel(form, text="ID VIDEOJUEGO  (automático)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 3))
        self.ent_id = make_entry(self.ventana, form, "Se genera automáticamente")
        self.ent_id.grid(row=1, column=0, sticky="ew", padx=18)
        self.ent_id.bind("<FocusOut>", lambda e: self._buscar())
        self.ent_id.bind("<Return>",   lambda e: self._buscar())

        # Título — VARCHAR(150) NOT NULL
        ctk.CTkLabel(form, text="TÍTULO  (máx. 150, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=2, column=0, sticky="w", padx=18, pady=(12, 3))
        self.ent_titulo = make_entry(self.ventana, form, "Nombre del videojuego", max_chars=150)
        self.ent_titulo.grid(row=3, column=0, sticky="ew", padx=18)

        # Precio — DECIMAL NOT NULL > 0
        ctk.CTkLabel(form, text="PRECIO  (decimal, > 0, NOT NULL)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=4, column=0, sticky="w", padx=18, pady=(12, 3))
        self.ent_precio = make_entry(self.ventana, form, "Ej. 999.99", max_chars=12)
        self.ent_precio.grid(row=5, column=0, sticky="ew", padx=18)

        # Fecha Lanzamiento — DATE NULL
        ctk.CTkLabel(form, text="FECHA LANZAMIENTO  (YYYY-MM-DD, opcional)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).grid(row=6, column=0, sticky="w", padx=18, pady=(12, 3))
        self.ent_fecha = make_entry(self.ventana, form, "Ej. 2024-03-15", max_chars=10)
        self.ent_fecha.grid(row=7, column=0, sticky="ew", padx=18)

        ctk.CTkFrame(form, height=14, fg_color="transparent").grid(row=8, column=0)

        # Botones de tablas hijas: Plataforma, Detalle_Ventas
        hijos_frame = ctk.CTkFrame(form, fg_color="transparent")
        hijos_frame.grid(row=9, column=0, padx=18, pady=(0, 14), sticky="ew")
        for txt, cmd in [
            ("🕹  Plataformas",       self._ver_plataformas),
            ("📋  Detalle de Ventas", self._ver_detalle_ventas),
        ]:
            ctk.CTkButton(hijos_frame, text=txt, height=30,
                          fg_color=BG_INPUT, text_color=CYAN,
                          font=("Segoe UI", 10, "bold"), corner_radius=6,
                          command=cmd).pack(fill="x", pady=2)

        # Botonera CRUD
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
            left, text="← Volver a Clasificaciones",
            height=34, fg_color="transparent",
            border_width=1, border_color=BORDER,
            text_color=GRAY_TEXT, hover_color=BG_CARD,
            corner_radius=8, font=("Segoe UI", 11),
            command=self._volver_padre
        ).pack(fill="x", pady=(10, 0))

        self.lbl_status = make_status(ba)

    def _grid(self, parent):
        right = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                             border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text=f"VIDEOJUEGOS DE CLASIFICACIÓN: {self.id_clas}",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=16, pady=(12, 6))
        self.tree = make_treeview(
            right,
            columnas=["ID", "Título", "Precio", "Lanzamiento"],
            anchos=[50, 240, 90, 110]
        )
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sel_fila())

    def _s(self, msg, color=CYAN):
        set_status(self.lbl_status, msg, color)

    def _limpiar(self):
        for e in [self.ent_id, self.ent_titulo, self.ent_precio, self.ent_fecha]:
            e.delete(0, "end")
        self._s(""); self.ent_titulo.focus_set()

    def _refrescar(self):
        try:
            for r in self.tree.get_children(): self.tree.delete(r)
            for r in self.dao.obtener_por_clasificacion(self.id_clas):
                precio = r[2] if r[2] is not None else 0
                fecha  = str(r[3]) if r[3] else ""
                self.tree.insert("", "end",
                                 values=(r[0], r[1] or "", f"${precio:,.2f}", fecha))
        except Exception as e:
            self._s(f"✖  Error al cargar: {e}", RED)

    def _sel_fila(self):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self.ent_id.delete(0, "end");     self.ent_id.insert(0, v[0])
        self.ent_titulo.delete(0, "end"); self.ent_titulo.insert(0, v[1])
        # Limpia formato de precio para edición
        precio_limpio = v[2].replace("$", "").replace(",", "")
        self.ent_precio.delete(0, "end"); self.ent_precio.insert(0, precio_limpio)
        self.ent_fecha.delete(0, "end");  self.ent_fecha.insert(0, v[3])
        self._s(f"  Videojuego ID '{v[0]}' cargado.", GRAY_TEXT)

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
                self.ent_titulo.delete(0, "end"); self.ent_titulo.insert(0, row[2] or "")
                self.ent_precio.delete(0, "end"); self.ent_precio.insert(0, str(row[3]) if row[3] else "")
                self.ent_fecha.delete(0, "end");  self.ent_fecha.insert(0, str(row[4]) if row[4] else "")
                self._s(f"✔  Videojuego ID '{id_}' encontrado.", CYAN)
            else:
                self._s(f"⚠  No existe videojuego con ID '{id_}'.", AMBER)
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _validar_precio(self, txt):
        """Valida que el precio sea decimal positivo."""
        try:
            p = float(txt)
            if p <= 0:
                self._s("⚠  El precio debe ser mayor a 0 (CHECK constraint).", RED)
                self.ent_precio.focus_set(); return None
            return p
        except ValueError:
            self._s("⚠  El precio debe ser un número decimal (Ej. 999.99).", RED)
            self.ent_precio.focus_set(); return None

    def _alta(self):
        titulo = self.ent_titulo.get().strip()
        precio_txt = self.ent_precio.get().strip()
        fecha  = self.ent_fecha.get().strip() or None

        if not titulo:
            self._s("⚠  El título es obligatorio (NOT NULL).", RED)
            self.ent_titulo.focus_set(); return
        if not precio_txt:
            self._s("⚠  El precio es obligatorio (NOT NULL).", RED)
            self.ent_precio.focus_set(); return

        precio = self._validar_precio(precio_txt)
        if precio is None: return

        try:
            self.dao.insertar(self.id_clas, titulo, precio, fecha)
            self._s(f"✔  Videojuego '{titulo}' guardado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _cambios(self):
        id_txt = self.ent_id.get().strip()
        titulo = self.ent_titulo.get().strip()
        precio_txt = self.ent_precio.get().strip()
        fecha  = self.ent_fecha.get().strip() or None

        if not id_txt:
            self._s("⚠  Selecciona un videojuego del grid.", RED); return
        if not titulo:
            self._s("⚠  El título es obligatorio (NOT NULL).", RED)
            self.ent_titulo.focus_set(); return
        if not precio_txt:
            self._s("⚠  El precio es obligatorio (NOT NULL).", RED)
            self.ent_precio.focus_set(); return

        precio = self._validar_precio(precio_txt)
        if precio is None: return

        try:
            id_ = int(id_txt)
            if not self.dao.buscar_por_id(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            self.dao.actualizar(id_, titulo, precio, fecha)
            self._s(f"✔  Videojuego ID '{id_}' actualizado.", GREEN)
            self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _baja(self):
        id_txt = self.ent_id.get().strip()
        if not id_txt:
            self._s("⚠  Selecciona un videojuego del grid.", RED); return
        try:
            id_ = int(id_txt)
        except ValueError:
            self._s("⚠  ID inválido.", RED); return
        try:
            if not self.dao.buscar_por_id(id_):
                self._s(f"⚠  El ID '{id_}' no existe.", RED); return
            if self.dao.tiene_hijos(id_):
                self._s(f"✖  No se puede eliminar: el videojuego tiene plataformas o ventas asociadas.", RED)
                return
            if not messagebox.askyesno("Confirmar baja",
                                       f"¿Eliminar el videojuego ID '{id_}'?\nEsta acción no se puede deshacer."):
                return
            self.dao.eliminar(id_)
            self._s(f"✔  Videojuego ID '{id_}' eliminado.", GREEN)
            self._limpiar(); self._refrescar()
        except Exception as e:
            self._s(f"✖  {e}", RED)

    def _volver_padre(self):
        from clasificacion_view import ClasificacionView
        self.ventana._limpiar()
        ClasificacionView(self.ventana, self.usuario, self.puesto, self.cb_volver)

    # ── Botones de hijos ─────────────────────────────────────────────────────
    def _validar_id(self):
        id_ = self.ent_id.get().strip()
        if not id_: self._s("⚠  Selecciona un videojuego.", RED); return None
        try: return int(id_)
        except: self._s("⚠  ID inválido.", RED); return None

    def _ver_plataformas(self):
        id_ = self._validar_id()
        if id_ is None: return
        from plataforma_view import PlataformaView
        self.ventana._limpiar()
        PlataformaView(self.ventana, self.usuario, self.puesto, self.cb_volver,
                       id_videojuego=id_)

    def _ver_detalle_ventas(self):
        id_ = self._validar_id()
        if id_ is None: return
        from detalle_venta_view import DetalleVentaView
        self.ventana._limpiar()
        DetalleVentaView(self.ventana, self.usuario, self.puesto, self.cb_volver,
                         filtro_videojuego=id_)
