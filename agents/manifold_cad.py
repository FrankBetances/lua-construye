"""ManifoldCadAgent. Genera el STL de fabricación y el GLB de RA de cada maestro."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import manifold3d

from agents.malla_io import escribir_glb, escribir_stl

LIMITE_GLB = 100 * 1024


def ejecutar(raiz: Path) -> dict:
    geometria = _cargar(raiz / "sets" / "S1-camino" / "cad" / "geometria.py", "geometria_s1")
    bom = json.loads((raiz / "sets" / "S1-camino" / "pruebas" / "bom.json").read_text(encoding="utf-8"))
    pedidos = [p["codigo"] for p in bom["maestros"]]
    if set(pedidos) != set(geometria.CODIGOS) or len(pedidos) != len(set(pedidos)):
        raise RuntimeError(
            "El BOM y el generador no listan los mismos códigos: "
            f"{pedidos} frente a {list(geometria.CODIGOS)}"
        )
    if list((raiz / "sets" / "S1-camino").rglob("*.scad")):
        raise RuntimeError("hay un .scad en el set; OpenSCAD está prohibido")

    stl_dir = raiz / "sets" / "S1-camino" / "stl"
    ar_dir = raiz / "sets" / "S1-camino" / "ar"
    maestros = []
    for codigo in pedidos:
        segmentos = geometria.P.SEGMENTOS_STL
        manifold3d.set_circular_segments(segmentos)
        solido = geometria.construir(codigo, segmentos)
        if str(solido.status()) != "Error.NoError" or solido.is_empty():
            raise RuntimeError(f"{codigo} no es un sólido válido: {solido.status()}")
        caras = escribir_stl(stl_dir / f"{codigo}.stl", solido)
        caja = [round(float(v), 3) for v in solido.bounding_box()]
        glb_bytes, tolerancia = _glb(geometria, codigo, ar_dir / f"{codigo}.glb")
        ficha = geometria.metadatos(codigo)
        ficha.update(
            {
                "stl": f"sets/S1-camino/stl/{codigo}.stl",
                "glb": f"sets/S1-camino/ar/{codigo}.glb",
                "triangulos_stl": caras,
                "bbox_mm": caja,
                "volumen_mm3": round(float(solido.volume()), 1),
                "glb_bytes": glb_bytes,
                "glb_simplificacion_mm": tolerancia,
                "glb_bajo_100kb": glb_bytes < LIMITE_GLB,
            }
        )
        maestros.append(ficha)
        if glb_bytes >= LIMITE_GLB:
            raise RuntimeError(f"{codigo}.glb pesa {glb_bytes} bytes, por encima de 100 KB")

    ruta = raiz / "sets" / "S1-camino" / "pruebas" / "maestros.json"
    ruta.write_text(json.dumps({"maestros": maestros}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"maestros": maestros}


def _glb(geometria, codigo: str, ruta: Path) -> tuple[int, float]:
    segmentos = geometria.P.SEGMENTOS_AR
    manifold3d.set_circular_segments(segmentos)
    solido = geometria.construir(codigo, segmentos)
    tolerancia = 0.0
    peso = escribir_glb(ruta, solido)
    for candidata in (0.25, 0.5, 0.8, 1.2):
        if peso < LIMITE_GLB:
            break
        tolerancia = candidata
        peso = escribir_glb(ruta, solido.simplify(candidata))
    return peso, tolerancia


def _cargar(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"no se pudo cargar {ruta}")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo
