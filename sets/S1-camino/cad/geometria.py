"""Sólidos paramétricos del Set 1 con manifold3d.

Cada función devuelve un sólido hermético. La unión entre baldosas es
una cola de milano vertical (espiga): se imprime sin voladizo y se
monta bajándola. Las fichas y las placas entran por snap de nervio.
No hay OpenSCAD ni archivos .scad.
"""

from __future__ import annotations

import sys
from pathlib import Path

_CAD = Path(__file__).resolve().parent
if str(_CAD) not in sys.path:
    sys.path.insert(0, str(_CAD))

import parametros as P
from manifold3d import CrossSection, Manifold

CODIGOS = (
    "K-ZOCALO-G",
    "K-PLACA-INICIO",
    "K-PLACA-META",
    "K-PATIN-G",
    "S1-REC-LIS-G",
    "S1-REC-RUG-G",
    "S1-CUR-G",
    "S1-TEE-G",
    "S1-CMD-AVA-G",
    "S1-CMD-PAR-G",
    "S1-CMD-GIR-G",
    "S1-CMD-SAL-G",
    "S1-DEST-PARQUE",
    "S1-DEST-CAMA",
)

UNION = {
    "K-ZOCALO-G": "espiga",
    "K-PLACA-INICIO": "snap",
    "K-PLACA-META": "snap",
    "K-PATIN-G": "espiga",
    "S1-REC-LIS-G": "espiga",
    "S1-REC-RUG-G": "espiga",
    "S1-CUR-G": "espiga",
    "S1-TEE-G": "espiga",
    "S1-CMD-AVA-G": "snap",
    "S1-CMD-PAR-G": "snap",
    "S1-CMD-GIR-G": "snap",
    "S1-CMD-SAL-G": "snap",
    "S1-DEST-PARQUE": "snap",
    "S1-DEST-CAMA": "snap",
}

NOMBRES = {
    "K-ZOCALO-G": "Zócalo universal",
    "K-PLACA-INICIO": "Placa de identidad INICIO",
    "K-PLACA-META": "Placa de identidad META",
    "K-PATIN-G": "Patín guía",
    "S1-REC-LIS-G": "Baldosa recta lisa",
    "S1-REC-RUG-G": "Baldosa recta rugosa",
    "S1-CUR-G": "Curva de 90 grados",
    "S1-TEE-G": "Intersección en T",
    "S1-CMD-AVA-G": "Ficha de comando avanza",
    "S1-CMD-PAR-G": "Ficha de comando para",
    "S1-CMD-GIR-G": "Ficha de comando gira",
    "S1-CMD-SAL-G": "Ficha de comando salta",
    "S1-DEST-PARQUE": "Placa de destino parque",
    "S1-DEST-CAMA": "Placa de destino cama",
}


def caja(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float) -> Manifold:
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))


def _eje_z(solido: Manifold) -> float:
    caja_mm = solido.bounding_box()
    return float(caja_mm[5])


def cola_macho_x(y: float, x_cara: float, signo: int) -> Manifold:
    """Espiga de cola de milano. signo +1 sale hacia +X."""
    z0, z1 = 0.0, P.ALTURA_BASE_MM
    solape = 0.15
    if signo > 0:
        x_cuello0 = x_cara - solape
        x_cuello1 = x_cara + P.CUELLO_FONDO_MM
        x_bulbo1 = x_cara + P.CUELLO_FONDO_MM + P.BULBO_FONDO_MM
        cuello = caja(x_cuello0, y - P.CUELLO_ANCHO_MM / 2, z0, x_cuello1, y + P.CUELLO_ANCHO_MM / 2, z1)
        bulbo = caja(x_cuello1, y - P.BULBO_ANCHO_MM / 2, z0, x_bulbo1, y + P.BULBO_ANCHO_MM / 2, z1)
    else:
        x_cuello1 = x_cara + solape
        x_cuello0 = x_cara - P.CUELLO_FONDO_MM
        x_bulbo0 = x_cara - P.CUELLO_FONDO_MM - P.BULBO_FONDO_MM
        cuello = caja(x_cuello0, y - P.CUELLO_ANCHO_MM / 2, z0, x_cuello1, y + P.CUELLO_ANCHO_MM / 2, z1)
        bulbo = caja(x_bulbo0, y - P.BULBO_ANCHO_MM / 2, z0, x_cuello0, y + P.BULBO_ANCHO_MM / 2, z1)
    return cuello + bulbo


