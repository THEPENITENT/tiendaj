import customtkinter as ctk
from tkinter import messagebox
from login_dao import LoginDAO
from colores import *

# Vistas - catálogos base
from clasificacion_view import ClasificacionView
from videojuego_view     import VideojuegoView
from genero_view         import GeneroView
from proveedor_view      import ProveedorView

# Vistas - geográficos
from pais_view           import PaisView
from geo_views           import EstadosView, CiudadView, ColoniaView, CalleView

# Vistas - principales
from sucursal_view       import SucursalView
from cliente_view        import ClienteView
from empleado_view       import EmpleadoView
from plataforma_view     import PlataformaView
from inventario_view     import InventarioView

# Vistas - ventas
from venta_view          import VentaView
from detalle_venta_view  import DetalleVentaView

# Vistas - contacto
from contacto_views      import TelefonoView, CorreoView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """
    Ventana principal. Gestiona navegación entre todas las pantallas.
    resizable(True, True) para que el usuario pueda maximizar/minimizar.
    """

    def __init__(self):
        super().__init__()
        self.title("Videogames Saltillo")
        self.configure(fg_color=BG_DARK)
        self.resizable(True, True)          # ← resize habilitado
        self.minsize(480, 520)              # tamaño mínimo para que no rompa el layout

        self._usuario = ""
        self._puesto  = ""
        self._mostrar_login()

    # ── Utilidades ────────────────────────────────────────────────────────────
    def _limpiar(self):
        for w in self.winfo_children():
            w.destroy()

    def _topbar(self):
        ctk.CTkFrame(self, height=3, fg_color=CYAN, corner_radius=0).pack(
            fill="x", side="top")

    def _entry(self, parent, placeholder, show=None, max_chars=None):
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            show=show or "",
            height=42,
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            corner_radius=8,
            font=("Segoe UI", 13),
            text_color=WHITE,
        )
        if max_chars:
            vcmd = self.register(lambda P: len(P) <= max_chars)
            e._entry.configure(validate="key", validatecommand=(vcmd, "%P"))
        return e

    # ═══════════════════════════════════════════════════════════════════════════
    # PANTALLA 1 · LOGIN
    # ═══════════════════════════════════════════════════════════════════════════
    def _mostrar_login(self):
        self._limpiar()
        self.geometry("480x600")
        self._topbar()

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=50, pady=40)

        ctk.CTkLabel(wrap, text="🎮", font=("Segoe UI", 42)).pack(pady=(10, 6))
        ctk.CTkLabel(wrap, text="VIDEOGAMES SALTILLO",
                     font=("Segoe UI", 20, "bold"), text_color=WHITE).pack(pady=(0, 4))
        ctk.CTkLabel(wrap, text="Inicia sesión para continuar",
                     font=("Segoe UI", 12), text_color=GRAY_TEXT).pack(pady=(0, 20))

        card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=10)

        # ID empleado — el campo acepta números (idempleados INT)
        ctk.CTkLabel(card, text="ID DE EMPLEADO",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=24, pady=(20, 4))
        self.user_entry = self._entry(card, "Ingresa tu ID", max_chars=10)
        self.user_entry.pack(fill="x", padx=24)

        # Contraseña — VARCHAR(100)
        ctk.CTkLabel(card, text="CONTRASEÑA  (máx. 100)",
                     font=("Segoe UI", 10, "bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", padx=24, pady=(14, 4))
        self.pass_entry = self._entry(card, "••••••••", show="•", max_chars=100)
        self.pass_entry.pack(fill="x", padx=24)

        self.pass_entry.bind("<Return>", lambda e: self._validar_login())

        ctk.CTkButton(
            card, text="INICIAR SESIÓN  →", height=46,
            font=("Segoe UI", 14, "bold"),
            fg_color=PURPLE, hover_color=PURPLE_LT,
            corner_radius=10, command=self._validar_login,
        ).pack(fill="x", padx=24, pady=(18, 24))

        ctk.CTkLabel(wrap, text="Sistema de Gestión v1.0  ·  Tec Saltillo",
                     font=("Segoe UI", 10), text_color=GRAY_TEXT).pack(pady=(16, 0))

        self.user_entry.focus_set()

    def _validar_login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()

        if not u or not p:
            messagebox.showwarning("Campos vacíos", "Ingresa ID y contraseña.")
            return
        if len(p) > 100:
            messagebox.showwarning("Límite excedido",
                                   "La contraseña excede los 100 caracteres permitidos.")
            return

        exito, resultado = LoginDAO().verificar_credenciales(u, p)
        if exito:
            self._usuario = u
            self._puesto  = resultado
            self._mostrar_menu()
        else:
            messagebox.showerror("Acceso denegado", resultado)

    # ═══════════════════════════════════════════════════════════════════════════
    # PANTALLA 2 · MENÚ PRINCIPAL
    # ═══════════════════════════════════════════════════════════════════════════
    def _mostrar_menu(self):
        self._limpiar()
        self.geometry("620x780")
        self._topbar()

        # Header usuario (fuera del scroll)
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=40, pady=(20, 20))

        hdr = ctk.CTkFrame(outer, fg_color=BG_CARD, corner_radius=12,
                           border_width=1, border_color=BORDER)
        hdr.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(hdr, text="🎮", font=("Segoe UI", 28)).pack(
            side="left", padx=16, pady=12)
        info = ctk.CTkFrame(hdr, fg_color="transparent")
        info.pack(side="left", pady=12)
        ctk.CTkLabel(info, text=f"Bienvenido, {self._usuario}",
                     font=("Segoe UI", 15, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(info, text=self._puesto.upper(),
                     font=("Segoe UI", 10, "bold"), text_color=CYAN).pack(anchor="w")

        # Frame scrollable para el menú
        wrap = ctk.CTkScrollableFrame(outer, fg_color="transparent",
                                       scrollbar_button_color=BORDER,
                                       scrollbar_button_hover_color=PURPLE)
        wrap.pack(fill="both", expand=True)

        # ── Catálogos base ────────────────────────────────────────────────────
        self._seccion(wrap, "CATÁLOGOS BASE")
        self._opcion(wrap, "📋", "Clasificaciones",  self._ir_clasificaciones)
        self._opcion(wrap, "🎯", "Géneros",          self._ir_generos)
        self._opcion(wrap, "🏭", "Proveedores",      self._ir_proveedores)

        # ── Catálogos geográficos (submenú) ───────────────────────────────────
        self._seccion(wrap, "CATÁLOGOS GEOGRÁFICOS")
        self._opcion(wrap, "🌎", "Países / Estados / Ciudades / Colonias / Calles",
                     self._ir_geograficos)

        # ── Entidades principales ─────────────────────────────────────────────
        self._seccion(wrap, "ENTIDADES PRINCIPALES")
        self._opcion(wrap, "🏢", "Sucursales",      self._ir_sucursales)
        self._opcion(wrap, "👤", "Clientes",        self._ir_clientes)
        self._opcion(wrap, "👨‍💼", "Empleados",      self._ir_empleados)
        self._opcion(wrap, "🎮", "Videojuegos",     self._ir_videojuegos)
        self._opcion(wrap, "🕹", "Plataformas",     self._ir_plataformas)
        self._opcion(wrap, "📦", "Inventarios",     self._ir_inventarios)

        # ── Ventas ────────────────────────────────────────────────────────────
        self._seccion(wrap, "MÓDULO DE VENTAS")
        self._opcion(wrap, "💰", "Ventas",            self._ir_ventas)
        self._opcion(wrap, "📋", "Detalle de Ventas", self._ir_detalle_ventas)

        # ── Contacto ──────────────────────────────────────────────────────────
        self._seccion(wrap, "CONTACTO")
        self._opcion(wrap, "📞", "Teléfonos", self._ir_telefonos)
        self._opcion(wrap, "📧", "Correos",   self._ir_correos)

        # Cerrar sesión (fuera del scroll)
        ctk.CTkButton(
            outer, text="Cerrar sesión",
            height=38, fg_color="transparent",
            border_width=1, border_color=RED,
            text_color=RED, hover_color="#2A1010",
            corner_radius=8, font=("Segoe UI", 12),
            command=self._mostrar_login,
        ).pack(fill="x", pady=(12, 0))

    def _seccion(self, parent, texto):
        """Etiqueta de sección dentro del menú."""
        ctk.CTkLabel(parent, text=texto,
                     font=("Segoe UI", 9, "bold"),
                     text_color=GRAY_TEXT).pack(anchor="w", pady=(10, 2))

    def _opcion(self, parent, icono, texto, cmd, activo=True):
        """Tarjeta-botón clickeable del menú."""
        f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10,
                         border_width=1, border_color=BORDER)
        f.pack(fill="x", pady=3)
        ctk.CTkLabel(f, text=icono, font=("Segoe UI", 18)).pack(
            side="left", padx=14, pady=10)
        ctk.CTkLabel(f, text=texto, font=("Segoe UI", 12),
                     text_color=WHITE if activo else GRAY_TEXT).pack(side="left")
        if activo and cmd:
            f.bind("<Button-1>", lambda e: cmd())
            for child in f.winfo_children():
                child.bind("<Button-1>", lambda e: cmd())
        else:
            ctk.CTkLabel(f, text="Próximamente",
                         font=("Segoe UI", 10),
                         text_color=GRAY_TEXT).pack(side="right", padx=14)

    # ═══════════════════════════════════════════════════════════════════════════
    # SUBMENÚ GEOGRÁFICO
    # ═══════════════════════════════════════════════════════════════════════════
    def _ir_geograficos(self):
        self._limpiar()
        self.geometry("580x560")
        self._topbar()

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=40, pady=30)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(hdr, text="🌎", font=("Segoe UI", 22)).pack(side="left", padx=(0, 10))
        ttl = ctk.CTkFrame(hdr, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Catálogos Geográficos",
                     font=("Segoe UI", 16, "bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Selecciona el catálogo a gestionar",
                     font=("Segoe UI", 11), text_color=GRAY_TEXT).pack(anchor="w")

        ctk.CTkFrame(wrap, height=1, fg_color=BORDER).pack(fill="x", pady=10)

        # Opciones de la cadena geográfica en orden
        geo = [
            ("🌍", "Países",   self._ir_paises),
            ("🗺",  "Estados",  self._ir_estados),
            ("🏙",  "Ciudades", self._ir_ciudades),
            ("🏘",  "Colonias", self._ir_colonias),
            ("🛣",  "Calles",   self._ir_calles),
        ]
        for icono, txt, cmd in geo:
            self._opcion(wrap, icono, txt, cmd)

        ctk.CTkButton(
            wrap, text="← Volver al menú",
            height=36, fg_color="transparent",
            border_width=1, border_color=BORDER,
            text_color=GRAY_TEXT, hover_color=BG_CARD,
            corner_radius=8, font=("Segoe UI", 11),
            command=self._mostrar_menu,
        ).pack(fill="x", pady=(20, 0))

    # ═══════════════════════════════════════════════════════════════════════════
    # NAVEGACIÓN A CADA PANTALLA
    # ═══════════════════════════════════════════════════════════════════════════
    def _ir_clasificaciones(self):
        self._limpiar()
        ClasificacionView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_generos(self):
        self._limpiar()
        GeneroView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_proveedores(self):
        self._limpiar()
        ProveedorView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_paises(self):
        self._limpiar()
        PaisView(self, self._usuario, self._puesto, self._ir_geograficos)

    def _ir_estados(self):
        self._limpiar()
        EstadosView(self, self._usuario, self._puesto, self._ir_geograficos)

    def _ir_ciudades(self):
        self._limpiar()
        CiudadView(self, self._usuario, self._puesto, self._ir_geograficos)

    def _ir_colonias(self):
        self._limpiar()
        ColoniaView(self, self._usuario, self._puesto, self._ir_geograficos)

    def _ir_calles(self):
        self._limpiar()
        CalleView(self, self._usuario, self._puesto, self._ir_geograficos)

    # ── Entidades principales ────────────────────────────────────────────────
    def _ir_sucursales(self):
        self._limpiar()
        SucursalView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_clientes(self):
        self._limpiar()
        ClienteView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_empleados(self):
        self._limpiar()
        EmpleadoView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_videojuegos(self):
        """Para acceder a videojuegos primero hay que pasar por clasificaciones,
        ya que es FK obligatoria. Mostramos el catálogo de clasificaciones."""
        self._ir_clasificaciones()

    def _ir_plataformas(self):
        self._limpiar()
        PlataformaView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_inventarios(self):
        self._limpiar()
        InventarioView(self, self._usuario, self._puesto, self._mostrar_menu)

    # ── Ventas ────────────────────────────────────────────────────────────────
    def _ir_ventas(self):
        self._limpiar()
        VentaView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_detalle_ventas(self):
        self._limpiar()
        DetalleVentaView(self, self._usuario, self._puesto, self._mostrar_menu)

    # ── Contacto ──────────────────────────────────────────────────────────────
    def _ir_telefonos(self):
        self._limpiar()
        TelefonoView(self, self._usuario, self._puesto, self._mostrar_menu)

    def _ir_correos(self):
        self._limpiar()
        CorreoView(self, self._usuario, self._puesto, self._mostrar_menu)


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
