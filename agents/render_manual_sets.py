#!/usr/bin/env python3
"""
render_manual_sets.py · Renderizado 3D real en Blender (Cycles) para el manual IKEA de los 11 sets
==================================================================================================

Ejecución:
    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P agents/render_manual_sets.py
    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P agents/render_manual_sets.py -- --rapido

Lee los STL reales de montaje (`sets/*/stl/*.stl`), el muñeco Lúa V5 (`el cubo de luz`
de `../Proyecto Lua/lua-firmware/cad/lua-v5/montaje/*.stl`) y los STL de cama con sostén
(`entrega/masque3d-sets-v1/*/*.stl`), generando en `docs/cad/manual/` todas las vistas de:
  - Portada del ecosistema con Lúa V5 (cubo de luz) y piezas reales
  - Probetas de encaje (P1)
  - Despiece y pasos de montaje con flechas 3D rojas para S0, S1, S2, S3, S4, S5, S6
  - Vistas de cama (con sostén en naranja) y escala comparativa con Lúa V5 para S8, S9, S10 y S11
  - Hoja de taller con el desprendimiento de sostenes impresos
"""
from __future__ import annotations

import json
import math
import os
import struct
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "docs" / "cad" / "manual"
FW_CANDIDATOS = [
    RAIZ.parent / "Proyecto Lua" / "lua-firmware",
    RAIZ.parent / "lua-firmware",
]
FW_DIR = next((p for p in FW_CANDIDATOS if p.is_dir()), FW_CANDIDATOS[0])

COLORES = {
    "blanco": (0.92, 0.92, 0.90, 1.0),
    "gris": (0.56, 0.59, 0.63, 1.0),
    "gris_claro": (0.76, 0.78, 0.81, 1.0),
    "oscuro": (0.14, 0.16, 0.20, 1.0),
    "placa": (0.24, 0.25, 0.28, 1.0),
    "turquesa": (0.20, 0.66, 0.64, 1.0),
    "azul": (0.12, 0.38, 0.78, 1.0),
    "azul_claro": (0.32, 0.62, 0.90, 1.0),
    "rojo": (0.86, 0.18, 0.15, 1.0),
    "amarillo": (0.96, 0.74, 0.12, 1.0),
    "verde": (0.18, 0.64, 0.28, 1.0),
    "verde_claro": (0.46, 0.76, 0.36, 1.0),
    "naranja": (0.94, 0.46, 0.12, 1.0),
    "rosa": (0.94, 0.44, 0.64, 1.0),
    "morado": (0.48, 0.28, 0.74, 1.0),
    "tierra": (0.48, 0.32, 0.20, 1.0),
    "arena": (0.86, 0.78, 0.62, 1.0),
    "sosten": (0.96, 0.50, 0.10, 1.0),
    "cama": (0.82, 0.84, 0.87, 1.0),
    "flecha": (0.86, 0.10, 0.10, 1.0),
    "translucido": (0.98, 0.94, 0.86, 1.0),
}


def material(nombre: str, rgba: tuple[float, float, float, float], rug: float = 0.35, emision: float = 0.0):
    key = f"{nombre}_{rug:.2f}_{emision:.2f}"
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rug
    if emision > 0:
        for k in ("Emission Color", "Emission"):
            if k in b.inputs:
                b.inputs[k].default_value = rgba
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emision
    return m


def escena(rapido: bool = False, ancho: int = 1500, alto: int = 960):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = 16 if rapido else 28
    try:
        s.cycles.use_denoising = True
    except Exception:
        pass
    f = 0.65 if rapido else 1.0
    s.render.resolution_x = int(ancho * f)
    s.render.resolution_y = int(alto * f)
    s.render.film_transparent = False
    try:
        s.view_settings.view_transform = "AgX"
    except TypeError:
        s.view_settings.view_transform = "Filmic"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
        try:
            s.view_settings.look = look
            break
        except TypeError:
            continue
    w = bpy.data.worlds.new("estudio")
    s.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.94, 0.95, 0.96, 1.0)
    bg.inputs["Strength"].default_value = 0.95
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    s.collection.objects.link(cam)
    s.camera = cam
    return s, cam


def luces(s, centro: Vector, radio: float):
    k = max(radio, 25.0) / 60.0
    for nombre, e, tam, d in [
        ("clave", 9.2e5, 240.0, (0.55, -0.65, 0.65)),
        ("relleno", 3.6e5, 320.0, (-0.65, -0.50, 0.45)),
        ("contra", 5.2e5, 220.0, (-0.15, 0.65, 0.70)),
    ]:
        luz = bpy.data.lights.new(nombre, "AREA")
        luz.energy = e * k * k
        luz.size = tam * k
        o = bpy.data.objects.new(nombre, luz)
        s.collection.objects.link(o)
        pos = Vector(centro) + Vector(d).normalized() * 430.0 * k
        o.location = pos
        o.rotation_euler = (Vector(centro) - pos).to_track_quat("-Z", "Y").to_euler()


def suavizar(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
    except Exception:
        pass


def caja_de(obs) -> tuple[Vector, Vector]:
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    bpy.context.view_layer.update()
    for o in obs:
        if o is None:
            continue
        for p in o.bound_box:
            q = o.matrix_world @ Vector(p)
            lo = Vector(map(min, lo, q))
            hi = Vector(map(max, hi, q))
    return lo, hi


def encuadrar(cam, obs, direccion=(0.78, -1.0, 0.62), lente=55.0, margen=0.88, s=None):
    lo, hi = caja_de(obs)
    centro = (lo + hi) / 2
    radio = max((hi - lo).length / 2, 10.0)
    cam.data.lens = lente
    sensor = cam.data.sensor_width
    fov = 2 * math.atan(sensor / 2 / lente)
    if s is not None and s.render.resolution_y < s.render.resolution_x:
        fov = 2 * math.atan(math.tan(fov / 2) * s.render.resolution_y / s.render.resolution_x)
    dist = radio * margen / math.sin(fov / 2)
    ojo = centro + Vector(direccion).normalized() * dist
    cam.location = ojo
    cam.rotation_euler = (centro - ojo).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_end = max(dist * 6, 5000.0)
    return centro, radio


def foto(s, cam, obs, nombre_rel: str, direccion=(0.78, -1.0, 0.62), lente=55.0, margen=0.88):
    destino = DESTINO / nombre_rel
    destino.parent.mkdir(parents=True, exist_ok=True)
    centro, radio = encuadrar(cam, obs, direccion=direccion, lente=lente, margen=margen, s=s)
    luces(s, centro, radio)
    s.render.filepath = str(destino)
    bpy.ops.render.render(write_still=True)
    print(f"  · {destino.relative_to(RAIZ)}")


def cargar_stl(
    ruta: Path | str,
    color_key: str,
    pos: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_deg: tuple[float, float, float] = (0.0, 0.0, 0.0),
    escala: float = 1.0,
    normalizar_min: bool = False,
    centrar_xy: bool = False,
):
    ruta = Path(ruta)
    antes = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(ruta))
    nuevos = [x for x in bpy.data.objects if x not in antes]
    o = nuevos[0]
    o.name = ruta.stem
    o.scale = (escala, escala, escala)
    if any(rot_deg):
        o.rotation_euler = Euler([math.radians(a) for a in rot_deg], "XYZ")
    bpy.context.view_layer.update()
    if normalizar_min or centrar_xy:
        lo, hi = caja_de([o])
        dx = -(lo.x + hi.x) / 2 if centrar_xy else (-lo.x if normalizar_min else 0.0)
        dy = -(lo.y + hi.y) / 2 if centrar_xy else (-lo.y if normalizar_min else 0.0)
        dz = -lo.z if normalizar_min else 0.0
        o.location += Vector((dx, dy, dz))
        bpy.context.view_layer.update()
    o.location += Vector(pos)
    emision = 0.25 if color_key == "translucido" else 0.0
    o.data.materials.append(material(color_key, COLORES[color_key], emision=emision))
    suavizar(o)
    return o


def flecha(desde: tuple[float, float, float], hasta: tuple[float, float, float], r: float = 2.4):
    d = Vector(hasta) - Vector(desde)
    L = d.length
    if L < 1.0:
        return []
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=L * 0.68, vertices=28)
    cil = bpy.context.active_object
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.5, radius2=0.0, depth=L * 0.32, vertices=28)
    cono = bpy.context.active_object
    q = d.to_track_quat("Z", "Y")
    cil.rotation_euler = q.to_euler()
    cono.rotation_euler = q.to_euler()
    cil.location = Vector(desde) + d.normalized() * (L * 0.34)
    cono.location = Vector(desde) + d.normalized() * (L * 0.84)
    m = material("flecha", COLORES["flecha"], rug=0.35, emision=0.15)
    for o in (cil, cono):
        o.data.materials.append(m)
    return [cil, cono]


def lua_v5_muneco(
    pos: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rot_z_deg: float = 0.0,
    gris: bool = False,
):
    """Carga el muñeco Lúa V5 completo (el cubo de luz + cabeza + accesorios de serie).
    En lua-firmware el frente de Lúa mira hacia -Y (pata_izq/der en -Y) y su base
    apoya en z = -4.0 mm. Si rot_z_deg = 90, Lúa mira hacia +X (el sentido del camino).
    """
    base_v5 = FW_DIR / "cad" / "lua-v5"
    montaje_v5 = base_v5 / "montaje"
    montaje_v3 = FW_DIR / "cad" / "v3" / "montaje"
    if not montaje_v5.is_dir():
        return []

    cubo_json = json.loads((base_v5 / "cubo_v5.json").read_text(encoding="utf-8"))
    cabeza_json = json.loads((base_v5 / "cabeza_v5.json").read_text(encoding="utf-8"))
    colores_v5 = {n: d["color"] for n, d in cubo_json["piezas"].items()}
    colores_v5.update({n: d["color"] for n, d in cabeza_json["piezas"].items()})
    m_v4 = np.array(cabeza_json["montaje_extra"]["anillo_placa"]["marco"], float)

    piezas_v5 = [
        "cubo_caja",
        "cubo_fondo",
        "pata_izq",
        "pata_der",
        "brazo_izq",
        "brazo_der",
        "ala_izq",
        "ala_der",
        "cola",
        "lazo",
        "cabeza_bloque",
        "cabeza_tapa",
        "rosca_cuello",
        "oreja_izq",
        "oreja_der",
        "flor",
    ]
    obs = []
    ang = math.radians(rot_z_deg)
    R_rot = Matrix.Rotation(ang, 4, "Z")
    T_pos = Matrix.Translation(Vector(pos) + Vector((0.0, 0.0, 4.0)))
    M_total = T_pos @ R_rot

    for n in piezas_v5:
        p_stl = montaje_v5 / f"{n}.stl"
        if not p_stl.is_file():
            continue
        ck = "gris_claro" if gris else colores_v5.get(n, "blanco")
        if ck not in COLORES:
            ck = "blanco"
        antes = set(bpy.data.objects)
        bpy.ops.wm.stl_import(filepath=str(p_stl))
        o = [x for x in bpy.data.objects if x not in antes][0]
        o.name = f"lua_{n}"
        o.matrix_world = M_total @ o.matrix_world
        em = 0.22 if ck == "translucido" and not gris else 0.0
        o.data.materials.append(material(ck, COLORES[ck], emision=em))
        suavizar(o)
        obs.append(o)

    aro_stl = montaje_v3 / "aro_visor.stl"
    if aro_stl.is_file():
        antes = set(bpy.data.objects)
        bpy.ops.wm.stl_import(filepath=str(aro_stl))
        o = [x for x in bpy.data.objects if x not in antes][0]
        o.name = "lua_aro_visor"
        o.location = Vector(m_v4[:3, 3].tolist())
        bpy.context.view_layer.update()
        o.matrix_world = M_total @ o.matrix_world
        ck = "gris_claro" if gris else "blanco"
        o.data.materials.append(material(ck, COLORES[ck]))
        suavizar(o)
        obs.append(o)

    # Disco oscuro del visor GC9A01 para que la cara se lea nítida
    bpy.ops.mesh.primitive_cylinder_add(
        radius=24.0,
        depth=8.0,
        vertices=48,
        location=(0.0, -34.0, 121.0),
        rotation=(math.radians(90), 0.0, 0.0),
    )
    visor = bpy.context.active_object
    visor.name = "lua_visor_lcd"
    bpy.context.view_layer.update()
    visor.matrix_world = M_total @ visor.matrix_world
    visor.data.materials.append(material("placa", COLORES["placa"], rug=0.2))
    obs.append(visor)
    return obs


def stl_set(carpeta: str, codigo: str) -> Path:
    p = RAIZ / "sets" / carpeta / "stl" / f"{codigo}.stl"
    if p.is_file():
        return p
    p2 = RAIZ / "entrega" / "masque3d-sets-v1" / carpeta / f"{codigo}.stl"
    if p2.is_file():
        return p2
    return RAIZ / "entrega" / "masque3d-sets-v1" / "00-comun" / f"{codigo}.stl"


def rejilla_catalogo(items: list[tuple[Path, str]], cols: int = 4, sep_x: float = 28.0, sep_y: float = 32.0):
    """Coloca una lista de (ruta_stl, color_key) en una rejilla ordenada sobre Z=0."""
    obs = []
    x_cursor = 0.0
    y_cursor = 0.0
    alto_fila = 0.0
    for idx, (ruta, color_key) in enumerate(items):
        if idx > 0 and idx % cols == 0:
            x_cursor = 0.0
            y_cursor += alto_fila + sep_y
            alto_fila = 0.0
        o = cargar_stl(ruta, color_key, normalizar_min=True)
        lo, hi = caja_de([o])
        ancho = hi.x - lo.x
        fondo = hi.y - lo.y
        o.location += Vector((x_cursor, y_cursor, 0.0))
        x_cursor += ancho + sep_x
        alto_fila = max(alto_fila, fondo)
        obs.append(o)
    return obs


