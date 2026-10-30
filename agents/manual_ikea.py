#!/usr/bin/env python3
"""
manual_ikea.py · Manual de montaje tipo IKEA de los 11 sets de Lúa Construye (30/10/2026)
=========================================================================================

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P agents/render_manual_sets.py
    python3 agents/manual_ikea.py

Genera:
  - docs/MANUAL-ENSAMBLAJE-IKEA-11-SETS.html
  - docs/MANUAL-ENSAMBLAJE-IKEA-11-SETS.pdf
  - entrega/masque3d-sets-v1/MANUAL-ENSAMBLAJE-IKEA.pdf

A partir de los renders 3D de Blender Cycles en `docs/cad/manual/` (los STL reales de
`sets/*/stl/*.stl`, `entrega/masque3d-sets-v1/*/*.stl` y el muñeco Lúa V5 `el cubo de luz`
de `lua-firmware/cad/lua-v5/montaje/*.stl`). Si falta cualquier imagen 3D, aborta: no se
entrega un manual con huecos ni con esquemas de cajas.

NO PROBADO: describe el montaje diseñado en el código (30/10/2026). Que las piezas encajen
y aguanten impresas lo dirá la primera tirada en el PLA de Masque3D.
"""
from __future__ import annotations

import html
import os
import shutil
import sys
import textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-lua-manual")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
IMG_DIR = RAIZ / "docs" / "cad" / "manual"
SALIDA_HTML = RAIZ / "docs" / "MANUAL-ENSAMBLAJE-IKEA-11-SETS.html"
SALIDA_PDF = RAIZ / "docs" / "MANUAL-ENSAMBLAJE-IKEA-11-SETS.pdf"
SALIDA_ENTREGA_PDF = RAIZ / "entrega" / "masque3d-sets-v1" / "MANUAL-ENSAMBLAJE-IKEA.pdf"
FECHA = "30/10/2026"

# Dimensiones A4 en milímetros (coordenadas top-down: y=0 arriba, y=297 abajo)
W_MM = 210.0
H_MM = 297.0
M_X = 13.0
M_TOP = 13.0
M_BOT = 14.0
ANCHO_UTIL = W_MM - 2 * M_X  # 184 mm

C_TEXTO = "#1b1f24"
C_SUB = "#4b5563"
C_GRIS_BORDE = "#8b949e"
C_TABLA_HEAD = "#eaedf0"
C_TABLA_PAR = "#f7f8fa"
C_AVISO_BG = "#fffbeb"
C_AVISO_BORDE = "#1b1f24"
C_CHIP_BG = "#f3f4f6"


def verificar_imagen(nombre: str) -> Path:
    p = IMG_DIR / nombre
    if not p.is_file():
        sys.exit(
            f"✗ Falta la imagen 3D {p.relative_to(RAIZ)}. "
            "Corre antes: /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P agents/render_manual_sets.py"
        )
    return p


def recortar_estudio(ruta: Path, pad_ratio: float = 0.06) -> Image.Image:
    """Recorta el margen gris sobrante alrededor de las piezas 3D manteniendo el fondo de estudio."""
    im = Image.open(ruta).convert("RGB")
    arr = np.asarray(im, dtype=np.int16)
    bg = arr[0, 0]
    diff = np.abs(arr - bg).max(axis=2)
    ys, xs = np.where(diff > 7)
    if len(xs) == 0 or len(ys) == 0:
        return im
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    w_box = max(x1 - x0, 1)
    h_box = max(y1 - y0, 1)
    pad_x = int(w_box * pad_ratio) + 12
    pad_y = int(h_box * pad_ratio) + 12
    x0 = max(0, x0 - pad_x)
    y0 = max(0, y0 - pad_y)
    x1 = min(im.width, x1 + pad_x)
    y1 = min(im.height, y1 + pad_y)
    return im.crop((x0, y0, x1, y1))


