"""Escribe cada carpeta de impresión: STL, GLB, BOM, orden, dibujo y manual."""

from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import zlib
from pathlib import Path

from manifold3d import Manifold

from agents.lote_geometria import HIPOTESIS, TEXTOS, _CATALOGO, carpeta_codigos, construir
from agents.malla_io import escribir_glb, escribir_stl, leer_stl

DIAMETRO = 31.75
PROFUNDIDAD = 57.1
PARED = 3.20
ESFERA_G = 44.5
RADIO = 1.60
LIMITE_GLB = 100 * 1024

EXCLUIDAS = {
    "P1-probeta-encaje": [
        "No es una pieza del juguete. Sirve para elegir la holgura en el PLA de Masque3D.",
    ],
    "S0-kit-lua": [
        "K-CUELLO no se imprime: es la unidad sellada del fabricante y queda fuera del alcance del niño.",
    ],
    "S2-estacion-sonido": [
        "S2-RES-ROJ con pared de 1,5 mm no se imprime: incumple el mínimo de 3,2 mm.",
        "Las nueve piezas S2-RES-*-E-A/B/C mantienen pared de 8 mm y cambian la cavidad. El tono no se ha medido.",
        "S2-BAL-E se entrega como banco y brazo. El eje va unido al brazo; no hay pasador suelto.",
    ],
    "S3-laboratorio-rampas": [
        "La esfera E de 38 mm no se genera: SETS la marca por verificar para menores de 36 meses y no llega a 44,5 mm.",
        "Con H = 31,80 mm la rampa mediría 254,40 mm y no cabe en la cama. H queda en 19,20 mm.",
    ],
    "S4-maquina-soplo": [
        "S4-BOQ no se imprime en PLA por FDM. Cada niño necesita embocadura de otro proveedor, sin compartirla.",
        "S4-ROT-E y S4-MOL-G se parten en jaula y aspas. El eje es integral al rotor.",
        "El contrapeso de las compuertas es volumen de PLA, no un lastre suelto. Los gramos no se han pesado.",
    ],
    "S5-puente-equilibrio": [
        "La viga de 10 × 31,80 mm mediría 318 mm y no cabe en la cama. Esta viga mide 186 mm.",
        "S5-PAS-G es un clip en U. Un pasador pequeño entraría en el cilindro de piezas pequeñas.",
        "20, 40 y 60 g son un objetivo a 1,24 g/cm³. No hay báscula en esta máquina y la tolerancia de ±0,5 g no está verificada.",
    ],
    "S6-jardin": [
        "Los prismas son geometría opaca de PLA. El azul y el amarillo translúcidos piden PETG o resina, que aquí no se fabrican.",
        "El macro-escenario del apartado 7 no tiene carpeta: no condiciona estos STL.",
    ],
}


def publicar(raiz: Path) -> dict:
    cache: dict[str, dict] = {}
    orden = []
    for codigos in carpeta_codigos().values():
        for codigo in codigos:
            if codigo not in orden:
                orden.append(codigo)
    for codigo in orden:
        cache[codigo] = _fabricar(codigo)
    informes = []
    for carpeta, codigos in carpeta_codigos().items():
        informes.append(_carpeta(raiz, carpeta, codigos, cache))
    return {"carpetas": informes}


def _fabricar(codigo: str) -> dict:
    ficha = _CATALOGO[codigo]
    solido = construir(codigo)
    return {
        "solido": solido,
        "volumen": float(solido.volume()),
        "bbox": [float(v) for v in solido.bounding_box()],
        "ficha": ficha,
    }


