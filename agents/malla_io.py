"""Lectura y escritura de STL binario y de GLB. Sin dependencias fuera de numpy."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
from manifold3d import Manifold, Mesh

_CABECERA = b"Lua Construye Set 1 manifold3d"


def escribir_stl(ruta: Path, solido: Manifold) -> int:
    malla = solido.to_mesh()
    vertices = np.asarray(malla.vert_properties[:, :3], dtype=np.float64)
    caras = np.asarray(malla.tri_verts, dtype=np.int64)
    bloques = []
    for cara in caras:
        p0, p1, p2 = vertices[cara[0]], vertices[cara[1]], vertices[cara[2]]
        normal = np.cross(p1 - p0, p2 - p0)
        largo = float(np.linalg.norm(normal))
        if largo < 1e-12:
            continue
        normal = normal / largo
        trozo = struct.pack("<3f", *normal)
        for punto in (p0, p1, p2):
            trozo += struct.pack("<3f", *punto)
        trozo += struct.pack("<H", 0)
        bloques.append(trozo)
    if not bloques:
        raise RuntimeError(f"STL vacío: {ruta}")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("wb") as salida:
        salida.write(_CABECERA.ljust(80, b" "))
        salida.write(struct.pack("<I", len(bloques)))
        salida.writelines(bloques)
    return len(bloques)


def leer_stl(ruta: Path) -> Manifold:
    datos = ruta.read_bytes()
    if datos[:5].lower() == b"solid" and b"\x00" not in datos[:80]:
        raise RuntimeError(f"STL ASCII no admitido: {ruta}")
    ncaras = struct.unpack_from("<I", datos, 80)[0]
    esperado = 84 + ncaras * 50
    if len(datos) < esperado:
        raise RuntimeError(f"STL truncado: {ruta}")
    puntos = np.empty((ncaras, 3, 3), dtype=np.float64)
    for i in range(ncaras):
        base = 84 + i * 50
        nums = struct.unpack_from("<12fH", datos, base)
        puntos[i, 0] = nums[3:6]
        puntos[i, 1] = nums[6:9]
        puntos[i, 2] = nums[9:12]
    soldado, caras = _soldar(puntos)
    malla = Mesh(
        np.ascontiguousarray(soldado, dtype=np.float32),
        np.ascontiguousarray(caras, dtype=np.uint32),
    )
    return Manifold(malla)


def _soldar(puntos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    plano = np.round(puntos.reshape(-1, 3), 3)
    unicos, inverso = np.unique(plano, axis=0, return_inverse=True)
    caras = inverso.reshape(-1, 3).astype(np.uint32)
    return unicos.astype(np.float32), caras


def escribir_glb(ruta: Path, solido: Manifold) -> int:
    malla = solido.to_mesh()
    vertices = np.asarray(malla.vert_properties[:, :3], dtype=np.float32)
    caras = np.asarray(malla.tri_verts, dtype=np.uint32)
    if len(vertices) > 65535:
        solido = solido.simplify(0.8)
        malla = solido.to_mesh()
        vertices = np.asarray(malla.vert_properties[:, :3], dtype=np.float32)
        caras = np.asarray(malla.tri_verts, dtype=np.uint32)
    indices = caras.reshape(-1).astype(np.uint16 if len(vertices) <= 65535 else np.uint32)
    pos = np.ascontiguousarray(vertices, dtype=np.float32).tobytes()
    idx = np.ascontiguousarray(indices).tobytes()
    pos = pos + b"\x00" * ((4 - len(pos) % 4) % 4)
    binario = pos + idx
    binario += b"\x00" * ((4 - len(binario) % 4) % 4)
    minimo = vertices.min(axis=0).tolist()
    maximo = vertices.max(axis=0).tolist()
    componente = 5123 if indices.dtype == np.uint16 else 5125
    documento = {
        "asset": {"version": "2.0", "generator": "ManifoldCadAgent"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": ruta.stem}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "mode": 4}]}],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": int(len(vertices)),
                "type": "VEC3",
                "min": [float(v) for v in minimo],
                "max": [float(v) for v in maximo],
            },
            {
                "bufferView": 1,
                "componentType": componente,
                "count": int(len(indices)),
                "type": "SCALAR",
            },
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(pos), "target": 34962},
            {"buffer": 0, "byteOffset": len(pos), "byteLength": len(idx), "target": 34963},
        ],
        "buffers": [{"byteLength": len(binario)}],
    }
    import json

    crudo = json.dumps(documento, separators=(",", ":")).encode("utf-8")
    crudo += b" " * ((4 - len(crudo) % 4) % 4)
    cuerpo = b"".join(
        (
            struct.pack("<I", len(crudo)),
            b"JSON",
            crudo,
            struct.pack("<I", len(binario)),
            b"BIN\x00",
            binario,
        )
    )
    archivo = b"glTF" + struct.pack("<II", 2, 12 + len(cuerpo)) + cuerpo
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(archivo)
    return len(archivo)