def render_portada(rapido: bool):
    s, cam = escena(rapido, 1600, 960)
    obs = []
    # Zócalo + Placa Inicio + Lúa V5 + loseta recta + curva + ficha comando
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-ZOCALO-G"), "blanco", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-PLACA-INICIO"), "azul", pos=(16, 138.5, 16), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-REC-LIS-G"), "verde_claro", pos=(127.2, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-CMD-AVA-G"), "amarillo", pos=(127.2 + 40, 78, 15), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-CUR-G"), "turquesa", pos=(254.4, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-PATIN-G"), "amarillo", pos=(127.2 + 6, 3, 7.4), normalizar_min=True))
    obs += lua_v5_muneco(pos=(127.2 + 64, 64, 19.2), rot_z_deg=90.0, gris=False)

    # Elementos representativos de S2..S6 alrededor
    # S6 Árbol y flor en tierra (detrás a la izquierda)
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TIE-G"), "tierra", pos=(20, 220, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-SEM-G"), "amarillo", pos=(20 + 19, 220 + 31, 16), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TAL-G"), "verde", pos=(20 + 24, 220 + 36, 46), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-FLO-G"), "rosa", pos=(20 + 6, 220 + 21, 90), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-PRI-AZU"), "azul_claro", pos=(20 + 20, 220 + 75, 18), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-PRI-AMA"), "amarillo", pos=(20 + 76, 220 + 56, 18), normalizar_min=True))

    # S3 Rampa + bisagra + esfera (detrás a la derecha)
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-BIS-G"), "azul", pos=(220, 220, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-RAM-G"), "amarillo", pos=(230, 218, 26), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-ESF-LIS-G"), "rojo", pos=(270, 245, 38), normalizar_min=True))

    # S4 Molinete + S5 Balancín (delante)
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-MOL-JAULA-G"), "blanco", pos=(395, 40, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-MOL-ASPAS-G"), "turquesa", pos=(394, 56, 16), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-FUL-G"), "naranja", pos=(160, -100, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-VIG-G"), "azul", pos=(115, -98, 33), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-MAS-60"), "rojo", pos=(125, -99, 48), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-MAS-20"), "amarillo", pos=(235, -94, 48), normalizar_min=True))

    foto(s, cam, obs, "portada.png", direccion=(0.72, -1.0, 0.65), lente=52.0, margen=0.86)


def render_p1(rapido: bool):
    s, cam = escena(rapido, 1500, 820)
    obs = []
    # Las 6 parejas en dos filas (escala G y escala E)
    for i, suf in enumerate(("015", "020", "025")):
        x = i * 115.0
        # Escala G delante
        obs.append(cargar_stl(stl_set("P1-probeta-encaje", f"P1-HEM-G-{suf}"), "gris", pos=(x, 0, 0), normalizar_min=True))
        obs.append(cargar_stl(stl_set("P1-probeta-encaje", f"P1-MAC-G-{suf}"), "azul", pos=(x, 0, 44), normalizar_min=True, rot_deg=(180, 0, 0)))
        obs += flecha((x + 42, 27, 42), (x + 42, 27, 22), r=2.0)
        # Escala E detrás
        obs.append(cargar_stl(stl_set("P1-probeta-encaje", f"P1-HEM-E-{suf}"), "gris", pos=(x, 90, 0), normalizar_min=True))
        obs.append(cargar_stl(stl_set("P1-probeta-encaje", f"P1-MAC-E-{suf}"), "turquesa", pos=(x, 90, 44), normalizar_min=True, rot_deg=(180, 0, 0)))
        obs += flecha((x + 42, 90 + 27, 42), (x + 42, 90 + 27, 22), r=2.0)
    foto(s, cam, obs, "p1_probetas.png", direccion=(0.68, -1.0, 0.58), lente=55.0, margen=0.88)


def render_s0(rapido: bool):
    # Despiece S0 + Lúa V5
    s, cam = escena(rapido, 1500, 860)
    items = [
        (stl_set("S0-kit-lua", "K-ZOCALO-G"), "blanco"),
        (stl_set("S0-kit-lua", "K-PATIN-G"), "amarillo"),
        (stl_set("S0-kit-lua", "K-PLACA-INICIO"), "verde"),
        (stl_set("S0-kit-lua", "K-PLACA-META"), "rojo"),
        (stl_set("S0-kit-lua", "K-PLACA-ESCUCHA"), "azul"),
        (stl_set("S0-kit-lua", "K-PLACA-RECEPTOR"), "naranja"),
        (stl_set("S0-kit-lua", "K-PLACA-FRONTAL"), "turquesa"),
        (stl_set("S0-kit-lua", "K-PLACA-NIVEL"), "amarillo"),
        (stl_set("S0-kit-lua", "K-PLACA-JARDIN"), "rosa"),
        (stl_set("S3-laboratorio-rampas", "S3-PIL-1-G"), "azul_claro"),
        (stl_set("S3-laboratorio-rampas", "S3-PIL-3-G"), "azul_claro"),
        (stl_set("S3-laboratorio-rampas", "S3-PIL-6-G"), "azul_claro"),
    ]
    obs = rejilla_catalogo(items, cols=4, sep_x=24.0, sep_y=26.0)
    obs += lua_v5_muneco(pos=(-110.0, 95.0, 0.0), rot_z_deg=35.0, gris=False)
    foto(s, cam, obs, "s0_despiece.png", direccion=(0.45, -1.0, 0.78), lente=52.0, margen=0.88)

    # S0 Paso 1: Placa de identidad bajando al zócalo + Lúa V5 bajando a la cuna
    s, cam = escena(rapido, 1450, 860)
    obs = []
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-ZOCALO-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-PLACA-INICIO"), "azul", pos=(16, 138.5, 58), normalizar_min=True))
    obs += flecha((60, 162, 54), (60, 162, 22), r=2.3)
    obs += lua_v5_muneco(pos=(63.6, 63.6, 72.0), rot_z_deg=90.0, gris=False)
    obs += flecha((63.6, 63.6, 68), (63.6, 63.6, 26), r=2.6)
    foto(s, cam, obs, "s0_paso_1.png", direccion=(0.75, -1.0, 0.56), lente=55.0, margen=0.88)

    # S0 Paso 2: Bandeja K-PATIN-G en ranura de baldosa + Pilares graduados apilados
    s, cam = escena(rapido, 1450, 860)
    obs = []
    obs.append(cargar_stl(stl_set("S1-camino", "S1-REC-LIS-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-PATIN-G"), "amarillo", pos=(5.6, 2.6, 48.0), normalizar_min=True))
    obs += flecha((63.6, 63.6, 44), (63.6, 63.6, 18), r=2.3)
    obs += lua_v5_muneco(pos=(63.6, 63.6, 108.0), rot_z_deg=90.0, gris=False)
    obs += flecha((63.6, 63.6, 102), (63.6, 63.6, 72), r=2.3)
    # A la derecha: torre de pilares S3-PIL-1..3-G apilándose
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-PIL-1-G"), "gris", pos=(190, 40, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-PIL-2-G"), "azul_claro", pos=(190, 40, 19.2), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-PIL-3-G"), "turquesa", pos=(190, 40, 68.0), normalizar_min=True))
    obs += flecha((212, 62, 65), (212, 62, 42), r=2.2)
    foto(s, cam, obs, "s0_paso_2.png", direccion=(0.72, -1.0, 0.52), lente=55.0, margen=0.88)


