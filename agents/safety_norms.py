"""SafetyNormsAuditor. Contrasta cada STL con EN 71-1 y con la pared mínima de FDM."""

from __future__ import annotations

import json
from pathlib import Path

from manifold3d import Manifold

from agents.malla_io import leer_stl

DIAMETRO = 31.75
PROFUNDIDAD = 57.1
PARED = 3.20
CAMA = (220.0, 220.0, 270.0)
ESFERA_G = 44.5
RADIO_EROSION = 1.60
UNIONES = {"espiga", "rosca", "snap"}


def ejecutar(raiz: Path) -> dict:
    maestros = json.loads(
        (raiz / "sets" / "S1-camino" / "pruebas" / "maestros.json").read_text(encoding="utf-8")
    )["maestros"]
    informes = []
    for ficha in maestros:
        informes.append(_auditar(raiz, ficha))
    fallo = [i["codigo"] for i in informes if not i["apto"]]
    documento = {
        "norma": "EN 71-1, criterio de diseño del README §7. No es ensayo de laboratorio.",
        "cilindro_mm": {"diametro": DIAMETRO, "profundidad": PROFUNDIDAD},
        "pared_min_mm": PARED,
        "esfera_g_min_mm": ESFERA_G,
        "cama_mm": list(CAMA),
        "apto": not fallo,
        "rechazados": fallo,
        "piezas": informes,
    }
    ruta = raiz / "sets" / "S1-camino" / "pruebas" / "auditoria.json"
    ruta.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if fallo:
        raise RuntimeError("auditoría rechazó: " + ", ".join(fallo))
    return documento


def _auditar(raiz: Path, ficha: dict) -> dict:
    ruta = raiz / ficha["stl"]
    solido = leer_stl(ruta)
    estado = str(solido.status())
    caja = solido.bounding_box()
    dims = [caja[3] - caja[0], caja[4] - caja[1], caja[5] - caja[2]]
    ordenadas = sorted(dims)
    cabe = _cabe_en_cilindro(ordenadas)
    dos_ejes = ordenadas[1] > DIAMETRO
    # Cada cota cabe en la cama 220 × 220 × 270. Ninguna pieza de este set
    # usa la altura de 270: el límite que manda es 220 mm en los tres ejes.
    cama = all(d <= 220.0 for d in dims)
    union = ficha["union"]
    rosca = ficha["rosca_mm"]
    rosca_ok = rosca is None or rosca >= 3.0
    volumen_ok = abs(solido.volume() - ficha["volumen_mm3"]) / ficha["volumen_mm3"] < 0.01
    nucleo = _nucleo(solido, ficha)
    es_esfera = "ESF" in ficha["codigo"]
    esfera_ok = (not es_esfera) or min(dims) >= ESFERA_G
    comprobaciones = {
        "stl_hermetico": estado == "Error.NoError" and not solido.is_empty(),
        "volumen_coincide": volumen_ok,
        "no_entra_en_el_cilindro": not cabe,
        "dos_ejes_mayores_que_el_cilindro": dos_ejes,
        "cabe_en_la_cama": cama,
        "union_mecanica": union in UNIONES,
        "rosca": rosca_ok,
        "nucleo_tras_erocion_1_60mm": nucleo > 500.0,
        "esfera_g": esfera_ok,
        "pared_declarada": ficha["pared_min_mm"] >= PARED,
    }
    return {
        "codigo": ficha["codigo"],
        "union": union,
        "dims_mm": [round(d, 2) for d in dims],
        "nucleo_mm3": round(nucleo, 1),
        "esfera": "no aplica" if not es_esfera else "comprobada",
        "comprobaciones": comprobaciones,
        "apto": all(comprobaciones.values()),
    }


def _cabe_en_cilindro(dims_ordenadas: list[float]) -> bool:
    """True si la caja cabe entera en el cilindro en alguna orientación alineada."""
    a, b, c = dims_ordenadas
    candidatos = ((c, a, b), (b, a, c), (a, b, c))
    for largo, u, v in candidatos:
        if largo <= PROFUNDIDAD and (u * u + v * v) <= DIAMETRO * DIAMETRO:
            return True
    return False


def _nucleo(solido: Manifold, ficha: dict) -> float:
    recorte = 1.8 if ficha["codigo"] in {"S1-REC-RUG-G"} or ficha["codigo"].startswith(("K-PLACA", "S1-DEST", "S1-CMD")) else 0.0
    cuerpo = solido
    if recorte > 0:
        caja = solido.bounding_box()
        tapa = Manifold.cube(
            (caja[3] - caja[0] + 8.0, caja[4] - caja[1] + 8.0, recorte),
            False,
        ).translate((caja[0] - 4.0, caja[1] - 4.0, caja[5] - recorte))
        cuerpo = solido - tapa
    esfera = Manifold.sphere(RADIO_EROSION, 12)
    nucleo = cuerpo.minkowski_difference(esfera)
    if nucleo.is_empty():
        return 0.0
    return float(nucleo.volume())