def cola_hembra_x(y: float, x_cara: float, hacia_dentro: int) -> Manifold:
    """Vaciado de la cola. hacia_dentro +1 entra en el sólido hacia +X."""
    h = P.HOLGURA_MM
    z0, z1 = -0.4, P.ALTURA_BASE_MM + 0.4
    an = P.CUELLO_ANCHO_MM + 2 * h
    ab = P.BULBO_ANCHO_MM + 2 * h
    d1 = P.CUELLO_FONDO_MM + h
    d2 = P.BULBO_FONDO_MM + h
    if hacia_dentro > 0:
        cuello = caja(x_cara - 0.4, y - an / 2, z0, x_cara + d1, y + an / 2, z1)
        bulbo = caja(x_cara + P.CUELLO_FONDO_MM, y - ab / 2, z0, x_cara + d1 + d2, y + ab / 2, z1)
    else:
        cuello = caja(x_cara - d1, y - an / 2, z0, x_cara + 0.4, y + an / 2, z1)
        bulbo = caja(x_cara - d1 - d2, y - ab / 2, z0, x_cara - P.CUELLO_FONDO_MM, y + ab / 2, z1)
    return cuello + bulbo


def cola_macho_y(x: float, y_cara: float, signo: int) -> Manifold:
    z0, z1 = 0.0, P.ALTURA_BASE_MM
    solape = 0.15
    if signo > 0:
        y0 = y_cara - solape
        y1 = y_cara + P.CUELLO_FONDO_MM
        y2 = y_cara + P.CUELLO_FONDO_MM + P.BULBO_FONDO_MM
        cuello = caja(x - P.CUELLO_ANCHO_MM / 2, y0, z0, x + P.CUELLO_ANCHO_MM / 2, y1, z1)
        bulbo = caja(x - P.BULBO_ANCHO_MM / 2, y1, z0, x + P.BULBO_ANCHO_MM / 2, y2, z1)
    else:
        y1 = y_cara + solape
        y0 = y_cara - P.CUELLO_FONDO_MM
        yb = y_cara - P.CUELLO_FONDO_MM - P.BULBO_FONDO_MM
        cuello = caja(x - P.CUELLO_ANCHO_MM / 2, y0, z0, x + P.CUELLO_ANCHO_MM / 2, y1, z1)
        bulbo = caja(x - P.BULBO_ANCHO_MM / 2, yb, z0, x + P.BULBO_ANCHO_MM / 2, y0, z1)
    return cuello + bulbo


def cola_hembra_y(x: float, y_cara: float, hacia_dentro: int) -> Manifold:
    h = P.HOLGURA_MM
    z0, z1 = -0.4, P.ALTURA_BASE_MM + 0.4
    an = P.CUELLO_ANCHO_MM + 2 * h
    ab = P.BULBO_ANCHO_MM + 2 * h
    d1 = P.CUELLO_FONDO_MM + h
    d2 = P.BULBO_FONDO_MM + h
    if hacia_dentro > 0:
        cuello = caja(x - an / 2, y_cara - 0.4, z0, x + an / 2, y_cara + d1, z1)
        bulbo = caja(x - ab / 2, y_cara + P.CUELLO_FONDO_MM, z0, x + ab / 2, y_cara + d1 + d2, z1)
    else:
        cuello = caja(x - an / 2, y_cara - d1, z0, x + an / 2, y_cara + 0.4, z1)
        bulbo = caja(x - ab / 2, y_cara - d1 - d2, z0, x + ab / 2, y_cara - P.CUELLO_FONDO_MM, z1)
    return cuello + bulbo


def _embudo(x_boca: float, x_fondo: float, y: float, ancho_boca: float, ancho_fondo: float, z0: float, z1: float) -> Manifold:
    y0b, y1b = y - ancho_boca / 2, y + ancho_boca / 2
    y0f, y1f = y - ancho_fondo / 2, y + ancho_fondo / 2
    if x_boca <= x_fondo:
        poly = [(x_boca, y0b), (x_fondo, y0f), (x_fondo, y1f), (x_boca, y1b)]
    else:
        poly = [(x_fondo, y0f), (x_boca, y0b), (x_boca, y1b), (x_fondo, y1f)]
    return Manifold.extrude(CrossSection([poly]), z1 - z0).translate((0.0, 0.0, z0))


def ranura_recta() -> Manifold:
    """Ranura de 12 mm a lo largo de X, con chaflán de boca en los dos extremos."""
    w = P.BALDOSA_MM
    y = w / 2
    z0 = P.ALTURA_BASE_MM - P.RANURA_PROF_MM
    z1 = P.ALTURA_BASE_MM + 0.4
    largo = P.CHAFLAN_LARGO_MM
    boca = P.RANURA_ANCHO_MM + 2 * P.CHAFLAN_MM
    centro = caja(largo, y - P.RANURA_ANCHO_MM / 2, z0, w - largo, y + P.RANURA_ANCHO_MM / 2, z1)
    boca_ini = _embudo(0.0, largo, y, boca, P.RANURA_ANCHO_MM, z0, z1)
    boca_fin = _embudo(w, w - largo, y, boca, P.RANURA_ANCHO_MM, z0, z1)
    return centro + boca_ini + boca_fin


def _embudo_y(y_boca: float, y_fondo: float, x: float, ancho_boca: float, ancho_fondo: float, z0: float, z1: float) -> Manifold:
    x0b, x1b = x - ancho_boca / 2.0, x + ancho_boca / 2.0
    x0f, x1f = x - ancho_fondo / 2.0, x + ancho_fondo / 2.0
    # Contorno en sentido antihorario: extrude lo descarta si va al revés.
    if y_boca >= y_fondo:
        poly = [(x0f, y_fondo), (x1f, y_fondo), (x1b, y_boca), (x0b, y_boca)]
    else:
        poly = [(x0b, y_boca), (x1b, y_boca), (x1f, y_fondo), (x0f, y_fondo)]
    return Manifold.extrude(CrossSection([poly]), z1 - z0).translate((0.0, 0.0, z0))


def ranura_te() -> Manifold:
    """Ranura pasante en X y rama hacia +Y. Tres bocas con chaflán."""
    w = P.BALDOSA_MM
    z0 = P.ALTURA_BASE_MM - P.RANURA_PROF_MM
    z1 = P.ALTURA_BASE_MM + 0.4
    largo = P.CHAFLAN_LARGO_MM
    boca = P.RANURA_ANCHO_MM + 2 * P.CHAFLAN_MM
    y = w / 2
    x = w / 2
    pasante = caja(largo, y - P.RANURA_ANCHO_MM / 2, z0, w - largo, y + P.RANURA_ANCHO_MM / 2, z1)
    rama = caja(x - P.RANURA_ANCHO_MM / 2, y, z0, x + P.RANURA_ANCHO_MM / 2, w - largo, z1)
    b0 = _embudo(0.0, largo, y, boca, P.RANURA_ANCHO_MM, z0, z1)
    b1 = _embudo(w, w - largo, y, boca, P.RANURA_ANCHO_MM, z0, z1)
    by = _embudo_y(w + 0.2, w - largo, x, boca, P.RANURA_ANCHO_MM, z0, z1)
    return pasante + rama + b0 + b1 + by