class LienzoPagina:
    """Lienzo A4 con coordenadas en milímetros de arriba abajo (y=0 arriba, y=297 abajo).
    Garantiza que ningún bloque de texto, tabla o imagen 3D se solape ni se invierta."""

    def __init__(self, pdf: PdfPages, num_pagina: int, total_paginas: int):
        self.pdf = pdf
        self.num_pagina = num_pagina
        self.total_paginas = total_paginas
        self.fig = plt.figure(figsize=(W_MM / 25.4, H_MM / 25.4), dpi=300)
        self.fig.patch.set_facecolor("white")
        self.ax = self.fig.add_axes([0.0, 0.0, 1.0, 1.0])
        self.ax.set_xlim(0.0, W_MM)
        self.ax.set_ylim(H_MM, 0.0)  # y=0 arriba, y=297 abajo
        self.ax.axis("off")
        self.y = M_TOP

    def titulo_h1(self, texto: str, subtitulo: str = ""):
        self.ax.text(
            M_X, self.y, texto,
            fontsize=21.5, fontweight="bold", color=C_TEXTO,
            family="DejaVu Sans", va="top", ha="left"
        )
        self.y += 9.5
        if subtitulo:
            self.ax.text(
                M_X, self.y, subtitulo,
                fontsize=9.8, color=C_SUB,
                family="DejaVu Sans", va="top", ha="left"
            )
            self.y += 6.2

    def titulo_h2(self, codigo_set: str, titulo_es: str, titulo_gl: str, fase: str = ""):
        # Pastilla negra con el código del set
        w_tag = max(18.0, len(codigo_set) * 2.7 + 6.0)
        rect = FancyBboxPatch(
            (M_X, self.y), w_tag, 7.2,
            boxstyle="round,pad=0,rounding_size=1.4",
            facecolor=C_TEXTO, edgecolor=C_TEXTO, linewidth=1.0
        )
        self.ax.add_patch(rect)
        self.ax.text(
            M_X + w_tag / 2, self.y + 3.6, codigo_set,
            fontsize=9.5, fontweight="bold", color="white",
            family="DejaVu Sans", va="center", ha="center"
        )
        self.ax.text(
            M_X + w_tag + 3.2, self.y + 0.5, titulo_es,
            fontsize=12.4, fontweight="bold", color=C_TEXTO,
            family="DejaVu Sans", va="top", ha="left"
        )
        sub_linea = f"GL: {titulo_gl}" + (f"  ·  {fase}" if fase else "")
        self.ax.text(
            M_X + w_tag + 3.2, self.y + 5.6, sub_linea,
            fontsize=7.6, color=C_SUB,
            family="DejaVu Sans", va="top", ha="left"
        )
        self.y += 11.2
        self.ax.plot([M_X, W_MM - M_X], [self.y - 1.4, self.y - 1.4], color=C_TEXTO, linewidth=0.9)

    def chips(self, etiquetas: list[str]):
        x = M_X
        h_chip = 5.4
        for et in etiquetas:
            w = len(et) * 1.62 + 5.2
            if x + w > W_MM - M_X:
                x = M_X
                self.y += h_chip + 1.6
            r = FancyBboxPatch(
                (x, self.y), w, h_chip,
                boxstyle="round,pad=0,rounding_size=2.4",
                facecolor=C_CHIP_BG, edgecolor=C_TEXTO, linewidth=0.9
            )
            self.ax.add_patch(r)
            self.ax.text(
                x + w / 2, self.y + h_chip / 2, et,
                fontsize=7.8, fontweight="bold", color=C_TEXTO,
                family="DejaVu Sans", va="center", ha="center"
            )
            x += w + 2.2
        self.y += h_chip + 2.8

    def parrafo(self, texto: str, fontsize: float = 8.8, bold_prefix: str = "", color: str = C_TEXTO):
        ancho_chars = int(ANCHO_UTIL / (fontsize * 0.215))
        completo = (f"{bold_prefix} {texto}".strip()) if bold_prefix else texto
        lineas = textwrap.wrap(completo, width=ancho_chars)
        h_linea = fontsize * 0.44
        for i, lin in enumerate(lineas):
            pesos = "bold" if (i == 0 and bold_prefix and lin.startswith(bold_prefix) and len(lineas) == 1) else "normal"
            self.ax.text(
                M_X, self.y, lin,
                fontsize=fontsize, fontweight=pesos, color=color,
                family="DejaVu Sans", va="top", ha="left"
            )
            self.y += h_linea
        self.y += 1.8

    def aviso(self, titulo_negrita: str, texto: str, fontsize: float = 8.3):
        ancho_chars = int((ANCHO_UTIL - 7.0) / (fontsize * 0.218))
        lineas = textwrap.wrap(f"{titulo_negrita}  {texto}", width=ancho_chars)
        h_linea = fontsize * 0.44
        alto_caja = len(lineas) * h_linea + 4.4
        r = Rectangle(
            (M_X, self.y), ANCHO_UTIL, alto_caja,
            facecolor=C_AVISO_BG, edgecolor=C_AVISO_BORDE, linewidth=1.2
        )
        self.ax.add_patch(r)
        yy = self.y + 2.2
        for i, lin in enumerate(lineas):
            self.ax.text(
                M_X + 3.2, yy, lin,
                fontsize=fontsize,
                fontweight="bold" if i == 0 else "normal",
                color=C_TEXTO, family="DejaVu Sans", va="top", ha="left"
            )
            yy += h_linea
        self.y += alto_caja + 2.8

    def imagen(self, nombre_png: str, alto_mm: float, x_mm: float | None = None, ancho_mm: float | None = None, Pie: str = ""):
        ruta = verificar_imagen(nombre_png)
        im = recortar_estudio(ruta)
        x0 = M_X if x_mm is None else x_mm
        w_max = ANCHO_UTIL if ancho_mm is None else ancho_mm
        h_max = alto_mm

        # Contenedor gris suave con borde limpio
        r_bg = FancyBboxPatch(
            (x0, self.y), w_max, h_max,
            boxstyle="round,pad=0,rounding_size=1.8",
            facecolor="#eef0f3", edgecolor="#d0d7de", linewidth=0.7
        )
        self.ax.add_patch(r_bg)

        # Ajuste exacto de relación de aspecto dentro del contenedor (con margen interno de 1.2 mm)
        pad = 1.2
        w_in = max(w_max - 2 * pad, 5.0)
        h_in = max(h_max - 2 * pad, 5.0)
        aspect_im = im.width / max(im.height, 1)
        aspect_box = w_in / h_in
        if aspect_im >= aspect_box:
            w_fit = w_in
            h_fit = w_in / aspect_im
        else:
            h_fit = h_in
            w_fit = h_in * aspect_im

        x_fit = x0 + (w_max - w_fit) / 2.0
        y_fit = self.y + (h_max - h_fit) / 2.0

        # Axes dedicado en coordenadas normalizadas de figura [left, bottom, width, height].
        # origin='upper' por defecto en ax_img garantiza que la imagen SIEMPRE salga al derecho.
        left_norm = x_fit / W_MM
        bottom_norm = (H_MM - (y_fit + h_fit)) / H_MM
        width_norm = w_fit / W_MM
        height_norm = h_fit / H_MM
        ax_img = self.fig.add_axes([left_norm, bottom_norm, width_norm, height_norm])
        ax_img.imshow(im, origin="upper")
        ax_img.axis("off")

        self.y += h_max + 1.4
        if Pie:
            self.ax.text(
                x0 + w_max / 2, self.y, Pie,
                fontsize=7.6, color=C_SUB,
                family="DejaVu Sans", va="top", ha="center"
            )
            self.y += 4.2
        else:
            self.y += 1.4

    def tabla(
        self,
        cabeceras: list[str],
        filas: list[list[str]],
        anchos_mm: list[float],
        fontsize: float = 7.7,
    ):
        h_linea = fontsize * 0.43
        pad_v = 1.4
        # Cabecera
        h_head = h_linea + 2 * pad_v + 0.4
        x = M_X
        for col_idx, (cab, w_col) in enumerate(zip(cabeceras, anchos_mm)):
            r = Rectangle(
                (x, self.y), w_col, h_head,
                facecolor=C_TABLA_HEAD, edgecolor=C_GRIS_BORDE, linewidth=0.65
            )
            self.ax.add_patch(r)
            self.ax.text(
                x + 1.8, self.y + pad_v + 0.2, cab,
                fontsize=fontsize, fontweight="bold", color=C_TEXTO,
                family="DejaVu Sans", va="top", ha="left"
            )
            x += w_col
        self.y += h_head

        # Filas
        for r_idx, fila in enumerate(filas):
            celdas_envueltas = []
            max_lineas = 1
            for texto_celda, w_col in zip(fila, anchos_mm):
                max_c = max(6, int((w_col - 3.2) / (fontsize * 0.218)))
                lins = textwrap.wrap(str(texto_celda), width=max_c) or [""]
                celdas_envueltas.append(lins)
                max_lineas = max(max_lineas, len(lins))
            h_fila = max_lineas * h_linea + 2 * pad_v
            bg = C_TABLA_PAR if r_idx % 2 == 1 else "white"
            x = M_X
            for c_idx, (lins, w_col) in enumerate(zip(celdas_envueltas, anchos_mm)):
                r = Rectangle(
                    (x, self.y), w_col, h_fila,
                    facecolor=bg, edgecolor=C_GRIS_BORDE, linewidth=0.55
                )
                self.ax.add_patch(r)
                peso = "bold" if c_idx == 0 else "normal"
                for l_i, l_txt in enumerate(lins):
                    self.ax.text(
                        x + 1.8, self.y + pad_v + l_i * h_linea, l_txt,
                        fontsize=fontsize, fontweight=peso, color=C_TEXTO,
                        family="DejaVu Sans", va="top", ha="left"
                    )
                x += w_col
            self.y += h_fila
        self.y += 2.6

    def paso_ikea(
        self,
        num: int,
        titulo_es: str,
        titulo_gl: str,
        codigos: list[str],
        texto_es: str,
        texto_gl: str,
        nombre_png: str,
        alto_bloque_mm: float = 72.0,
    ):
        """Dibuja un bloque de paso estilo IKEA / lua-firmware:
        columna izquierda con número grande, título bilingüe, chips de códigos y explicación;
        columna derecha con el render 3D real de Blender con flechas rojas de montaje."""
        y0 = self.y
        w_izq = 78.0
        w_der = ANCHO_UTIL - w_izq - 4.0
        x_der = M_X + w_izq + 4.0

        # Marco sutil del paso
        marco = FancyBboxPatch(
            (M_X, y0), ANCHO_UTIL, alto_bloque_mm,
            boxstyle="round,pad=0,rounding_size=1.8",
            facecolor="white", edgecolor="#d0d7de", linewidth=0.75
        )
        self.ax.add_patch(marco)

        # Número grande del paso y cabecera a ancho completo del bloque
        x_tit = M_X + (18.5 if num >= 10 else 13.5)
        self.ax.text(
            M_X + 3.0, y0 + 1.8, str(num),
            fontsize=23.5, fontweight="bold", color=C_TEXTO,
            family="DejaVu Sans", va="top", ha="left"
        )
        self.ax.text(
            x_tit, y0 + 2.0, titulo_es,
            fontsize=10.1, fontweight="bold", color=C_TEXTO,
            family="DejaVu Sans", va="top", ha="left"
        )
        self.ax.text(
            x_tit, y0 + 6.4, f"GL: {titulo_gl}",
            fontsize=7.7, color=C_SUB,
            family="DejaVu Sans", va="top", ha="left"
        )

        # Chips de piezas que intervienen en el paso
        yk = y0 + 11.4
        xk = M_X + 3.0
        for cod in codigos:
            wc = len(cod) * 1.62 + 4.8
            if xk + wc > M_X + w_izq:
                xk = M_X + 3.0
                yk += 5.0
            rc = FancyBboxPatch(
                (xk, yk), wc, 4.3,
                boxstyle="round,pad=0,rounding_size=1.0",
                facecolor=C_CHIP_BG, edgecolor=C_TEXTO, linewidth=0.75
            )
            self.ax.add_patch(rc)
            self.ax.text(
                xk + wc / 2, yk + 2.15, cod,
                fontsize=6.9, fontweight="bold", color=C_TEXTO,
                family="DejaVu Sans", va="center", ha="center"
            )
            xk += wc + 1.6
        yk += 6.0

        # Texto ES
        ancho_chars = int((w_izq - 5.0) / (8.0 * 0.218))
        for lin in textwrap.wrap(f"ES: {texto_es}", width=ancho_chars):
            self.ax.text(
                M_X + 3.0, yk, lin,
                fontsize=8.0, color=C_TEXTO,
                family="DejaVu Sans", va="top", ha="left"
            )
            yk += 3.5
        yk += 1.3
        # Texto GL
        for lin in textwrap.wrap(f"GL: {texto_gl}", width=ancho_chars):
            self.ax.text(
                M_X + 3.0, yk, lin,
                fontsize=7.6, color=C_SUB,
                family="DejaVu Sans", va="top", ha="left"
            )
            yk += 3.3

        # Imagen 3D a la derecha (debajo de la banda de título para no pisar nunca el texto)
        self.y = y0 + 11.0
        self.imagen(nombre_png, alto_mm=alto_bloque_mm - 12.8, x_mm=x_der, ancho_mm=w_der)
        self.y = y0 + alto_bloque_mm + 3.2

    def cerrar(self):
        # Línea y pie de página fijo en el margen inferior
        y_pie = H_MM - M_BOT + 2.0
        self.ax.plot([M_X, W_MM - M_X], [y_pie - 2.2, y_pie - 2.2], color="#d0d7de", linewidth=0.6)
        self.ax.text(
            M_X, y_pie,
            f"Lúa Construye · Manual 11 sets ({FECHA})",
            fontsize=7.1, color=C_SUB, family="DejaVu Sans", va="top", ha="left"
        )
        self.ax.text(
            W_MM * 0.59, y_pie,
            "NO PROBADO · Montaje diseñado en CAD (verificar en tirada PLA)",
            fontsize=7.0, fontweight="bold", color=C_SUB, family="DejaVu Sans", va="top", ha="center"
        )
        self.ax.text(
            W_MM - M_X, y_pie,
            f"{self.num_pagina} / {self.total_paginas}",
            fontsize=7.8, fontweight="bold", color=C_TEXTO, family="DejaVu Sans", va="top", ha="right"
        )
        self.pdf.savefig(self.fig)
        plt.close(self.fig)


# ==============================================================================
# DATOS DE LOS SETS Y PÁGINAS (fieles al código 30/10/2026 y piezas.csv)
# ==============================================================================

TABLA_PAQUETE_PORTADA = [
    ["P1-probeta-encaje", "Fase 1 · Probetas de encaje G y E", "12", "306 g", "Se imprime ANTES que los sets (holguras 0,15 / 0,20 / 0,25 mm)"],
    ["00-comun", "Fase 2 · Zócalo, patín, 7 placas y 6 pilares", "15", "760 g", "Común a los sets 1 a 6 · Huella de Lúa V5 (cubo 108×108 mm)"],
    ["S1-camino", "Fase 3 · Set 1: El Camino de Lúa", "10 (23 ud)", "1303 g", "Baldosas con colas de milano, fichas de orden y 2 destinos"],
    ["S2-estacion-sonido", "Fase 7 · Set 2: La Estación de Sonido y Eco", "13 (14 ud)", "1831 g", "Martillo articulado, 9 resonadores (A/B/C), raspadores y espátula"],
    ["S3-laboratorio-rampas", "Fase 5 · Set 3: Laboratorio de Rampas y Gravedad", "7 (9 ud)", "684 g", "Bisagra en C, rampa L=8H, fricción, curva peraltada, receptor y esferas"],
    ["S4-maquina-soplo", "Fase 8 · Set 4: La Máquina de Soplo y Viento", "8 (9 ud)", "989 g", "Canal, codo 90°, rotor E, molinete G y 2 compuertas (sin embocadura)"],
    ["S5-puente-equilibrio", "Fase 4 · Set 5: El Puente de Equilibrio y Fuerza", "6 (10 ud)", "415 g", "Fulcro redondeado, viga de 186 mm, masas 20/40/60 g y clips en U"],
    ["S6-jardin", "Fase 6 · Set 6: El Jardín del Sol y la Semilla", "12 (16 ud)", "1274 g", "Tierra, semilla, 5 tallos roscados, flor, copa, 3 frutos, prismas y sombras"],
    ["NO-IMPRIMIR (S7)", "Set 7 · La Granja de Lúa (excluido del ZIP)", "0", "—", "Escena de la app con partes en el aire · Pendiente de despiezar"],
    ["S8..S11 (Oficios)", "Sets 8, 9, 10 (60 %) y Set 11 (33 %) · Maquetas", "4", "1379 g", "Escenas decorativas de una pieza sin soporte · No son sets de bloques"],
]

