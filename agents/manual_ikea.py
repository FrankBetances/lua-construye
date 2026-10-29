"""Generador del Manual de Ensamblaje Oficial Tipo IKEA para los 11 Sets de Lúa Construye.

Produce un documento PDF de alta calidad editorial con estética minimalista sueca (tipo IKEA),
instrucciones visuales paso a paso, BOM gráfico, directivas de seguridad EN 71-1,
mediación analógica adulta LOMLOE y advertencias de montaje 'BIEN vs MAL'.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Configurar directorio de caché temporal para matplotlib en entorno seguro
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.makedirs("/tmp/matplotlib", exist_ok=True)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches
from PIL import Image

# Dimensiones A4 en pulgadas (8.27 x 11.69 in = 210 x 297 mm)
PAGE_WIDTH = 8.27
PAGE_HEIGHT = 11.69

# Paleta de colores estilo IKEA / Earlify
COLOR_BG = "#FFFFFF"
COLOR_PANEL_BG = "#F8FAFC"
COLOR_PANEL_BORDER = "#E2E8F0"
COLOR_PRIMARY_BLUE = "#0058A3"      # Azul corporativo IKEA
COLOR_ACCENT_YELLOW = "#FFDA1A"     # Amarillo IKEA
COLOR_TEXT_DARK = "#0F172A"         # Slate 900
COLOR_TEXT_MUTED = "#64748B"        # Slate 500
COLOR_TEXT_SUBTLE = "#94A3B8"       # Slate 400
COLOR_GOOD_GREEN = "#16A34A"        # Verde Check
COLOR_BAD_RED = "#DC2626"           # Rojo Cross
COLOR_BOX_LINE = "#CBD5E1"


def create_base_page(fig):
    """Limpia los ejes y retorna el axis configurado con coordenadas [0, 1] x [0, 1]."""
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return ax


def draw_header(ax, set_code, title_es, title_gl, subtitle, page_num, total_pages=14):
    """Dibuja el encabezado canónico de cada página de set."""
    # Barra superior azul IKEA
    ax.add_patch(patches.Rectangle((0.05, 0.94), 0.90, 0.045, facecolor=COLOR_PRIMARY_BLUE, edgecolor="none"))
    
    # Badge número de Set
    ax.add_patch(patches.Circle((0.085, 0.9625), 0.016, facecolor=COLOR_ACCENT_YELLOW, edgecolor="none"))
    ax.text(0.085, 0.9625, set_code, ha="center", va="center", fontsize=11, fontweight="bold", color=COLOR_TEXT_DARK)
    
    # Título principal en blanco
    ax.text(0.12, 0.9625, title_es.upper(), ha="left", va="center", fontsize=13, fontweight="bold", color="#FFFFFF")
    
    # Subtítulo / metadatos a la derecha
    ax.text(0.93, 0.9625, f"Pág. {page_num} de {total_pages}", ha="right", va="center", fontsize=9, fontweight="bold", color=COLOR_ACCENT_YELLOW)
    
    # Barra de subtítulo bilingüe
    ax.text(0.05, 0.925, f"Galego: {title_gl}  ·  {subtitle}", ha="left", va="center", fontsize=8.5, color=COLOR_TEXT_MUTED, style="italic")
    ax.plot([0.05, 0.95], [0.915, 0.915], color=COLOR_PANEL_BORDER, lw=1)


def draw_footer(ax, page_num, total_pages=14):
    """Dibuja el pie de página oficial con certificación y seguridad."""
    ax.plot([0.05, 0.95], [0.045, 0.045], color=COLOR_PANEL_BORDER, lw=1)
    
    # Texto de certificación legal y no-PHI
    ax.text(0.05, 0.03, "LÚA CONSTRUYE · Ecosistema Earlify Health · Directiva 2009/48/CE · Cumplimiento EN 71-1 (Paredes ≥ 3,2 mm · Anti-asfixia > 31,75 mm)",
            ha="left", va="center", fontsize=6.8, color=COLOR_TEXT_MUTED)
    
    ax.text(0.95, 0.03, f"{page_num} / {total_pages}", ha="right", va="center", fontsize=8, fontweight="bold", color=COLOR_TEXT_DARK)


def draw_bom_box(ax, x, y, w, h, parts_list):
    """Caja de inventario BOM estilo IKEA con multiplicadores (xN) y códigos."""
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.01",
                                        facecolor=COLOR_PANEL_BG, edgecolor=COLOR_BOX_LINE, lw=0.8))
    
    # Título del inventario
    ax.add_patch(patches.Rectangle((x + 0.01, y + h - 0.024), 0.15, 0.02, facecolor=COLOR_TEXT_DARK, edgecolor="none"))
    ax.text(x + 0.085, y + h - 0.014, "INVENTARIO (BOM)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#FFFFFF")
    ax.text(x + 0.17, y + h - 0.014, "Revisa y cuenta todas las piezas antes de montar · Revisa as pezas antes de montar",
            ha="left", va="center", fontsize=7, color=COLOR_TEXT_MUTED)

    # Distribuir piezas en hasta 2 filas de cajitas
    n = len(parts_list)
    if n == 0:
        return
    cols = min(4, n)
    cw = (w - 0.03) / cols
    rows = (n + cols - 1) // cols
    rh = (h - 0.035) / rows
    
    for i, (code, name, qty) in enumerate(parts_list):
        r = i // cols
        c = i % cols
        px = x + 0.015 + c * cw
        py = y + h - 0.032 - (r + 1) * rh
        
        # Mini tarjeta de pieza
        ax.add_patch(patches.FancyBboxPatch((px, py + 0.003), cw - 0.01, rh - 0.006, boxstyle="square,pad=0",
                                            facecolor="#FFFFFF", edgecolor=COLOR_PANEL_BORDER, lw=0.6))
        # Badge de cantidad
        ax.add_patch(patches.Circle((px + 0.018, py + rh / 2), 0.012, facecolor=COLOR_PRIMARY_BLUE, edgecolor="none"))
        ax.text(px + 0.018, py + rh / 2, f"{qty}×", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#FFFFFF")
        
        # Código y nombre
        ax.text(px + 0.036, py + rh * 0.65, code, ha="left", va="center", fontsize=7.2, fontweight="bold", color=COLOR_TEXT_DARK)
        nombre_corto = name if len(name) <= 24 else name[:22] + "..."
        ax.text(px + 0.036, py + rh * 0.30, nombre_corto, ha="left", va="center", fontsize=6.2, color=COLOR_TEXT_MUTED)


def draw_check_box(ax, x, y, w, h, good_text, bad_text):
    """Caja comparativa estilo IKEA: BIEN (Check verde) vs MAL (Cruz roja)."""
    hw = (w - 0.015) / 2
    # BIEN
    ax.add_patch(patches.FancyBboxPatch((x, y), hw, h, boxstyle="round,pad=0.005,rounding_size=0.008",
                                        facecolor="#F0FDF4", edgecolor=COLOR_GOOD_GREEN, lw=1))
    ax.add_patch(patches.Circle((x + 0.02, y + h - 0.02), 0.012, facecolor=COLOR_GOOD_GREEN, edgecolor="none"))
    ax.text(x + 0.02, y + h - 0.02, "✔", ha="center", va="center", fontsize=10, fontweight="bold", color="#FFFFFF")
    ax.text(x + 0.038, y + h - 0.02, "CORRECTO / BEN", ha="left", va="center", fontsize=8, fontweight="bold", color=COLOR_GOOD_GREEN)
    ax.text(x + 0.015, y + (h - 0.03) / 2, good_text, ha="left", va="center", fontsize=7, color=COLOR_TEXT_DARK, wrap=True)

    # MAL
    ax.add_patch(patches.FancyBboxPatch((x + hw + 0.015, y), hw, h, boxstyle="round,pad=0.005,rounding_size=0.008",
                                        facecolor="#FEF2F2", edgecolor=COLOR_BAD_RED, lw=1))
    ax.add_patch(patches.Circle((x + hw + 0.035, y + h - 0.02), 0.012, facecolor=COLOR_BAD_RED, edgecolor="none"))
    ax.text(x + hw + 0.035, y + h - 0.02, "✖", ha="center", va="center", fontsize=10, fontweight="bold", color="#FFFFFF")
    ax.text(x + hw + 0.053, y + h - 0.02, "INCORRECTO / MAL", ha="left", va="center", fontsize=8, fontweight="bold", color=COLOR_BAD_RED)
    ax.text(x + hw + 0.03, y + (h - 0.03) / 2, bad_text, ha="left", va="center", fontsize=7, color=COLOR_TEXT_DARK, wrap=True)


def draw_mediation_box(ax, x, y, w, h, rule_text, tpr_list, vocab_text):
    """Panel inferior de mediación pedagógica LOMLOE y rol del adulto."""
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.01",
                                        facecolor="#FFFBEB", edgecolor="#FCD34D", lw=0.8))
    
    # Encabezado
    ax.add_patch(patches.Rectangle((x + 0.01, y + h - 0.02), 0.19, 0.018, facecolor="#D97706", edgecolor="none"))
    ax.text(x + 0.105, y + h - 0.011, "MEDIACIÓN ADULTA (LOMLOE)", ha="center", va="center", fontsize=7, fontweight="bold", color="#FFFFFF")
    
    # Regla 1 innegociable
    ax.text(x + 0.22, y + h - 0.011, "MANDATO: El niño manipula las piezas físicas; el adulto sostiene la tableta. La criatura NO toca la pantalla.",
            ha="left", va="center", fontsize=7.2, fontweight="bold", color="#92400E")
    
    # Línea 1: TPR (Total Physical Response)
    ax.text(x + 0.015, y + h * 0.52, f"Consignas verbales TPR: {tpr_list}", ha="left", va="center", fontsize=7.2, color=COLOR_TEXT_DARK)
    
    # Línea 2: Vocabulario espacial
    ax.text(x + 0.015, y + h * 0.22, f"Lenguaje espacial BrickSmart: {vocab_text}", ha="left", va="center", fontsize=6.8, color=COLOR_TEXT_MUTED)


def render_cover_page(fig):
    """Página 1: Portada Oficial IKEA para Lúa Construye."""
    ax = create_base_page(fig)
    
    # Fondo minimalista
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor="#F8FAFC", edgecolor="none"))
    
    # Banda superior IKEA
    ax.add_patch(patches.Rectangle((0.08, 0.88), 0.84, 0.06, facecolor=COLOR_PRIMARY_BLUE, edgecolor="none"))
    ax.text(0.12, 0.91, "E A R L I F Y   H E A L T H   ·   L Ú A   C O N S T R U Y E", ha="left", va="center", fontsize=11, fontweight="bold", color="#FFFFFF")
    ax.text(0.88, 0.91, "EDICIÓN 2026", ha="right", va="center", fontsize=11, fontweight="bold", color=COLOR_ACCENT_YELLOW)
    
    # Gran Título Estilo IKEA
    ax.text(0.50, 0.80, "LÚA CONSTRUYE", ha="center", va="center", fontsize=34, fontweight="heavy", color=COLOR_TEXT_DARK)
    ax.text(0.50, 0.74, "MANUAL DE ENSAMBLAJE UNIVERSAL", ha="center", va="center", fontsize=17, fontweight="bold", color=COLOR_PRIMARY_BLUE)
    ax.text(0.50, 0.705, "Guía Gráfica Paso a Paso para los 11 Sets Tangibles", ha="center", va="center", fontsize=11, color=COLOR_TEXT_MUTED)
    ax.text(0.50, 0.685, "Guía Gráfica Paso a Paso para os 11 Sets Tanxibles (Galego / Castellano)", ha="center", va="center", fontsize=9.5, color=COLOR_TEXT_SUBTLE, style="italic")
    
    # Cuadro de la imagen Hero (Lúa V5 sobre el camino)
    hero_path = "docs/lua-v5-camino.png"
    if os.path.exists(hero_path):
        im = Image.open(hero_path)
        # Recuadro con sombra
        ax.add_patch(patches.FancyBboxPatch((0.08, 0.27), 0.84, 0.38, boxstyle="round,pad=0.01,rounding_size=0.015",
                                            facecolor="#FFFFFF", edgecolor=COLOR_BOX_LINE, lw=1.2))
        ax.imshow(im, extent=[0.09, 0.91, 0.28, 0.64], aspect="auto", zorder=3)
    
    # Sellos de certificación IKEA y seguridad EN 71-1
    badges = [
        ("EN 71-1 SAFE", "Anti-asfixia > 31.75 mm\nParedes ≥ 3.2 mm", COLOR_PRIMARY_BLUE),
        ("ZERO-NETWORK", "100% Offline y Analógico\nSin pantallas para el niño", "#059669"),
        ("PASO DUPLO", "Modularidad 31.80 mm\nCompatibilidad universal", "#D97706"),
        ("LOMLOE STEAM", "Educación Infantil 0-6\nNeurodesarrollo motriz", "#7C3AED"),
    ]
    bw = 0.19
    for i, (b_title, b_sub, b_col) in enumerate(badges):
        bx = 0.08 + i * 0.217
        ax.add_patch(patches.FancyBboxPatch((bx, 0.14), bw, 0.095, boxstyle="round,pad=0.006,rounding_size=0.01",
                                            facecolor="#FFFFFF", edgecolor=b_col, lw=1.5))
        ax.text(bx + bw / 2, 0.205, b_title, ha="center", va="center", fontsize=8.5, fontweight="bold", color=b_col)
        ax.text(bx + bw / 2, 0.165, b_sub, ha="center", va="center", fontsize=6.8, color=COLOR_TEXT_MUTED, multialignment="center")
    
    # Pie de portada con contacto y referencia legal
    ax.plot([0.08, 0.92], [0.10, 0.10], color=COLOR_BOX_LINE, lw=1)
    ax.text(0.50, 0.075, "Ecosistema Earlify Health · frank.alberto.betancesreinoso@gmail.com · Masque3D Release v1",
            ha="center", va="center", fontsize=8, color=COLOR_TEXT_MUTED)
    ax.text(0.50, 0.055, "Diseñado bajo normativa europea de seguridad de juguetes · Compatible con Lúa V5",
            ha="center", va="center", fontsize=7.5, color=COLOR_TEXT_SUBTLE)


def render_safety_page(fig):
    """Página 2: Normas IKEA de Ensamblaje, Herramientas y Seguridad."""
    ax = create_base_page(fig)
    
    # Header
    draw_header(ax, "00", "NORMAS GENERALES DE ENSAMBLAJE", "NORMAS XERAIS DE ENSAMBLAXE",
                "Seguridad, ergonomía y el gesto canónico de montaje", 2)
    
    # Bloque 1: ANTES DE EMPEZAR (IKEA Checklist)
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.65), 0.90, 0.24, boxstyle="round,pad=0.01,rounding_size=0.015",
                                        facecolor=COLOR_PANEL_BG, edgecolor=COLOR_PRIMARY_BLUE, lw=1.2))
    ax.add_patch(patches.Rectangle((0.07, 0.86), 0.24, 0.024, facecolor=COLOR_PRIMARY_BLUE, edgecolor="none"))
    ax.text(0.19, 0.872, "1. ANTES DE EMPEZAR / ANTES DE COMEZAR", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")
    
    rules = [
        ("1 · SIN PEGAMENTO NI TORNILLOS", "Todas las uniones son reversibles: espigas Duplo, ranuras deslizantes y roscas helicoidales. No emplees adhesivos.", COLOR_BAD_RED),
        ("2 · SUPERFICIE SUAVE Y LIMPIA", "Monta siempre sobre una mesa lisa o alfombra limpia para proteger los acabados del PLA y evitar desgastes prematuros.", COLOR_PRIMARY_BLUE),
        ("3 · SEGURIDAD INFANTIL EN 71-1", "Cada pieza cumple el criterio anti-asfixia (>31,75 mm) y no entra en el cilindro de piezas pequeñas. Paredes ≥ 3,2 mm.", COLOR_GOOD_GREEN),
        ("4 · LA CRIATURA NO TOCA LA PANTALLA", "El niño es el constructor analógico. El adulto mediador gestiona la app o tableta situada en un soporte estable.", "#D97706"),
    ]
    for i, (rtitle, rdesc, rcol) in enumerate(rules):
        rx = 0.07 + (i % 2) * 0.44
        ry = 0.77 if i < 2 else 0.68
        ax.add_patch(patches.Circle((rx + 0.015, ry + 0.035), 0.012, facecolor=rcol, edgecolor="none"))
        ax.text(rx + 0.035, ry + 0.04, rtitle, ha="left", va="center", fontsize=8, fontweight="bold", color=COLOR_TEXT_DARK)
        ax.text(rx + 0.035, ry + 0.012, rdesc, ha="left", va="top", fontsize=7, color=COLOR_TEXT_MUTED, wrap=True)
    
    # Bloque 2: EL GESTO CANÓNICO DE MONTAJE (Vector de Inserción)
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.36), 0.90, 0.26, boxstyle="round,pad=0.01,rounding_size=0.015",
                                        facecolor="#FFFFFF", edgecolor=COLOR_BOX_LINE, lw=1))
    ax.add_patch(patches.Rectangle((0.07, 0.59), 0.28, 0.024, facecolor=COLOR_TEXT_DARK, edgecolor="none"))
    ax.text(0.21, 0.602, "2. EL GESTO CANÓNICO: CADA PIEZA BAJA", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")
    
    # Diagrama visual de inserción
    ax.text(0.08, 0.55, "En todos los sets rige la regla geométrica: el vector de inserción es estrictamente vertical (0, 0, −1).",
            ha="left", va="center", fontsize=8.2, fontweight="bold", color=COLOR_TEXT_DARK)
    ax.text(0.08, 0.525, "En tódolos sets a peza baixa sobre as espigas Duplo de paso 31,80 mm sen forzar nin dobrar.",
            ha="left", va="center", fontsize=7.5, color=COLOR_TEXT_MUTED, style="italic")
    
    # 3 Pasos con flechas grandes
    gestos = [
        ("① ALINEAR", "Enfrenta las espigas macho con los alveolos hembra verticalmente."),
        ("② DESCENDER", "Aplica presión suave descendente perpendicular a la cama."),
        ("③ ¡CLIC!", "Verifica el encaje completo a ras. No debe quedar holgura visible."),
    ]
    for i, (g_num, g_desc) in enumerate(gestos):
        gx = 0.08 + i * 0.29
        ax.add_patch(patches.FancyBboxPatch((gx, 0.39), 0.26, 0.11, boxstyle="round,pad=0.006,rounding_size=0.01",
                                            facecolor=COLOR_PANEL_BG, edgecolor=COLOR_PRIMARY_BLUE, lw=0.8))
        ax.text(gx + 0.13, 0.47, g_num, ha="center", va="center", fontsize=10, fontweight="bold", color=COLOR_PRIMARY_BLUE)
        ax.text(gx + 0.13, 0.42, g_desc, ha="center", va="center", fontsize=7.2, color=COLOR_TEXT_DARK, multialignment="center")
    
    # Bloque 3: LA BANDEJA PATÍN DE LÚA V5
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.08), 0.90, 0.25, boxstyle="round,pad=0.01,rounding_size=0.015",
                                        facecolor="#F0FDF4", edgecolor=COLOR_GOOD_GREEN, lw=1))
    ax.add_patch(patches.Rectangle((0.07, 0.305), 0.32, 0.024, facecolor=COLOR_GOOD_GREEN, edgecolor="none"))
    ax.text(0.23, 0.317, "3. LA BANDEJA PATÍN DE LÚA V5 (K-PATIN-G)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")
    
    ax.text(0.08, 0.27, "El robot Lúa V5 (base cúbica 108×108 mm) NO se ancla rígidamente: se apoya en el patín-bandeja.",
            ha="left", va="center", fontsize=8, fontweight="bold", color=COLOR_TEXT_DARK)
    ax.text(0.08, 0.245, "• El patín entra en la ranura guía de 12 mm de las baldosas mediante sus pivotes redondos redondeados.", ha="left", va="center", fontsize=7.3, color=COLOR_TEXT_DARK)
    ax.text(0.08, 0.22, "• La bandeja sujeta el cuerpo de Lúa por los flancos: si el niño levanta a Lúa, el patín permanece en la guía.", ha="left", va="center", fontsize=7.3, color=COLOR_TEXT_DARK)
    ax.text(0.08, 0.195, "• El patín eleva la base 13,2 mm garantizando 0 mm³ de choque contra las fichas de comando.", ha="left", va="center", fontsize=7.3, color=COLOR_TEXT_DARK)
    
    draw_check_box(ax, 0.08, 0.10, 0.84, 0.075,
                   "Lúa apoyada en su bandeja patín desliza libremente por rectas, curvas y T sin tropezar.",
                   "Colocar a Lúa directamente sobre la baldosa sin patín: roza el suelo y choca con los comandos.")
    
    draw_footer(ax, 2)


def render_set_page(fig, page_num, set_code, title_es, title_gl, subtitle, parts, steps, despiece_img, planta_img,
                    good_text, bad_text, tpr_cmds, vocab_text):
    """Plantilla estándar y unificada para cada uno de los 11 sets."""
    ax = create_base_page(fig)
    draw_header(ax, set_code, title_es, title_gl, subtitle, page_num)
    
    # 1. Caja BOM (Inventario)
    draw_bom_box(ax, 0.05, 0.77, 0.90, 0.13, parts)
    
    # 2. Área Central de Montaje: Izquierda Pasos IKEA, Derecha Ilustración Isométrica
    # Columna Izquierda: Pasos de Ensamblaje
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.25), 0.44, 0.50, boxstyle="round,pad=0.008,rounding_size=0.01",
                                        facecolor="#FFFFFF", edgecolor=COLOR_BOX_LINE, lw=1))
    ax.add_patch(patches.Rectangle((0.065, 0.72), 0.22, 0.022, facecolor=COLOR_PRIMARY_BLUE, edgecolor="none"))
    ax.text(0.175, 0.731, "PASOS DE ENSAMBLAJE", ha="center", va="center", fontsize=8, fontweight="bold", color="#FFFFFF")
    
    step_y = 0.69
    step_h = 0.43 / len(steps)
    for i, (stitle, sdesc_es, sdesc_gl) in enumerate(steps):
        sy = step_y - (i + 0.5) * step_h
        # Círculo con número de paso IKEA
        ax.add_patch(patches.Circle((0.08, sy + 0.015), 0.015, facecolor=COLOR_TEXT_DARK, edgecolor="none"))
        ax.text(0.08, sy + 0.015, str(i + 1), ha="center", va="center", fontsize=9, fontweight="bold", color="#FFFFFF")
        
        # Título del paso
        ax.text(0.105, sy + 0.022, stitle, ha="left", va="center", fontsize=7.8, fontweight="bold", color=COLOR_PRIMARY_BLUE)
        # Instrucción Español
        ax.text(0.105, sy + 0.005, sdesc_es, ha="left", va="center", fontsize=6.8, color=COLOR_TEXT_DARK)
        # Instrucción Galego
        ax.text(0.105, sy - 0.012, sdesc_gl, ha="left", va="center", fontsize=6.2, color=COLOR_TEXT_MUTED, style="italic")
        if i < len(steps) - 1:
            ax.plot([0.08, 0.47], [sy - 0.024, sy - 0.024], color=COLOR_PANEL_BORDER, lw=0.5, linestyle=":")
    
    # Columna Derecha: Ilustración Técnica Isométrica y Planta
    ax.add_patch(patches.FancyBboxPatch((0.51, 0.25), 0.44, 0.50, boxstyle="round,pad=0.008,rounding_size=0.01",
                                        facecolor=COLOR_PANEL_BG, edgecolor=COLOR_BOX_LINE, lw=1))
    ax.add_patch(patches.Rectangle((0.525, 0.72), 0.24, 0.022, facecolor=COLOR_TEXT_DARK, edgecolor="none"))
    ax.text(0.645, 0.731, "DESPIECE Y DISPOSICIÓN", ha="center", va="center", fontsize=8, fontweight="bold", color="#FFFFFF")
    
    # Dibujar Despiece Arriba
    if despiece_img and os.path.exists(despiece_img):
        im1 = Image.open(despiece_img)
        ax.imshow(im1, extent=[0.52, 0.94, 0.48, 0.71], aspect="auto", zorder=3)
        ax.text(0.53, 0.485, "Vista Isométrica de Despiece", fontsize=6.5, color=COLOR_TEXT_MUTED, style="italic")
    
    # Dibujar Planta Abajo
    if planta_img and os.path.exists(planta_img):
        im2 = Image.open(planta_img)
        ax.imshow(im2, extent=[0.52, 0.94, 0.26, 0.46], aspect="auto", zorder=3)
        ax.text(0.53, 0.265, "Vista en Planta de Montaje", fontsize=6.5, color=COLOR_TEXT_MUTED, style="italic")
    
    # 3. Caja de Verificación BIEN vs MAL
    draw_check_box(ax, 0.05, 0.155, 0.90, 0.085, good_text, bad_text)
    
    # 4. Caja de Mediación Adulta (LOMLOE)
    draw_mediation_box(ax, 0.05, 0.055, 0.90, 0.085, "", tpr_cmds, vocab_text)
    
    # Pie de página
    draw_footer(ax, page_num)


def render_closing_page(fig):
    """Página 14: Cuadro de Métricas Técnicas, Directivas de Juguetes y Cierre."""
    ax = create_base_page(fig)
    draw_header(ax, "✓", "ESPECIFICACIÓN TÉCNICA Y NORMATIVA", "ESPECIFICACIÓN TÉCNICA E NORMATIVA",
                "Métricas de fabricación FDM, ensayos mecánicos y gobernanza", 14)
    
    # Bloque 1: Resumen de Fabricación Masque3D
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.64), 0.90, 0.25, boxstyle="round,pad=0.01,rounding_size=0.015",
                                        facecolor=COLOR_PANEL_BG, edgecolor=COLOR_PRIMARY_BLUE, lw=1))
    ax.add_patch(patches.Rectangle((0.07, 0.86), 0.30, 0.024, facecolor=COLOR_PRIMARY_BLUE, edgecolor="none"))
    ax.text(0.22, 0.872, "PARÁMETROS DE IMPRESIÓN (PLA)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")
    
    params = [
        ("Material", "PLA virgen biodegradable libre de metales pesados (EN 71-3)."),
        ("Boquilla / Capa", "Boquilla de 0,4 mm · Altura de capa recomendada 0,20 mm."),
        ("Perímetros mínimos", "6 perímetros macizos en todas las piezas (garantía de impacto)."),
        ("Relleno (Infill)", "100 % en piezas pequeñas, ejes, patín y roscas; 30–40 % en baldosas."),
        ("Orientación de cama", "Cada STL va orientado en su plano óptimo. Sin soportes automáticos."),
        ("Masa total estimada", "Aprox. 17,8 kg a relleno 100 % (unos 11,5 kg optimizado)."),
    ]
    for i, (p_label, p_val) in enumerate(params):
        py = 0.825 - i * 0.028
        ax.text(0.08, py, f"• {p_label}:", ha="left", va="center", fontsize=7.5, fontweight="bold", color=COLOR_TEXT_DARK)
        ax.text(0.32, py, p_val, ha="left", va="center", fontsize=7.2, color=COLOR_TEXT_MUTED)
    
    # Bloque 2: Conformidad Normativa EN 71-1
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.34), 0.90, 0.28, boxstyle="round,pad=0.01,rounding_size=0.015",
                                        facecolor="#FFFFFF", edgecolor=COLOR_GOOD_GREEN, lw=1.2))
    ax.add_patch(patches.Rectangle((0.07, 0.59), 0.38, 0.024, facecolor=COLOR_GOOD_GREEN, edgecolor="none"))
    ax.text(0.26, 0.602, "EVALUACIÓN DE SEGURIDAD EN 71-1 Y DIRECTIVA 2009/48/CE", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#FFFFFF")
    
    checks = [
        ("Cilindro de partes pequeñas", "Ninguna pieza física entra en el cilindro normalizado (31,75 mm × 57,10 mm). Apto 0-36 meses."),
        ("Pared mínima estructural", "Espesor de pared ≥ 3,20 mm en todo el sólido (fuera de filetes de rosca a 51°)."),
        ("Esferas de rodadura", "Diámetro de 44,50 mm (> 31,75 mm límite de asfixia en piezas esféricas)."),
        ("Bordes y aristas vivas", "Radio de redondeo mínimo r ≥ 1,60 mm en todas las esquinas accesibles."),
        ("Uniones mecánicas reversibles", "Cero adhesivos químicos. Desmontable sin desprendimiento de fragmentos."),
        ("Muro Regulatorio Educativo", "Descubre con Lúa y Lúa Construye no constituyen producto sanitario (No SaMD)."),
    ]
    for i, (c_label, c_val) in enumerate(checks):
        cy = 0.555 - i * 0.033
        ax.add_patch(patches.Circle((0.08, cy), 0.008, facecolor=COLOR_GOOD_GREEN, edgecolor="none"))
        ax.text(0.08, cy, "✔", ha="center", va="center", fontsize=6.5, color="#FFFFFF")
        ax.text(0.10, cy + 0.006, c_label, ha="left", va="center", fontsize=7.5, fontweight="bold", color=COLOR_TEXT_DARK)
        ax.text(0.10, cy - 0.008, c_val, ha="left", va="center", fontsize=6.8, color=COLOR_TEXT_MUTED)

    # Bloque 3: Créditos Institucionales y Gobernanza
    ax.add_patch(patches.FancyBboxPatch((0.05, 0.07), 0.90, 0.24, boxstyle="round,pad=0.01,rounding_size=0.015",
                                        facecolor="#FFFBEB", edgecolor="#FCD34D", lw=1))
    ax.add_patch(patches.Rectangle((0.07, 0.28), 0.24, 0.022, facecolor="#D97706", edgecolor="none"))
    ax.text(0.19, 0.291, "CRÉDITOS Y CONTACTO OFICIAL", ha="center", va="center", fontsize=8, fontweight="bold", color="#FFFFFF")
    
    ax.text(0.08, 0.24, "LÚA CONSTRUYE es un proyecto del Ecosistema Earlify Health S.L.", ha="left", va="center", fontsize=8.5, fontweight="bold", color=COLOR_TEXT_DARK)
    ax.text(0.08, 0.21, "Diseño e Integración Pedagógica: Dr. Frank Alberto Betances Reinoso (Fundador y CEO)", ha="left", va="center", fontsize=8, color=COLOR_TEXT_DARK)
    ax.text(0.08, 0.18, "Correo Electrónico Oficial Invariable: frank.alberto.betancesreinoso@gmail.com", ha="left", va="center", fontsize=8, fontweight="bold", color=COLOR_PRIMARY_BLUE)
    ax.text(0.08, 0.15, "Fabricación y Prototipado 3D FDM: Masque3D · Versión de Modelos: Entrega v1 (2026)", ha="left", va="center", fontsize=7.5, color=COLOR_TEXT_MUTED)
    ax.text(0.08, 0.12, "Marco Pedagógico: LOMLOE (Educación Infantil 0-6) · Metodología Analógica STEAM BrickSmart", ha="left", va="center", fontsize=7.5, color=COLOR_TEXT_MUTED)
    ax.text(0.08, 0.09, "Todos los derechos reservados © 2026 Earlify Health S.L. · Prohibida su copia sin autorización.", ha="left", va="center", fontsize=7, color=COLOR_TEXT_SUBTLE)
    
    draw_footer(ax, 14)


def build_manual_pdf(output_pdf_path: str):
    """Genera el manual completo de 14 páginas."""
    output_path = Path(output_pdf_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Generando manual IKEA en {output_path}...")
    with PdfPages(output_path) as pdf:
        
        # PÁGINA 1: Portada
        print("  -> Renderizando Página 1: Portada...")
        fig1 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_cover_page(fig1)
        pdf.savefig(fig1, dpi=150)
        plt.close(fig1)
        
        # PÁGINA 2: Normas de Ensamblaje y Seguridad
        print("  -> Renderizando Página 2: Normas de Ensamblaje...")
        fig2 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_safety_page(fig2)
        pdf.savefig(fig2, dpi=150)
        plt.close(fig2)
        
        # PÁGINA 3: SET 0 · Kit Común Lúa
        print("  -> Renderizando Página 3: Set 0 Kit Lúa...")
        fig3 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig3, 3, "S0", "KIT COMÚN LÚA", "Kit Común Lúa",
            "Base universal, zócalo con llave asimétrica y patín guía",
            [
                ("K-ZOCALO-G", "Zócalo universal con cuna", 2),
                ("K-PATIN-G", "Bandeja patín guía de Lúa", 1),
                ("K-PLACA-*", "Placas identidad táctiles", 7),
                ("S3-PIL-1..6", "Pilares graduados 1 a 6", 6),
            ],
            [
                ("COLOCAR ZÓCALO", "Apoya el zócalo K-ZOCALO-G sobre la mesa con la apertura hacia el frente.", "Apoia o zócalo sobre a mesa coa apertura cara adiante."),
                ("INSERTAR PLACA", "Desliza la placa de identidad (INICIO/META) en la ranura frontal con vector (0,0,-1).", "Desliza a placa na rañura frontal con vector (0,0,-1)."),
                ("ACOPLAR PATÍN", "Encaja la bandeja K-PATIN-G bajo el fondo de Lúa V5 con sus dos clics laterales.", "Encaixa a bandexa patín baixo o fondo de Lúa V5."),
                ("ASENTAR A LÚA", "Introduce a Lúa en la cuna del zócalo: la llave asimétrica asegura orientación correcta.", "Introduce a Lúa na cuna: a chave asimétrica asegura a posición."),
            ],
            "sets/S0-kit-lua/tarjetas/despiece.png", "sets/S0-kit-lua/tarjetas/planta.png",
            "Lúa asienta suavemente mirando hacia la salida de la cuna y lista para deslizar.",
            "Intentar forzar a Lúa al revés: la cuna asimétrica bloquea las patas e impide encajar.",
            "«¡Lúa en posición!», «¡Coloca a placa!», «¡Listo para saír!»",
            "Delante, detrás, dentro, fuera, horizontal, vertical."
        )
        pdf.savefig(fig3, dpi=150)
        plt.close(fig3)
        
        # PÁGINA 4: SET 1 · El Camino de Lúa
        print("  -> Renderizando Página 4: Set 1 El Camino...")
        fig4 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig4, 4, "S1", "EL CAMINO DE LÚA", "O Camiño de Lúa",
            "Programación tangible desconectada y desensibilización táctil",
            [
                ("S1-REC-LIS-G", "Baldosa recta lisa", 3),
                ("S1-REC-RUG-G", "Baldosa recta rugosa", 3),
                ("S1-CUR-G", "Baldosa curva 90°", 4),
                ("S1-TEE-G", "Intersección en T", 2),
                ("S1-CMD-*", "Fichas de comando TPR", 4),
                ("S1-DEST-*", "Placas destino (parque/cama)", 2),
            ],
            [
                ("CONECTAR RECTA", "Une la baldosa lisa con espigas Duplo de paso 31,8 mm al zócalo INICIO.", "Une a baldosa lisa ao zócalo INICIO sen forzar as espigas."),
                ("AÑADIR CURVA", "Empalma la curva de 90° asegurando la continuidad suave de la ranura guía.", "Empalma a curva asegurando a continuidade da rañura guía."),
                ("INSERTAR FICHAS", "Presiona las fichas de comando (Avanza, Gira, Salta) en las ranuras laterales.", "Presiona as fichas de comando nos petos laterais da baldosa."),
                ("DESLIZAR A LÚA", "Desliza a Lúa mediante su patín a lo largo del camino hasta el zócalo META.", "Desliza a Lúa polo camiño ata chegar ao zócalo META."),
            ],
            "sets/S1-camino/tarjetas/recta-despiece.png", "sets/S1-camino/tarjetas/recta-planta.png",
            "La ranura guía de 12 mm mantiene continuidad perfecta entre piezas sin desalineaciones.",
            "Desconectar baldosas tirando en ángulo: siempre desacoplar verticalmente hacia arriba.",
            "«¡Paso adiante!», «¡Xira á esquerda!», «¡Para!», «¡Salta!»",
            "Recto, curvo, áspero, suave, bifurcación, izquierda, derecha."
        )
        pdf.savefig(fig4, dpi=150)
        plt.close(fig4)
        
        # PÁGINA 5: SET 2 · La Estación de Sonido y Eco
        print("  -> Renderizando Página 5: Set 2 Estación de Sonido...")
        fig5 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig5, 5, "S2", "LA ESTACIÓN DE SONIDO Y ECO", "A Estación de Son e Eco",
            "Acústica analógica, frecuencias resonantes y percusión motriz",
            [
                ("S2-BAL-BASE-E", "Banco soporte basculante", 1),
                ("S2-BAL-BRAZO-E", "Brazo martillo percutor", 1),
                ("S2-RES-AZU-*", "Resonador azul (agudo)", 3),
                ("S2-RES-AMA-*", "Resonador amarillo (medio)", 3),
                ("S2-RES-ROJ-*", "Resonador rojo (grave)", 3),
                ("S2-RAS-E", "Raspadores guiro estriados", 2),
            ],
            [
                ("MONTAR SOPORTE", "Asienta el banco soporte S2-BAL-BASE-E en la superficie de trabajo.", "Asenta o banco soporte S2-BAL-BASE-E na superficie de traballo."),
                ("ENHEBRAR BRAZO", "Coloca el eje del brazo basculante sobre las dos cunas abiertas en U.", "Coloca o eixo do brazo basculante sobre as cunas abertas en U."),
                ("ORDENAR CAVAS", "Coloca los resonadores de mayor a menor tamaño (Rojo → Amarillo → Azul).", "Coloca os resonadores de maior a menor (Vermello, Amarelo, Azul)."),
                ("PERCUTIR / RASPAR", "Acciona el martillo suavemente y raspa los cilindros con la espátula.", "Acciona o martelo suavemente e raspa os cilindros coa espátula."),
            ],
            "sets/S2-estacion-sonido/tarjetas/despiece.png", "sets/S2-estacion-sonido/tarjetas/planta.png",
            "El brazo martillo bascula libremente por gravedad y percute en el centro del resonador.",
            "Apretar o forzar el eje contra el banco: debe pivotar sin rozamiento lateral.",
            "«¡Toca forte!», «¡Toca suave!», «¡Escoita o eco!», «¡Raspa rápido!»",
            "Grave, agudo, resonancia, vibración, eco, intensidad, timbre."
        )
        pdf.savefig(fig5, dpi=150)
        plt.close(fig5)
        
        # PÁGINA 6: SET 3 · El Laboratorio de Rampas y Gravedad
        print("  -> Renderizando Página 6: Set 3 Laboratorio de Rampas...")
        fig6 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig6, 6, "S3", "EL LABORATORIO DE RAMPAS", "O Laboratorio de Rampas",
            "Plano inclinado, fuerza centrípeta, rozamiento y conservación",
            [
                ("S3-RAM-G", "Rampa inclinada acanalada", 1),
                ("S3-BIS-G", "Bisagra angular basculante", 1),
                ("S3-FRI-G", "Tramo estriado de fricción", 1),
                ("S3-CUR-PER-G", "Curva peraltada centrípeta", 1),
                ("S3-REC-G", "Módulo receptor de llegada", 1),
                ("S3-ESF-LIS/RUG", "Esferas Ø45 mm (antiasfixia)", 4),
            ],
            [
                ("ELEVAR PILAR", "Apila los pilares S3-PIL-1 a 6 según la inclinación deseada.", "Apila os piares segundo a inclinación que queiras experimentar."),
                ("ACOPLAR BISAGRA", "Inserta la bisagra S3-BIS-G sobre la cabeza del pilar superior.", "Inserta a bisagra S3-BIS-G na cabeza do pilar máis alto."),
                ("CONECTAR RAMPA", "Encaja el tramo de rampa a la bisagra y enlaza la curva peraltada.", "Encaixa a rampa á bisagra e enlaza coa curva peraltada."),
                ("SOLTAR ESFERAS", "Lanza la esfera lisa y la rugosa para comparar su aceleración y frenado.", "Lanza a esfera lisa e a rugosa para comparar aceleración e freado."),
            ],
            "sets/S3-laboratorio-rampas/tarjetas/despiece.png", "sets/S3-laboratorio-rampas/tarjetas/planta.png",
            "Las esferas de Ø45 mm son 100% seguras bajo EN 71-1 y ruedan guiadas por el peralte.",
            "Usar canicas pequeñas no homologadas (<31,75 mm): peligro severo de asfixia.",
            "«¡Roda!», «¡Freo!», «¡Acelera!», «¡Curva rápida!»",
            "Inclinación, pendiente, rápido, lento, fricción, altura, peso."
        )
        pdf.savefig(fig6, dpi=150)
        plt.close(fig6)
        
        # PÁGINA 7: SET 4 · La Máquina de Soplo y Viento
        print("  -> Renderizando Página 7: Set 4 Máquina de Soplo...")
        fig7 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig7, 7, "S4", "LA MÁQUINA DE SOPLO Y VIENTO", "A Máquina de Sopro e Vento",
            "Neumática visual, praxias bucofonatorias y energía cinética del aire",
            [
                ("S4-CAN-E", "Canal recto de soplado", 2),
                ("S4-COD-E", "Codo de desvío 90°", 1),
                ("S4-ROT-JAULA/ASPAS", "Rotor tangencial montado", 2),
                ("S4-MOL-JAULA/ASPAS", "Molinete axial montado", 2),
                ("S4-COM-LIG-E", "Compuerta ligera basculante", 1),
                ("S4-COM-PES-E", "Compuerta pesada", 1),
            ],
            [
                ("CANALIZAR AIRE", "Conecta los dos tramos rectos S4-CAN-E y el codo sobre la mesa.", "Conecta os dous tramos rectos e o cóbado sobre a mesa."),
                ("MONTAR ROTOR", "Apoya el eje de las aspas en las cunas abiertas en U de la jaula.", "Apoia o eixo das aspas nas cunas en U da gaiola."),
                ("INSERTAR COMPUERTA", "Introduce la compuerta basculante en la ranura guía vertical del canal.", "Introduce a comparta basculante na rañura guía do canal."),
                ("SOPLAR Y OBSERVAR", "Sopla hacia la embocadura individual y comprueba la rotación y elevación.", "Sopra cara a embocadura e comproba o xiro e elevación."),
            ],
            "sets/S4-maquina-soplo/tarjetas/despiece.png", "sets/S4-maquina-soplo/tarjetas/planta.png",
            "El rotor gira con soplos suaves gracias al apoyo en U libre de fricción.",
            "Compartir embocaduras entre menores: utilizar siempre boquillas higiénicas desechables.",
            "«¡Sopra forte!», «¡Sopra amodo!», «¡Mofletes inflados!», «¡Xira!»",
            "Presión, flujo, aire, viento, rotación, ligero, pesado, impulso."
        )
        pdf.savefig(fig7, dpi=150)
        plt.close(fig7)
        
        # PÁGINA 8: SET 5 · El Puente de Equilibrio y Fuerza
        print("  -> Renderizando Página 8: Set 5 Puente de Equilibrio...")
        fig8 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig8, 8, "S5", "EL PUENTE DE EQUILIBRIO Y FUERZA", "A Ponte de Equilibrio e Forza",
            "Estática de palancas, balanza mecánica y equivalencias de masa",
            [
                ("S5-FUL-G", "Fulcro central prismático", 1),
                ("S5-VIG-G", "Viga calibrada alvéolos 31,8", 1),
                ("S5-MAS-20", "Masa calibrada de 20 g", 2),
                ("S5-MAS-40", "Masa calibrada de 40 g", 1),
                ("S5-MAS-60", "Masa calibrada de 60 g", 1),
                ("S5-PAS-G", "Clips pasadores en U", 4),
            ],
            [
                ("UBICAR FULCRO", "Apoya el fulcro triangular S5-FUL-G en el centro de la mesa.", "Apoia o fulcro triangular no centro da mesa."),
                ("NIVELAR VIGA", "Haz descansar la ranura central de la viga S5-VIG-G sobre la arista del fulcro.", "Descansa a rañura central da viga sobre a aresta do fulcro."),
                ("COLOCAR MASAS", "Introduce las masas cilíndricas en los alveolos laterales a distancias iguales.", "Introduce as masas nos alvéolos laterais a distancias iguais."),
                ("FIJAR CLIPS", "Asegura las masas mediante los pasadores en U y experimenta la palanca.", "Asegura as masas cos pasadores en U e experimenta a palanca."),
            ],
            "sets/S5-puente-equilibrio/tarjetas/despiece.png", "sets/S5-puente-equilibrio/tarjetas/planta.png",
            "La viga oscila libremente indicando el balance exacto de fuerzas (Ley de la Palanca).",
            "Colocar la viga descentrada: falsea la relación de equilibrio y provoca vuelcos bruscos.",
            "«¡Equilibrio!», «¡Inclina!», «¡Pesa máis!», «¡Queda recto!»",
            "Balanza, peso, distancia, centro, compensar, fuerza, fulcro."
        )
        pdf.savefig(fig8, dpi=150)
        plt.close(fig8)
        
        # PÁGINA 9: SET 6 · El Jardín del Sol, la Sombra y la Semilla
        print("  -> Renderizando Página 9: Set 6 Jardín del Sol...")
        fig9 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig9, 9, "S6", "EL JARDÍN DEL SOL Y LA SEMILLA", "O Xardín do Sol e a Semente",
            "Crecimiento vegetal, rosca helicoidal a 51°, botánica y sombras",
            [
                ("S6-TIE-G", "Base tierra roscada helicoidal", 1),
                ("S6-SEM-G", "Semilla táctil con rosca macho", 1),
                ("S6-TAL-G", "Tallos modulares roscados", 5),
                ("S6-FLO-G", "Flor de pétalos expandidos", 1),
                ("S6-COP-G", "Copa de árbol frondoso", 1),
                ("S6-FRU-*", "Frutos (manzana/naranja/pera)", 3),
            ],
            [
                ("PLANTAR SEMILLA", "Gira la semilla en sentido horario ↻ dentro de la rosca hembra de la base tierra.", "Xira a semente en sentido horario ↻ dentro da rosca da terra."),
                ("ENROSCAR TALLOS", "Acopla cada tallo adicional girando suavemente hasta sentir el tope natural.", "Acopla cada talo xirando amodo ata sentir o tope natural."),
                ("CORONAR FLOR", "Corona la planta con la flor S6-FLO-G o la copa frondosa S6-COP-G.", "Corona a planta coa flor ou a copa frondosa de árbore."),
                ("COLGAR FRUTOS", "Cuelga los frutos en los orificios de la copa y proyecta sombras con linterna.", "Colga os froitos e proxecta sombras cunha lanterna exterior."),
            ],
            "sets/S6-jardin/tarjetas/despiece.png", "sets/S6-jardin/tarjetas/planta.png",
            "La rosca helicoidal a 51° avanza 3 mm por vuelta sin holguras ni desprendimiento vertical.",
            "Tirar verticalmente hacia arriba para sacar la semilla: las roscas se desenroscan, no se tiran.",
            "«¡Xira e medra!», «¡Enrosca!», «¡Colle a mazá!», «¡Mira a sombra!»",
            "Crecimiento, ciclo vital, tallo, fruto, sombra, luz, enroscar."
        )
        pdf.savefig(fig9, dpi=150)
        plt.close(fig9)
        
        # PÁGINA 10: SET 8 · Comisaría y Estación de Policía
        print("  -> Renderizando Página 10: Set 8 Policía...")
        fig10 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig10, 10, "S8", "COMISARÍA Y ESTACIÓN DE POLICÍA", "Comisaría e Estación de Policía",
            "Seguridad ciudadana, roles de auxilio comunitario y vías de servicio",
            [
                ("S8-POL-BASE", "Base táctica de operaciones", 1),
                ("S8-POL-TORRE", "Torre de telecomunicaciones", 1),
                ("S8-POL-GAR", "Bahía de garaje para patrullas", 1),
                ("S8-POL-ACC", "Rampa de acceso de vehículos", 1),
            ],
            [
                ("ASENTAR BASE", "Coloca la base táctica de la comisaría sobre la alfombra de actividades.", "Coloca a base táctica da comisaría sobre a alfombra de xogo."),
                ("ACOPLAR TORRE", "Monta la torre de vigilancia en el encaje posterior derecho.", "Monta a torre de vixilancia no encaixe posterior dereito."),
                ("HABILITAR GARAJE", "Despliega la bahía de estacionamiento de vehículos de patrulla.", "Desprega o garaxe para os vehículos de patrulla e axuda."),
                ("CONECTAR AL CAMINO", "Enlaza la rampa frontal con el Camino de Lúa (Set 1) para patrullar.", "Enlaza a rampa co Camiño de Lúa para simular patrullas."),
            ],
            "escenas-juego/oficios/policia.png", "sets/S8-policia/escena.png",
            "La maqueta apoya plana y la rampa permite la entrada y salida fluida de vehículos.",
            "Colocar la torre inclinada: comprobar que la base asiente sin restos de filamento.",
            "«¡Chamada de auxilio!», «¡Ronda de seguridade!», «¡Todos a salvo!»",
            "Comunidad, protección, patrulla, acceso, vigilancia, alerta."
        )
        pdf.savefig(fig10, dpi=150)
        plt.close(fig10)
        
        # PÁGINA 11: SET 9 · Parque y Estación de Bomberos
        print("  -> Renderizando Página 11: Set 9 Bomberos...")
        fig11 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig11, 11, "S9", "PARQUE Y ESTACIÓN DE BOMBEROS", "Parque e Estación de Bombeiros",
            "Respuesta ante emergencias, extinción, rescate y coordinación motriz",
            [
                ("S9-BOM-BASE", "Nave hangar para camión", 1),
                ("S9-BOM-RAMPA", "Rampa de salida rápida", 1),
                ("S9-BOM-TORRE", "Torre de mangueras y escala", 1),
                ("S9-BOM-AUTOB", "Camión autobomba integrado", 1),
            ],
            [
                ("UBICAR HANGAR", "Coloca la nave principal del parque de bomberos en posición central.", "Coloca a nave principal do parque de bombeiros no centro."),
                ("ACOPLAR RAMPA", "Encaja la rampa inclinada de salida rápida en el frontal del hangar.", "Encaixa a rampa de saída rápida no frontal do hangar."),
                ("FIJAR TORRE", "Inserta la torre de maniobras y secado de mangueras sobre la cubierta.", "Inserta a torre de manobras sobre a cuberta do edificio."),
                ("LANZAR CAMIÓN", "Desliza el camión autobomba por la rampa gravitatoria hacia la misión.", "Desliza o camión pola rampa gravitatoria cara á misión."),
            ],
            "escenas-juego/oficios/bomberos.png", "sets/S9-bomberos/escena.png",
            "La rampa sin desniveles permite el lanzamiento del vehículo sin que tropiecen las ruedas.",
            "Obstruir la salida del hangar con piezas sueltas de otros sets.",
            "«¡Alarma de bombeiros!», «¡Saída rápida!», «¡Apaga o lume!», «¡Rescate!»",
            "Emergencia, auxilio, escala, manguera, velocidad, descenso."
        )
        pdf.savefig(fig11, dpi=150)
        plt.close(fig11)
        
        # PÁGINA 12: SET 10 · Hospital Infantil y Centro de Salud
        print("  -> Renderizando Página 12: Set 10 Hospital...")
        fig12 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig12, 12, "S10", "HOSPITAL INFANTIL Y CENTRO DE SALUD", "Hospital Infantil e Centro de Saúde",
            "Desmitificación sanitaria, empatía, cuidados pediátricos y calma",
            [
                ("S10-HOS-BASE", "Pabellón de admisión y triaje", 1),
                ("S10-HOS-RAMPA", "Rampa de acceso de ambulancia", 1),
                ("S10-HOS-HELI", "Helipuerto de cubierta", 1),
                ("S10-HOS-CAMI", "Camilla de exploración infantil", 1),
            ],
            [
                ("SITUAR PABELLÓN", "Apoya la estructura principal del hospital infantil con el frontal despejado.", "Apoia a estrutura principal coa entrada frontal despexada."),
                ("INSTALAR RAMPA", "Conecta la rampa suave de acceso para el transporte de ambulancias.", "Conecta a rampa suave de acceso para o transporte sanitario."),
                ("MONTAR HELIPUERTO", "Encaja la plataforma circular del helipuerto en la azotea del hospital.", "Encaixa a plataforma circular do heliporto na azotea."),
                ("ACOMPAÑAR A LÚA", "Guía a Lúa en su revisión pediátrica para normalizar la atención de salud.", "Acompaña a Lúa na súa revisión para normalizar a saúde."),
            ],
            "escenas-juego/oficios/hospital.png", "sets/S10-hospital/escena.png",
            "Entrada accesible y despejada que transmite calidez y tranquilidad a la criatura.",
            "Presentar la escena médica como castigo: fomentar siempre el juego de cuidados afectivos.",
            "«¡Revisión médica!», «¡Coitiño con mimo!», «¡Curar a ferida!», «¡Todo ben!»",
            "Cuidado, salud, calma, latido, médico, enfermería, bienestar."
        )
        pdf.savefig(fig12, dpi=150)
        plt.close(fig12)
        
        # PÁGINA 13: SET 11 · Red de Trenes y Ferrocarril
        print("  -> Renderizando Página 13: Set 11 Trenes...")
        fig13 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_set_page(
            fig13, 13, "S11", "RED DE TRENES Y FERROCARRIL", "Rede de Trens e Ferrocarril",
            "Movilidad colectiva, seguridad en pasos a nivel y secuencias de tracción",
            [
                ("S11-TRE-ESTA", "Estación de viajeros y andén", 1),
                ("S11-TRE-VIAS", "Tramos de vía férrea Duplo", 4),
                ("S11-TRE-BARR", "Barrera basculante de paso", 1),
                ("S11-TRE-CONV", "Locomotora y vagón de carga", 2),
            ],
            [
                ("TRAZAR VÍAS", "Une los tramos de vía férrea asegurando la continuidad de la ranura guía.", "Une os tramos de vía asegurando a continuidade da guía."),
                ("COLOCAR ESTACIÓN", "Adosa el edificio de la estación y su andén cubierto al tramo recto.", "Coloca o edificio da estación e o seu andén xunto á vía."),
                ("MONTAR BARRERA", "Inserta la barrera basculante en el paso peatonal cruzado.", "Inserta a barreira basculante no paso de peóns."),
                ("RODAR CONVOY", "Acopla el vagón a la locomotora y desliza el tren respetando las barreras.", "Acopla o vagón á locomotora e desliza o tren con precaución."),
            ],
            "escenas-juego/oficios/trenes.png", "sets/S11-trenes/escena.png",
            "Las vías quedan continuas y la barrera sube y baja suavemente sin atorarse.",
            "Cruzar el paso peatonal cuando la barrera de seguridad está bajada.",
            "«¡Pasaxeiros ao tren!», «¡Baixa a barreira!», «¡Pi-piiii!», «¡Parada!»",
            "Ferrocarril, andén, vía, barrera, convoy, locomotora, viaje."
        )
        pdf.savefig(fig13, dpi=150)
        plt.close(fig13)
        
        # PÁGINA 14: Cierre, Especificaciones Técnicas y Gobernanza
        print("  -> Renderizando Página 14: Cuadro Normativo y Cierre...")
        fig14 = plt.figure(figsize=(PAGE_WIDTH, PAGE_HEIGHT), dpi=150)
        render_closing_page(fig14)
        pdf.savefig(fig14, dpi=150)
        plt.close(fig14)
        
    print(f"Manual IKEA de los 11 sets generado con éxito: {output_path} ({os.path.getsize(output_path)} bytes)")
    
    # Copiar también a entrega/masque3d-sets-v1/ para el taller de fabricación
    entrega_dest = Path("entrega/masque3d-sets-v1/MANUAL-ENSAMBLAJE-IKEA.pdf")
    if entrega_dest.parent.exists():
        import shutil
        shutil.copyfile(output_path, entrega_dest)
        print(f"Copia para taller guardada en {entrega_dest} ({os.path.getsize(entrega_dest)} bytes)")


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "docs/MANUAL-ENSAMBLAJE-IKEA-11-SETS.pdf"
    build_manual_pdf(destino)