def render_s1(rapido: bool):
    # S1 Despiece
    s, cam = escena(rapido, 1500, 860)
    items = [
        (stl_set("S1-camino", "K-ZOCALO-G"), "blanco"),
        (stl_set("S1-camino", "S1-REC-LIS-G"), "verde_claro"),
        (stl_set("S1-camino", "S1-REC-RUG-G"), "arena"),
        (stl_set("S1-camino", "S1-CUR-G"), "turquesa"),
        (stl_set("S1-camino", "S1-TEE-G"), "azul_claro"),
        (stl_set("S0-kit-lua", "K-PATIN-G"), "amarillo"),
        (stl_set("S0-kit-lua", "K-PLACA-INICIO"), "verde"),
        (stl_set("S0-kit-lua", "K-PLACA-META"), "rojo"),
        (stl_set("S1-camino", "S1-DEST-CAMA"), "morado"),
        (stl_set("S1-camino", "S1-DEST-PARQUE"), "naranja"),
        (stl_set("S1-camino", "S1-CMD-AVA-G"), "azul"),
        (stl_set("S1-camino", "S1-CMD-GIR-G"), "amarillo"),
        (stl_set("S1-camino", "S1-CMD-PAR-G"), "rojo"),
        (stl_set("S1-camino", "S1-CMD-SAL-G"), "rosa"),
    ]
    obs = rejilla_catalogo(items, cols=4, sep_x=24.0, sep_y=24.0)
    foto(s, cam, obs, "s1_despiece.png", direccion=(0.42, -1.0, 0.82), lente=52.0, margen=0.88)

    # S1 Paso 1: Acoplamiento vertical por colas de milano entre Zócalo y Baldosa Recta
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S1-camino", "K-ZOCALO-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-PLACA-INICIO"), "gris_claro", pos=(16, 138.5, 16), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-REC-LIS-G"), "verde_claro", pos=(127.2, 0, 56), normalizar_min=True))
    obs += flecha((132, 30, 52), (132, 30, 22), r=2.2)
    obs += flecha((132, 97.2, 52), (132, 97.2, 22), r=2.2)
    foto(s, cam, obs, "s1_paso_1.png", direccion=(0.68, -1.0, 0.58), lente=55.0, margen=0.88)

    # S1 Paso 2: Encadenado de tramo rugoso, bifurcación en T, curva y zócalo de Meta con destinos
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S1-camino", "K-ZOCALO-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-REC-LIS-G"), "gris", pos=(127.2, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-REC-RUG-G"), "arena", pos=(254.4, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-TEE-G"), "azul_claro", pos=(381.6, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-CUR-G"), "turquesa", pos=(508.8, 0, 55), normalizar_min=True))
    obs += flecha((514, 63.6, 52), (514, 63.6, 22), r=2.5)
    # Zócalo de meta y placas de destino
    obs.append(cargar_stl(stl_set("S1-camino", "K-ZOCALO-G"), "blanco", pos=(381.6, 136.8, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-DEST-CAMA"), "morado", pos=(381.6 + 16, 136.8 + 138.5, 52), normalizar_min=True))
    obs += flecha((381.6 + 60, 136.8 + 162, 48), (381.6 + 60, 136.8 + 162, 22), r=2.3)
    obs.append(cargar_stl(stl_set("S1-camino", "S1-DEST-PARQUE"), "naranja", pos=(240, 160, 0), normalizar_min=True))
    foto(s, cam, obs, "s1_paso_2.png", direccion=(0.58, -1.0, 0.68), lente=52.0, margen=0.88)

    # S1 Paso 3: Fichas de comando en los pozos + Lúa V5 sobre el patín recorriendo el carril
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S1-camino", "K-ZOCALO-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-PLACA-INICIO"), "verde", pos=(16, 138.5, 16), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-REC-LIS-G"), "gris", pos=(127.2, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-REC-RUG-G"), "gris", pos=(254.4, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S1-camino", "S1-CUR-G"), "gris", pos=(381.6, 0, 0), normalizar_min=True))
    # Fichas bajando a los pozos con flecha roja
    obs.append(cargar_stl(stl_set("S1-camino", "S1-CMD-AVA-G"), "azul", pos=(127.2 + 40, 78, 52), normalizar_min=True))
    obs += flecha((127.2 + 64, 96, 48), (127.2 + 64, 96, 22), r=2.2)
    obs.append(cargar_stl(stl_set("S1-camino", "S1-CMD-SAL-G"), "rosa", pos=(254.4 + 40, 78, 52), normalizar_min=True))
    obs += flecha((254.4 + 64, 96, 48), (254.4 + 64, 96, 22), r=2.2)
    obs.append(cargar_stl(stl_set("S1-camino", "S1-CMD-GIR-G"), "amarillo", pos=(381.6 + 66.8, 8, 52), normalizar_min=True))
    obs += flecha((381.6 + 90, 26, 48), (381.6 + 90, 26, 22), r=2.2)
    # Patín + Lúa V5 avanzando por el carril
    obs.append(cargar_stl(stl_set("S0-kit-lua", "K-PATIN-G"), "amarillo", pos=(127.2 + 5.6, 2.6, 7.4), normalizar_min=True))
    obs += lua_v5_muneco(pos=(127.2 + 63.6, 63.6, 19.2), rot_z_deg=90.0, gris=False)
    obs += flecha((250, 63.6, 28), (320, 63.6, 28), r=2.6)
    foto(s, cam, obs, "s1_paso_3.png", direccion=(0.58, -1.0, 0.62), lente=52.0, margen=0.88)