SETS_PAGINAS = [
    {
        "codigo": "S1",
        "carpeta": "S1-camino",
        "titulo_es": "Set 1 · El Camino de Lúa",
        "titulo_gl": "Set 1 · O Camiño de Lúa",
        "fase": "Fase 3 del plan de impresión · 10 STL propios + comunes de 00-comun",
        "resumen_es": (
            "Circuito físico de orientación espacial y secuencias paso a paso. El niño mira a Lúa V5 desde atrás "
            "para que la izquierda y la derecha de Lúa coincidan con las manos del niño. Las baldosas se unen por "
            "colas de milano verticales (resisten el empuje horizontal sin soltarse)."
        ),
        "aviso_tit": "ORIENTACIÓN Y PATÍN:",
        "aviso_txt": (
            "Lúa V5 (el cubo de 108 × 108 mm) se apoya sobre la bandeja K-PATIN-G, cuyos dos pivotes inferiores "
            "(Ø11,6 mm) corren por la ranura de 12 mm. En el zócalo de Inicio (K-ZOCALO-G), las patas delanteras de "
            "Lúa solo caben mirando hacia el camino (+X)."
        ),
        "img_despiece": "s1_despiece.png",
        "bom": [
            ["S1-REC-LIS-G", "Baldosa recta lisa con ranura de 12 mm y pozo", "4", "136,8 × 127,2 × 19,2 mm", "Colas de milano macho (+X) y hembra (0)"],
            ["S1-REC-RUG-G", "Baldosa recta rugosa (nervios táctiles de 1,5 mm)", "2", "136,8 × 127,2 × 20,7 mm", "Relieve redondeado en el lado −Y"],
            ["S1-CUR-G", "Baldosa curva de 90° con cuarto de anillo", "4", "127,2 × 136,8 × 19,2 mm", "Hembra en X=0 y macho en Y=127,2 mm"],
            ["S1-TEE-G", "Baldosa de bifurcación en T (tres bocas)", "1", "136,8 × 136,8 × 19,2 mm", "Paso recto en X y rama lateral hacia +Y"],
            ["S1-CMD-AVA/GIR/PAR/SAL-G", "Fichas de orden: Avanza (4), Gira (3), Para (2), Salta (1)", "10", "57,6 × 36,0 × 9,4 mm", "Snap lateral + recorte de llave 10,2 mm"],
            ["S1-DEST-CAMA / PARQUE", "Placas de destino: Cama y Parque", "2", "89,6 × 54,0 × 7,8 mm", "Entran en el bolsillo del segundo zócalo"],
            ["K-ZOCALO-G + K-PATIN-G", "Zócalo universal (×2) + Bandeja patín (de 00-comun)", "2 + 1", "136,8×190,8 / 116×122 mm", "Inicio y Meta + bandeja guía de Lúa V5"],
        ],
        "pasos": [
            (
                1,
                "Acoplar el zócalo de Inicio y la primera baldosa",
                "Acoplar o zócalo de Inicio e a primeira lousa",
                ["K-ZOCALO-G", "K-PLACA-INICIO", "S1-REC-LIS-G"],
                "Encaja la placa K-PLACA-INICIO en el bolsillo lateral del zócalo hasta notar el clic. Alinea las dos "
                "colas de milano hembra de S1-REC-LIS-G sobre los machos frontales del zócalo y desliza verticalmente "
                "hacia abajo hasta que las bases apoyen en la mesa.",
                "Encaixa a placa K-PLACA-INICIO no peto lateral do zócalo ata notar o clic. Aliña as dúas colas de "
                "milano femia de S1-REC-LIS-G sobre os machos frontais do zócalo e desliza cara abaixo.",
                "s1_paso_1.png",
            ),
            (
                2,
                "Trazar el camino: rectas, curva, bifurcación y meta",
                "Trazar o camiño: rectas, curva, bifurcación e meta",
                ["S1-REC-RUG-G", "S1-TEE-G", "S1-CUR-G", "S1-DEST-CAMA"],
                "Continúa encadenando de arriba abajo los tramos rectos o rugosos, la te de bifurcación S1-TEE-G y "
                "las curvas S1-CUR-G. Cierra el final del camino acoplando el segundo zócalo con K-PLACA-META o con "
                "las placas de destino S1-DEST-CAMA / S1-DEST-PARQUE.",
                "Continúa encadeando de arriba abaixo os tramos rectos ou rugosos, a bifurcación S1-TEE-G e as curvas "
                "S1-CUR-G. Pecha o final co segundo zócalo e a placa de Meta ou Destino.",
                "s1_paso_2.png",
            ),
            (
                3,
                "Colocar las fichas de comando y deslizar a Lúa V5",
                "Colocar as fichas de comando e deslizar a Lúa V5",
                ["S1-CMD-AVA-G", "S1-CMD-GIR-G", "K-PATIN-G", "LUA-V5"],
                "Baja cada ficha S1-CMD-* en el pozo de su baldosa haciendo coincidir la esquina recortada con el "
                "poste de llave hasta oír el snap. Pon la bandeja K-PATIN-G en la ranura de 12 mm, apoya dentro a "
                "Lúa V5 mirando al frente del camino y deslízala siguiendo las órdenes.",
                "Baixa cada ficha S1-CMD-* no pozo da súa lousa facendo coincidir a esquina recortada co poste de "
                "chave ata oír o snap. Pon o patín K-PATIN-G na rañura de 12 mm e apoia dentro a Lúa V5.",
                "s1_paso_3.png",
            ),
        ],
    },
    {
        "codigo": "S2",
        "carpeta": "S2-estacion-sonido",
        "titulo_es": "Set 2 · La Estación de Sonido y Eco",
        "titulo_gl": "Set 2 · A Estación de Son e Eco",
        "fase": "Fase 7 del plan de impresión · 13 STL propios + comunes de 00-comun",
        "resumen_es": (
            "Exploración acústica analógica de timbre, altura tonal (grave, medio, agudo) y ritmo mediante "
            "percusión y raspado. Lúa V5 se coloca de frente al niño sobre el zócalo con la placa Escucha; "
            "la tableta nunca emite audio encima del sonido físico de la pieza."
        ),
        "aviso_tit": "NOTA TÉCNICA HONESTA (LEEME-masque3d.md):",
        "aviso_txt": (
            "Cada familia de resonador (Azul grave, Amarillo medio, Rojo agudo) incluye 3 variantes (A, B, C) con "
            "pared de 8 mm y distinta cavidad/garganta para probar al oído cuál suena más distinto. El cuerpo del "
            "resonador mide 78 × 64 mm y el rebaje entre las mejillas del banco mide 34 × 34 mm (punto abierto)."
        ),
        "img_despiece": "s2_despiece.png",
        "bom": [
            ["S2-BAL-BASE-E", "Banco del martillo con mejillas en C", "1", "120,0 × 78,0 × 52,0 mm", "Aloja el eje del brazo sin pasadores sueltos"],
            ["S2-BAL-BRAZO-E", "Brazo del martillo con eje integral y maza", "1", "98,4 × 58,0 × 28,0 mm", "Eje Ø10,4 mm integrado en una sola pieza"],
            ["S2-RES-AZU-E-A/B/C", "Resonador grave (azul) · variantes A, B y C", "3", "78,0 × 64,0 × 72,0 mm", "Cavidad r=16 mm, prof 46/40 mm, garganta 6/7,2 mm"],
            ["S2-RES-AMA-E-A/B/C", "Resonador medio (amarillo) · variantes A, B y C", "3", "78,0 × 64,0 × 72,0 mm", "Cavidad r=13 mm, prof 34/28 mm, garganta 9/10,2 mm"],
            ["S2-RES-ROJ-E-A/B/C", "Resonador agudo (rojo) · variantes A, B y C", "3", "78,0 × 64,0 × 72,0 mm", "Cavidad r=10 mm, prof 24/18 mm, garganta 12/13,2 mm"],
            ["S2-RAS-E", "Raspador estriado encadenable", "2", "144,0 × 44,0 × 18,2 mm", "11 estrías redondeadas (r=2,2 mm) + espiga y mortaja"],
            ["S2-ESP-E", "Espátula sin filo (punta semicilíndrica)", "1", "122,0 × 44,0 × 16,0 mm", "Punta redondeada r=7 mm · Incluye mortaja trasera"],
            ["K-ZOCALO-G + ESCUCHA", "Zócalo universal + Placa Escucha (de 00-comun)", "1 + 1", "136,8 × 190,8 × 40,8 mm", "Lúa V5 mira de frente al niño (sin espejo)"],
        ],
        "pasos": [
            (
                1,
                "Encajar el brazo del martillo en el banco",
                "Encaixar o brazo do martelo no banco",
                ["S2-BAL-BASE-E", "S2-BAL-BRAZO-E"],
                "Apoya el banco S2-BAL-BASE-E en la mesa. Alinea los dos extremos del eje integral de S2-BAL-BRAZO-E "
                "sobre las bocas superiores en C de las mejillas del banco y presiona recto hacia abajo hasta que el "
                "eje entre en su alojamiento cilíndrico y bascule libremente.",
                "Apoia o banco S2-BAL-BASE-E na mesa. Aliña o eixe integral de S2-BAL-BRAZO-E sobre as bocas en C das "
                "meixelas do banco e preme recto cara abaixo ata que bascule libremente.",
                "s2_paso_1.png",
            ),
            (
                2,
                "Situar los resonadores y comparar las variantes A, B y C",
                "Situar os resoadores e comparar as variantes A, B e C",
                ["S2-RES-AZU-E-A", "S2-RES-AMA-E-A", "S2-RES-ROJ-E-A"],
                "Coloca un resonador ante la maza del martillo con la boca circular hacia arriba. En el taller, "
                "prueba con el martillo las variantes A, B y C de cada color (Azul grave, Amarillo medio, Rojo agudo) "
                "para elegir el trío cuyo timbre se distinga mejor al oído.",
                "Coloca un resoador ante a maza do martelo coa boca circular cara arriba. Proba as variantes A, B e C "
                "de cada cor (Azul grave, Amarelo medio, Vermello agudo) e escolle as que soen máis distintas.",
                "s2_paso_2.png",
            ),
            (
                3,
                "Encadenar los raspadores, usar la espátula y situar a Lúa",
                "Encadear os raspadores, usar a espátula e situar a Lúa",
                ["S2-RAS-E", "S2-ESP-E", "K-ZOCALO-G", "K-PLACA-ESCUCHA"],
                "Para un recorrido de raspado largo, introduce la espiga saliente de un S2-RAS-E en la mortaja del "
                "segundo S2-RAS-E. Desliza la punta redondeada de S2-ESP-E sobre las estrías. Coloca al lado el "
                "zócalo con K-PLACA-ESCUCHA y a Lúa V5 mirando de frente al niño.",
                "Introduce a espiga dun S2-RAS-E na mortaxa do segundo S2-RAS-E e desliza a espátula S2-ESP-E sobre "
                "as estrías. Coloca ao lado o zócalo con K-PLACA-ESCUCHA e a Lúa V5 mirando de fronte.",
                "s2_paso_3.png",
            ),
        ],
    },
    {
        "codigo": "S3",
        "carpeta": "S3-laboratorio-rampas",
        "titulo_es": "Set 3 · El Laboratorio de Rampas y Gravedad",
        "titulo_gl": "Set 3 · O Laboratorio de Rampas e Gravidade",
        "fase": "Fase 5 del plan de impresión · 7 STL propios + pilares y zócalo de 00-comun",
        "resumen_es": (
            "Experimentación física de pendiente, velocidad, rozamiento y conservación del movimiento. La altura "
            "modular es H = 19,20 mm (para que la rampa L = 8H = 153,60 mm quepa en la cama de 220 mm). Las dos "
            "esferas miden Ø45,0 mm (> 44,5 mm EN 71-1) y diferencian liso frente a rugoso sin piezas sueltas."
        ),
        "aviso_tit": "PROTECCIÓN DE LÚA V5:",
        "aviso_txt": (
            "El receptor final S3-REC-G incorpora una lengüeta transversal de tope un módulo (40 mm) antes de su "
            "extremo trasero. Así la esfera se detiene siempre dentro de la cubeta y nunca golpea a Lúa V5."
        ),
        "img_despiece": "s3_despiece.png",
        "bom": [
            ["S3-BIS-G", "Bloque bisagra con alojamiento en C", "1", "72,0 × 96,0 × 50,0 mm", "Recibe el eje de la rampa sin pasador suelto"],
            ["S3-RAM-G", "Rampa articulada en U con eje transversal", "1", "153,6 × 100,0 × 24,0 mm", "Canal interior de 48 mm para esferas de Ø45 mm"],
            ["S3-PIL-1..6-G", "Pilares apilables con 1 a 6 barras táctiles (de 00-comun)", "6", "44,0 × 47,2 × 25,2 mm", "Altura útil H = 19,20 mm · Tetón superior y pozo inferior"],
            ["S3-FRI-G", "Tramo de fricción reversible (9 nervios cilíndricos)", "1", "132,0 × 64,0 × 17,8 mm", "Cara superior nervada y cara inferior lisa + lengüeta"],
            ["S3-CUR-PER-G", "Curva peraltada de 90° (canal de revolución)", "1", "150,0 × 150,0 × 26,0 mm", "Fondo peraltado (z=8 mm dentro, z=12 mm fuera)"],
            ["S3-REC-G", "Receptor final con lengüeta de parada", "1", "156,0 × 80,0 × 36,0 mm", "Detiene la esfera 40 mm antes del borde trasero"],
            ["S3-ESF-LIS-G / RUG-G", "Esferas Ø45 mm: 2 lisas y 2 rugosas (14 botones)", "2 + 2", "Ø45,0 mm", "Superan el umbral de 44,5 mm para menores de 3 años"],
            ["K-ZOCALO-G + RECEPTOR", "Zócalo universal + Placa Receptor (de 00-comun)", "1 + 1", "136,8 × 190,8 × 40,8 mm", "Se sitúa detrás del receptor final"],
        ],
        "pasos": [
            (
                1,
                "Articular la rampa en la bisagra y graduar la altura con pilares",
                "Articular a rampa na bisagra e graduar a altura con piares",
                ["S3-BIS-G", "S3-RAM-G", "S3-PIL-1-G", "S3-PIL-2-G"],
                "Asienta el bloque bisagra S3-BIS-G y baja el eje transversal de la rampa S3-RAM-G dentro de su boca "
                "en C superior. Apila bajo la rampa los pilares graduados S3-PIL-1..6-G: dos pilares dan pendiente "
                "suave; cuatro pilares dan pendiente pronunciada.",
                "Asenta o bloque bisagra S3-BIS-G e baixa o eixe transversal da rampa S3-RAM-G na boca en C. Apila "
                "baixo a rampa os piares S3-PIL-1..6-G segundo a pendente buscada.",
                "s3_paso_1.png",
            ),
            (
                2,
                "Encadenar el tramo de fricción y la curva peraltada",
                "Encadear o tramo de fricción e a curva peraltada",
                ["S3-FRI-G", "S3-CUR-PER-G"],
                "A la salida de la rampa, acopla el tramo de fricción S3-FRI-G (con los nervios hacia arriba para "
                "frenar la esfera, o volteado del lado liso para dejarla correr) y, si el reto lo pide, encadena "
                "la curva peraltada de 90° S3-CUR-PER-G.",
                "Á saída da rampa, acopla o tramo de fricción S3-FRI-G (cos nervios cara arriba para frear ou liso "
                "para correr) e, se o reto o pide, a curva peraltada S3-CUR-PER-G.",
                "s3_paso_2.png",
            ),
            (
                3,
                "Cerrar con el receptor, proteger a Lúa y soltar las esferas",
                "Pechar co receptor, protexer a Lúa e soltar as esferas",
                ["S3-REC-G", "K-ZOCALO-G", "K-PLACA-RECEPTOR", "S3-ESF-LIS-G"],
                "Encaja la mortaja frontal del receptor S3-REC-G en la lengüeta del tramo anterior, con la pared de "
                "parada mirando hacia la rampa. Sitúa detrás el zócalo con K-PLACA-RECEPTOR y a Lúa V5, y suelta "
                "desde arriba la esfera lisa o rugosa para comparar su llegada.",
                "Encaixa o receptor S3-REC-G coa lingüeta mirando cara á rampa. Sitúa detrás o zócalo con "
                "K-PLACA-RECEPTOR e a Lúa V5, e solta desde arriba a esfera lisa ou rugosa.",
                "s3_paso_3.png",
            ),
        ],
    },
    {
        "codigo": "S4",
        "carpeta": "S4-maquina-soplo",
        "titulo_es": "Set 4 · La Máquina de Soplo y Viento",
        "titulo_gl": "Set 4 · A Máquina de Sopro e Vento",
        "fase": "Fase 8 del plan de impresión · 8 STL propios + comunes de 00-comun",
        "resumen_es": (
            "Juego aerodinámico de causa-efecto (dirección del aire y resistencia mecánica entre compuerta ligera y "
            "pesada). Finalidad exclusivamente lúdica y educativa: no es un espirómetro ni un tratamiento del velo. "
            "Las jaulas son abiertas por arriba con cunas en U en las paredes X para apoyar el eje de las aspas."
        ),
        "aviso_tit": "HIGIENE Y MENORES DE 3 AÑOS:",
        "aviso_txt": (
            "La embocadura personal (S4-EMB-E) NO está en esta carpeta ni se imprime en PLA FDM por higiene (las "
            "estrías entre capas acumulan humedad y no soportan lavado térmico). Con menores de 3 años solo se usa "
            "el molinete G (S4-MOL-*) y sopla la persona adulta."
        ),
        "img_despiece": "s4_despiece.png",
        "bom": [
            ["S4-CAN-E", "Cuerpo del canal aerodinámico con tobera Ø4 mm", "2", "156,0 × 52,0 × 52,0 mm", "Conducto interior cónico Ø24 → Ø4 mm + 2 pozos arriba"],
            ["S4-COD-E", "Codo de 90° para desviar el flujo de aire", "1", "78,0 × 78,0 × 40,0 mm", "Tubo interior r=8 mm y pared exterior r=20 mm"],
            ["S4-ROT-JAULA-E", "Jaula abierta del rotor con cunas en U", "1", "96,0 × 72,0 × 72,0 mm", "Pared de 8 mm, ventanas de aire y cuna r=5,4 mm"],
            ["S4-ROT-ASPAS-E", "Rotor de 4 aspas con eje integral", "1", "98,0 × 48,0 × 48,0 mm", "Eje Ø9,2 mm que asoma 1 mm por cada lado de la jaula"],
            ["S4-MOL-JAULA-G", "Jaula abierta del molinete (escala G)", "1", "120,0 × 96,0 × 96,0 mm", "Pared de 10 mm y cunas en U de r=6,2 mm"],
            ["S4-MOL-ASPAS-G", "Aspas anchas del molinete con eje integral", "1", "122,0 × 64,0 × 64,0 mm", "Eje Ø10,4 mm · Para soplo del adulto en etapa I2"],
            ["S4-COM-LIG-E / PES-E", "Compuerta ligera (1 barra, 8 mm) y pesada (3 barras, 16 mm)", "1 + 1", "76,0 × 44,0 × 16/24 mm", "Diferencia de masa por volumen de PLA (sin lastre suelto)"],
            ["K-ZOCALO-G + FRONTAL", "Zócalo universal + Placa Frontal (de 00-comun)", "1 + 1", "136,8 × 190,8 × 40,8 mm", "Lúa V5 mira de frente al niño"],
        ],
        "pasos": [
            (
                1,
                "Alojar las aspas en las cunas en U de su jaula",
                "Aloxar as aspas nos berces en U da súa gaiola",
                ["S4-ROT-JAULA-E", "S4-ROT-ASPAS-E", "S4-MOL-JAULA-G", "S4-MOL-ASPAS-G"],
                "Toma la jaula S4-ROT-JAULA-E (o S4-MOL-JAULA-G para el molinete grande) e introduce desde arriba el "
                "eje integral de las aspas S4-ROT-ASPAS-E (o S4-MOL-ASPAS-G) en las dos cunas en U de las paredes "
                "laterales. Comprueba con el dedo que gira libre sin rozar.",
                "Toma a gaiola S4-ROT-JAULA-E (ou S4-MOL-JAULA-G) e introduce desde arriba o eixe integral das aspas "
                "nos dous berces en U das paredes laterais. Comproba que xira sen rozar.",
                "s4_paso_1.png",
            ),
            (
                2,
                "Acoplar el canal, el codo de 90° y las compuertas",
                "Acoplar a canle, o cóbado de 90° e as comportas",
                ["S4-CAN-E", "S4-COD-E", "S4-COM-LIG-E", "S4-COM-PES-E"],
                "Sitúa el canal S4-CAN-E en la mesa y, si el reto pide doblar el recorrido del aire, enchufa en su "
                "boca el codo de 90° S4-COD-E. Clava la espiga de la compuerta ligera S4-COM-LIG-E (1 barra táctil) "
                "o de la pesada S4-COM-PES-E (3 barras táctiles) en los pozos superiores del canal.",
                "Sitúa a canle S4-CAN-E na mesa e, se o reto o pide, acopla o cóbado S4-COD-E. Crava a comporta "
                "lixeira S4-COM-LIG-E (1 barra) ou a pesada S4-COM-PES-E (3 barras) nos pozos superiores.",
                "s4_paso_2.png",
            ),
            (
                3,
                "Enfrentar la salida de aire al rotor y colocar a Lúa V5",
                "Enfrontar a saída de aire ao rotor e colocar a Lúa V5",
                ["S4-CAN-E", "S4-MOL-JAULA-G", "K-ZOCALO-G", "K-PLACA-FRONTAL"],
                "Alinea el orificio de salida del canal (Ø4 mm) frente a la ventana de la jaula del rotor o del "
                "molinete. Coloca al lado el zócalo con la placa K-PLACA-FRONTAL y a Lúa V5 mirando al niño.",
                "Aliña o orificio de saída da canle (Ø4 mm) fronte á xanela da gaiola do rotor ou do muíño. Coloca "
                "ao lado o zócalo coa placa K-PLACA-FRONTAL e a Lúa V5 mirando ao neno.",
                "s4_paso_3.png",
            ),
        ],
    },
    {
        "codigo": "S5",
        "carpeta": "S5-puente-equilibrio",
        "titulo_es": "Set 5 · El Puente de Equilibrio y Fuerza",
        "titulo_gl": "Set 5 · A Ponte de Equilibrio e Forza",
        "fase": "Fase 4 del plan de impresión · 6 STL propios + pilares y zócalo de 00-comun",
        "resumen_es": (
            "Palanca de primer género, ley del equilibrio (masa × distancia al fulcro) y construcción de un puente "
            "fijo estable. La viga mide 186 × 48 × 18 mm (diez módulos de 31,80 mm medirían 318 mm y no cabrían en "
            "la cama de 220 mm) e incorpora 5 pozos numerados a cada lado con marcas táctiles en los bordes."
        ),
        "aviso_tit": "REGLA DE SEGURIDAD DE LÚA V5:",
        "aviso_txt": (
            "Lúa V5 se coloca siempre en su zócalo con la placa Nivel junto a la viga, NUNCA encima del balancín "
            "suelto. Las masas de 20, 40 y 60 g son objetivos volumétricos en PLA a 1,24 g/cm³ (no pesadas en báscula)."
        ),
        "img_despiece": "s5_despiece.png",
        "bom": [
            ["S5-FUL-G", "Fulcro prismático con lomo cilíndrico redondeado", "1", "96,0 × 52,0 × 37,0 mm", "Arista superior cilíndrica r=5 mm y zócalo vertical de 6 mm"],
            ["S5-VIG-G", "Viga balancín con 5 posiciones por brazo", "1", "186,0 × 48,0 × 19,8 mm", "Rebaje central para el fulcro + marcas táctiles 1 a 5"],
            ["S5-MAS-20", "Masa de referencia 20 g (relieve de nube)", "2", "48,0 × 40,0 × 15,8 mm", "Volumen 14,6 cm³ · Tres botones superiores en línea"],
            ["S5-MAS-40", "Masa de referencia 40 g (relieve de hoja / cruz)", "1", "56,0 × 46,0 × 20,4 mm", "Volumen 30,8 cm³ · Relieve táctil en cruz arriba"],
            ["S5-MAS-60", "Masa de referencia 60 g (chaflán facetado)", "1", "64,0 × 50,0 × 20,1 mm", "Volumen 48,2 cm³ · Esquinas superiores achaflanadas"],
            ["S5-PAS-G", "Clip de puente en U (sustituye a pasadores pequeños)", "4", "64,0 × 40,0 × 28,0 mm", "Abraza la viga por encima · Cumple EN 71-1 (> 31,75 mm)"],
            ["S3-PIL-1..6-G + NIVEL", "Pilares graduados + Zócalo + Placa Nivel (de 00-comun)", "6 + 2", "44×47,2 / 136,8×190,8 mm", "Estribos del puente fijo y asiento lateral de Lúa V5"],
        ],
        "pasos": [
            (
                1,
                "Modo Balancín: apoyar la viga sobre el fulcro redondeado",
                "Modo Balancín: apoiar a viga sobre o fulcro redondeado",
                ["S5-FUL-G", "S5-VIG-G"],
                "Asienta el fulcro S5-FUL-G en la mesa con su lomo cilíndrico hacia arriba. Baja el rebaje central "
                "inferior de la viga S5-VIG-G sobre el lomo del fulcro: el rebaje centra la viga sin partirla y "
                "permite que bascule a izquierda y derecha.",
                "Asenta o fulcro S5-FUL-G na mesa co lombo cilíndrico cara arriba. Baixa o rebaixe central inferior "
                "da viga S5-VIG-G sobre o lombo do fulcro para que bascule libremente.",
                "s5_paso_1.png",
            ),
            (
                2,
                "Equilibrar las masas en las posiciones numeradas 1 a 5",
                "Equilibrar as masas nas posicións numeradas 1 a 5",
                ["S5-MAS-60", "S5-MAS-20", "S5-MAS-40"],
                "Cada lado de la viga tiene 5 pozos (identificados en el borde por barras táctiles de longitud "
                "creciente 1 a 5). Clava el tetón inferior de S5-MAS-60 en la posición 1 de un brazo y el de "
                "S5-MAS-20 en la posición 3 del brazo opuesto para comprobar que 60 × 1 equilibra a 20 × 3.",
                "Cada lado da viga ten 5 pozos numerados no bordo. Crava S5-MAS-60 na posición 1 dun brazo e "
                "S5-MAS-20 na posición 3 do brazo oposto para comprobar que 60 × 1 equilibra a 20 × 3.",
                "s5_paso_2.png",
            ),
            (
                3,
                "Modo Puente Fijo: estribos de pilares y bloqueo con clips en U",
                "Modo Ponte Fixa: estribos de piares e bloqueo con clips en U",
                ["S3-PIL-1-G", "S3-PIL-2-G", "S5-PAS-G", "K-PLACA-NIVEL"],
                "Retira el fulcro, levanta dos torres de igual altura con los pilares S3-PIL-* bajo los extremos de "
                "la viga y baja los clips en U S5-PAS-G por encima para inmovilizar el tablero. Coloca al lado el "
                "zócalo con K-PLACA-NIVEL y a Lúa V5 vista desde atrás.",
                "Retira o fulcro, apoia os extremos da viga sobre dúas torres iguais de piares S3-PIL-* e baixa os "
                "clips en U S5-PAS-G por riba. Pon ao lado o zócalo con K-PLACA-NIVEL e a Lúa V5.",
                "s5_paso_3.png",
            ),
        ],
    },
]


