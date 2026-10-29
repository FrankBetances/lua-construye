"""La carpeta para masque3d: todos los STL de los sets, cada uno con su sostén.

    python3 -m agents.paquete_masque3d --firmware ../lua-firmware

Escribe entrega/masque3d-sets-v1/ (una carpeta por set, más 00-comun con lo que
comparten) y su zip. Es la última etapa, en Blender: el sostén lo dibuja
`tools/blender/sosten.py` de lua-firmware y cada pieza se mide con
`tools/check-v3-piezas.py` de lua-firmware (cerrada, en la cama, voladizos con
sostén, paredes de 3,2 mm, aire entre sostén y pieza). Son las reglas 9.16 y
9.17 del CLAUDE.md de lua-firmware, que la auditoría de lua-construye no
miraba. Si una pieza no pasa, va a `NO-IMPRIMIR/` con el motivo y el LEEME lo
dice arriba.

El patín (K-PATIN-G) es el de Lúa V5: se copia tal cual de lua-v5/, con el
sostén que le dibujó lua-firmware y medido allí (make check-v5).

Lo que NO dice: que las piezas encajen ni aguanten impresas. NO PROBADO.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "entrega" / "masque3d-sets-v1"
DENSIDAD = 1.24
# Sets de una sola pieza decorativa (S8 a S11): no son jugables con Lúa V5 ni
# caben en la cama. No entran (ver el LEEME).
ESCENAS = ["S8-policia", "S9-bomberos", "S10-hospital", "S11-trenes"]
# El Set 1 va de un zócalo INICIO a un zócalo META: hacen falta dos a la vez,
# aunque su BOM diga uno.
CANTIDAD_MIN = {"K-ZOCALO-G": 2}


def _carpetas() -> dict[str, list[str]]:
    from agents.lote_geometria import carpeta_codigos

    sys.path.insert(0, str(RAIZ / "sets" / "S1-camino" / "cad"))
    import geometria

    c = {"S1-camino": list(geometria.CODIGOS)}
    c.update(carpeta_codigos())
    return dict(sorted(c.items()))


def _cantidad(carpeta: str, codigo: str) -> int:
    bom = json.loads((RAIZ / "sets" / carpeta / "pruebas" / "bom.json").read_text(encoding="utf-8"))
    for m in bom.get("maestros", bom.get("piezas", [])):
        if m.get("codigo") == codigo:
            return int(m.get("cantidad", 1))
    return 1


def _cargar_fw(fw: Path):
    sys.path.insert(0, str(fw / "tools" / "blender"))
    import geo  # noqa: F401  (Blender)
    import sosten

    spec = importlib.util.spec_from_file_location("check_v3_piezas", fw / "tools" / "check-v3-piezas.py")
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, ["check-v3-piezas"]
    spec.loader.exec_module(mod)
    sys.argv = argv
    return geo, sosten, mod


def _zonas(codigo: str) -> list[dict]:
    """Lo fino por diseño, como en lua-firmware: los dientes de la rosca (el
    filo de un diente en V es fino junto a la cresta) y su embocadura."""
    from agents import lote_geometria as L

    if L._CATALOGO.get(codigo, {}).get("union") != "rosca":
        return []
    pre = L._CATALOGO[codigo]["construir"]()
    bb = pre.bounding_box()
    marco = [[1, 0, 0, -bb[0]], [0, 1, 0, -bb[1]], [0, 0, 1, -bb[2]], [0, 0, 0, 1]]
    return [dict(tipo="cilindro", r0=L.R_MENOR - 0.6, r1=L.R_MAYOR + L.HOLGURA_ROSCA + 2.6,
                 z0=-1000.0, z1=1000.0, marco=marco, que="rosca: dientes en V y embocadura")]


def _reserva_rosca(codigo: str):
    """Dentro de una rosca no se dibuja sostén (9.17 de lua-firmware: un
    soporte dentro de una rosca la estropea y no se saca)."""
    from manifold3d import Manifold

    zonas = _zonas(codigo)
    if not zonas:
        return None
    z = zonas[0]
    cx, cy = z["marco"][0][3], z["marco"][1][3]
    return Manifold.cylinder(400.0, z["r1"], z["r1"], 96).translate((cx, cy, -100.0))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--firmware", default=str(RAIZ.parent / "lua-firmware"))
    ap.add_argument("--solo", default="")
    a = ap.parse_args(argv)
    fw = Path(a.firmware)
    geo, sosten, cv3 = _cargar_fw(fw)
    import bpy

    carpetas = _carpetas()
    uso: dict[str, list[str]] = {}
    for carpeta, codigos in carpetas.items():
        for c in codigos:
            uso.setdefault(c, []).append(carpeta)
    if not a.solo and SALIDA.exists():
        shutil.rmtree(SALIDA)
    filas, malas = [], []
    hechos = set()
    for carpeta, codigos in carpetas.items():
        for codigo in codigos:
            comun = len(uso[codigo]) > 1
            destino_c = "00-comun" if comun else carpeta
            if codigo in hechos or (a.solo and codigo not in a.solo.split(",")):
                continue
            hechos.add(codigo)
            cant = max([_cantidad(k, codigo) for k in uso[codigo]] + [CANTIDAD_MIN.get(codigo, 1)])
            ruta_src = RAIZ / "sets" / carpeta / "stl" / f"{codigo}.stl"
            destino = SALIDA / destino_c / f"{codigo}.stl"
            destino.parent.mkdir(parents=True, exist_ok=True)
            print(f"  {destino_c}/{codigo} ×{cant}", flush=True)
            if codigo == "K-PATIN-G":
                shutil.copyfile(RAIZ / "lua-v5" / "patin-imprimir.stl", destino)
                filas.append(dict(carpeta=destino_c, pieza=codigo, cantidad=cant, sets=" ".join(uso[codigo]),
                                  gramos_pieza="32", sosten_cm3="2.8",
                                  medida="medida en lua-firmware (make check-v5): verde", estado="imprimir"))
                continue
            # la malla, cerrada también en float32 (como la escribe el STL): se
            # suelda y se simplifica por debajo de 0,02 mm hasta que cierra
            from agents.malla_io import leer_stl

            V, F = sosten.malla(leer_stl(ruta_src))
            V, F = np.asarray(V, float), np.asarray(F, int)
            sop, informe = sosten.sosten(V, F, reservas=_reserva_rosca(codigo))
            if sop is not None:
                Vs, Fs = sosten.malla(sop)
                V = np.vstack([V, Vs])
                F = np.vstack([F, np.asarray(Fs) + len(V) - len(Vs)])
            bpy.ops.wm.read_factory_settings(use_empty=True)
            ob = geo.a_blender(V, F, codigo)
            geo.exportar_stl(ob, str(destino))
            info = {"referencia": str(ruta_src), "zonas": _zonas(codigo),
                    "M_impresion": np.eye(4).tolist()}
            r = cv3.medir(codigo, str(destino), info)
            ok = not r["fallos"]
            gr = r["masa"]
            filas.append(dict(carpeta=destino_c, pieza=codigo, cantidad=cant, sets=" ".join(uso[codigo]),
                              gramos_pieza=f"{gr:.0f}",
                              sosten_cm3=f"{(sop.volume() / 1000 if sop is not None else 0):.1f}",
                              medida="verde" if ok else "ROJO: " + " | ".join(r["fallos"][:3]),
                              estado="imprimir" if ok else "NO imprimir"))
            print(f"    {'✓' if ok else '✗'} {gr:.0f} g · sostén {len(informe)} · pared mín {r['pared_min']:.2f}"
                  + ("" if ok else " · " + r["fallos"][0]), flush=True)
            if not ok:
                malas.append((destino_c, codigo, r["fallos"]))
                nd = SALIDA / "NO-IMPRIMIR" / f"{codigo}.stl"
                nd.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(destino, nd)
    if a.solo:
        return 1 if malas else 0
    with (SALIDA / "piezas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    json.dump({"malas": malas}, (SALIDA / "medida.json").open("w", encoding="utf-8"), ensure_ascii=False, indent=1)
    shutil.copyfile(RAIZ / "docs" / "LEEME-masque3d.md", SALIDA / "LEEME.md")
    zipf = SALIDA.parent / "masque3d-sets-v1.zip"
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SALIDA.rglob("*")):
            if p.is_file() and "NO-IMPRIMIR" not in p.parts:
                z.write(p, p.relative_to(SALIDA.parent))
    total = sum(int(f["cantidad"]) * float(f["gramos_pieza"]) for f in filas if f["estado"] == "imprimir")
    print(f"\n· {len(filas)} piezas distintas · {len(malas)} en rojo · {total / 1000:.1f} kg de PLA al 100 % (cota)")
    print(f"· escrito {SALIDA} y {zipf}")
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