def ranura_curva(segmentos: int) -> Manifold:
    """Cuarto de anillo. Centro en la esquina (0, W), radio W/2."""
    w = P.BALDOSA_MM
    r = w / 2
    z0 = P.ALTURA_BASE_MM - P.RANURA_PROF_MM
    alto = P.RANURA_PROF_MM + 0.6
    radio_ext = r + P.RANURA_ANCHO_MM / 2
    radio_int = r - P.RANURA_ANCHO_MM / 2
    exterior = Manifold.cylinder(alto, radio_ext, radio_ext, segmentos).translate((0.0, w, z0 - 0.2))
    interior = Manifold.cylinder(alto + 0.4, radio_int, radio_int, segmentos).translate((0.0, w, z0 - 0.4))
    anillo = exterior - interior
    recorte = caja(-0.2, -0.2, z0 - 0.4, w + 0.2, w + 0.2, P.ALTURA_BASE_MM + 0.4)
    return anillo ^ recorte


def pozo(x0: float, y0: float) -> Manifold:
    """Pozo abierto por arriba, con poste de llave en la esquina min y ranuras de snap."""
    x1 = x0 + P.POZO_ANCHO_MM
    y1 = y0 + P.POZO_FONDO_MM
    z1 = P.ALTURA_BASE_MM + 0.3
    z0 = P.ALTURA_BASE_MM - P.POZO_PROF_MM
    vacio = caja(x0, y0, z0, x1, y1, z1)
    # El poste se devuelve al sólido (no forma parte del vaciado).
    poste = caja(x0, y0, z0, x0 + P.FICHA_LLAVE_MM, y0 + P.FICHA_LLAVE_MM, z1)
    vacio = vacio - poste
    # Ranuras de snap en las caras X, abiertas hacia arriba.
    margen = (P.POZO_FONDO_MM - P.SNAP_ANCHO_MM - P.SNAP_HOLGURA_RANURA_MM) / 2
    y_ranura0 = y0 + margen
    y_ranura1 = y_ranura0 + P.SNAP_ANCHO_MM + P.SNAP_HOLGURA_RANURA_MM
    prof = P.SNAP_RANURA_MM
    ranura_izq = caja(x0 - prof, y_ranura0, z0, x0 + 0.2, y_ranura1, z1)
    ranura_der = caja(x1 - 0.2, y_ranura0, z0, x1 + prof, y_ranura1, z1)
    return vacio + ranura_izq + ranura_der


def cuerpo_baldosa(segmentos: int) -> Manifold:
    w = P.BALDOSA_MM
    h = P.ALTURA_BASE_MM
    solido = caja(0.0, 0.0, 0.0, w, w, h)
    for y in P.COLA_Y_MM:
        solido = solido + cola_macho_x(y, w, +1)
        solido = solido - cola_hembra_x(y, 0.0, +1)
    return solido


def baldosa_recta(rugosa: bool, segmentos: int) -> Manifold:
    solido = cuerpo_baldosa(segmentos) - ranura_recta()
    x0, y0 = P.POZO_RECTA_XY
    solido = solido - pozo(x0, y0)
    if rugosa:
        solido = solido + nervios(segmentos)
    return solido