def pagina_1_portada(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 1, total_pags)
    c.titulo_h1(
        "Lúa Construye · Manual de montaje (11 sets)",
        f"Guía visual paso a paso tipo IKEA · Paquete masque3d-sets-v1 · {FECHA} · Español / Galego",
    )
    c.chips([
        "sin tornillos",
        "sin pegamento",
        "sin herramientas",
        "paso Duplo 31,80 mm",
        "pared >= 3,20 mm",
        "EN 71-1 (> 31,75 mm)",
    ])
    c.aviso(
        "NO PROBADO (CLAUDE.md · LEEME-masque3d.md):",
        "Este manual describe el montaje diseñado en los ficheros CAD a 30/10/2026. Que las piezas encajen y "
        "aguanten impresas solo lo dirá la pieza impresa en el PLA de Masque3D tras medir la Fase 1 "
        "(P1-probeta-encaje). El cuerpo de Lúa es el de Lúa V5, el cubo de luz (108 × 108 mm de base), que se "
        "imprime y monta con su propio paquete (lua-firmware).",
    )
    c.imagen(
        "portada.png",
        alto_mm=96.0,
        Pie="Vista general renderizada en Blender Cycles a partir de los STL reales: Lúa V5 (el cubo de luz) sobre su patín en el Set 1 y piezas de los Sets 2 a 6.",
    )
    c.parrafo(
        "Resumen de las carpetas del paquete de entrega (entrega/masque3d-sets-v1/ · 93 STL · 8,9 kg estimados):",
        fontsize=8.6,
        bold_prefix="Estructura del paquete:",
    )
    c.tabla(
        ["Carpeta", "Conjunto / Fase", "STL", "Masa est.", "Estado y alcance real en el paquete"],
        TABLA_PAQUETE_PORTADA,
        [32.0, 48.0, 14.0, 16.0, 74.0],
        fontsize=7.3,
    )
    c.cerrar()


