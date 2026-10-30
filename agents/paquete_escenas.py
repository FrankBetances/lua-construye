"""Sets 8 a 11 (escenas de una pieza) para masque3d: escalados a la cama de
200 mm (máximo 190 mm) y SIN soportes modelados en el STL (30/10/2026).

    python3 -m agents.paquete_escenas

Por indicación de Masque3D, el soporte lo añade directamente el taller en el
laminador. Son maquetas decorativas: escaladas, no casan con Lúa V5 ni con el
módulo de 31,8 mm. NO PROBADO.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from agents.paquete_masque3d import (
    ESCENAS,
    LADO_ESCENA,
    RAIZ,
    SALIDA,
    empaquetar_zip,
    escribir_tris_stl,
    leer_tris_stl,
    medir_stl_limpio,
)


def generar_escenas_sin_sosten() -> tuple[list[dict], list[tuple]]:
    filas = []
    malas = []
    for e in ESCENAS:
        src = RAIZ / "sets" / e / "stl" / "conjunto.stl"
        tris_raw = leer_tris_stl(src).astype(np.float64)
        pts = tris_raw.reshape(-1, 3)
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        k = min(1.0, LADO_ESCENA / float((hi - lo).max()))
        pts_scaled = np.round((pts - lo) * k, 3).astype(np.float32)
        tris_clean = pts_scaled.reshape(-1, 3, 3)

        nombre_pieza = f"{e}-escala-{k * 100:.0f}"
        destino = SALIDA / e / f"{nombre_pieza}.stl"
        # Eliminar cualquier otro STL previo en la carpeta de la escena
        if destino.parent.exists():
            for viejo in destino.parent.glob("*.stl"):
                if viejo != destino:
                    viejo.unlink()

        escribir_tris_stl(destino, tris_clean)
        r = medir_stl_limpio(leer_tris_stl(destino))
        ok = not r["fallos"]
        gr = r["masa_g"]
        filas.append(
            dict(
                carpeta=e,
                pieza=nombre_pieza,
                cantidad=1,
                sets=e,
                gramos_pieza=f"{gr:.0f}",
                sosten_cm3="0.0",
                medida="verde" if ok else "ROJO: " + " | ".join(r["fallos"]),
                estado="imprimir" if ok else "NO imprimir",
            )
        )
        print(
            f"  {'✓' if ok else '✗'} {e}/{nombre_pieza:22s} ×1  · {gr:4.0f} g · "
            f"sostén 0.0 cm³ · {r['caras']:5d} caras (escala {k * 100:.0f} %)",
            flush=True,
        )
        if not ok:
            malas.append((e, nombre_pieza, r["fallos"]))
    return filas, malas


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--firmware", default=str(RAIZ.parent / "lua-firmware"))
    ap.parse_args(argv)
    _, malas = generar_escenas_sin_sosten()
    empaquetar_zip()
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