def nervios(segmentos: int) -> Manifold:
    """Relieve de 1,5 mm, redondeado, solo en el lado −Y. No entra en la ranura."""
    radio = 1.60
    z_eje = P.ALTURA_BASE_MM - 0.10
    # El cilindro sobresale 1,50 mm: radio 1,60 con el eje 0,10 mm bajo la cara.
    largo = P.BALDOSA_MM - 24.0
    y = 8.0
    limite = (P.BALDOSA_MM - P.RANURA_ANCHO_MM) / 2 - 4.0
    solido = None
    n = max(12, segmentos // 2)
    while y < limite:
        c = Manifold.cylinder(largo, radio, radio, n)
        c = c.rotate((0.0, 90.0, 0.0)).translate((12.0, y, z_eje))
        solido = c if solido is None else solido + c
        y += 6.4
    if solido is None:
        raise RuntimeError("no se generaron nervios")
    return solido


def baldosa_curva(segmentos: int) -> Manifold:
    w = P.BALDOSA_MM
    solido = caja(0.0, 0.0, 0.0, w, w, P.ALTURA_BASE_MM)
    for y in P.COLA_Y_MM:
        solido = solido - cola_hembra_x(y, 0.0, +1)
    for x in P.COLA_Y_MM:
        solido = solido + cola_macho_y(x, w, +1)
    solido = solido - ranura_curva(segmentos)
    x0, y0 = P.POZO_CURVA_XY
    solido = solido - pozo(x0, y0)
    return solido


def baldosa_te(segmentos: int) -> Manifold:
    w = P.BALDOSA_MM
    solido = cuerpo_baldosa(segmentos)
    for x in P.COLA_Y_MM:
        solido = solido + cola_macho_y(x, w, +1)
    solido = solido - ranura_te()
    x0, y0 = P.POZO_TE_XY
    solido = solido - pozo(x0, y0)
    return solido


def _lua_v5() -> dict:
    """Cotas de Lúa V5: copia de lua-firmware (agents/lua_v5.py la compara)."""
    import json

    ruta = _CAD.parents[2] / "lua-v5" / "interfaz-construye.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def huella_lua(crece: float, segmentos: int) -> CrossSection:
    """Planta de la base de Lúa V5 (elipse + patas delanteras) en la baldosa:
    centro en (W/2, W/2), el frente de Lúa hacia +X."""
    import math

    L = _lua_v5()
    w = P.BALDOSA_MM
    cx = cy = w / 2
    b = L["base"]
    n = max(64, segmentos * 2)
    # lua x → baldosa y; lua y → baldosa −x (giro de +90°)
    elipse = [
        (cx + (b["ry"] + crece) * math.sin(2 * math.pi * k / n), cy + (b["rx"] + crece) * math.cos(2 * math.pi * k / n))
        for k in range(n)
    ][::-1]  # antihorario
    sec = CrossSection([elipse])
    pt = L["patas"]
    for x in pt["x"]:
        sec = sec + CrossSection.circle(pt["r"] + crece, n).translate((cx - pt["y"], cy + x))
    return sec


def cuna(segmentos: int) -> Manifold:
    """La cuna de Lúa V5, encima del zócalo."""
    w = P.BALDOSA_MM
    dentro = huella_lua(P.CUNA_HOLGURA_MM, segmentos)
    fuera = huella_lua(P.CUNA_HOLGURA_MM + P.CUNA_PARED_MM, segmentos)
    aro = Manifold.extrude(fuera - dentro, P.CUNA_ALTO_MM).translate((0.0, 0.0, P.ALTURA_BASE_MM))
    z0, z1 = P.ALTURA_BASE_MM - 0.1, P.ALTURA_BASE_MM + P.CUNA_ALTO_MM + 0.1
    # abierta por delante: Lúa sale de INICIO hacia la primera baldosa
    aro = aro - caja(w / 2 + P.CUNA_ABIERTA_X_MM, -1.0, z0, w + 10.0, w + 1.0, z1)
    # escotadura de la cola, detrás
    aro = aro - caja(-10.0, w / 2 - P.COLA_HUECO_MM, z0, w / 2, w / 2 + P.COLA_HUECO_MM, z1)
    return aro


def zocalo(segmentos: int) -> Manifold:
    """Zócalo para Lúa V5 (29/10/2026): la ranura y la espiga de las baldosas,
    la cuna con la huella de Lúa y, al lado, la franja con el bolsillo de la
    placa de identidad, fuera de la planta de Lúa para que no la tape."""
    w = P.BALDOSA_MM
    solido = caja(0.0, 0.0, 0.0, w, P.ZOCALO_FONDO_MM, P.ALTURA_BASE_MM)
    for y in P.COLA_Y_MM:
        solido = solido + cola_macho_x(y, w, +1)
        solido = solido - cola_hembra_x(y, 0.0, +1)
    solido = solido - ranura_recta()
    solido = solido + cuna(segmentos)
    solido = solido - bolsillo_placa(P.BOLSA_ZOCALO_Y0_MM)
    return solido


def bolsillo_placa(y0: float = P.BOLSA_Y0_MM) -> Manifold:
    x0 = P.BOLSA_X0_MM
    x1 = x0 + P.BOLSA_ANCHO_MM
    y1 = y0 + P.BOLSA_FONDO_MM
    z0 = P.ALTURA_BASE_MM - P.BOLSA_PROF_MM
    z1 = P.ALTURA_BASE_MM + 0.3
    vacio = caja(x0, y0, z0, x1, y1, z1)
    poste = caja(x0, y0, z0, x0 + P.PLACA_LLAVE_MM, y0 + P.PLACA_LLAVE_MM, z1)
    vacio = vacio - poste
    # Ranuras de snap en las caras Y (lados largos).
    ancho = P.SNAP_ANCHO_MM + P.SNAP_HOLGURA_RANURA_MM
    x_ranura0 = (x0 + x1) / 2 - ancho / 2
    x_ranura1 = x_ranura0 + ancho
    prof = P.SNAP_RANURA_MM
    sur_ranura = caja(x_ranura0, y0 - prof, z0, x_ranura1, y0 + 0.2, z1)
    norte = caja(x_ranura0, y1 - 0.2, z0, x_ranura1, y1 + prof, z1)
    return vacio + sur_ranura + norte


def _recorte_llave(solido: Manifold, llave: float) -> Manifold:
    return solido - caja(-0.2, -0.2, -0.2, llave, llave, _eje_z(solido) + 0.4)


def _nervios_snap_x(ancho: float, fondo: float, alto: float) -> Manifold:
    """Dos nervios en las caras X, a media profundidad, lejos de la llave."""
    y0 = (fondo - P.SNAP_ANCHO_MM) / 2
    y1 = y0 + P.SNAP_ANCHO_MM
    sal = P.SNAP_SALIENTE_MM
    izq = caja(-sal, y0, 0.0, 0.15, y1, alto)
    der = caja(ancho - 0.15, y0, 0.0, ancho + sal, y1, alto)
    return izq + der


def _nervios_snap_y(ancho: float, fondo: float, alto: float) -> Manifold:
    x0 = (ancho - P.SNAP_ANCHO_MM) / 2
    x1 = x0 + P.SNAP_ANCHO_MM
    sal = P.SNAP_SALIENTE_MM
    sur = caja(x0, -sal, 0.0, x1, 0.15, alto)
    norte = caja(x0, fondo - 0.15, 0.0, x1, fondo + sal, alto)
    return sur + norte


def ficha(icono: str, segmentos: int) -> Manifold:
    ancho, fondo, alto = P.FICHA_ANCHO_MM, P.FICHA_FONDO_MM, P.FICHA_ALTO_MM
    solido = caja(0.0, 0.0, 0.0, ancho, fondo, alto)
    solido = solido + _nervios_snap_x(ancho, fondo, alto)
    # El recorte local iguala el poste; la holgura de 0,20 mm la da el inset del pozo.
    solido = _recorte_llave(solido, P.FICHA_LLAVE_MM)
    solido = solido + icono_en(icono, ancho, fondo, alto, segmentos)
    return solido


def placa(icono: str, segmentos: int) -> Manifold:
    ancho = P.BOLSA_ANCHO_MM - 2 * P.HOLGURA_MM
    fondo = P.BOLSA_FONDO_MM - 2 * P.HOLGURA_MM
    alto = P.PLACA_ALTO_MM
    solido = caja(0.0, 0.0, 0.0, ancho, fondo, alto)
    solido = solido + _nervios_snap_y(ancho, fondo, alto)
    solido = _recorte_llave(solido, P.PLACA_LLAVE_MM)
    solido = solido + icono_en(icono, ancho, fondo, alto, segmentos)
    return solido


def icono_en(nombre: str, ancho: float, fondo: float, alto: float, segmentos: int) -> Manifold:
    """Relieve geométrico. Sin letras y sin emoji. Apoyado en la cara superior.

    29/10: cada trazo se engruesa 0,4 mm por lado sobre el dibujo de la v1. Los
    trazos de 2,4 y 2,8 mm (escucha, nivel, jardín, salta, cama) quedaban por
    debajo de la pared de 3,2 mm que mide check-v3-piezas de lua-firmware.
    """
    from manifold3d import JoinType

    trazo = _icono_v1(nombre, ancho, fondo, alto, segmentos)
    z0 = trazo.bounding_box()[2]
    alto_trazo = trazo.bounding_box()[5] - z0
    planta = trazo.project().offset(P.ICONO_ENGROSE_MM, JoinType.Round, 2.0, max(16, segmentos // 2))
    return Manifold.extrude(planta, alto_trazo).translate((0.0, 0.0, z0))


def _icono_v1(nombre: str, ancho: float, fondo: float, alto: float, segmentos: int) -> Manifold:
    """El dibujo del icono de la v1, sin engrosar."""
    z = alto - 0.05
    h = P.ICONO_ALTO_MM + 0.05
    cx, cy = ancho * 0.62, fondo * 0.55
    if nombre == "avanza":
        cuerpo = caja(cx - 10, cy - 2.2, z, cx + 2, cy + 2.2, z + h)
        punta = caja(cx + 1, cy - 5.5, z, cx + 8, cy + 5.5, z + h)
        return cuerpo + punta
    if nombre == "para":
        return caja(cx - 6, cy - 6, z, cx + 6, cy + 6, z + h)
    if nombre == "gira":
        n = max(16, segmentos // 2)
        ext = Manifold.cylinder(h, 7.0, 7.0, n).translate((cx, cy, z))
        inte = Manifold.cylinder(h + 0.4, 4.0, 4.0, n).translate((cx, cy, z - 0.2))
        arco = (ext - inte) ^ caja(cx - 0.2, cy - 8, z - 0.2, cx + 8, cy + 8, z + h + 0.2)
        return arco
    if nombre == "salta":
        a = caja(cx - 8, cy - 1.4, z, cx - 1, cy + 1.4, z + h)
        b = caja(cx - 1, cy + 1.0, z, cx + 6, cy + 3.8, z + h)
        c = caja(cx + 2, cy + 3.2, z, cx + 9, cy + 6.0, z + h)
        return a + b + c
    if nombre == "inicio":
        return caja(cx - 8, cy - 2.4, z, cx + 6, cy + 2.4, z + h) + caja(cx + 4, cy - 5, z, cx + 8, cy + 5, z + h)
    if nombre == "meta":
        n = max(16, segmentos // 2)
        ext = Manifold.cylinder(h, 6.5, 6.5, n).translate((cx, cy, z))
        inte = Manifold.cylinder(h + 0.4, 3.2, 3.2, n).translate((cx, cy, z - 0.2))
        return ext - inte
    if nombre == "parque":
        n = max(16, segmentos // 2)
        return Manifold.cylinder(h, 5.5, 5.5, n).translate((cx, cy, z))
    if nombre == "cama":
        base = caja(cx - 8, cy - 4, z, cx + 8, cy + 3, z + h)
        cabecero = caja(cx - 8, cy + 2, z, cx - 5, cy + 6, z + h)
        return base + cabecero
    if nombre == "escucha":
        return (
            caja(cx - 8, cy - 1.2, z, cx - 2, cy + 1.2, z + h)
            + caja(cx - 1, cy - 3.2, z, cx + 3, cy + 3.2, z + h)
            + caja(cx + 4, cy - 5.2, z, cx + 8, cy + 5.2, z + h)
        )
    if nombre == "receptor":
        return (
            caja(cx - 8, cy - 5, z, cx - 4, cy + 5, z + h)
            + caja(cx - 8, cy - 5, z, cx + 8, cy - 1.5, z + h)
            + caja(cx + 4, cy - 5, z, cx + 8, cy + 5, z + h)
        )
    if nombre == "frontal":
        n = max(16, segmentos // 2)
        return Manifold.cylinder(h, 5.5, 5.5, n).translate((cx, cy, z)) + caja(cx - 1.6, cy - 8, z, cx + 1.6, cy + 8, z + h)
    if nombre == "nivel":
        return caja(cx - 9, cy - 1.4, z, cx + 9, cy + 1.4, z + h) + caja(cx - 2.2, cy - 6, z, cx + 2.2, cy - 1, z + h)
    if nombre == "jardin":
        return (
            caja(cx - 1.4, cy - 7, z, cx + 1.4, cy + 2, z + h)
            + caja(cx - 7, cy - 1, z, cx - 1, cy + 2.2, z + h)
            + caja(cx + 1, cy + 1, z, cx + 7, cy + 4.2, z + h)
        )
    raise KeyError(nombre)


def patin(segmentos: int) -> Manifold:
    """El patín de Lúa V5: copia de lua-firmware (lua-v5/patin-montaje.stl).

    Se engancha con dos clics en la base de Lúa y corre con dos pivotes
    redondos que caben también por la curva. El de la v1 (`patin_v1`) no se
    enganchaba a nada y su carril recto de 50 mm no pasaba por la curva.
    """
    del segmentos
    sys.path.insert(0, str(_CAD.parents[2]))
    from agents.malla_io import leer_stl

    return leer_stl(_CAD.parents[2] / "lua-v5" / "patin-montaje.stl")


def patin_v1(segmentos: int) -> Manifold:
    """Patín de la v1 (28/10). Se conserva; ya no se imprime."""
    del segmentos
    p = P.PATIN_PLANTA_MM
    solido = caja(0.0, 0.0, 0.0, p, p, P.PATIN_ALTO_MM)
    cx = p / 2
    cy = p / 2
    carril = caja(
        cx - P.PATIN_CARRIL_LARGO_MM / 2,
        cy - P.PATIN_CARRIL_ANCHO_MM / 2,
        P.PATIN_ALTO_MM - 0.15,
        cx + P.PATIN_CARRIL_LARGO_MM / 2,
        cy + P.PATIN_CARRIL_ANCHO_MM / 2,
        P.PATIN_ALTO_MM + P.PATIN_CARRIL_ALTO_MM,
    )
    return solido + carril


def construir(codigo: str, segmentos: int) -> Manifold:
    if codigo == "K-ZOCALO-G":
        return zocalo(segmentos)
    if codigo == "K-PLACA-INICIO":
        return placa("inicio", segmentos)
    if codigo == "K-PLACA-META":
        return placa("meta", segmentos)
    if codigo == "K-PATIN-G":
        return patin(segmentos)
    if codigo == "S1-REC-LIS-G":
        return baldosa_recta(False, segmentos)
    if codigo == "S1-REC-RUG-G":
        return baldosa_recta(True, segmentos)
    if codigo == "S1-CUR-G":
        return baldosa_curva(segmentos)
    if codigo == "S1-TEE-G":
        return baldosa_te(segmentos)
    if codigo == "S1-CMD-AVA-G":
        return ficha("avanza", segmentos)
    if codigo == "S1-CMD-PAR-G":
        return ficha("para", segmentos)
    if codigo == "S1-CMD-GIR-G":
        return ficha("gira", segmentos)
    if codigo == "S1-CMD-SAL-G":
        return ficha("salta", segmentos)
    if codigo == "S1-DEST-PARQUE":
        return placa("parque", segmentos)
    if codigo == "S1-DEST-CAMA":
        return placa("cama", segmentos)
    raise KeyError(codigo)


def metadatos(codigo: str) -> dict:
    return {
        "codigo": codigo,
        "nombre": NOMBRES[codigo],
        "escala": "G",
        "union": UNION[codigo],
        "pared_min_mm": P.PARED_MIN_MM,
        "rosca_mm": None,
        "hipotesis_planta": (
            "Baldosa y zócalo: 4 × 31,80 mm. "
            "SETS no da el ancho del cuerpo de Lúa; se usa 2 módulos + 2 módulos."
        ),
    }