def pagina_2_probetas_y_taller(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 2, total_pags)
    c.titulo_h2(
        "P1 + TALLER",
        "Fase 1: Probetas de encaje y soportes en laminador",
        "Fase 1: Probetas de encaixe e soportes no laminador",
        "Antes de lanzar la tirada de los sets",
    )
    c.parrafo(
        "Antes de imprimir los sets para el aula o el hogar, el taller imprime las 12 probetas de "
        "P1-probeta-encaje (6 parejas en escala G con tetón Ø9,40 × 4,50 mm y 6 parejas en escala E con tetón "
        "Ø6,40 × 3,20 mm). No son un juguete y no se entregan a menores.",
        fontsize=8.5,
    )
    c.imagen(
        "p1_probetas.png",
        alto_mm=62.0,
        Pie="Las 6 parejas de probetas P1-MAC/HEM (delante escala G en azul; detrás escala E en turquesa) con muescas laterales 1, 2 y 3 según su holgura.",
    )
    c.tabla(
        ["Código pareja", "Escala y tetón", "Holgura radial", "Marca lateral", "Comprobación en taller (3 pasos)"],
        [
            ["P1-MAC/HEM-G-015", "Escala G (Ø9,40 × 4,5 mm)", "0,15 mm (pozo Ø9,70)", "1 muesca", "1. Imprime la pareja del mismo sufijo en el PLA definitivo."],
            ["P1-MAC/HEM-G-020", "Escala G (Ø9,40 × 4,5 mm)", "0,20 mm (pozo Ø9,80)", "2 muescas", "2. Baja el macho recto sobre el pozo hembra, sin forzar."],
            ["P1-MAC/HEM-G-025", "Escala G (Ø9,40 × 4,5 mm)", "0,25 mm (pozo Ø9,90)", "3 muescas", "3. Anota cuál agarra firme sin bailar ni clavarse."],
            ["P1-MAC/HEM-E-*", "Escala E (Ø6,40 × 3,2 mm)", "0,15 / 0,20 / 0,25 mm", "1, 2 y 3 muescas", "Mismo ensayo para las uniones de los Sets 2 y 4 (escala E)."],
        ],
        [34.0, 35.0, 29.0, 22.0, 64.0],
        fontsize=7.4,
    )
    c.aviso(
        "SIN SOPORTES MODELADOS EN EL STL (INDICACIÓN DE MASQUE3D · 30/10/2026):",
        "Los 87 ficheros STL de entrega/masque3d-sets-v1/ van limpios, SIN soportes dibujados dentro del fichero "
        "(sosten_cm3 = 0,0) y ya orientados sobre la cama (z = 0). El centro de impresión aplica sus soportes en el "
        "laminador donde haya voladizos (carriles del patín, ejes, esferas, codo, frutos, pétalos y maquetas S8..S11), "
        "bloqueando soportes dentro de las roscas del Set 6 (S6-SEM-G, S6-TAL-G, S6-FLO-G y S6-COP-G).",
        fontsize=8.0,
    )
    c.imagen(
        "taller_sostenes.png",
        alto_mm=58.0,
        Pie="Ejemplos de piezas de entrega/masque3d-sets-v1/ orientadas sobre la cama sin soporte modelado: K-PATIN-G, S3-RAM-G, S4-ROT-ASPAS-E y S6-FLO-G.",
    )
    c.cerrar()


