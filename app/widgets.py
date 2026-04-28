# widgets.py — Funciones de UI reutilizables en todas las vistas
import tkinter.ttk as ttk
import customtkinter as ctk
from colores import *


def make_topbar(ventana):
    """Barra de acento cyan en la parte superior."""
    ctk.CTkFrame(ventana, height=3, fg_color=CYAN, corner_radius=0).pack(
        fill="x", side="top")


def make_entry(ventana, parent, placeholder, show=None, max_chars=None, width=None):
    """Entry estilizado con límite de caracteres opcional."""
    kwargs = dict(
        placeholder_text=placeholder,
        show=show or "",
        height=40,
        fg_color=BG_INPUT,
        border_color=BORDER,
        border_width=1,
        corner_radius=8,
        font=("Segoe UI", 13),
        text_color=WHITE,
    )
    if width:
        kwargs["width"] = width
    e = ctk.CTkEntry(parent, **kwargs)
    if max_chars:
        vcmd = ventana.register(lambda P: len(P) <= max_chars)
        e._entry.configure(validate="key", validatecommand=(vcmd, "%P"))
    return e


def make_label(parent, texto, size=10, bold=True, color=None):
    """Label de campo (etiqueta pequeña sobre un entry)."""
    ctk.CTkLabel(
        parent, text=texto,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        text_color=color or GRAY_TEXT
    ).grid_configure() if False else None
    return ctk.CTkLabel(
        parent, text=texto,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        text_color=color or GRAY_TEXT
    )


def make_boton(parent, texto, comando, color=None, ancho=120, alto=36):
    """Botón estilizado estándar."""
    return ctk.CTkButton(
        parent, text=texto,
        width=ancho, height=alto,
        font=("Segoe UI", 12, "bold"),
        fg_color=color or PURPLE,
        hover_color=color or PURPLE,
        corner_radius=8,
        command=comando,
    )


def make_treeview(parent, columnas, anchos):
    """
    Crea un Treeview estilizado con tema oscuro.
    columnas : list[str] — nombres de columnas
    anchos   : list[int] — ancho de cada columna en px
    Retorna (tree, scrollbar_frame) — ya empaquetados dentro de parent.
    """
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("App.Treeview",
                    background=BG_INPUT, foreground=WHITE,
                    fieldbackground=BG_INPUT, rowheight=30,
                    font=("Segoe UI", 12), borderwidth=0)
    style.configure("App.Treeview.Heading",
                    background=BG_CARD, foreground=CYAN,
                    font=("Segoe UI", 11, "bold"), relief="flat")
    style.map("App.Treeview",
              background=[("selected", PURPLE)],
              foreground=[("selected", WHITE)])

    tree = ttk.Treeview(parent, columns=columnas, show="headings",
                        style="App.Treeview", selectmode="browse")
    for col, ancho in zip(columnas, anchos):
        tree.heading(col, text=col)
        tree.column(col, width=ancho, anchor="center" if ancho <= 100 else "w")

    sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 12))
    sb.pack(side="right", fill="y", pady=(0, 12), padx=(0, 6))
    return tree


def make_status(parent):
    """Label de mensajes inline (verde/rojo/cyan)."""
    lbl = ctk.CTkLabel(parent, text="",
                       font=("Segoe UI", 11),
                       text_color=CYAN, wraplength=270)
    lbl.pack(pady=(8, 0))
    return lbl


def set_status(lbl, msg, color=None):
    from colores import CYAN
    lbl.configure(text=msg, text_color=color or CYAN)


def make_combo(parent, valores_dict, placeholder="Selecciona una opción"):
    """
    OptionMenu para seleccionar FK.
    valores_dict: { 'ID - Nombre': id_real }
    """
    opciones = list(valores_dict.keys()) if valores_dict else ["(sin registros)"]
    combo = ctk.CTkOptionMenu(
        parent,
        values=opciones,
        fg_color=BG_INPUT,
        button_color=PURPLE,
        button_hover_color=PURPLE_LT,
        dropdown_fg_color=BG_CARD,
        dropdown_hover_color=BORDER,
        text_color=WHITE,
        font=("Segoe UI", 12),
        height=40,
    )
    combo.set(opciones[0] if valores_dict else placeholder)
    return combo


def get_combo_value(combo, valores_dict):
    """Retorna el id_real del valor seleccionado en el combo, o None si no es válido."""
    return valores_dict.get(combo.get())


def set_combo_by_id(combo, valores_dict, id_buscado):
    """Selecciona en el combo la opción cuyo valor coincide con id_buscado."""
    if id_buscado is None:
        return
    for k, v in valores_dict.items():
        if str(v) == str(id_buscado):
            combo.set(k)
            return


def make_form_panel(parent, col=0):
    """
    Crea el panel izquierdo estándar con:
      - scroll_f : CTkScrollableFrame  → aquí va el form card + hijos buttons
      - btns_area: CTkFrame            → aquí van los botones CRUD + Volver + status (fijos)
    Retorna (left, scroll_f, btns_area)
    """
    left = ctk.CTkFrame(parent, fg_color="transparent")
    left.grid(row=0, column=col, sticky="nsew", padx=(0, 14) if col == 0 else 0)

    scroll_f = ctk.CTkScrollableFrame(
        left, fg_color="transparent", width=310,
        scrollbar_button_color=BORDER,
        scrollbar_button_hover_color=PURPLE,
    )
    scroll_f.pack(fill="both", expand=True)
    scroll_f.columnconfigure(0, weight=1)

    btns_area = ctk.CTkFrame(left, fg_color="transparent")
    btns_area.pack(fill="x", pady=(8, 0), side="bottom")

    return left, scroll_f, btns_area


def make_campo(scroll_f, label_txt, row):
    """Label de campo sobre un entry dentro de un form en grid."""
    ctk.CTkLabel(scroll_f, text=label_txt,
                 font=("Segoe UI", 10, "bold"),
                 text_color=GRAY_TEXT).grid(row=row, column=0, sticky="w",
                                            padx=18, pady=(12, 3))