def render_s2(rapido: bool):
    # S2 Despiece
    s, cam = escena(rapido, 1500, 860)
    items = [
        (stl_set("S2-estacion-sonido", "S2-BAL-BASE-E"), "blanco"),
        (stl_set("S2-estacion-sonido", "S2-BAL-BRAZO-E"), "amarillo"),
        (stl_set("S2-estacion-sonido", "S2-RES-AZU-E-A"), "azul"),
        (stl_set("S2-estacion-sonido", "S2-RES-AZU-E-B"), "azul_claro"),
        (stl_set("S2-estacion-sonido", "S2-RES-AMA-E-A"), "amarillo"),
        (stl_set("S2-estacion-sonido", "S2-RES-AMA-E-B"), "naranja"),
        (stl_set("S2-estacion-sonido", "S2-RES-ROJ-E-A"), "rojo"),
        (stl_set("S2-estacion-sonido", "S2-RES-ROJ-E-B"), "rosa"),
        (stl_set("S2-estacion-sonido", "S2-RAS-E"), "verde"),
        (stl_set("S2-estacion-sonido", "S2-ESP-E"), "turquesa"),
        (stl_set("S2-estacion-sonido", "K-ZOCALO-G"), "blanco"),
        (stl_set("S2-estacion-sonido", "K-PLACA-ESCUCHA"), "azul"),
    ]
    obs = rejilla_catalogo(items, cols=4, sep_x=24.0, sep_y=24.0)
    foto(s, cam, obs, "s2_despiece.png", direccion=(0.45, -1.0, 0.78), lente=52.0, margen=0.88)

    # S2 Paso 1: Brazo con eje integral bajando al banco del martillo
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-BAL-BASE-E"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-BAL-BRAZO-E"), "amarillo", pos=(16, 10, 72), normalizar_min=True))
    obs += flecha((38, 39, 68), (38, 39, 44), r=2.3)
    foto(s, cam, obs, "s2_paso_1.png", direccion=(0.72, -1.0, 0.56), lente=55.0, margen=0.88)

    # S2 Paso 2: Resonadores (Azul grave, Amarillo medio, Rojo agudo) frente al martillo
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-BAL-BASE-E"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-BAL-BRAZO-E"), "gris_claro", pos=(16, 10, 28), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-RES-AZU-E-A"), "azul", pos=(145, 7, 0), normalizar_min=True))
    obs += flecha((140, 39, 36), (112, 39, 36), r=2.3)
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-RES-AMA-E-A"), "amarillo", pos=(240, 7, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-RES-ROJ-E-A"), "rojo", pos=(335, 7, 0), normalizar_min=True))
    foto(s, cam, obs, "s2_paso_2.png", direccion=(0.65, -1.0, 0.55), lente=55.0, margen=0.88)

    # S2 Paso 3: Dos raspadores encadenados + espátula + Zócalo con Placa Escucha y Lúa V5 de frente
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-RAS-E"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-RAS-E"), "verde", pos=(168, 0, 0), normalizar_min=True))
    obs += flecha((165, 22, 10), (138, 22, 10), r=2.2)
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "S2-ESP-E"), "naranja", pos=(30, 8, 42), normalizar_min=True))
    obs += flecha((50, 30, 32), (115, 30, 32), r=2.2)
    # Zócalo con placa Escucha y Lúa V5 mirando al frente (-Y)
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "K-ZOCALO-G"), "blanco", pos=(110, 85, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S2-estacion-sonido", "K-PLACA-ESCUCHA"), "azul", pos=(110 + 16, 85 + 138.5, 16), normalizar_min=True))
    obs += lua_v5_muneco(pos=(110 + 63.6, 85 + 63.6, 19.2), rot_z_deg=0.0, gris=False)
    foto(s, cam, obs, "s2_paso_3.png", direccion=(0.65, -1.0, 0.58), lente=52.0, margen=0.88)


def render_s3(rapido: bool):
    # S3 Despiece
    s, cam = escena(rapido, 1500, 860)
    items = [
        (stl_set("S3-laboratorio-rampas", "S3-BIS-G"), "azul"),
        (stl_set("S3-laboratorio-rampas", "S3-RAM-G"), "amarillo"),
        (stl_set("S3-laboratorio-rampas", "S3-FRI-G"), "naranja"),
        (stl_set("S3-laboratorio-rampas", "S3-CUR-PER-G"), "verde"),
        (stl_set("S3-laboratorio-rampas", "S3-REC-G"), "rojo"),
        (stl_set("S3-laboratorio-rampas", "S3-ESF-LIS-G"), "azul_claro"),
        (stl_set("S3-laboratorio-rampas", "S3-ESF-RUG-G"), "rosa"),
        (stl_set("S3-laboratorio-rampas", "S3-PIL-1-G"), "turquesa"),
        (stl_set("S3-laboratorio-rampas", "S3-PIL-3-G"), "turquesa"),
        (stl_set("S3-laboratorio-rampas", "S3-PIL-6-G"), "turquesa"),
        (stl_set("S3-laboratorio-rampas", "K-ZOCALO-G"), "blanco"),
        (stl_set("S3-laboratorio-rampas", "K-PLACA-RECEPTOR"), "morado"),
    ]
    obs = rejilla_catalogo(items, cols=4, sep_x=24.0, sep_y=24.0)
    foto(s, cam, obs, "s3_despiece.png", direccion=(0.45, -1.0, 0.78), lente=52.0, margen=0.88)

    # S3 Paso 1: Eje de la rampa en la boca en C de la bisagra + torre de pilares graduados
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-BIS-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-PIL-1-G"), "gris", pos=(115, 26, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-PIL-2-G"), "azul_claro", pos=(115, 26, 48), normalizar_min=True))
    obs += flecha((137, 48, 45), (137, 48, 24), r=2.2)
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-RAM-G"), "amarillo", pos=(4, -2, 68), normalizar_min=True))
    obs += flecha((22, 48, 64), (22, 48, 36), r=2.4)
    foto(s, cam, obs, "s3_paso_1.png", direccion=(0.68, -1.0, 0.55), lente=55.0, margen=0.88)

    # S3 Paso 2: Tramo de fricción y curva peraltada de 90° a la salida de la rampa
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-BIS-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-PIL-1-G"), "gris", pos=(115, 26, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-RAM-G"), "gris_claro", pos=(4, -2, 22), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-FRI-G"), "naranja", pos=(165, 16, 0), normalizar_min=True))
    obs += flecha((162, 48, 26), (195, 48, 26), r=2.3)
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-CUR-PER-G"), "verde", pos=(315, 0, 0), normalizar_min=True))
    obs += flecha((300, 48, 26), (330, 48, 26), r=2.3)
    foto(s, cam, obs, "s3_paso_2.png", direccion=(0.62, -1.0, 0.62), lente=52.0, margen=0.88)

    # S3 Paso 3: Receptor con lengüeta de parada + Zócalo Receptor con Lúa protegida + Esferas Ø45 mm
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-BIS-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-RAM-G"), "gris", pos=(4, -2, 22), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-FRI-G"), "gris", pos=(160, 16, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-REC-G"), "rojo", pos=(292, 8, 0), normalizar_min=True))
    # Esferas bajando al canal
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-ESF-LIS-G"), "azul", pos=(35, 25, 68), normalizar_min=True))
    obs += flecha((57, 48, 65), (57, 48, 38), r=2.3)
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "S3-ESF-RUG-G"), "amarillo", pos=(105, 115, 0), normalizar_min=True))
    # Zócalo y Lúa detrás de la lengüeta de tope del receptor
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "K-ZOCALO-G"), "blanco", pos=(460, -16, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S3-laboratorio-rampas", "K-PLACA-RECEPTOR"), "morado", pos=(460 + 16, -16 + 138.5, 16), normalizar_min=True))
    obs += lua_v5_muneco(pos=(460 + 63.6, -16 + 63.6, 19.2), rot_z_deg=-90.0, gris=False)
    foto(s, cam, obs, "s3_paso_3.png", direccion=(0.58, -1.0, 0.58), lente=52.0, margen=0.88)


def render_s4(rapido: bool):
    # S4 Despiece
    s, cam = escena(rapido, 1500, 860)
    items = [
        (stl_set("S4-maquina-soplo", "S4-CAN-E"), "azul_claro"),
        (stl_set("S4-maquina-soplo", "S4-COD-E"), "azul"),
        (stl_set("S4-maquina-soplo", "S4-ROT-JAULA-E"), "blanco"),
        (stl_set("S4-maquina-soplo", "S4-ROT-ASPAS-E"), "amarillo"),
        (stl_set("S4-maquina-soplo", "S4-MOL-JAULA-G"), "blanco"),
        (stl_set("S4-maquina-soplo", "S4-MOL-ASPAS-G"), "turquesa"),
        (stl_set("S4-maquina-soplo", "S4-COM-LIG-E"), "verde"),
        (stl_set("S4-maquina-soplo", "S4-COM-PES-E"), "rojo"),
        (stl_set("S4-maquina-soplo", "K-ZOCALO-G"), "blanco"),
        (stl_set("S4-maquina-soplo", "K-PLACA-FRONTAL"), "naranja"),
    ]
    obs = rejilla_catalogo(items, cols=4, sep_x=24.0, sep_y=24.0)
    foto(s, cam, obs, "s4_despiece.png", direccion=(0.45, -1.0, 0.78), lente=52.0, margen=0.88)

    # S4 Paso 1: Rotor y Molinete bajando por las cunas en U de sus jaulas abiertas
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-ROT-JAULA-E"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-ROT-ASPAS-E"), "amarillo", pos=(-1, 12, 86), normalizar_min=True))
    obs += flecha((48, 36, 82), (48, 36, 46), r=2.3)

    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-MOL-JAULA-G"), "gris", pos=(150, -12, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-MOL-ASPAS-G"), "turquesa", pos=(149, 4, 110), normalizar_min=True))
    obs += flecha((210, 36, 106), (210, 36, 58), r=2.5)
    foto(s, cam, obs, "s4_paso_1.png", direccion=(0.72, -1.0, 0.56), lente=55.0, margen=0.88)

    # S4 Paso 2: Canal de aire + Codo 90° + Compuertas ligera (1 barra) y pesada (3 barras)
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-CAN-E"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-COD-E"), "azul", pos=(-96, -10, 6), normalizar_min=True))
    obs += flecha((-22, 26, 26), (-2, 26, 26), r=2.2)
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-COM-LIG-E"), "verde", pos=(82, 4, 72), normalizar_min=True))
    obs += flecha((120, 26, 68), (120, 26, 46), r=2.2)
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-COM-PES-E"), "rojo", pos=(175, 4, 0), normalizar_min=True))
    foto(s, cam, obs, "s4_paso_2.png", direccion=(0.68, -1.0, 0.55), lente=55.0, margen=0.88)

    # S4 Paso 3: Canal enfrentado a la ventana de la jaula + Zócalo Frontal con Lúa V5
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-CAN-E"), "gris", pos=(0, 22, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-COM-LIG-E"), "verde", pos=(82, 26, 46), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-MOL-JAULA-G"), "gris_claro", pos=(172, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "S4-MOL-ASPAS-G"), "turquesa", pos=(171, 16, 16), normalizar_min=True))
    obs += flecha((154, 48, 26), (174, 48, 26), r=2.2)
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "K-ZOCALO-G"), "blanco", pos=(320, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S4-maquina-soplo", "K-PLACA-FRONTAL"), "naranja", pos=(320 + 16, 138.5, 16), normalizar_min=True))
    obs += lua_v5_muneco(pos=(320 + 63.6, 63.6, 19.2), rot_z_deg=0.0, gris=False)
    foto(s, cam, obs, "s4_paso_3.png", direccion=(0.62, -1.0, 0.58), lente=52.0, margen=0.88)


def render_s5(rapido: bool):
    # S5 Despiece
    s, cam = escena(rapido, 1500, 860)
    items = [
        (stl_set("S5-puente-equilibrio", "S5-FUL-G"), "naranja"),
        (stl_set("S5-puente-equilibrio", "S5-VIG-G"), "azul"),
        (stl_set("S5-puente-equilibrio", "S5-MAS-20"), "amarillo"),
        (stl_set("S5-puente-equilibrio", "S5-MAS-40"), "verde"),
        (stl_set("S5-puente-equilibrio", "S5-MAS-60"), "rojo"),
        (stl_set("S5-puente-equilibrio", "S5-PAS-G"), "turquesa"),
        (stl_set("S5-puente-equilibrio", "S3-PIL-2-G"), "azul_claro"),
        (stl_set("S5-puente-equilibrio", "S3-PIL-4-G"), "azul_claro"),
        (stl_set("S5-puente-equilibrio", "K-ZOCALO-G"), "blanco"),
        (stl_set("S5-puente-equilibrio", "K-PLACA-NIVEL"), "morado"),
    ]
    obs = rejilla_catalogo(items, cols=4, sep_x=24.0, sep_y=24.0)
    foto(s, cam, obs, "s5_despiece.png", direccion=(0.45, -1.0, 0.78), lente=52.0, margen=0.88)

    # S5 Paso 1: Viga numerada bajando sobre el lomo redondeado del fulcro
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-FUL-G"), "gris", pos=(45, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-VIG-G"), "azul", pos=(0, 2, 62), normalizar_min=True))
    obs += flecha((93, 26, 58), (93, 26, 36), r=2.3)
    foto(s, cam, obs, "s5_paso_1.png", direccion=(0.68, -1.0, 0.54), lente=55.0, margen=0.88)

    # S5 Paso 2: Masas 60 g (pos 1) y 20 g (pos 3) bajando a los pozos numerados de la viga
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-FUL-G"), "gris", pos=(45, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-VIG-G"), "gris_claro", pos=(0, 2, 33), normalizar_min=True))
    # Masa 60 en pos 1 izquierda (x = 93 - 21 = 72) y Masa 20 en pos 3 derecha (x = 93 + 49 = 142)
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-MAS-60"), "rojo", pos=(72 - 32, 1, 78), normalizar_min=True))
    obs += flecha((72, 26, 74), (72, 26, 52), r=2.2)
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-MAS-20"), "amarillo", pos=(142 - 24, 6, 78), normalizar_min=True))
    obs += flecha((142, 26, 74), (142, 26, 52), r=2.2)
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-MAS-40"), "verde", pos=(205, 3, 0), normalizar_min=True))
    foto(s, cam, obs, "s5_paso_2.png", direccion=(0.68, -1.0, 0.56), lente=55.0, margen=0.88)

    # S5 Paso 3: Modo Puente Fijo sobre pilares con clips en U + Zócalo Nivel y Lúa V5 al lado
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S3-PIL-1-G"), "gris", pos=(10, 2, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S3-PIL-2-G"), "gris", pos=(10, 2, 19.2), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S3-PIL-1-G"), "gris", pos=(132, 2, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S3-PIL-2-G"), "gris", pos=(132, 2, 19.2), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-VIG-G"), "gris_claro", pos=(0, 2, 38.4), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-PAS-G"), "turquesa", pos=(4, 6, 82), normalizar_min=True))
    obs += flecha((32, 26, 78), (32, 26, 56), r=2.2)
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "S5-PAS-G"), "turquesa", pos=(122, 6, 82), normalizar_min=True))
    obs += flecha((154, 26, 78), (154, 26, 56), r=2.2)
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "K-ZOCALO-G"), "blanco", pos=(220, -20, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S5-puente-equilibrio", "K-PLACA-NIVEL"), "morado", pos=(220 + 16, -20 + 138.5, 16), normalizar_min=True))
    obs += lua_v5_muneco(pos=(220 + 63.6, -20 + 63.6, 19.2), rot_z_deg=90.0, gris=False)
    foto(s, cam, obs, "s5_paso_3.png", direccion=(0.64, -1.0, 0.58), lente=52.0, margen=0.88)


def render_s6(rapido: bool):
    # S6 Despiece
    s, cam = escena(rapido, 1500, 860)
    items = [
        (stl_set("S6-jardin", "S6-TIE-G"), "tierra"),
        (stl_set("S6-jardin", "S6-SEM-G"), "amarillo"),
        (stl_set("S6-jardin", "S6-TAL-G"), "verde"),
        (stl_set("S6-jardin", "S6-FLO-G"), "rosa"),
        (stl_set("S6-jardin", "S6-COP-G"), "verde_claro"),
        (stl_set("S6-jardin", "S6-FRU-MAN"), "amarillo"),
        (stl_set("S6-jardin", "S6-FRU-NAR"), "naranja"),
        (stl_set("S6-jardin", "S6-FRU-MANZ"), "rojo"),
        (stl_set("S6-jardin", "S6-PRI-AZU"), "azul_claro"),
        (stl_set("S6-jardin", "S6-PRI-AMA"), "amarillo"),
        (stl_set("S6-jardin", "S6-SIL-ARB"), "verde"),
        (stl_set("S6-jardin", "S6-SIL-LUN"), "morado"),
        (stl_set("S6-jardin", "K-ZOCALO-G"), "blanco"),
        (stl_set("S6-jardin", "K-PLACA-JARDIN"), "rosa"),
    ]
    obs = rejilla_catalogo(items, cols=5, sep_x=22.0, sep_y=22.0)
    foto(s, cam, obs, "s6_despiece.png", direccion=(0.45, -1.0, 0.78), lente=52.0, margen=0.88)

    # S6 Paso 1: Semilla bajando al alvéolo (48, 60) y tallos roscados apilándose en vertical
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TIE-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-SEM-G"), "amarillo", pos=(48 - 29, 60 - 29, 44), normalizar_min=True))
    obs += flecha((48, 60, 42), (48, 60, 22), r=2.2)
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TAL-G"), "verde", pos=(48 - 24, 60 - 24, 108), normalizar_min=True))
    obs += flecha((48, 60, 104), (48, 60, 82), r=2.2)
    foto(s, cam, obs, "s6_paso_1.png", direccion=(0.72, -1.0, 0.54), lente=55.0, margen=0.88)

    # S6 Paso 2: Copa del árbol roscada al tallo + 3 frutos bajando a sus pozos + Corona floral al lado
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TIE-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-SEM-G"), "gris", pos=(48 - 29, 60 - 29, 16), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TAL-G"), "gris", pos=(48 - 24, 60 - 24, 36), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-COP-G"), "verde", pos=(48 - 36, 60 - 36, 82), normalizar_min=True))
    # 3 frutos bajando a los pozos de la copa
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-FRU-MAN"), "amarillo", pos=(48 - 26 + 24, 60 - 21 + 14, 152), normalizar_min=True))
    obs += flecha((48 + 24, 60 + 14, 148), (48 + 24, 60 + 14, 128), r=2.0)
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-FRU-NAR"), "naranja", pos=(48 - 22 - 24, 60 - 22 + 14, 152), normalizar_min=True))
    obs += flecha((48 - 24, 60 + 14, 148), (48 - 24, 60 + 14, 128), r=2.0)
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-FRU-MANZ"), "rojo", pos=(48 - 22, 60 - 22 - 28, 152), normalizar_min=True))
    obs += flecha((48, 60 - 28, 148), (48, 60 - 28, 128), r=2.0)
    # Corona floral intercambiable al lado
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-FLO-G"), "rosa", pos=(185, 25, 0), normalizar_min=True))
    foto(s, cam, obs, "s6_paso_2.png", direccion=(0.72, -1.0, 0.50), lente=55.0, margen=0.88)

    # S6 Paso 3: Prismas de agua/sol en sus pozos + Pantallas de sombra + Zócalo Jardín con Lúa V5
    s, cam = escena(rapido, 1450, 840)
    obs = []
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TIE-G"), "gris", pos=(0, 0, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-SEM-G"), "gris", pos=(48 - 29, 60 - 29, 16), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-TAL-G"), "gris", pos=(48 - 24, 60 - 24, 36), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-FLO-G"), "rosa", pos=(48 - 42, 60 - 39, 82), normalizar_min=True))
    # Prismas bajando a (48, 96) y (100, 78)
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-PRI-AZU"), "azul_claro", pos=(48 - 28, 96 - 16, 56), normalizar_min=True))
    obs += flecha((48, 96, 52), (48, 96, 26), r=2.1)
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-PRI-AMA"), "amarillo", pos=(100 - 24, 78 - 15, 56), normalizar_min=True))
    obs += flecha((100, 78, 52), (100, 78, 26), r=2.1)
    # Pantalla de luna bajando a la ranura de noche (96..154, 16..32)
    obs.append(cargar_stl(stl_set("S6-jardin", "S6-SIL-LUN"), "morado", pos=(65, 20, 62), rot_deg=(90, 0, 0), normalizar_min=True))
    obs += flecha((125, 24, 58), (125, 24, 26), r=2.1)
    # Zócalo Jardín + Lúa V5 al lado
    obs.append(cargar_stl(stl_set("S6-jardin", "K-ZOCALO-G"), "blanco", pos=(195, -15, 0), normalizar_min=True))
    obs.append(cargar_stl(stl_set("S6-jardin", "K-PLACA-JARDIN"), "rosa", pos=(195 + 16, -15 + 138.5, 16), normalizar_min=True))
    obs += lua_v5_muneco(pos=(195 + 63.6, -15 + 63.6, 19.2), rot_z_deg=90.0, gris=False)
    foto(s, cam, obs, "s6_paso_3.png", direccion=(0.65, -1.0, 0.56), lente=52.0, margen=0.88)


