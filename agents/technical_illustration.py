"""TechnicalIllustrationAgent. Plantas y despiece isométrico, en SVG y PNG."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ARISTAS = (
    (0, 1), (2, 3), (4, 5), (6, 7),
    (0, 2), (1, 3), (4, 6), (5, 7),
    (0, 4), (1, 5), (2, 6), (3, 7),
)


def ejecutar(raiz: Path) -> dict:
    base = raiz / "sets" / "S1-camino"
    secuencia = json.loads((base / "pruebas" / "secuencia.json").read_text(encoding="utf-8"))
    dag = json.loads((base / "pruebas" / "dag.json").read_text(encoding="utf-8"))
    maestros = {
        m["codigo"]: m
        for m in json.loads((base / "pruebas" / "maestros.json").read_text(encoding="utf-8"))["maestros"]
    }
    salida = base / "tarjetas"
    salida.mkdir(parents=True, exist_ok=True)
    hechos = []
    for nombre in ("recta", "curva", "te"):
        pasos = secuencia["tarjetas"][nombre]["montaje"]
        svg_planta, png_planta = _planta(pasos, dag["paso_mm"])
        (salida / f"{nombre}-planta.svg").write_text(svg_planta, encoding="utf-8")
        _png(salida / f"{nombre}-planta.png", png_planta)
        hechos.append(f"sets/S1-camino/tarjetas/{nombre}-planta.svg")
        hechos.append(f"sets/S1-camino/tarjetas/{nombre}-planta.png")
    svg_iso, png_iso = _despiece(secuencia["tarjetas"]["recta"]["montaje"], maestros)
    (salida / "recta-despiece.svg").write_text(svg_iso, encoding="utf-8")
    _png(salida / "recta-despiece.png", png_iso)
    hechos.append("sets/S1-camino/tarjetas/recta-despiece.svg")
    hechos.append("sets/S1-camino/tarjetas/recta-despiece.png")
    return {"archivos": hechos}


def _planta(pasos: list[dict], paso: float) -> tuple[str, tuple[int, int, bytes]]:
    ancho, alto = 980, 520
    lienzo = _lienzo(ancho, alto)
    lineas = []
    etiquetas = []
    xs = [p["origen_mm"][0] for p in pasos]
    ys = [p["origen_mm"][1] for p in pasos]
    minx, miny = min(xs), min(ys)
    escala = 1.35
    ox, oy = 70.0, 80.0

    def px(x: float, y: float) -> tuple[float, float]:
        return ox + (x - minx) * escala, oy + (y - miny) * escala

    for paso_i in pasos:
        x, y, _z = paso_i["origen_mm"]
        if paso_i["rol"] in {"ancla", "baldosa"}:
            lado = paso
        else:
            lado_x = 90.0 if paso_i["rol"] == "placa" else 63.6
            lado_y = 46.0 if paso_i["rol"] == "placa" else 63.6
            a, b = px(x, y)
            c, d = px(x + lado_x, y + lado_y)
            _rect(lienzo, lineas, a, b, c, d, (40, 70, 90) if paso_i["rol"] == "placa" else (120, 80, 40))
            etiquetas.append((a + 4, b + 16, paso_i["codigo"]))
            continue
        a, b = px(x, y)
        c, d = px(x + lado, y + lado)
        _rect(lienzo, lineas, a, b, c, d, (30, 30, 30))
        # Ranura, eje de la baldosa.
        mx1, my1 = px(x + 8, y + lado / 2)
        mx2, my2 = px(x + lado - 8, y + lado / 2)
        _trazo(lienzo, lineas, mx1, my1, mx2, my2, (150, 90, 40))
        etiquetas.append((a + 8, b + 22, f"{paso_i['orden']}. {paso_i['codigo']}"))
    titulo = "Planta. La flecha de montaje es vertical: la pieza baja sobre la espiga."
    return _svg(ancho, alto, lineas, etiquetas, titulo), (ancho, alto, bytes(lienzo))


def _despiece(pasos: list[dict], maestros: dict) -> tuple[str, tuple[int, int, bytes]]:
    ancho, alto = 1100, 720
    lienzo = _lienzo(ancho, alto)
    lineas = []
    etiquetas = []
    proyectados = []
    for paso in pasos:
        caja = maestros[paso["codigo"]]["bbox_mm"]
        dx, dy, dz = paso["desplazamiento_despiece_mm"]
        ox, oy, oz = paso["origen_mm"]
        origen = (ox + caja[0] + dx, oy + caja[1] + dy, oz + caja[2] + dz)
        tam = (caja[3] - caja[0], caja[4] - caja[1], caja[5] - caja[2])
        esquinas = _esquinas(origen, tam)
        proy = [_iso(*p) for p in esquinas]
        proyectados.append(proy)
        centro = _iso(
            origen[0] + tam[0] / 2,
            origen[1] + tam[1] / 2,
            origen[2] + tam[2] + 18,
        )
        base = _iso(origen[0] + tam[0] / 2, origen[1] + tam[1] / 2, origen[2] + tam[2])
        proyectados.append((centro, base, paso))
    xs = [p[0] for grupo in proyectados if isinstance(grupo, list) for p in grupo]
    ys = [p[1] for grupo in proyectados if isinstance(grupo, list) for p in grupo]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    escala = min(900 / (maxx - minx + 1), 520 / (maxy - miny + 1))
    ox, oy = 80.0, 80.0

    def a_px(xy: tuple[float, float]) -> tuple[float, float]:
        return ox + (xy[0] - minx) * escala, oy + (maxy - xy[1]) * escala

    for grupo in proyectados:
        if not isinstance(grupo, list):
            continue
        pts = [a_px(p) for p in grupo]
        for i, j in ARISTAS:
            _trazo(lienzo, lineas, pts[i][0], pts[i][1], pts[j][0], pts[j][1], (25, 25, 25))
    for grupo in proyectados:
        if isinstance(grupo, list):
            continue
        centro, base, paso = grupo
        c = a_px(centro)
        b = a_px(base)
        _flecha(lienzo, lineas, c[0], c[1], b[0], b[1])
        etiquetas.append((b[0] + 6, b[1] - 8, f"{paso['orden']} {paso['codigo']}"))
    titulo = "Despiece del recorrido recto. La flecha es el vector de insercion, hacia abajo."
    return _svg(ancho, alto, lineas, etiquetas, titulo), (ancho, alto, bytes(lienzo))


def _esquinas(origen: tuple[float, float, float], tam: tuple[float, float, float]) -> list[tuple[float, float, float]]:
    x, y, z = origen
    dx, dy, dz = tam
    return [
        (x + dx * (i & 1), y + dy * ((i >> 1) & 1), z + dz * ((i >> 2) & 1))
        for i in range(8)
    ]


def _iso(x: float, y: float, z: float) -> tuple[float, float]:
    return (x - y) * 0.866, (x + y) * 0.5 + z


def _lienzo(ancho: int, alto: int) -> bytearray:
    return bytearray([247, 244, 239] * ancho * alto)


def _rect(lienzo, lineas, x0, y0, x1, y1, color) -> None:
    _trazo(lienzo, lineas, x0, y0, x1, y0, color)
    _trazo(lienzo, lineas, x1, y0, x1, y1, color)
    _trazo(lienzo, lineas, x1, y1, x0, y1, color)
    _trazo(lienzo, lineas, x0, y1, x0, y0, color)


def _flecha(lienzo, lineas, x0, y0, x1, y1) -> None:
    _trazo(lienzo, lineas, x0, y0, x1, y1, (20, 70, 120))
    # Punta sencilla, sin caracteres.
    vx, vy = x1 - x0, y1 - y0
    largo = (vx * vx + vy * vy) ** 0.5 or 1.0
    ux, uy = vx / largo, vy / largo
    px, py = -uy, ux
    ax, ay = x1 - ux * 12 + px * 5, y1 - uy * 12 + py * 5
    bx, by = x1 - ux * 12 - px * 5, y1 - uy * 12 - py * 5
    _trazo(lienzo, lineas, x1, y1, ax, ay, (20, 70, 120))
    _trazo(lienzo, lineas, x1, y1, bx, by, (20, 70, 120))


def _trazo(lienzo, lineas, x0, y0, x1, y1, color) -> None:
    lineas.append((x0, y0, x1, y1, color))
    _bresenham(lienzo, int(x0), int(y0), int(x1), int(y1), color)


def _bresenham(lienzo: bytearray, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    ancho = 1100 if len(lienzo) > 980 * 520 * 3 else 980
    # El despiece usa 1100 y la planta 980. Se deduce por el tamaño del buffer.
    if len(lienzo) == 1100 * 720 * 3:
        ancho, alto = 1100, 720
    else:
        ancho, alto = 980, 520
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx - dy
    while True:
        _punto(lienzo, ancho, alto, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def _punto(lienzo, ancho, alto, x, y, color) -> None:
    if 0 <= x < ancho and 0 <= y < alto:
        i = (y * ancho + x) * 3
        lienzo[i : i + 3] = bytes(color)


def _svg(ancho: int, alto: int, lineas, etiquetas, titulo: str) -> str:
    partes = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        f'<rect width="100%" height="100%" fill="#f7f4ef"/>',
        f'<text x="24" y="36" font-family="sans-serif" font-size="16" fill="#222">{_xml(titulo)}</text>',
    ]
    for x0, y0, x1, y1, color in lineas:
        r, g, b = color
        partes.append(
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
            f'stroke="rgb({r},{g},{b})" stroke-width="1.4"/>'
        )
    for x, y, texto in etiquetas:
        partes.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="12" fill="#222">{_xml(texto)}</text>'
        )
    partes.append("</svg>\n")
    return "\n".join(partes)


def _xml(texto: str) -> str:
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _png(ruta: Path, imagen: tuple[int, int, bytes]) -> None:
    ancho, alto, rgb = imagen
    crudo = bytearray()
    fila = ancho * 3
    for y in range(alto):
        crudo.append(0)
        crudo.extend(rgb[y * fila : (y + 1) * fila])

    def chunk(etiqueta: bytes, datos: bytes) -> bytes:
        return struct.pack(">I", len(datos)) + etiqueta + datos + struct.pack(">I", zlib.crc32(etiqueta + datos) & 0xFFFFFFFF)

    archivo = b"\x89PNG\r\n\x1a\n"
    archivo += chunk(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
    archivo += chunk(b"IDAT", zlib.compress(bytes(crudo), 9))
    archivo += chunk(b"IEND", b"")
    ruta.write_bytes(archivo)