def pagina_3_s0_inventario(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 3, total_pags)
    c.titulo_h2(
        "00-COMUN",
        "Set 0 · Kit Común Lúa V5: Inventario y Despiece",
        "Set 0 · Kit Común Lúa V5: Inventario e Despece",
        "Fase 2 del plan de impresión · 15 STL en 00-comun/",
    )
    c.aviso(
        "UN SOLO MUÑECO LÚA (DECISIÓN DEL 29/10/2026):",
        "El cuerpo de Lúa es siempre Lúa V5, el cubo de luz (108 × 108 mm de base con sus 7 enchufes de clic y "
        "su cabeza roscada), que se imprime con el paquete de lua-firmware. Las antiguas piezas K-TRONCO-G, "
        "K-LOMO-G, K-PATA-* y K-COLA-G eran un segundo cuerpo incompatible y ya NO se imprimen en 00-comun/.",
    )
    c.imagen(
        "s0_despiece.png",
        alto_mm=88.0,
        Pie="Despiece 3D de 00-comun/: zócalo K-ZOCALO-G, bandeja K-PATIN-G, las 7 placas de mundo K-PLACA-* y los 6 pilares S3-PIL-1..6-G junto a Lúa V5.",
    )
    c.tabla(
        ["Código STL", "Pieza", "Ud.", "Dimensiones (mm)", "Masa", "Función en los sets 1 a 6"],
        [
            ["K-ZOCALO-G", "Zócalo universal con cuna para Lúa V5", "2*", "136,8 × 190,8 × 40,8", "243 g", "Cuna de 122×122 mm para el cubo + bolsillo lateral de placa"],
            ["K-PATIN-G", "Bandeja patín guía de Lúa V5", "1", "116,0 × 122,0 × 29,8", "92 g", "Dos pivotes Ø11,6 mm en la ranura de 12 mm (solo en Set 1)"],
            ["K-PLACA-INICIO", "Placa de identidad Inicio (flecha)", "1", "89,6 × 54,0 × 7,8", "34 g", "Marca el zócalo de salida en el Set 1"],
            ["K-PLACA-META", "Placa de identidad Meta (anillo)", "1", "89,6 × 54,0 × 7,8", "34 g", "Marca el zócalo de llegada en el Set 1"],
            ["K-PLACA-ESCUCHA", "Placa de identidad Escucha (ondas)", "1", "89,6 × 54,0 × 7,8", "34 g", "Identifica el zócalo de Lúa en el Set 2 (Sonido)"],
            ["K-PLACA-RECEPTOR", "Placa de identidad Receptor (U)", "1", "89,6 × 54,0 × 7,8", "34 g", "Identifica el zócalo detrás del receptor en el Set 3 (Rampas)"],
            ["K-PLACA-FRONTAL", "Placa de identidad Frontal (barras)", "1", "89,6 × 54,0 × 7,8", "34 g", "Identifica el zócalo frente al niño en el Set 4 (Soplo)"],
            ["K-PLACA-NIVEL", "Placa de identidad Nivel (balanza)", "1", "89,6 × 54,0 × 7,8", "34 g", "Identifica el zócalo junto a la viga en el Set 5 (Equilibrio)"],
            ["K-PLACA-JARDIN", "Placa de identidad Jardín (brote)", "1", "89,6 × 54,0 × 7,8", "34 g", "Identifica el zócalo junto a la tierra en el Set 6 (Jardín)"],
            ["S3-PIL-1..6-G", "Pilares graduados con 1 a 6 barras táctiles", "6", "44,0 × 47,2 × 25,2", "187 g", "Altura útil H=19,20 mm · Comunes a los Sets 2, 3 y 5"],
        ],
        [34.0, 46.0, 10.0, 31.0, 14.0, 49.0],
        fontsize=7.3,
    )
    c.cerrar()


def pagina_4_s0_pasos(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 4, total_pags)
    c.titulo_h2(
        "00-COMUN",
        "Set 0 · Cómo se montan el Zócalo, el Patín y los Pilares",
        "Set 0 · Como se montan o Zócalo, o Patín e os Piares",
        "Instrucciones comunes para los Sets 1 a 6",
    )
    c.paso_ikea(
        1,
        "Colocar la placa del mundo y sentar a Lúa V5 en la cuna",
        "Colocar a placa do mundo e sentar a Lúa V5 no berce",
        ["K-ZOCALO-G", "K-PLACA-*", "LUA-V5"],
        "Elige la placa K-PLACA-* del set correspondiente, alinea su esquina recortada con el poste de llave "
        "(14,2 × 14,2 mm) del bolsillo lateral del zócalo y presiona hacia abajo hasta el clic de los nervios de "
        "snap. A continuación, apoya el cubo de Lúa V5 dentro de la cuna cuadrada mirando hacia la salida (+X): "
        "al revés, sus patas delanteras chocan y no asienta.",
        "Elixe a placa K-PLACA-* do set correspondente, aliña a esquina recortada co poste de chave do peto "
        "lateral do zócalo e preme cara abaixo ata o clic. Despois, apoia o cubo de Lúa V5 dentro do berce "
        "mirando cara á saída (+X).",
        "s0_paso_1.png",
        alto_bloque_mm=106.0,
    )
    c.paso_ikea(
        2,
        "Usar la bandeja patín en el Set 1 y apilar los pilares graduados",
        "Usar a bandexa patín no Set 1 e apilar os piares graduados",
        ["K-PATIN-G", "S1-REC-LIS-G", "S3-PIL-1..6-G"],
        "En el Set 1, encaja los dos pivotes inferiores de la bandeja amarilla K-PATIN-G en la ranura de 12 mm "
        "de la baldosa y apoya encima el fondo de 108 × 108 mm del cubo de Lúa V5 (la bandeja sujeta el cubo por "
        "los costados; si levantas a Lúa, el patín se queda en el camino). En los Sets 2 a 6 no se usa el patín. "
        "A la derecha: apila los pilares S3-PIL-1..6-G encajando el tetón superior (Ø12 mm) en el pozo inferior.",
        "No Set 1, encaixa os dous pivotes inferiores da bandexa K-PATIN-G na rañura de 12 mm da lousa e apoia "
        "enriba o cubo de Lúa V5 (se levantas a Lúa, o patín queda no camiño). Nos Sets 2 a 6 non se usa o patín. "
        "Á dereita: apila os piares S3-PIL-1..6-G encaixando o tetón superior no pozo inferior.",
        "s0_paso_2.png",
        alto_bloque_mm=106.0,
    )
    c.aviso(
        "REGLA DE ORIENTACIÓN ESPACIAL EN TODOS LOS SETS:",
        "En los Sets 1 (Camino), 5 (Puente) y 6 (Jardín), el niño se sitúa detrás de Lúa V5 para compartir su "
        "misma izquierda y derecha. En los Sets 2 (Sonido) y 4 (Soplo), Lúa V5 mira de frente al niño.",
        fontsize=8.1,
    )
    c.cerrar()


def paginas_set_par(pdf: PdfPages, info: dict, pag_ini: int, total_pags: int):
    # Página A: Inventario + Despiece 3D
    c1 = LienzoPagina(pdf, pag_ini, total_pags)
    c1.titulo_h2(info["codigo"], info["titulo_es"], info["titulo_gl"], info["fase"])
    c1.parrafo(info["resumen_es"], fontsize=8.5)
    c1.aviso(info["aviso_tit"], info["aviso_txt"], fontsize=8.0)
    c1.imagen(
        info["img_despiece"],
        alto_mm=88.0,
        Pie=f"Despiece 3D renderizado en Blender con los STL reales de {info['carpeta']}/.",
    )
    c1.tabla(
        ["Código STL", "Pieza", "Ud.", "Dimensiones (mm)", "Unión / Detalle constructivo"],
        info["bom"],
        [34.0, 56.0, 12.0, 32.0, 50.0],
        fontsize=7.4,
    )
    c1.cerrar()

    # Página B: Los 3 pasos de montaje tipo IKEA
    c2 = LienzoPagina(pdf, pag_ini + 1, total_pags)
    c2.titulo_h2(
        info["codigo"],
        f"{info['titulo_es']} · Pasos de montaje",
        f"{info['titulo_gl']} · Pasos de montaxe",
        "Secuencia paso a paso con flechas de inserción",
    )
    for num, tit_es, tit_gl, cods, txt_es, txt_gl, png_paso in info["pasos"]:
        c2.paso_ikea(num, tit_es, tit_gl, cods, txt_es, txt_gl, png_paso, alto_bloque_mm=78.0)
    c2.cerrar()