def _separar_pieza_y_sosten(ruta_limpia: Path, ruta_con_sosten: Path, nombre: str, color_pieza: str, pos=(0.0, 0.0, 0.0)):
    """Separa los primeros N_clean triángulos (pieza) de los restantes (sostén naranja)
    en un STL empaquetado con sosten.py."""
    n_clean = struct.unpack("<I", ruta_limpia.read_bytes()[:84][80:84])[0]
    raw = np.fromfile(ruta_con_sosten, dtype=[("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")], offset=84)
    tris = raw["v"]
    t_pieza = tris[:n_clean]
    t_sost = tris[n_clean:]

    obs = []
    for suf, bloque, col in [("pieza", t_pieza, color_pieza), ("sosten", t_sost, "sosten")]:
        if len(bloque) == 0:
            continue
        verts = bloque.reshape(-1, 3)
        u_verts, inv = np.unique(verts, axis=0, return_inverse=True)
        faces = inv.reshape(-1, 3)
        me = bpy.data.meshes.new(f"{nombre}_{suf}")
        me.from_pydata(u_verts.tolist(), [], faces.tolist())
        me.update()
        o = bpy.data.objects.new(f"{nombre}_{suf}", me)
        bpy.context.scene.collection.objects.link(o)
        o.location = Vector(pos)
        o.data.materials.append(material(col, COLORES[col]))
        suavizar(o)
        obs.append(o)
    return obs


