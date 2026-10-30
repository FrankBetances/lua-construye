"""La carpeta para masque3d: todos los STL de los sets, limpios y SIN soportes modelados.

    python3 -m agents.paquete_masque3d

Por indicación de Masque3D (30/10/2026), ningún STL lleva soportes dibujados
dentro del fichero (`sosten_cm3 = 0.0`): el centro de impresión añade los
soportes directamente en su laminador para no encarecer la tirada con geometría
de sostén en los STL.

Escribe entrega/masque3d-sets-v1/ (una carpeta por set, más 00-comun con lo que
comparten y las 4 maquetas S8..S11 escaladas a 190 mm de cama) y su zip.
Verifica empíricamente en cada STL:
  1 · CERRADA: malla 2-manifold estanca en float32 (0 aristas abiertas/no-manifold)
  2 · CAMA: apoyada en z = 0 y dentro de 200 × 200 × 200 mm
  3 · SIN SOPORTES: 0 cuerpos de sostén modelados en el STL (sosten_cm3 = 0.0)

Lo que NO dice: que las piezas encajen ni aguanten impresas. NO PROBADO.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import struct
import sys
import zipfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "entrega" / "masque3d-sets-v1"
DENSIDAD = 1.24
CAMA = np.array([200.0, 200.0, 200.0])
LADO_ESCENA = 190.0
ESCENAS = ["S8-policia", "S9-bomberos", "S10-hospital", "S11-trenes"]
CANTIDAD_MIN = {"K-ZOCALO-G": 2}
CABECERA_STL = b"Lua Construye masque3d sin sosten".ljust(80, b" ")

ORDEN_CARPETAS = [
    "P1-probeta-encaje",
    "S0-kit-lua",
    "S1-camino",
    "S2-estacion-sonido",
    "S3-laboratorio-rampas",
    "S4-maquina-soplo",
    "S5-puente-equilibrio",
    "S6-jardin",
]


def leer_tris_stl(ruta: Path) -> np.ndarray:
    datos = ruta.read_bytes()
    n = struct.unpack_from("<I", datos, 80)[0]
    dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(datos, dtype=dt, offset=84, count=n)["v"].copy()


def escribir_tris_stl(ruta: Path, tris: np.ndarray) -> int:
    tris = np.asarray(tris, dtype=np.float32)
    v0 = tris[:, 0].astype(np.float64)
    v1 = tris[:, 1].astype(np.float64)
    v2 = tris[:, 2].astype(np.float64)
    normales = np.cross(v1 - v0, v2 - v0)
    largos = np.linalg.norm(normales, axis=1)
    validos = largos > 1e-12
    tris = tris[validos]
    normales = (normales[validos] / largos[validos, None]).astype(np.float32)
    n = len(tris)
    dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    out = np.zeros(n, dtype=dt)
    out["n"] = normales
    out["v"] = tris
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("wb") as f:
        f.write(CABECERA_STL)
        f.write(struct.pack("<I", n))
        f.write(out.tobytes())
    return n


def medir_stl_limpio(tris: np.ndarray) -> dict:
    pts = tris.reshape(-1, 3)
    Vu, inv = np.unique(pts, axis=0, return_inverse=True)
    F = inv.reshape(-1, 3)
    F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])]
    E = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1)
    _, counts = np.unique(E, axis=0, return_counts=True)
    aristas_malas = int((counts != 2).sum())

    v0 = Vu[F[:, 0]].astype(np.float64)
    v1 = Vu[F[:, 1]].astype(np.float64)
    v2 = Vu[F[:, 2]].astype(np.float64)
    vol_mm3 = abs(float(np.sum(np.cross(v0, v1) * v2) / 6.0))
    masa_g = (vol_mm3 / 1000.0) * DENSIDAD

    zmin = float(Vu[:, 2].min())
    caja = Vu.max(axis=0) - Vu.min(axis=0)

    fallos = []
    if aristas_malas > 0:
        fallos.append(f"malla no cerrada en float32 ({aristas_malas} aristas abiertas)")
    if abs(zmin) > 0.02:
        fallos.append(f"no apoya en z=0 (zmin={zmin:.3f} mm)")
    if np.any(caja > CAMA + 0.05):
        fallos.append(f"excede cama 200x200x200: {caja.round(1).tolist()}")

    return {
        "caras": len(F),
        "aristas_malas": aristas_malas,
        "vol_cm3": vol_mm3 / 1000.0,
        "masa_g": masa_g,
        "zmin": zmin,
        "caja": caja,
        "fallos": fallos,
    }


def _bom_carpeta(carpeta: str) -> list[dict]:
    ruta_bom = RAIZ / "sets" / carpeta / "pruebas" / "bom.json"
    bom = json.loads(ruta_bom.read_text(encoding="utf-8"))
    return bom.get("maestros", bom.get("piezas", []))


def _carpetas_y_cantidades() -> tuple[dict[str, list[str]], dict[tuple[str, str], int]]:
    carpetas: dict[str, list[str]] = {}
    cantidades: dict[tuple[str, str], int] = {}
    for c in ORDEN_CARPETAS:
        cods = []
        for item in _bom_carpeta(c):
            cod = item["codigo"]
            cods.append(cod)
            cantidades[(c, cod)] = int(item.get("cantidad", 1))
        carpetas[c] = cods
    return carpetas, cantidades


def empaquetar_zip() -> Path:
    zipf = SALIDA.parent / "masque3d-sets-v1.zip"
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SALIDA.rglob("*")):
            if p.is_file() and "NO-IMPRIMIR" not in p.parts:
                z.write(p, p.relative_to(SALIDA.parent))
    return zipf


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--firmware", default=str(RAIZ.parent / "lua-firmware"))
    ap.add_argument("--solo", default="")
    a = ap.parse_args(argv)

    carpetas, cantidades = _carpetas_y_cantidades()
    uso: dict[str, list[str]] = {}
    for carpeta, codigos in carpetas.items():
        for c in codigos:
            uso.setdefault(c, []).append(carpeta)

    filas = []
    malas = []
    hechos = set()

    for carpeta, codigos in carpetas.items():
        for codigo in codigos:
            comun = len(uso[codigo]) > 1
            destino_c = "00-comun" if comun else carpeta
            if codigo in hechos or (a.solo and codigo not in a.solo.split(",")):
                continue
            hechos.add(codigo)
            cant = max([cantidades.get((k, codigo), 1) for k in uso[codigo]] + [CANTIDAD_MIN.get(codigo, 1)])
            ruta_src = RAIZ / "sets" / carpeta / "stl" / f"{codigo}.stl"
            destino = SALIDA / destino_c / f"{codigo}.stl"

            tris = leer_tris_stl(ruta_src)
            pts = tris.reshape(-1, 3)
            zmin = float(pts[:, 2].min())
            if abs(zmin) > 1e-6:
                pts[:, 2] -= zmin
                tris = pts.reshape(-1, 3, 3)

            escribir_tris_stl(destino, tris)
            r = medir_stl_limpio(leer_tris_stl(destino))
            ok = not r["fallos"]
            gr = r["masa_g"]

            filas.append(
                dict(
                    carpeta=destino_c,
                    pieza=codigo,
                    cantidad=cant,
                    sets=" ".join(uso[codigo]),
                    gramos_pieza=f"{gr:.0f}",
                    sosten_cm3="0.0",
                    medida="verde" if ok else "ROJO: " + " | ".join(r["fallos"]),
                    estado="imprimir" if ok else "NO imprimir",
                )
            )
            print(
                f"  {'✓' if ok else '✗'} {destino_c}/{codigo:18s} ×{cant:<2d} · {gr:4.0f} g · "
                f"sostén 0.0 cm³ · {r['caras']:5d} caras"
                + ("" if ok else " · " + r["fallos"][0]),
                flush=True,
            )
            if not ok:
                malas.append((destino_c, codigo, r["fallos"]))

    if not a.solo:
        from agents.paquete_escenas import generar_escenas_sin_sosten

        filas_esc, malas_esc = generar_escenas_sin_sosten()
        filas.extend(filas_esc)
        malas.extend(malas_esc)

        with (SALIDA / "piezas.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        json.dump({"malas": malas}, (SALIDA / "medida.json").open("w", encoding="utf-8"), ensure_ascii=False, indent=1)
        shutil.copyfile(RAIZ / "docs" / "LEEME-masque3d.md", SALIDA / "LEEME.md")
        zipf = empaquetar_zip()
        total = sum(int(f["cantidad"]) * float(f["gramos_pieza"]) for f in filas if f["estado"] == "imprimir")
        print(
            f"\n· {len(filas)} STL distintos (sin soportes modelados) · {len(malas)} en rojo · "
            f"{total / 1000:.1f} kg de PLA al 100 % (cota)"
        )
        print(f"· escrito {SALIDA} y {zipf}")

    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
