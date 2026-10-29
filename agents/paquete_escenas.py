"""Sets 8 a 11 (escenas de una pieza) para masque3d: escalados a la cama de
200 mm, con su sostén (sosten.py de lua-firmware) y medidos con check-v3-piezas.

    python3 -m agents.paquete_escenas --firmware ../lua-firmware

Son maquetas decorativas: escaladas, no casan con Lúa V5 ni con el módulo de
31,8 mm. NO PROBADO.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import numpy as np

from agents.paquete_masque3d import RAIZ, SALIDA, _cargar_fw

ESCENAS = ["S8-policia", "S9-bomberos", "S10-hospital", "S11-trenes"]
LADO = 190.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--firmware", default=str(RAIZ.parent / "lua-firmware"))
    a = ap.parse_args(argv)
    geo, sosten, cv3 = _cargar_fw(Path(a.firmware))
    import bpy
    from agents.malla_io import escribir_stl, leer_stl

    malas = []
    for e in ESCENAS:
        s = leer_stl(RAIZ / "sets" / e / "stl" / "conjunto.stl")
        bb = s.bounding_box()
        k = min(1.0, LADO / max(bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]))
        s = s.translate((-bb[0], -bb[1], -bb[2])).scale((k, k, k))
        ref = SALIDA / e / "_ref.stl"
        ref.parent.mkdir(parents=True, exist_ok=True)
        escribir_stl(ref, s)
        V, F = sosten.malla(s)
        V, F = np.asarray(V, float), np.asarray(F, int)
        sop, _ = sosten.sosten(V, F)
        if sop is not None:
            Vs, Fs = sosten.malla(sop)
            F = np.vstack([F, np.asarray(Fs) + len(V)])
            V = np.vstack([V, Vs])
        bpy.ops.wm.read_factory_settings(use_empty=True)
        destino = SALIDA / e / f"{e}-escala-{k * 100:.0f}.stl"
        geo.exportar_stl(geo.a_blender(V, F, e), str(destino))
        r = cv3.medir(e, str(destino), {"cuerpos": len(s.decompose())})
        ref.unlink()
        print(f"  {e}: escala {k:.2f} · {r['masa']:.0f} g · {'verde' if not r['fallos'] else r['fallos'][0]}")
        if r["fallos"]:
            malas.append(e)
    zipf = SALIDA.parent / "masque3d-sets-v1.zip"
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SALIDA.rglob("*")):
            if p.is_file() and "NO-IMPRIMIR" not in p.parts:
                z.write(p, p.relative_to(SALIDA.parent))
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