def render_oficios(rapido: bool):
    """Sets 8, 9, 10 y 11: a la izquierda cómo sale de la impresora (con sostén en naranja
    sobre la cama), y a la derecha la maqueta limpia junto al zócalo + Lúa V5 a escala real."""
    oficios = [
        ("S8-policia", "60", 0.60, "azul", "s8_policia.png"),
        ("S9-bomberos", "60", 0.60, "rojo", "s9_bomberos.png"),
        ("S10-hospital", "60", 0.60, "turquesa", "s10_hospital.png"),
        ("S11-trenes", "33", 0.33, "verde", "s11_trenes.png"),
    ]
    for carpeta, esc_txt, k_esc, col, archivo_png in oficios:
        s, cam = escena(rapido, 1500, 760)
        obs = []
        ruta_limpia = RAIZ / "sets" / carpeta / "stl" / "conjunto.stl"
        ruta_entrega = RAIZ / "entrega" / "masque3d-sets-v1" / carpeta / f"{carpeta}-escala-{esc_txt}.stl"
        # Izquierda: en la cama con sostén en naranja
        obs += _separar_pieza_y_sosten(ruta_limpia, ruta_entrega, carpeta, col, pos=(0.0, 0.0, 0.0))
        bpy.ops.mesh.primitive_plane_add(size=210.0, location=(95.0, 65.0, -0.2))
        cama = bpy.context.active_object
        cama.data.materials.append(material("cama", COLORES["cama"], rug=0.6))
        obs.append(cama)

        # Flecha de paso de la cama a la mesa limpia
        obs += flecha((205, 60, 45), (245, 60, 45), r=2.6)

        # Derecha: maqueta limpia a la misma escala de impresión + Lúa V5 a escala 100% al lado
        o_limpia = cargar_stl(ruta_limpia, col, escala=k_esc, normalizar_min=True, pos=(260.0, 0.0, 0.0))
        obs.append(o_limpia)
        obs.append(cargar_stl(stl_set("S0-kit-lua", "K-ZOCALO-G"), "blanco", pos=(475.0, 0.0, 0.0), normalizar_min=True))
        obs += lua_v5_muneco(pos=(475.0 + 63.6, 63.6, 19.2), rot_z_deg=0.0, gris=False)

        foto(s, cam, obs, archivo_png, direccion=(0.45, -1.0, 0.68), lente=52.0, margen=0.88)


