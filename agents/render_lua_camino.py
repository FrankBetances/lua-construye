"""Imagen de Lúa V5 en el zócalo y sobre el camino del Set 1, en Blender.

    python3 -m agents.render_lua_camino --firmware ../lua-firmware

Escribe docs/lua-v5-camino.png. Es para mirar (no mide nada): las medidas son
agents.check_lua_camino.
"""

from __future__ import annotations

import argparse
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "sets" / "S1-camino" / "cad"))

import geometria as G  # noqa: E402
import parametros as P  # noqa: E402

from agents.lua_v5 import interfaz  # noqa: E402
from agents.malla_io import escribir_stl, leer_stl  # noqa: E402

CUERPO = {"base": (0.18, 0.18, 0.2), "vientre": (0.95, 0.78, 0.25), "pecho": (0.95, 0.55, 0.2),
          "brazo_izq": (0.2, 0.7, 0.7), "brazo_der": (0.2, 0.7, 0.7), "cola": (0.95, 0.45, 0.4)}


def _objeto(solido, nombre, color, tmp):
    ruta = Path(tmp) / f"{nombre}.stl"
    escribir_stl(ruta, solido)
    bpy.ops.wm.stl_import(filepath=str(ruta))
    ob = bpy.context.selected_objects[0]
    ob.name = nombre
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = 0.55
    ob.data.materials.append(m)
    for pol in ob.data.polygons:
        pol.use_smooth = False
    return ob


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--firmware", default=str(RAIZ.parent / "lua-firmware"))
    ap.add_argument("--salida", default=str(RAIZ / "docs" / "lua-v5-camino.png"))
    a = ap.parse_args(argv)
    fw = Path(a.firmware)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    w = P.BALDOSA_MM
    c = w / 2
    z_p = -interfaz()["patin"]["z_baldosa"]
    with tempfile.TemporaryDirectory() as tmp:
        _objeto(G.zocalo(48), "zocalo", (0.85, 0.8, 0.7), tmp)
        _objeto(G.placa("inicio", 48).translate((P.BOLSA_X0_MM + 0.2, P.BOLSA_ZOCALO_Y0_MM + 0.2,
                                                 P.ALTURA_BASE_MM - P.BOLSA_PROF_MM)), "placa", (0.3, 0.6, 0.3), tmp)
        _objeto(G.baldosa_recta(True, 48).translate((w + 0.4, 0, 0)), "rugosa", (0.75, 0.7, 0.6), tmp)
        _objeto(G.ficha("avanza", 48).translate((w + 0.4 + P.POZO_RECTA_XY[0] + 0.2, P.POZO_RECTA_XY[1] + 0.2,
                                                  P.ALTURA_BASE_MM - P.POZO_PROF_MM)), "ficha", (0.9, 0.3, 0.3), tmp)
        _objeto(G.baldosa_curva(48).translate((2 * w + 0.8, 0, 0)), "curva", (0.75, 0.7, 0.6), tmp)
        for x, nombre in ((c, "a"), (w + 0.4 + c, "b")):
            for n, col in CUERPO.items():
                s = leer_stl(fw / "cad" / "lua-v5" / "montaje" / f"{n}.stl")
                _objeto(s.rotate((0, 0, 90)).translate((x, c, P.ALTURA_BASE_MM + z_p)), f"{n}_{nombre}", col, tmp)
            s = leer_stl(RAIZ / "lua-v5" / "patin-montaje.stl")
            _objeto(s.rotate((0, 0, 90)).translate((x, c, P.ALTURA_BASE_MM + z_p)), f"patin_{nombre}",
                    (0.35, 0.35, 0.4), tmp)
    esc = bpy.context.scene
    # Cycles en CPU: en el contenedor no hay OpenGL para Workbench
    esc.render.engine = "CYCLES"
    esc.cycles.device = "CPU"
    esc.cycles.samples = 32
    esc.cycles.use_denoising = False
    esc.render.resolution_x, esc.render.resolution_y = 1600, 1000
    esc.view_settings.view_transform = "AgX"
    mundo = bpy.data.worlds.new("estudio")
    esc.world = mundo
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.93, 0.94, 0.96, 1.0)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    for nombre, e, d in (("clave", 6.0e6, (0.5, -0.7, 0.8)), ("relleno", 2.5e6, (-0.7, -0.4, 0.5))):
        luz = bpy.data.objects.new(nombre, bpy.data.lights.new(nombre, "AREA"))
        luz.data.energy, luz.data.size = e, 400.0
        esc.collection.objects.link(luz)
        luz.location = Vector((1.3 * w, c, 0)) + Vector(d) * 700
        luz.rotation_euler = (Vector((1.3 * w, c, 0)) - luz.location).to_track_quat("-Z", "Y").to_euler()
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    esc.collection.objects.link(cam)
    esc.camera = cam
    vistas = {
        "": (Vector((1.3 * w, c + 10, 40)), Vector((420, -300, 330)), 38),
        "-lado": (Vector((0.8 * w, c, 35)), Vector((0, -520, 25)), 45),
    }
    for sufijo, (objetivo, desde, lente) in vistas.items():
        cam.location = objetivo + desde
        cam.rotation_euler = (objetivo - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lente
        ruta = a.salida.replace(".png", f"{sufijo}.png")
        esc.render.filepath = ruta
        bpy.ops.render.render(write_still=True)
        print(f"· escrito {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