def pagina_15_s6_inventario_y_despiece(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 15, total_pags)
    c.titulo_h2(
        "S6",
        "Set 6 · El Jardín del Sol, la Sombra y la Semilla",
        "Set 6 · O Xardín do Sol, a Sombra e a Semente",
        "Fase 6 del plan de impresión · 12 STL propios + comunes de 00-comun",
    )
    c.parrafo(
        "Crecimiento modular por rosca helicoidal vertical (paso 8 mm, flanco a 51° de la horizontal, 3 vueltas "
        "completas, imprimible en vertical sin soporte dentro de la rosca) y teatro de luz y sombras con linterna "
        "manejada exclusivamente por la persona adulta.",
        fontsize=8.4,
    )
    c.aviso(
        "MATERIAL DE LOS PRISMAS Y USO DE LA LINTERNA:",
        "Los ficheros S6-PRI-AZU.stl y S6-PRI-AMA.stl definen la geometría de los prismas de agua y sol; para que "
        "dejen pasar la luz coloreada deben imprimirse en PETG translúcido azul y amarillo (el STL no lleva color). "
        "La linterna la sostiene siempre la persona adulta, nunca el menor.",
        fontsize=7.9,
    )
    c.imagen(
        "s6_despiece.png",
        alto_mm=80.0,
        Pie="Despiece 3D de S6-jardin/: base de tierra, semilla, tallo roscado (×5), flor, copa, 3 frutos, 2 prismas, 2 pantallas opacas y zócalo.",
    )
    c.tabla(
        ["Código STL", "Pieza", "Ud.", "Dimensiones (mm)", "Unión / Detalle constructivo"],
        [
            ["S6-TIE-G", "Base de tierra con alvéolo, 2 pozos y ranura", "1", "160,0 × 120,0 × 24,0 mm", "Alvéolo liso Ø40,4 mm en (48,60) + pozos y ranura"],
            ["S6-SEM-G", "Semilla con tetón inferior liso y rosca arriba", "1", "58,0 × 58,0 × 43,0 mm", "Boss liso Ø39,2 mm abajo + espiga roscada paso 8 mm"],
            ["S6-TAL-G", "Tallo de rosca gruesa apilable", "5", "48,0 × 48,0 × 67,6 mm", "Collar hembra abajo (36 mm) + espiga macho arriba"],
            ["S6-FLO-G", "Corona floral de 6 pétalos", "1", "84,0 × 77,7 × 50,6 mm", "Collar hembra roscado abajo · Comparte rosca con la copa"],
            ["S6-COP-G", "Copa de árbol con 3 pozos para frutos", "1", "72,0 × 72,0 × 60,6 mm", "Cuenco superior con 3 pozos a 120° (r=4,4 mm)"],
            ["S6-FRU-MAN / NAR / MANZ", "Frutos: Mango, Naranja y Manzana", "1+1+1", "52×42 / Ø45 / Ø45 mm", "Cada fruto lleva espiga inferior Ø8 × 6 mm"],
            ["S6-PRI-AZU / AMA", "Prisma de agua (azul) y Prisma de sol (amarillo)", "1 + 1", "56×43×42 / 48×39×70 mm", "Meseta superior de 6 mm + espiga inferior Ø12 mm"],
            ["S6-SIL-ARB / LUN", "Pantallas opacas de sombra: Árbol y Luna", "1 + 1", "120,0 × 124/110 × 8,0 mm", "Marco de 8 mm · La de luna entra en la ranura de noche"],
            ["K-ZOCALO-G + JARDIN", "Zócalo universal + Placa Jardín (de 00-comun)", "1 + 1", "136,8 × 190,8 × 40,8 mm", "El niño mira a Lúa V5 desde atrás"],
        ],
        [34.0, 54.0, 12.0, 34.0, 50.0],
        fontsize=7.2,
    )
    c.cerrar()


def pagina_16_s6_pasos(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 16, total_pags)
    c.titulo_h2(
        "S6",
        "Set 6 · El Jardín: Pasos de montaje",
        "Set 6 · O Xardín: Pasos de montaxe",
        "Secuencia paso a paso con flechas de inserción",
    )
    c.paso_ikea(
        1,
        "Plantar la semilla en el alvéolo y enroscar los tallos",
        "Plantar a semente no alvéolo e enroscar os talos",
        ["S6-TIE-G", "S6-SEM-G", "S6-TAL-G"],
        "Apoya la base de tierra S6-TIE-G en la mesa e introduce el cilindro inferior liso de la semilla S6-SEM-G "
        "en el alvéolo circular hasta que su placa cuadrada asiente a ras. Toma un tallo S6-TAL-G y enróscalo en "
        "sentido horario (3 vueltas, paso 8 mm) sobre la espiga de la semilla. Apila tantos tallos como pida el reto.",
        "Apoia a base de terra S6-TIE-G na mesa e mete o cilindro inferior liso da semente S6-SEM-G no alvéolo "
        "circular ata quedar a ras. Enrosca en sentido horario un talo S6-TAL-G sobre a semente e apila os seguintes.",
        "s6_paso_1.png",
        alto_bloque_mm=78.0,
    )
    c.paso_ikea(
        2,
        "Coronar con la copa del árbol o la flor y colgar los frutos",
        "Coroar coa copa da árbore ou a flor e colgar os froitos",
        ["S6-COP-G", "S6-FLO-G", "S6-FRU-MAN", "S6-FRU-NAR", "S6-FRU-MANZ"],
        "Enrosca en la cima del último tallo la corona floral S6-FLO-G o la copa de árbol S6-COP-G (ambas llevan "
        "el mismo collar hembra). Cuando uses la copa S6-COP-G, encaja las espigas inferiores de los tres frutos "
        "(mango S6-FRU-MAN, naranja S6-FRU-NAR y manzana S6-FRU-MANZ) en los tres pozos superiores del cuenco.",
        "Enrosca na cima do último talo a coroa floral S6-FLO-G ou a copa S6-COP-G. Cando uses a copa, encaixa as "
        "espigas inferiores dos tres froitos (manga, laranxa e mazá) nos tres pozos superiores do cunco.",
        "s6_paso_2.png",
        alto_bloque_mm=78.0,
    )
    c.paso_ikea(
        3,
        "Colocar los prismas de agua y sol, la pantalla de noche y a Lúa",
        "Colocar os prismas de auga e sol, a pantalla de noite e a Lúa",
        ["S6-PRI-AZU", "S6-PRI-AMA", "S6-SIL-LUN", "K-PLACA-JARDIN"],
        "Clava el prisma azul S6-PRI-AZU en el pozo del agua y el prisma amarillo S6-PRI-AMA en el pozo del sol. "
        "Para el reto de sombra nocturna, encaja la pestaña de la pantalla S6-SIL-LUN en la ranura de noche de la "
        "tierra. Sitúa al lado el zócalo con K-PLACA-JARDIN y a Lúa V5 vista desde atrás.",
        "Crava o prisma azul S6-PRI-AZU no pozo da auga e o amarelo S6-PRI-AMA no do sol. Encaixa a pestana da "
        "pantalla S6-SIL-LUN na rañura de noite e sitúa ao lado o zócalo con K-PLACA-JARDIN e a Lúa V5.",
        "s6_paso_3.png",
        alto_bloque_mm=78.0,
    )
    c.cerrar()


def pagina_17_s7_s8_s9(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 17, total_pags)
    c.titulo_h2(
        "S7 · S8 · S9",
        "Set 7 (No imprimir) y Maquetas S8 Policía y S9 Bomberos",
        "Set 7 (Non imprimir) e Maquetas S8 Policía e S9 Bombeiros",
        "Estado real en entrega/masque3d-sets-v1/",
    )
    c.aviso(
        "ESTADO HONESTO DE LOS SETS 7 A 11 (docs/LEEME-masque3d.md):",
        "• Set 7 (La Granja de Lúa): está en NO-IMPRIMIR/S7-granja-escena.stl (y fuera del ZIP). Es una escena de "
        "la app de 381,6 × 381,6 mm con tejados y postigos colgando en el aire; no se puede imprimir hasta "
        "despiezarla con uniones reales.\n"
        "• Sets 8, 9, 10 y 11 (Oficios): son maquetas decorativas de UNA SOLA PIEZA escaladas al 60 % (S8, S9, S10) "
        "o al 33 % (S11) para caber en la cama de 200 mm, limpias sin soportes modelados (el taller los añade en el "
        "laminador). No tienen paso de 31,80 mm ni piezas desmontables.",
        fontsize=7.9,
    )
    c.paso_ikea(
        8,
        "Set 8 · Comisaría de Policía (maqueta de 1 pieza al 60 %)",
        "Set 8 · Comisaría de Policía (maqueta de 1 peza ao 60 %)",
        ["S8-policia-escala-60.stl"],
        "190,0 × 114,0 × 83,2 mm (741 g al 100 %; ~260 g con relleno 30 %). Izquierda: STL limpio sobre la cama de "
        "200 mm (el taller aplica soporte de laminador en el dintel y el vehículo). Derecha: tras retirar los "
        "soportes del laminador, la maqueta se coloca en la mesa junto a Lúa V5 en su zócalo.",
        "190,0 × 114,0 × 83,2 mm (sen soportes modelados). Esquerda: STL limpo na cama para laminar con soportes "
        "automáticos. Dereita: maqueta dunha peza na mesa xunto a Lúa V5.",
        "s8_policia.png",
        alto_bloque_mm=98.0,
    )
    c.paso_ikea(
        9,
        "Set 9 · Parque de Bomberos (maqueta de 1 pieza al 60 %)",
        "Set 9 · Parque de Bombeiros (maqueta de 1 peza ao 60 %)",
        ["S9-bomberos-escala-60.stl"],
        "190,0 × 114,0 × 114,4 mm (744 g al 100 %; ~265 g con relleno 30 %). Izquierda: pieza limpia en la cama "
        "(el laminador añade soporte bajo los dinteles, la sirena y el camión). Derecha: tras retirar los soportes "
        "y verificar que no queden picos, se sitúa junto al zócalo de Lúa V5 como escenario guiado por el adulto.",
        "190,0 × 114,0 × 114,4 mm (sen soportes modelados). Esquerda: peza limpa na cama para laminar. Dereita: tras "
        "retirar os soportes do laminador, sitúase xunto ao zócalo de Lúa V5.",
        "s9_bomberos.png",
        alto_bloque_mm=98.0,
    )
    c.cerrar()