def render_taller_sostenes(rapido: bool):
    """Muestra ejemplos representativos de piezas de S0..S6 tal como van a la cama
    en entrega/masque3d-sets-v1/, con su sostén en naranja."""
    s, cam = escena(rapido, 1500, 760)
    obs = []
    ejemplos = [
        (RAIZ / "sets" / "S0-kit-lua" / "stl" / "K-PATIN-G.stl",
         RAIZ / "entrega" / "masque3d-sets-v1" / "00-comun" / "K-PATIN-G.stl",
         "patin", "amarillo", (0.0, 0.0, 0.0)),
        (RAIZ / "sets" / "S3-laboratorio-rampas" / "stl" / "S3-RAM-G.stl",
         RAIZ / "entrega" / "masque3d-sets-v1" / "S3-laboratorio-rampas" / "S3-RAM-G.stl",
         "rampa", "azul", (145.0, 0.0, 0.0)),
        (RAIZ / "sets" / "S4-maquina-soplo" / "stl" / "S4-ROT-ASPAS-E.stl",
         RAIZ / "entrega" / "masque3d-sets-v1" / "S4-maquina-soplo" / "S4-ROT-ASPAS-E.stl",
         "rotor", "turquesa", (325.0, 10.0, 0.0)),
        (RAIZ / "sets" / "S6-jardin" / "stl" / "S6-FLO-G.stl",
         RAIZ / "entrega" / "masque3d-sets-v1" / "S6-jardin" / "S6-FLO-G.stl",
         "flor", "rosa", (450.0, 10.0, 0.0)),
    ]
    for r_lim, r_ent, nom, col, pos in ejemplos:
        obs += _separar_pieza_y_sosten(r_lim, r_ent, nom, col, pos=pos)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(270.0, 60.0, -0.2))
    cama = bpy.context.active_object
    cama.scale = (580.0, 180.0, 1.0)
    cama.data.materials.append(material("cama", COLORES["cama"], rug=0.6))
    obs.append(cama)
    foto(s, cam, obs, "taller_sostenes.png", direccion=(0.35, -1.0, 0.72), lente=52.0, margen=0.88)


def main():
    rapido = "--rapido" in sys.argv
    print(f"· render_manual_sets · Blender {bpy.app.version_string} · rapido={rapido}")
    render_portada(rapido)
    render_p1(rapido)
    render_s0(rapido)
    render_s1(rapido)
    render_s2(rapido)
    render_s3(rapido)
    render_s4(rapido)
    render_s5(rapido)
    render_s6(rapido)
    render_oficios(rapido)
    render_taller_sostenes(rapido)
    print("· Todas las imágenes 3D del manual generadas en docs/cad/manual/")


if __name__ == "__main__":
    main()