def _carpeta(raiz: Path, carpeta: str, codigos: list[str], cache: dict) -> dict:
    base = raiz / "sets" / carpeta
    stl_dir = base / "stl"
    ar_dir = base / "ar"
    pruebas = base / "pruebas"
    manual = base / "manual"
    tarjetas = base / "tarjetas"
    for ruta in (stl_dir, ar_dir, pruebas, manual, tarjetas):
        ruta.mkdir(parents=True, exist_ok=True)

    maestros = []
    for codigo in codigos:
        hecho = cache[codigo]
        solido = hecho["solido"]
        caras = escribir_stl(stl_dir / f"{codigo}.stl", solido)
        glb_bytes, tolerancia = _glb(ar_dir / f"{codigo}.glb", solido)
        if glb_bytes >= LIMITE_GLB:
            raise RuntimeError(f"{codigo}.glb pesa {glb_bytes} bytes")
        ficha = hecho["ficha"]
        maestros.append(
            {
                "codigo": codigo,
                "nombre": ficha["nombre"],
                "cantidad": ficha["cantidad"],
                "union": ficha["union"],
                "rosca_mm": ficha["rosca_mm"],
                "pared_min_mm": ficha["pared_min_mm"],
                "recorte_mm": ficha["recorte_mm"],
                "esfera": ficha["esfera"],
                "nota": ficha["nota"],
                "stl": f"sets/{carpeta}/stl/{codigo}.stl",
                "glb": f"sets/{carpeta}/ar/{codigo}.glb",
                "triangulos_stl": caras,
                "bbox_mm": [round(v, 3) for v in hecho["bbox"]],
                "volumen_mm3": round(hecho["volumen"], 1),
                "glb_bytes": glb_bytes,
                "glb_simplificacion_mm": tolerancia,
            }
        )

    auditoria = _auditar(raiz, maestros)
    if not auditoria["apto"]:
        raise RuntimeError(carpeta + " rechazado: " + ", ".join(auditoria["rechazados"]))

    secuencia = _secuencia(maestros)
    _dibujo(tarjetas, secuencia, carpeta)
    textos = TEXTOS[carpeta]
    (manual / "textos.json").write_text(
        json.dumps(_textos(textos), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    bom = {
        "carpeta": carpeta,
        "titulo": textos["titulo"],
        "fase": textos["fase"],
        "hipotesis": HIPOTESIS,
        "excluidas": EXCLUIDAS[carpeta],
        "maestros": [
            {
                "codigo": m["codigo"],
                "nombre": m["nombre"],
                "cantidad": m["cantidad"],
                "union": m["union"],
                "nota": m["nota"],
            }
            for m in maestros
        ],
    }
    (pruebas / "bom.json").write_text(json.dumps(bom, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (pruebas / "maestros.json").write_text(
        json.dumps({"maestros": maestros}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (pruebas / "secuencia.json").write_text(
        json.dumps(secuencia, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (pruebas / "auditoria.json").write_text(
        json.dumps(auditoria, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (pruebas / "dag.json").write_text(
        json.dumps(_dag(secuencia), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    typst = _typst(raiz, base, textos, bom, secuencia, auditoria)
    return {
        "carpeta": carpeta,
        "piezas": len(maestros),
        "auditoria": auditoria["apto"],
        "pdf": typst["pdf"],
        "typst": typst["resultados"],
    }


def _glb(ruta: Path, solido: Manifold) -> tuple[int, float]:
    tolerancia = 0.0
    peso = escribir_glb(ruta, solido)
    for candidata in (0.25, 0.5, 0.8, 1.2):
        if peso < LIMITE_GLB:
            break
        tolerancia = candidata
        peso = escribir_glb(ruta, solido.simplify(candidata))
    return peso, tolerancia


def _auditar(raiz: Path, maestros: list[dict]) -> dict:
    informes = []
    for ficha in maestros:
        solido = leer_stl(raiz / ficha["stl"])
        caja = solido.bounding_box()
        dims = [caja[3] - caja[0], caja[4] - caja[1], caja[5] - caja[2]]
        ordenadas = sorted(dims)
        nucleo = _nucleo(solido, ficha["recorte_mm"])
        esfera_ok = (not ficha["esfera"]) or min(dims) >= ESFERA_G
        comprobaciones = {
            "stl_hermetico": str(solido.status()) == "Error.NoError" and not solido.is_empty(),
            "volumen_coincide": abs(solido.volume() - ficha["volumen_mm3"]) / ficha["volumen_mm3"] < 0.01,
            "no_entra_en_el_cilindro": not _cabe(ordenadas),
            "dos_ejes_mayores_que_el_cilindro": ordenadas[1] > DIAMETRO,
            "cabe_en_la_cama": all(d <= 220.0 for d in dims),
            "union_mecanica": ficha["union"] in {"espiga", "rosca", "snap"},
            "rosca": ficha["rosca_mm"] is None or ficha["rosca_mm"] >= 3.0,
            "nucleo_tras_erocion_1_60mm": nucleo > 500.0,
            "esfera_g": esfera_ok,
            "pared_declarada": ficha["pared_min_mm"] >= PARED,
        }
        informes.append(
            {
                "codigo": ficha["codigo"],
                "dims_mm": [round(d, 2) for d in dims],
                "nucleo_mm3": round(nucleo, 1),
                "comprobaciones": comprobaciones,
                "apto": all(comprobaciones.values()),
            }
        )
    fallo = [i["codigo"] for i in informes if not i["apto"]]
    return {
        "norma": "EN 71-1, criterio de diseño. No es ensayo de laboratorio.",
        "cilindro_mm": {"diametro": DIAMETRO, "profundidad": PROFUNDIDAD},
        "pared_min_mm": PARED,
        "esfera_g_min_mm": ESFERA_G,
        "cama_mm": [220.0, 220.0, 270.0],
        "apto": not fallo,
        "rechazados": fallo,
        "piezas": informes,
    }


def _cabe(dims: list[float]) -> bool:
    a, b, c = dims
    for largo, u, v in ((c, a, b), (b, a, c), (a, b, c)):
        if largo <= PROFUNDIDAD and (u * u + v * v) <= DIAMETRO * DIAMETRO:
            return True
    return False


def _nucleo(solido: Manifold, recorte: float) -> float:
    cuerpo = solido
    if recorte > 0:
        caja = solido.bounding_box()
        tapa = Manifold.cube((caja[3] - caja[0] + 8, caja[4] - caja[1] + 8, recorte), False)
        cuerpo = solido - tapa.translate((caja[0] - 4, caja[1] - 4, caja[5] - recorte))
    nucleo = cuerpo.minkowski_difference(Manifold.sphere(RADIO, 8))
    if nucleo.is_empty():
        return 0.0
    return float(nucleo.volume())


def _secuencia(maestros: list[dict]) -> dict:
    x = 0.0
    pasos = []
    for i, ficha in enumerate(maestros, start=1):
        bb = ficha["bbox_mm"]
        sx, sy, sz = bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]
        pasos.append(
            {
                "orden": i,
                "id": f"p{i}",
                "codigo": ficha["codigo"],
                "cantidad": ficha["cantidad"],
                "u": [0, 0, -1],
                "origen_mm": [round(x, 1), 0.0, 0.0],
                "tamano_mm": [round(sx, 1), round(sy, 1), round(sz, 1)],
                "desfase_explosion_mm": [0.0, 0.0, round((i - 1) * 18.0, 1)],
            }
        )
        x += sx + 14.0
    return {
        "metodo": "La pieza que recibe va antes. La que entra baja con u = (0, 0, -1).",
        "montaje": pasos,
    }


def _dag(secuencia: dict) -> dict:
    pasos = secuencia["montaje"]
    aristas = []
    for previo, actual in zip(pasos, pasos[1:]):
        aristas.append(
            {
                "desde": previo["codigo"],
                "hasta": actual["codigo"],
                "u": [0, 0, -1],
            }
        )
    return {"nodos": [p["codigo"] for p in pasos], "aristas": aristas}


def _dibujo(salida: Path, secuencia: dict, carpeta: str) -> None:
    pasos = secuencia["montaje"]
    ancho, alto = 1400, 640
    lienzo = bytearray([247, 244, 239] * ancho * alto)
    lineas = []
    etiquetas = []
    total = max(p["origen_mm"][0] + p["tamano_mm"][0] for p in pasos)
    escala = min(1.1, (ancho - 80) / total)
    ox, oy = 36.0, 70.0

    def px(x: float, y: float) -> tuple[float, float]:
        return ox + x * escala, oy + y * escala

    for paso in pasos:
        x, y, _z = paso["origen_mm"]
        sx, sy, _sz = paso["tamano_mm"]
        a, b = px(x, y)
        c, d = px(x + sx, y + sy)
        _rect(lienzo, lineas, a, b, c, d, (40, 70, 90), ancho, alto)
        etiquetas.append((a + 3, min(d - 4, b + 14), f"{paso['orden']}"))
    svg = _svg(ancho, alto, lineas, etiquetas, f"{carpeta}. Planta del kit. El número es el orden.")
    (salida / "planta.svg").write_text(svg, encoding="utf-8")
    _png(salida / "planta.png", ancho, alto, lienzo)

    lienzo2 = bytearray([247, 244, 239] * ancho * alto)
    lineas2 = []
    etiquetas2 = []
    puntos = []
    for paso in pasos:
        x, y, _z = paso["origen_mm"]
        dx, dy, dz = paso["desfase_explosion_mm"]
        sx, sy, sz = paso["tamano_mm"]
        esquinas = []
        for ox_ in (0, sx):
            for oy_ in (0, sy):
                for oz_ in (0, sz):
                    esquinas.append(_iso(x + ox_ + dx, y + oy_ + dy, oz_ + dz))
        puntos.extend(esquinas)
    if not puntos:
        return
    minx = min(p[0] for p in puntos)
    maxx = max(p[0] for p in puntos)
    miny = min(p[1] for p in puntos)
    maxy = max(p[1] for p in puntos)
    escala2 = min((ancho - 80) / (maxx - minx + 1), (alto - 90) / (maxy - miny + 1))

    def mapa(pt):
        return 40 + (pt[0] - minx) * escala2, alto - 40 - (pt[1] - miny) * escala2

    for paso in pasos:
        x, y, _z = paso["origen_mm"]
        dx, dy, dz = paso["desfase_explosion_mm"]
        sx, sy, sz = paso["tamano_mm"]
        verts = []
        for ox_ in (0, sx):
            for oy_ in (0, sy):
                for oz_ in (0, sz):
                    verts.append(mapa(_iso(x + ox_ + dx, y + oy_ + dy, oz_ + dz)))
        for i, j in ((0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)):
            _trazo(lienzo2, lineas2, verts[i][0], verts[i][1], verts[j][0], verts[j][1], (30, 30, 30), ancho, alto)
        cx = sum(v[0] for v in verts) / 8
        cy = sum(v[1] for v in verts) / 8
        etiquetas2.append((cx, cy, str(paso["orden"])))
    (salida / "despiece.svg").write_text(
        _svg(ancho, alto, lineas2, etiquetas2, f"{carpeta}. Despiece. Cada pieza baja."),
        encoding="utf-8",
    )
    _png(salida / "despiece.png", ancho, alto, lienzo2)


def _iso(x: float, y: float, z: float) -> tuple[float, float]:
    return (x - y) * 0.866, (x + y) * 0.5 + z


def _rect(lienzo, lineas, x0, y0, x1, y1, color, ancho, alto) -> None:
    _trazo(lienzo, lineas, x0, y0, x1, y0, color, ancho, alto)
    _trazo(lienzo, lineas, x1, y0, x1, y1, color, ancho, alto)
    _trazo(lienzo, lineas, x1, y1, x0, y1, color, ancho, alto)
    _trazo(lienzo, lineas, x0, y1, x0, y0, color, ancho, alto)


def _trazo(lienzo, lineas, x0, y0, x1, y1, color, ancho, alto) -> None:
    lineas.append((x0, y0, x1, y1, color))
    _bresenham(lienzo, int(x0), int(y0), int(x1), int(y1), color, ancho, alto)


def _bresenham(lienzo, x0, y0, x1, y1, color, ancho, alto) -> None:
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx - dy
    while True:
        if 0 <= x0 < ancho and 0 <= y0 < alto:
            i = (y0 * ancho + x0) * 3
            lienzo[i : i + 3] = bytes(color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def _svg(ancho, alto, lineas, etiquetas, titulo) -> str:
    partes = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        '<rect width="100%" height="100%" fill="#f7f4ef"/>',
        f'<text x="24" y="32" font-family="sans-serif" font-size="16" fill="#222">{_xml(titulo)}</text>',
    ]
    for x0, y0, x1, y1, color in lineas:
        r, g, b = color
        partes.append(
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="rgb({r},{g},{b})" stroke-width="1.3"/>'
        )
    for x, y, texto in etiquetas:
        partes.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="11" fill="#222">{_xml(texto)}</text>'
        )
    partes.append("</svg>\n")
    return "\n".join(partes)


def _xml(texto: str) -> str:
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _png(ruta: Path, ancho: int, alto: int, rgb: bytearray) -> None:
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


def _textos(textos: dict) -> dict:
    return {
        "audiencia": "adulto que media",
        "titulo": textos["titulo"],
        "fase": textos["fase"],
        "regla_pantalla": {
            "es": "El niño mueve los bloques. El adulto sostiene la tableta. La criatura no toca la pantalla.",
            "gl": "O neno move os bloques. O adulto sostén a tableta. A criatura non toca a pantalla.",
        },
        "premio": {
            "es": "El reconocimiento es para el adulto que acompaña, no para el niño.",
            "gl": "O recoñecemento é para o adulto que acompaña, non para o neno.",
        },
        "orientacion": textos["orientacion"],
        "escena": {"es": textos["es"], "gl": textos["gl"]},
        "pasos": [{"es": es, "gl": gl} for es, gl in textos["pasos"]],
    }


def _t(texto: str) -> str:
    return (
        texto.replace("\\", "\\\\")
        .replace("#", "\\#")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("*", "\\*")
        .replace("_", "\\_")
    )


def _typst(raiz: Path, base: Path, textos: dict, bom: dict, secuencia: dict, auditoria: dict) -> dict:
    filas = []
    for pieza in bom["maestros"]:
        filas.append(f"  [{_t(pieza['codigo'])}], [{_t(pieza['nombre'])}], [{pieza['cantidad']}],")
    pasos = []
    for paso in textos["pasos"]:
        pasos.append(f"  [{_t(paso[0])}\\ #text(size: 9pt, fill: rgb(\"#555555\"))[{_t(paso[1])}]],")
    fuera = []
    for linea in bom["excluidas"]:
        fuera.append(f"  [{_t(linea)}],")
    aptos = sum(1 for p in auditoria["piezas"] if p["apto"])
    fuente = base / "manual" / "manual.typ"
    fuente.write_text(
        f"""#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= {_t(textos["titulo"])}
{_t(textos["fase"])}. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
{_t(textos["es"])}

#text(fill: rgb("#555555"))[{_t(textos["gl"])}]

{_t(textos["orientacion"])}

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
{chr(10).join(filas)}
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
{chr(10).join(pasos)}
)

== Qué no va en esta carpeta
#list(
{chr(10).join(fuera)}
)

== Comprobación de diseño
{aptos} de {len(auditoria["piezas"])} mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
""",
        encoding="utf-8",
    )
    typst = shutil.which("typst") or shutil.which("typst", path=str(Path.home() / ".local" / "bin"))
    if typst is None:
        return {"pdf": False, "resultados": [{"comando": f"typst compile {fuente}", "exit": 127}]}
    entorno = os.environ.copy()
    entorno["PATH"] = str(Path.home() / ".local" / "bin") + os.pathsep + entorno.get("PATH", "")
    pdf = fuente.with_suffix(".pdf")
    comando = [typst, "compile", "--root", str(raiz), str(fuente), str(pdf)]
    proc = subprocess.run(comando, cwd=raiz, env=entorno, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"typst falló en {fuente.name}: {proc.stderr.strip()}")
    return {"pdf": True, "resultados": [{"comando": " ".join(comando), "exit": proc.returncode}]}