def pagina_18_s10_s11_resumen(pdf: PdfPages, total_pags: int):
    c = LienzoPagina(pdf, 18, total_pags)
    c.titulo_h2(
        "S10 · S11",
        "Maquetas S10 Hospital (60 %) y S11 Trenes (33 %)",
        "Maquetas S10 Hospital (60 %) e S11 Trens (33 %)",
        "Preparación en taller y tabla resumen de las 4 maquetas",
    )
    c.paso_ikea(
        10,
        "Set 10 · Hospital Infantil (maqueta de 1 pieza al 60 %)",
        "Set 10 · Hospital Infantil (maqueta de 1 peza ao 60 %)",
        ["S10-hospital-escala-60.stl"],
        "190,0 × 113,7 × 87,3 mm (821 g al 100 %; ~290 g con relleno 30 %). Izquierda: STL limpio sobre la cama "
        "(el laminador añade soporte bajo la cruz de la fachada y la ambulancia). Derecha: tras limpiar soportes en "
        "el taller, la maqueta acompaña a Lúa V5 en la mesa para anticipar visitas médicas.",
        "190,0 × 113,7 × 87,3 mm (sen soportes modelados). Esquerda: peza limpa na cama. Dereita: tras retirar os "
        "soportes do laminador no taller, a maqueta acompaña a Lúa V5 na mesa.",
        "s10_hospital.png",
        alto_bloque_mm=88.0,
    )
    c.paso_ikea(
        11,
        "Set 11 · Estación de Trenes (maqueta de 1 pieza al 33 %)",
        "Set 11 · Estación de Trens (maqueta de 1 peza ao 33 %)",
        ["S11-trenes-escala-33.stl"],
        "160,5 × 190,0 × 54,4 mm (184 g al 100 %). Como el circuito original mide 576 mm, está escalada al 33 % "
        "para caber en 190 mm. Izquierda: STL limpio en la cama (soportes aplicados en el laminador). Derecha: "
        "maqueta limpia junto a Lúa V5 (observa la diferencia real de escala entre el tren al 33 % y Lúa al 100 %).",
        "160,5 × 190,0 × 54,4 mm (sen soportes modelados). Escalada ao 33 % para caber en 190 mm. Esquerda: na cama "
        "sen soporte modelado. Dereita: maqueta limpa xunto a Lúa V5 a escala 100 %.",
        "s11_trenes.png",
        alto_bloque_mm=88.0,
    )
    c.tabla(
        ["Fichero STL en entrega/", "Escala", "En cama (mm)", "Caras", "Soportes en laminador y alcance"],
        [
            ["S8-policia/S8-policia-escala-60.stl", "60 %", "190,0 × 114,0 × 83,2", "2046", "Sin soporte en STL · Laminador sostiene puerta y vehículo · 1 pieza"],
            ["S9-bomberos/S9-bomberos-escala-60.stl", "60 %", "190,0 × 114,0 × 114,4", "6542", "Sin soporte en STL · Laminador sostiene arcos y camión · 1 pieza"],
            ["S10-hospital/S10-hospital-escala-60.stl", "60 %", "190,0 × 113,7 × 87,3", "1550", "Sin soporte en STL · Laminador sostiene fachada y ambulancia · 1 pieza"],
            ["S11-trenes/S11-trenes-escala-33.stl", "33 %", "160,5 × 190,0 × 54,4", "3144", "Sin soporte en STL · Laminador sostiene pórticos y vagones · 1 pieza"],
        ],
        [50.0, 14.0, 34.0, 18.0, 68.0],
        fontsize=7.3,
    )
    c.cerrar()


def generar_html() -> str:
    """Genera también la versión HTML limpia (docs/MANUAL-ENSAMBLAJE-IKEA-11-SETS.html)
    con la misma estructura y referencias a docs/cad/manual/*.png."""
    css = """
    @page { size: A4; margin: 13mm 13mm 15mm 13mm; }
    body { font-family: 'DejaVu Sans', Arial, sans-serif; color: #1b1f24; margin: 0; font-size: 9.5pt; }
    section { page-break-after: always; position: relative; min-height: 264mm; box-sizing: border-box; padding-bottom: 10mm; }
    h1 { font-size: 22pt; margin: 0 0 2mm; }
    h2 { font-size: 14pt; margin: 0 0 2mm; border-bottom: 1.5px solid #1b1f24; padding-bottom: 1.5mm; }
    .sub { color: #4b5563; font-size: 9.5pt; margin-bottom: 3mm; }
    .chips span { display: inline-block; border: 1.2px solid #1b1f24; border-radius: 12px; padding: 1px 8px;
      margin-right: 5px; margin-bottom: 4px; font-size: 8pt; font-weight: bold; background: #f3f4f6; }
    .aviso { border: 1.5px solid #1b1f24; background: #fffbeb; padding: 2.5mm 3.5mm; font-size: 8.5pt; margin: 3mm 0; }
    img { max-width: 100%; height: auto; border-radius: 4px; background: #eef0f3; display: block; margin: 2mm auto; }
    .paso { display: grid; grid-template-columns: 78mm 1fr; gap: 4mm; margin-bottom: 3.5mm; border: 1px solid #d0d7de;
      border-radius: 6px; padding: 2.5mm; page-break-inside: avoid; align-items: center; }
    .num { font-size: 26pt; font-weight: bold; line-height: 1; float: left; margin-right: 3mm; }
    .letras span { display: inline-block; border: 1px solid #1b1f24; border-radius: 4px; padding: 0 5px;
      margin-right: 3px; margin-bottom: 2px; font-weight: bold; font-size: 7.5pt; background: #f3f4f6; }
    table { border-collapse: collapse; width: 100%; font-size: 8pt; margin-top: 2mm; }
    td, th { border: 1px solid #8b949e; padding: 1.5mm 2mm; vertical-align: top; text-align: left; }
    th { background: #eaedf0; }
    .pie { position: absolute; bottom: 0; left: 0; right: 0; font-size: 7.5pt; color: #4b5563;
      border-top: 1px solid #d0d7de; padding-top: 1.5mm; display: flex; justify-content: space-between; }
    """
    secciones = []
    # Portada HTML
    filas_p1 = "".join(
        f"<tr><td><b>{html.escape(r[0])}</b></td><td>{html.escape(r[1])}</td><td>{html.escape(r[2])}</td>"
        f"<td>{html.escape(r[3])}</td><td>{html.escape(r[4])}</td></tr>"
        for r in TABLA_PAQUETE_PORTADA
    )
    secciones.append(f"""<section>
    <h1>Lúa Construye · Manual de montaje (11 sets)</h1>
    <div class="sub">Guía visual paso a paso tipo IKEA · Paquete masque3d-sets-v1 · {FECHA} · ES / GL</div>
    <div class="chips"><span>sin tornillos</span><span>sin pegamento</span><span>sin herramientas</span>
    <span>paso Duplo 31,80 mm</span><span>pared &gt;= 3,20 mm</span><span>EN 71-1 (&gt; 31,75 mm)</span></div>
    <div class="aviso"><b>NO PROBADO.</b> Este manual describe el montaje diseñado en CAD a {FECHA}. Que las piezas
    encajen y aguanten impresas lo dirá la primera tirada en el PLA de Masque3D tras medir la Fase 1
    (<code>P1-probeta-encaje</code>). El muñeco Lúa es <b>Lúa V5, el cubo de luz</b> (108 × 108 mm).</div>
    <img src="cad/manual/portada.png" style="max-height:92mm;">
    <table><tr><th>Carpeta</th><th>Conjunto / Fase</th><th>STL</th><th>Masa</th><th>Estado y alcance</th></tr>{filas_p1}</table>
    <div class="pie"><span>Lúa Construye · {FECHA}</span><span>NO PROBADO</span><span>1</span></div>
    </section>""")

    for idx_s, info in enumerate(SETS_PAGINAS, start=1):
        filas_b = "".join(
            f"<tr><td><b>{html.escape(b[0])}</b></td><td>{html.escape(b[1])}</td><td>{html.escape(b[2])}</td>"
            f"<td>{html.escape(b[3])}</td><td>{html.escape(b[4])}</td></tr>"
            for b in info["bom"]
        )
        pasos_h = ""
        for num, tit_es, tit_gl, cods, txt_es, txt_gl, png_paso in info["pasos"]:
            chips_h = "".join(f"<span>{html.escape(c)}</span>" for c in cods)
            pasos_h += f"""<div class="paso"><div><div class="num">{num}</div>
            <b>{html.escape(tit_es)}</b><br><small>GL: {html.escape(tit_gl)}</small>
            <div class="letras" style="margin-top:2mm;">{chips_h}</div>
            <p style="margin:1.5mm 0;"><b>ES:</b> {html.escape(txt_es)}</p>
            <p style="margin:1mm 0;color:#4b5563;"><b>GL:</b> {html.escape(txt_gl)}</p></div>
            <div><img src="cad/manual/{png_paso}" style="max-height:68mm;"></div></div>"""
        secciones.append(f"""<section>
        <h2>{html.escape(info['codigo'])} · {html.escape(info['titulo_es'])} / {html.escape(info['titulo_gl'])}</h2>
        <p>{html.escape(info['resumen_es'])}</p>
        <div class="aviso"><b>{html.escape(info['aviso_tit'])}</b> {html.escape(info['aviso_txt'])}</div>
        <img src="cad/manual/{info['img_despiece']}" style="max-height:80mm;">
        <table><tr><th>Código STL</th><th>Pieza</th><th>Ud.</th><th>Dimensiones</th><th>Unión / Detalle</th></tr>{filas_b}</table>
        </section><section>
        <h2>{html.escape(info['codigo'])} · Pasos de montaje</h2>
        {pasos_h}
        </section>""")

    return (
        '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
        f"<title>Lúa Construye · Manual de montaje 11 sets ({FECHA})</title>"
        f"<style>{css}</style></head><body>\n" + "\n".join(secciones) + "\n</body></html>\n"
    )


def main() -> int:
    total_paginas = 18
    SALIDA_PDF.parent.mkdir(parents=True, exist_ok=True)
    SALIDA_ENTREGA_PDF.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(SALIDA_PDF) as pdf:
        info_meta = pdf.infodict()
        info_meta["Title"] = "Lúa Construye · Manual de montaje tipo IKEA de los 11 sets (30/10/2026)"
        info_meta["Author"] = "Earlify Health S.L. · Lúa Construye"
        info_meta["Subject"] = "Manual bilingüe ES/GL con renders 3D reales de Blender Cycles y pasos de montaje"

        pagina_1_portada(pdf, total_paginas)
        pagina_2_probetas_y_taller(pdf, total_paginas)
        pagina_3_s0_inventario(pdf, total_paginas)
        pagina_4_s0_pasos(pdf, total_paginas)

        pag_actual = 5
        for info_set in SETS_PAGINAS:
            paginas_set_par(pdf, info_set, pag_actual, total_paginas)
            pag_actual += 2

        pagina_15_s6_inventario_y_despiece(pdf, total_paginas)
        pagina_16_s6_pasos(pdf, total_paginas)
        pagina_17_s7_s8_s9(pdf, total_paginas)
        pagina_18_s10_s11_resumen(pdf, total_paginas)

    shutil.copy2(SALIDA_PDF, SALIDA_ENTREGA_PDF)
    SALIDA_HTML.write_text(generar_html(), encoding="utf-8")
    print(f"· HTML generado: {SALIDA_HTML.relative_to(RAIZ)}")
    print(f"· PDF generado:  {SALIDA_PDF.relative_to(RAIZ)} ({SALIDA_PDF.stat().st_size // 1024} KB)")
    print(f"· Copia entrega: {SALIDA_ENTREGA_PDF.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
