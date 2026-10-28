"""Sólidos de los sets 0 y 2 a 6, de la probeta de la fase 1 y de las
piezas del Set 0 que cada escena nombra.

La fuente de las piezas es docs/SETS.md y el plan de impresión del
apartado 8. Donde el documento no da milímetros, la cifra está en
HIPOTESIS y se repite en el BOM. No hay archivos .scad.

El Set 1 no se regenera aquí: sus maestros siguen en sets/S1-camino.
El zócalo, el patín y las placas salen de ese mismo generador para
que el encaje de la placa no diverja.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

from manifold3d import CrossSection, Manifold, OpType

SEG = 32
PARED = 3.20
ROSCA = 3.60
PASO_ROSCA = 8.0
VUELTAS = 3

# Rosca gruesa. Diente 3,60 mm, por encima de los 3,00 mm del reglamento.
R_MENOR = 13.40
R_MAYOR = 17.00
R_BORE = 17.40
R_CRESTA = 13.85

_S1 = None


def _s1():
    global _S1
    if _S1 is None:
        ruta = Path(__file__).resolve().parents[1] / "sets" / "S1-camino" / "cad" / "geometria.py"
        spec = importlib.util.spec_from_file_location("geometria_s1_lote", ruta)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"no se pudo cargar {ruta}")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        _S1 = modulo
    return _S1


def caja(x0, y0, z0, x1, y1, z1) -> Manifold:
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), False).translate((x0, y0, z0))


def cil(h, r, seg=SEG) -> Manifold:
    return Manifold.cylinder(h, r, r, seg, False)


def asentar(solido: Manifold) -> Manifold:
    caja_ = solido.bounding_box()
    return solido.translate((-caja_[0], -caja_[1], -caja_[2]))


def _dientes(radio_base: float, prof: float, z0: float, fase: float) -> Manifold:
    """Rosca de filete cuadrado. El paso es 8 mm y el diente no llena el vano."""
    n_vuelta = 12
    total = VUELTAS * n_vuelta
    bloques = []
    for i in range(total):
        ang = fase + 2 * math.pi * i / n_vuelta
        z = z0 + PASO_ROSCA * i / n_vuelta
        bloque = Manifold.cube((prof, 4.4, 2.8), True)
        bloque = bloque.translate((radio_base + prof / 2.0, 0.0, 0.0))
        bloque = bloque.rotate((0.0, 0.0, math.degrees(ang)))
        bloque = bloque.translate((0.0, 0.0, z))
        bloques.append(bloque)
    return Manifold.batch_boolean(bloques, OpType.Add)


def rosca_macho(z0: float) -> Manifold:
    nucleo = cil(PASO_ROSCA * VUELTAS + 6.0, R_MENOR).translate((0.0, 0.0, z0))
    return nucleo + _dientes(R_MENOR, R_MAYOR - R_MENOR, z0 + 2.2, 0.0)


def collar_hembra(z0: float) -> Manifold:
    """Collar con cresta desfasada medio paso: el diente macho cae en el vano."""
    alto = PASO_ROSCA * VUELTAS + 8.0
    tubo = cil(alto, 24.0).translate((0.0, 0.0, z0)) - cil(alto + 2.0, R_BORE).translate((0.0, 0.0, z0 - 1.0))
    cresta = _dientes(R_CRESTA, R_BORE - R_CRESTA, z0 + 2.2 + PASO_ROSCA / 2.0, 0.0)
    return tubo + cresta


def _exigir(solido: Manifold, codigo: str) -> Manifold:
    if str(solido.status()) != "Error.NoError" or solido.is_empty():
        raise RuntimeError(f"{codigo} no es un sólido válido: {solido.status()}")
    return solido


# --- Fase 1. Probeta de encaje. La pieza es grande; el tetón es el ensayo. ---

HOLGURAS = (0.15, 0.20, 0.25)
TETON = {"G": (4.70, 4.50), "E": (3.20, 3.20)}


def _probeta(escala: str, holgura: float, macho: bool, marcas: int) -> Manifold:
    radio, alto = TETON[escala]
    cuerpo = caja(0, 0, 0, 84, 52, 20)
    if macho:
        cuerpo = cuerpo + cil(alto, radio).translate((42, 26, 20))
    else:
        cuerpo = cuerpo - cil(7.0, radio + holgura).translate((42, 26, 14.0))
    for i in range(marcas):
        cuerpo = cuerpo + caja(8 + i * 7, -3.4, 6, 12 + i * 7, 0.2, 14)
    return cuerpo


# --- Set 0. Kit. K-CUELLO no se modela: lo integra el fabricante. ---

def tronco() -> Manifold:
    cuerpo = caja(0, 0, 0, 72, 64, 40)
    # Llave del cuello, asimétrica hacia +X. El niño la palpa.
    cuerpo = cuerpo - caja(34, 20, 30, 62, 44, 40.4)
    cuerpo = cuerpo - caja(22, 30, 30, 40, 44, 40.4)
    # Pozos delanteros con muesca de llave. Los traseros son redondos.
    for x in (16, 52):
        cuerpo = cuerpo - caja(x - 8, 4, -0.4, x + 8, 18, 11)
        cuerpo = cuerpo - caja(x - 8, 4, -0.4, x - 3, 9, 11)
        cuerpo = cuerpo - cil(11.4, 6.40).translate((x, 48, -0.4))
    # Ranuras del lomo y de la cola, en la cara posterior.
    cuerpo = cuerpo - caja(10, 54, 24, 24, 64.6, 36)
    cuerpo = cuerpo - caja(48, 54, 24, 62, 64.6, 36)
    cuerpo = cuerpo - caja(28, 54, 6, 44, 64.6, 18)
    return cuerpo


def lomo() -> Manifold:
    cuerpo = caja(0, 0, 0, 76, 24, 20)
    cuerpo = cuerpo + caja(8, -9.4, 4, 21.5, 0.1, 15.5)
    cuerpo = cuerpo + caja(46, -9.4, 4, 59.5, 0.1, 15.5)
    return cuerpo


def _pata(delantera: bool) -> Manifold:
    cuerpo = caja(0, 0, 0, 48, 40, 36)
    if delantera:
        cuerpo = cuerpo + caja(16, 12, 36, 31.5, 25.5, 45.4)
        cuerpo = cuerpo + caja(16, 12, 36, 20.5, 16.5, 45.4)
    else:
        cuerpo = cuerpo + cil(9.6, 6.15).translate((24, 20, 36))
    return cuerpo


def cola() -> Manifold:
    cuerpo = caja(0, 0, 0, 88, 32, 18)
    cuerpo = cuerpo + caja(36, -9.4, 4, 51.5, 0.1, 15.5)
    # Estrechamiento posterior, sin arista viva: se conserva un canto de 8 mm.
    cuerpo = cuerpo - caja(70, -0.2, 12, 88.2, 8, 18.4)
    cuerpo = cuerpo - caja(70, 24, 12, 88.2, 32.2, 18.4)
    return cuerpo


def _placa(icono: str) -> Manifold:
    return _s1().placa(icono, SEG)


def _zocalo() -> Manifold:
    return _s1().zocalo(SEG)


def _patin() -> Manifold:
    return _s1().patin(SEG)


# --- Set 2. Estación de sonido. Paredes iguales; cambia la cavidad. ---

def resonador(radio: float, prof: float, garganta: float) -> Manifold:
    """Volumen exterior común. La pared real es 8 mm, muy por encima de 3,2."""
    cuerpo = caja(0, 0, 0, 78, 64, 72)
    cuerpo = cuerpo - cil(prof, radio).translate((39, 32, 16))
    cuerpo = cuerpo - cil(14, garganta).translate((39, 32, 60))
    # Espiga de apoyo, común a las tres familias, para el banco del martillo.
    cuerpo = cuerpo + caja(24, 22, -4.0, 54, 42, 0.2)
    return cuerpo


def bal_base() -> Manifold:
    cuerpo = caja(0, 0, 0, 120, 78, 16)
    cuerpo = cuerpo - caja(36, 22, 11, 70, 56, 16.4)
    cuerpo = cuerpo + caja(18, 0, 16, 46, 14, 52)
    cuerpo = cuerpo + caja(18, 64, 16, 46, 78, 52)
    # El cilindro, tras rotar 90° en X, queda hacia −Y y aquí atraviesa las dos carrilleras.
    eje = cil(86, 7.2).rotate((90, 0, 0)).translate((32, 82, 34))
    boca = caja(24, -1, 38, 40, 79, 54)
    cuerpo = cuerpo - eje - boca
    cuerpo = cuerpo + caja(100, 28, 16, 116, 50, 40)
    return cuerpo


def bal_brazo() -> Manifold:
    eje = cil(58, 6.4).rotate((90, 0, 0)).translate((16, 52, 14))
    brazo = caja(10, 18, 8, 92, 34, 22)
    cabeza = caja(78, 10, 4, 108, 42, 28)
    tacon = caja(84, 20, 0, 96, 32, 10)
    return eje + brazo + cabeza + tacon


def raspador() -> Manifold:
    cuerpo = caja(0, 0, 0, 132, 44, 16)
    for i in range(8):
        y = 10 + i * 4.2
        nervio = cil(120, 2.2).rotate((0, 90, 0)).translate((6, y, 16))
        cuerpo = cuerpo + nervio
    # Espiga en un extremo y caja en el otro, para unir los dos raspadores.
    cuerpo = cuerpo + caja(132, 14, 4, 144, 30, 12)
    cuerpo = cuerpo - caja(-0.4, 14.4, 4.3, 12, 29.6, 11.6)
    return cuerpo


def espatula() -> Manifold:
    cuerpo = caja(20, 0, 0, 120, 44, 12)
    punta = cil(12, 22).rotate((0, 90, 0)).translate((20, 22, 6))
    # Caja que recibe la espiga del raspador.
    cuerpo = cuerpo - caja(108, 14.4, 2.2, 120.4, 29.6, 9.8)
    return cuerpo + punta


# --- Set 3. Rampas. H = 19,20 mm porque 8 × 31,80 no cabe en la cama. ---

H_PILAR = 19.20
L_RAMPA = 8.0 * H_PILAR  # 153,60


def rampa() -> Manifold:
    # Canal de 48 mm: la esfera de 45 mm pasa con holgura. Paredes laterales de 8 mm.
    cuerpo = caja(0, 0, 0, L_RAMPA, 64, 24)
    cuerpo = cuerpo - caja(-1, 8, 10, L_RAMPA + 1, 56, 26)
    eje = cil(100, 6.4).rotate((90, 0, 0)).translate((18, 82, 14))
    return cuerpo + eje


def bisagra() -> Manifold:
    cuerpo = caja(0, 0, 0, 72, 96, 16)
    cuerpo = cuerpo + caja(4, 0, 16, 40, 14, 50)
    cuerpo = cuerpo + caja(4, 82, 16, 40, 96, 50)
    eje = cil(104, 7.0).rotate((90, 0, 0)).translate((22, 100, 32))
    boca = caja(14, -1, 36, 30, 97, 52)
    return cuerpo - eje - boca


def pilar(numero: int) -> Manifold:
    cuerpo = caja(0, 0, 0, 44, 44, H_PILAR)
    cuerpo = cuerpo - cil(8.0, 6.25).translate((22, 22, -0.4))
    cuerpo = cuerpo + cil(6.0, 6.00).translate((22, 22, H_PILAR))
    ancho, hueco = 4.0, 2.2
    total = numero * ancho + (numero - 1) * hueco
    x0 = 22 - total / 2
    for i in range(numero):
        x = x0 + i * (ancho + hueco)
        cuerpo = cuerpo + caja(x, 42.0, 5, x + ancho, 47.2, 13)
    return cuerpo


def esfera(rugosa: bool) -> Manifold:
    solido = Manifold.sphere(22.5, 48)
    if rugosa:
        for i in range(14):
            a = i * 2.399
            b = (i * 0.7) % math.pi
            x = 20.6 * math.sin(b) * math.cos(a)
            y = 20.6 * math.sin(b) * math.sin(a)
            z = 20.6 * math.cos(b)
            solido = solido + Manifold.sphere(2.3, 10).translate((x, y, z))
    return solido


def friccion() -> Manifold:
    cuerpo = caja(0, 0, 0, 120, 64, 16)
    for i in range(9):
        y = 8 + i * 5
        nervio = cil(100, 1.8).rotate((0, 90, 0)).translate((10, y, 16))
        cuerpo = cuerpo + nervio
    cuerpo = cuerpo + caja(120, 20, 4, 132, 36, 12)
    return cuerpo


def curva_peraltada() -> Manifold:
    solido = caja(0, 0, 0, 150, 150, 26)
    cx, cy, radio = 18.0, 18.0, 78.0
    vacios = []
    for i in range(16):
        ang = (i + 0.5) * math.pi / 2 / 16
        vacio = caja(-9, -24, 0, 9, 24, 18)
        # El peralte sube el fondo hacia el exterior de la curva.
        vacio = vacio.translate((0, 0, 8 + 4 * math.sin(ang)))
        vacio = vacio.rotate((0, 0, math.degrees(ang)))
        vacio = vacio.translate((cx + radio * math.cos(ang), cy + radio * math.sin(ang), 0))
        vacios.append(vacio)
    # Bocas abiertas en los dos extremos del cuarto de vuelta.
    vacios.append(caja(78, -2, 8, 152, 48, 24))
    vacios.append(caja(-2, 78, 12, 48, 152, 26))
    return solido - Manifold.batch_boolean(vacios, OpType.Add)


def receptor() -> Manifold:
    cuerpo = caja(0, 0, 0, 156, 80, 18)
    cuerpo = cuerpo - caja(8, 16, 8, 108, 64, 20)
    # Lengüeta: la esfera se detiene un módulo (31,8 mm) antes del extremo.
    cuerpo = cuerpo + caja(108, 8, 18, 116, 72, 36)
    cuerpo = cuerpo - caja(-0.4, 22.4, 4.4, 14, 37.6, 12.4)
    return cuerpo


# --- Set 4. Soplo. Sin embocadura: no es PLA de FDM. ---

def canal() -> Manifold:
    cuerpo = caja(0, 0, 0, 156, 52, 52)
    bore = Manifold.cylinder(164, 12.0, 2.0, SEG, False).rotate((0, 90, 0)).translate((-4, 26, 26))
    cuerpo = cuerpo - bore
    # Dos pozos para las compuertas, lejos del conducto.
    cuerpo = cuerpo - caja(112, 18, 42, 128, 34, 52.4)
    cuerpo = cuerpo - caja(134, 18, 42, 150, 34, 52.4)
    return cuerpo


def codo() -> Manifold:
    largo, r_ext, r_int = 58.0, 20.0, 8.0

    def tubo(eje: str, interior: bool) -> Manifold:
        radio = r_int if interior else r_ext
        extra = 16.0 if interior else 0.0
        retro = 10.0 if interior else 0.0
        pieza = Manifold.cylinder(largo + extra, radio, radio, SEG, False).translate((0, 0, -retro))
        if eje == "x":
            return pieza.rotate((0, 90, 0))
        return pieza.rotate((90, 0, 0)).translate((0, largo + extra - retro, 0))

    solido = tubo("x", False) + tubo("y", False) + Manifold.sphere(r_ext, SEG)
    solido = solido - tubo("x", True) - tubo("y", True)
    return solido.translate((r_ext + 2, r_ext + 2, r_ext + 2))


def _jaula(lado_x, lado_y, lado_z, pared, radio_eje, ranuras) -> Manifold:
    cuerpo = caja(0, 0, 0, lado_x, lado_y, lado_z)
    cuerpo = cuerpo - caja(pared, pared, pared, lado_x - pared, lado_y - pared, lado_z - pared)
    for x0, x1, z0, z1 in ranuras:
        cuerpo = cuerpo - caja(x0, -1, z0, x1, pared + 1, z1)
        cuerpo = cuerpo - caja(x0, lado_y - pared - 1, z0, x1, lado_y + 1, z1)
    eje = cil(lado_y + 8, radio_eje).rotate((90, 0, 0)).translate((lado_x / 2, lado_y + 4, lado_z / 2))
    return cuerpo - eje


def rotor_jaula() -> Manifold:
    return _jaula(
        96, 72, 72, 8.0, 5.4,
        ((22, 74, 20, 34), (22, 74, 40, 54)),
    )


def rotor_aspas() -> Manifold:
    eje = cil(80, 4.6).rotate((0, 90, 0)).translate((0, 0, 0))
    aspas = []
    for i in range(4):
        aspa = caja(-5, -2.4, 7, 5, 2.4, 24)
        aspas.append(aspa.rotate((90.0 * i, 0.0, 0.0)).translate((40, 0, 0)))
    return eje + Manifold.batch_boolean(aspas, OpType.Add)


def mol_jaula() -> Manifold:
    return _jaula(
        120, 96, 96, 10.0, 6.2,
        ((28, 52, 24, 40), (68, 92, 24, 40), (28, 52, 56, 72), (68, 92, 56, 72)),
    )


def mol_aspas() -> Manifold:
    eje = cil(104, 5.2).rotate((0, 90, 0)).translate((0, 0, 0))
    aspas = []
    for i in range(4):
        aspa = caja(-6, -4.0, 8, 6, 4.0, 32)
        aspas.append(aspa.rotate((90.0 * i, 0.0, 0.0)).translate((52, 0, 0)))
    return eje + Manifold.batch_boolean(aspas, OpType.Add)


def compuerta(grueso: float, barras: int) -> Manifold:
    hoja = caja(0, 0, 0, 76, 44, grueso)
    espiga = cil(8.0, 5.4).translate((38, 16, grueso))
    for i in range(barras):
        hoja = hoja + caja(10 + i * 8, 30, grueso - 0.1, 15 + i * 8, 38, grueso + 2.2)
    return hoja + espiga


# --- Set 5. Palanca. La viga de 10 × 31,80 mm no cabe en 220 mm. ---

def fulcro() -> Manifold:
    perfil = [(0, 0), (96, 0), (64, 32), (32, 32)]
    solido = Manifold.extrude(CrossSection([perfil]), 52)
    lomo_redondo = cil(52, 5.0).translate((48, 32, 0))
    return (solido + lomo_redondo).rotate((90, 0, 0)).translate((0, 52, 0))


def viga() -> Manifold:
    cuerpo = caja(0, 0, 0, 186, 48, 18)
    # Asiento del fulcro, al centro, sin partir la viga.
    cuerpo = cuerpo - caja(88, 8, -0.4, 98, 40, 4)
    centros = (21, 35, 49, 63, 77)
    for dx in centros:
        for signo in (-1, 1):
            x = 93 + signo * dx
            cuerpo = cuerpo - cil(7.0, 5.3).translate((x, 24, 12))
            puesto = centros.index(dx) + 1
            largo = 4.0 + puesto * 3.2
            cuerpo = cuerpo + caja(x - 1.8, 1.5, 16.4, x + 1.8, 1.5 + largo, 19.8)
            cuerpo = cuerpo + caja(x - 1.8, 46.5 - largo, 16.4, x + 1.8, 46.5, 19.8)
    return cuerpo


def _masa(volumen_cuerpo: float, ancho: float, fondo: float, forma: str) -> Manifold:
    alto = volumen_cuerpo / (ancho * fondo)
    cuerpo = caja(0, 0, 0, ancho, fondo, alto)
    if forma == "nube":
        for dx in (-10, 0, 10):
            cuerpo = cuerpo + cil(3.2, 7.0).translate((ancho / 2 + dx, fondo / 2, alto))
    elif forma == "hoja":
        cuerpo = cuerpo + caja(8, fondo / 2 - 3, alto, ancho - 8, fondo / 2 + 3, alto + 3.4)
        cuerpo = cuerpo + caja(ancho / 2 - 3, 6, alto, ancho / 2 + 3, fondo - 6, alto + 3.4)
    else:
        cuerpo = cuerpo - caja(-0.2, -0.2, alto - 4, 8, 8, alto + 0.2)
        cuerpo = cuerpo - caja(ancho - 8, fondo - 8, alto - 4, ancho + 0.2, fondo + 0.2, alto + 0.2)
    cuerpo = cuerpo + cil(5.0, 4.6).translate((ancho / 2, fondo / 2, -5.0))
    return cuerpo


def pasador() -> Manifold:
    """Clip en U. No es un pasador suelto de diámetro pequeño."""
    cuerpo = caja(0, 0, 0, 64, 40, 28)
    cuerpo = cuerpo - caja(8, -0.4, 8, 56, 32, 28.4)
    return cuerpo


# --- Set 6. Jardín. Rosca vertical, frutos grandes, pantallas opacas. ---

def tierra() -> Manifold:
    cuerpo = caja(0, 0, 0, 160, 120, 24)
    cuerpo = cuerpo - cil(10.0, 20.2).translate((48, 60, 14))
    # Ranura de noche.
    cuerpo = cuerpo - caja(96, 16, 16, 154, 32, 24.4)
    # Pozos del prisma de agua y del prisma de sol.
    cuerpo = cuerpo - cil(7.0, 6.6).translate((48, 96, 17))
    cuerpo = cuerpo - cil(7.0, 6.6).translate((100, 78, 17))
    return cuerpo


def semilla() -> Manifold:
    disco = caja(-29, -29, 0, 29, 29, 12)
    boss = cil(8.0, 19.6).translate((0, 0, -8))
    return disco + boss + rosca_macho(12)


def tallo() -> Manifold:
    hembra = collar_hembra(0)
    vastago = cil(40, R_MENOR).translate((0, 0, 32))
    punta = cil(12, 12.0).translate((0, 0, 72))
    return hembra + vastago + _dientes(R_MENOR, R_MAYOR - R_MENOR, 40.0, 0.0) + punta


def _corona_floral(copa: bool) -> Manifold:
    solido = collar_hembra(0)
    if copa:
        cuenco = cil(20, 36).translate((0, 0, 28)) - cil(12, 22).translate((0, 0, 38))
        solido = solido + cuenco
        for i in range(3):
            ang = math.radians(i * 120 + 30)
            cx, cy = 28 * math.cos(ang), 28 * math.sin(ang)
            solido = solido - cil(7.0, 4.4).translate((cx, cy, 42))
    else:
        solido = solido + cil(10, 12).translate((0, 0, 28))
        petalos = []
        for i in range(6):
            petalo = caja(16, -5, 26, 42, 5, 34)
            petalo = petalo.rotate((0, 0, i * 60.0))
            petalos.append(petalo)
        solido = solido + Manifold.batch_boolean(petalos, OpType.Add)
    return solido


def fruto_mango() -> Manifold:
    cuerpo = Manifold.sphere(20, 32).scale((1.30, 1.05, 1.05))
    return cuerpo + cil(6.0, 4.0).translate((0, 0, -22))


def fruto_naranja() -> Manifold:
    return Manifold.sphere(22.5, 40) + cil(6.0, 4.0).translate((0, 0, -24))


def fruto_manzana() -> Manifold:
    cuerpo = Manifold.sphere(22.5, 40)
    cuerpo = cuerpo - Manifold.sphere(6.0, 16).translate((0, 0, 20))
    cuerpo = cuerpo + cil(6.0, 4.0).translate((0, 0, -24))
    return cuerpo


def prisma(ancho, fondo, alto) -> Manifold:
    perfil = [(0, 0), (ancho, 0), (ancho / 2, fondo)]
    solido = Manifold.extrude(CrossSection([perfil]), alto)
    return solido + cil(6.0, 6.0).translate((ancho / 2, fondo * 0.35, -6))


def _pantalla(hueco: str, noche: bool) -> Manifold:
    cuerpo = caja(0, 0, 0, 120, 96, 8)
    if hueco == "arbol":
        cuerpo = cuerpo - caja(52, 16, -0.4, 68, 48, 8.4)
        cuerpo = cuerpo - cil(10, 16).translate((60, 62, -1))
    else:
        cuerpo = cuerpo - cil(10, 18).translate((60, 52, -1))
    if noche:
        cuerpo = cuerpo + caja(32, -14, 0, 88, 0.2, 8)
    else:
        cuerpo = cuerpo + caja(20, -28, 0, 100, 0.2, 8)
    return cuerpo


def construir(codigo: str) -> Manifold:
    solido = _CATALOGO[codigo]["construir"]()
    return _exigir(asentar(solido), codigo)


def _f(codigo, nombre, cantidad, union, construir_fn, rosca_mm=None, recorte=0.0, esfera=False, nota=""):
    return {
        "codigo": codigo,
        "nombre": nombre,
        "cantidad": cantidad,
        "union": union,
        "rosca_mm": rosca_mm,
        "pared_min_mm": PARED,
        "recorte_mm": recorte,
        "esfera": esfera,
        "nota": nota,
        "construir": construir_fn,
    }


def _variantes_resonador():
    """Tres variantes por familia. La pared no cambia: cambia cavidad y garganta."""
    base = {
        "AZU": (16.0, 46.0, 6.0, "grave"),
        "AMA": (13.0, 34.0, 9.0, "medio"),
        "ROJ": (10.0, 24.0, 12.0, "agudo"),
    }
    piezas = []
    for color, (radio, prof, garganta, nombre) in base.items():
        for letra, dr, dp, dg in (("A", 0.0, 0.0, 0.0), ("B", 0.0, 0.0, 1.2), ("C", 0.0, -6.0, 0.0)):
            r, p, g = radio + dr, prof + dp, garganta + dg

            def _hacer(rr=r, pp=p, gg=g):
                return resonador(rr, pp, gg)

            piezas.append(
                _f(
                    f"S2-RES-{color}-E-{letra}",
                    f"Resonador {nombre} variante {letra}",
                    1,
                    "espiga",
                    _hacer,
                    nota=(
                        f"Cavidad r {r:.1f} mm, profundidad {p:.1f} mm, garganta r {g:.1f} mm. "
                        "Pared 8 mm. La variante de 1,5 mm no se imprime."
                    ),
                )
            )
    return piezas


def _probetas():
    piezas = []
    for escala in ("G", "E"):
        for i, holgura in enumerate(HOLGURAS, start=1):
            marca = f"{holgura:.2f}".replace(".", "")
            piezas.append(
                _f(
                    f"P1-MAC-{escala}-{marca}",
                    f"Probeta macho {escala} holgura {holgura:.2f} mm",
                    1,
                    "espiga",
                    lambda e=escala, h=holgura, n=i: _probeta(e, h, True, n),
                    nota=f"Tetón escala {escala}. La holgura se mide en la hembra del mismo sufijo.",
                )
            )
            piezas.append(
                _f(
                    f"P1-HEM-{escala}-{marca}",
                    f"Probeta hembra {escala} holgura {holgura:.2f} mm",
                    1,
                    "espiga",
                    lambda e=escala, h=holgura, n=i: _probeta(e, h, False, n),
                    nota=f"Pozo con holgura radial {holgura:.2f} mm sobre el tetón {escala}.",
                )
            )
    return piezas


def _pilares():
    return [
        _f(
            f"S3-PIL-{n}-G",
            f"Pilar con marca táctil {n}",
            1,
            "espiga",
            lambda k=n: pilar(k),
            nota="Altura H = 19,20 mm. El 8 × 31,80 mm de la rampa no cabe en la cama.",
        )
        for n in range(1, 7)
    ]


_COMUN = {
    "K-ZOCALO-G": _f("K-ZOCALO-G", "Zócalo universal", 1, "espiga", _zocalo, nota="Mismo sólido que el Set 1."),
    "K-PATIN-G": _f("K-PATIN-G", "Patín guía", 1, "espiga", _patin, nota="Mismo sólido que el Set 1. Corre en la ranura de 12 mm."),
    "K-PLACA-INICIO": _f("K-PLACA-INICIO", "Placa Inicio", 1, "snap", lambda: _placa("inicio"), recorte=1.8),
    "K-PLACA-META": _f("K-PLACA-META", "Placa Meta", 1, "snap", lambda: _placa("meta"), recorte=1.8),
    "K-PLACA-ESCUCHA": _f("K-PLACA-ESCUCHA", "Placa Escucha", 1, "snap", lambda: _placa("escucha"), recorte=1.8),
    "K-PLACA-RECEPTOR": _f("K-PLACA-RECEPTOR", "Placa Receptor", 1, "snap", lambda: _placa("receptor"), recorte=1.8),
    "K-PLACA-FRONTAL": _f("K-PLACA-FRONTAL", "Placa Frontal", 1, "snap", lambda: _placa("frontal"), recorte=1.8),
    "K-PLACA-NIVEL": _f("K-PLACA-NIVEL", "Placa Nivel", 1, "snap", lambda: _placa("nivel"), recorte=1.8),
    "K-PLACA-JARDIN": _f("K-PLACA-JARDIN", "Placa Jardín", 1, "snap", lambda: _placa("jardin"), recorte=1.8),
}

_CATALOGO = {
    **_COMUN,
    "K-TRONCO-G": _f("K-TRONCO-G", "Tronco con llave de cuello", 1, "espiga", tronco, nota="La llave del cuello está desplazada. K-CUELLO no se imprime."),
    "K-LOMO-G": _f("K-LOMO-G", "Bloque dorsal", 1, "espiga", lomo, nota="Cara superior plana."),
    "K-PATA-DEL-G": _f("K-PATA-DEL-G", "Pata delantera con llave", 2, "espiga", lambda: _pata(True)),
    "K-PATA-TRA-G": _f("K-PATA-TRA-G", "Pata trasera", 2, "espiga", lambda: _pata(False)),
    "K-COLA-G": _f("K-COLA-G", "Cola", 1, "espiga", cola, nota="Marca la parte de atrás de Lúa."),
    "S2-BAL-BASE-E": _f(
        "S2-BAL-BASE-E",
        "Banco del martillo",
        1,
        "snap",
        bal_base,
        nota="El código de SETS es S2-BAL-E. Se parte en banco y brazo para que el eje no sea una pieza suelta.",
    ),
    "S2-BAL-BRAZO-E": _f(
        "S2-BAL-BRAZO-E",
        "Brazo del martillo con eje",
        1,
        "snap",
        bal_brazo,
        nota="Eje integral al brazo. Entra a presión en el banco. No hay pasador suelto.",
    ),
    "S2-RAS-E": _f("S2-RAS-E", "Raspador estriado", 2, "espiga", raspador, recorte=2.4, nota="Estrías redondeadas de 4,4 mm."),
    "S2-ESP-E": _f("S2-ESP-E", "Espátula sin filo", 1, "espiga", espatula, nota="La punta es un medio cilindro."),
    "S3-RAM-G": _f("S3-RAM-G", "Rampa articulada", 1, "snap", rampa, nota=f"L = 8H = {L_RAMPA:.2f} mm con H = 19,20 mm."),
    "S3-BIS-G": _f("S3-BIS-G", "Bloque bisagra", 1, "snap", bisagra, nota="Alojamiento en C. Sin pasador suelto."),
    "S3-ESF-LIS-G": _f("S3-ESF-LIS-G", "Esfera lisa", 2, "espiga", lambda: esfera(False), esfera=True, nota="Diámetro 45 mm. La esfera E de 38 mm no se genera."),
    "S3-ESF-RUG-G": _f("S3-ESF-RUG-G", "Esfera rugosa", 2, "espiga", lambda: esfera(True), esfera=True, recorte=0.0, nota="Textura integrada. Sin lastre suelto."),
    "S3-FRI-G": _f("S3-FRI-G", "Tramo de fricción reversible", 1, "espiga", friccion, recorte=2.2),
    "S3-CUR-PER-G": _f("S3-CUR-PER-G", "Curva peraltada", 1, "espiga", curva_peraltada),
    "S3-REC-G": _f("S3-REC-G", "Receptor con lengüeta", 1, "espiga", receptor, nota="La lengüeta deja 40 mm, un módulo, antes del extremo."),
    "S4-CAN-E": _f("S4-CAN-E", "Cuerpo del canal", 2, "espiga", canal, nota="Salida de 4 mm de diámetro: es un orificio, no una pared."),
    "S4-COD-E": _f("S4-COD-E", "Codo de 90 grados", 1, "espiga", codo),
    "S4-ROT-JAULA-E": _f("S4-ROT-JAULA-E", "Jaula del rotor", 1, "snap", rotor_jaula, nota="El código de SETS es S4-ROT-E. La jaula y las aspas se imprimen aparte."),
    "S4-ROT-ASPAS-E": _f("S4-ROT-ASPAS-E", "Rotor de aspas", 1, "snap", rotor_aspas, nota="Eje integral de 9,2 mm. Holgura radial 0,8 mm con la jaula."),
    "S4-COM-LIG-E": _f("S4-COM-LIG-E", "Compuerta ligera", 1, "espiga", lambda: compuerta(8.0, 1), recorte=2.4, nota="El contrapeso es más PLA, no un lastre suelto."),
    "S4-COM-PES-E": _f("S4-COM-PES-E", "Compuerta pesada", 1, "espiga", lambda: compuerta(16.0, 3), recorte=2.4, nota="Más volumen de PLA que la ligera. Los gramos no se han pesado."),
    "S4-MOL-JAULA-G": _f("S4-MOL-JAULA-G", "Jaula del molinete", 1, "snap", mol_jaula, nota="Para el soplo del adulto con menores de 3 años."),
    "S4-MOL-ASPAS-G": _f("S4-MOL-ASPAS-G", "Aspas anchas del molinete", 1, "snap", mol_aspas),
    "S5-FUL-G": _f("S5-FUL-G", "Fulcro de arista redondeada", 1, "espiga", fulcro, nota="La arista es un cilindro de 5 mm. El desgaste de PETG no se ha ensayado."),
    "S5-VIG-G": _f(
        "S5-VIG-G",
        "Viga balancín",
        1,
        "espiga",
        viga,
        recorte=2.2,
        nota="186 mm. Diez módulos de 31,80 mm miden 318 mm y no caben en la cama.",
    ),
    "S5-MAS-20": _f("S5-MAS-20", "Masa de referencia 20 g", 2, "espiga", lambda: _masa(14600, 48, 40, "nube"), recorte=3.6, nota="Objetivo a 1,24 g/cm³. No pesada. Relieve de nube."),
    "S5-MAS-40": _f("S5-MAS-40", "Masa de referencia 40 g", 1, "espiga", lambda: _masa(30800, 56, 46, "hoja"), recorte=3.8, nota="Objetivo a 1,24 g/cm³. No pesada. Relieve de hoja."),
    "S5-MAS-60": _f("S5-MAS-60", "Masa de referencia 60 g", 1, "espiga", lambda: _masa(48200, 64, 50, "facetada"), nota="Objetivo a 1,24 g/cm³. No pesada. Chaflán facetado."),
    "S5-PAS-G": _f("S5-PAS-G", "Clip de puente", 4, "snap", pasador, nota="Sustituye al pasador pequeño, que entraría en el cilindro de piezas pequeñas."),
    "S6-TIE-G": _f("S6-TIE-G", "Base de tierra", 1, "espiga", tierra),
    "S6-SEM-G": _f("S6-SEM-G", "Semilla", 1, "rosca", semilla, rosca_mm=ROSCA),
    "S6-TAL-G": _f("S6-TAL-G", "Tallo de rosca gruesa", 5, "rosca", tallo, rosca_mm=ROSCA, nota="Cantidad 5: tres del kit y dos del reto 5."),
    "S6-FLO-G": _f("S6-FLO-G", "Corona floral", 1, "rosca", lambda: _corona_floral(False), rosca_mm=ROSCA),
    "S6-COP-G": _f("S6-COP-G", "Copa de árbol", 1, "rosca", lambda: _corona_floral(True), rosca_mm=ROSCA),
    "S6-FRU-MAN": _f("S6-FRU-MAN", "Fruto mango", 1, "espiga", fruto_mango),
    "S6-FRU-NAR": _f("S6-FRU-NAR", "Fruto naranja", 1, "espiga", fruto_naranja, esfera=True),
    "S6-FRU-MANZ": _f("S6-FRU-MANZ", "Fruto manzana", 1, "espiga", fruto_manzana, esfera=True),
    "S6-PRI-AZU": _f("S6-PRI-AZU", "Prisma de agua", 1, "espiga", lambda: prisma(56, 48, 36), nota="Geometría. El azul translúcido pide PETG; este STL no lleva color."),
    "S6-PRI-AMA": _f("S6-PRI-AMA", "Prisma de sol", 1, "espiga", lambda: prisma(48, 44, 64), nota="Geometría. El amarillo translúcido pide PETG; este STL no lleva color."),
    "S6-SIL-ARB": _f("S6-SIL-ARB", "Pantalla opaca del árbol", 1, "espiga", lambda: _pantalla("arbol", False), nota="Espesor 8 mm. El recorte deja marco de más de 8 mm."),
    "S6-SIL-LUN": _f("S6-SIL-LUN", "Pantalla opaca de la luna", 1, "espiga", lambda: _pantalla("luna", True), nota="La pestaña entra en la ranura de noche."),
}

for _pieza in _probetas() + _variantes_resonador() + _pilares():
    _CATALOGO[_pieza["codigo"]] = _pieza


HIPOTESIS = [
    "Módulo de planta 31,80 mm y altura de bloque 19,20 mm, como en el Set 1. D1 sigue abierta.",
    "Cuerpo de Lúa: 72 × 64 × 40 mm. SETS no da el milímetro del tronco.",
    "Tetón de la probeta G: diámetro 9,40 mm y alto 4,50 mm. Tetón E: diámetro 6,40 mm y alto 3,20 mm.",
    "Holgura de la probeta, radial: 0,15, 0,20 y 0,25 mm, en la hembra.",
    "Rampa: H = 19,20 mm y L = 153,60 mm. Con H = 31,80 mm, L = 254,40 mm y no cabe en la cama de 220 mm.",
    "Viga: 186 × 48 × 18 mm. Diez módulos de 31,80 mm miden 318 mm.",
    "Resonadores: pared de 8 mm y cavidad distinta. La pared de 1,5 mm queda fuera.",
    "Rosca del jardín: paso 8 mm, diente 3,60 mm, tres vueltas, impresa en vertical.",
    "Masas: volumen de PLA a 1,24 g/cm³ como objetivo de 20, 40 y 60 g. Sin báscula.",
    "Esfera G: diámetro 45 mm. La de 38 mm, marcada por verificar para menores de 36 meses, no se genera.",
]


def carpeta_codigos() -> dict[str, list[str]]:
    placas = [
        "K-PLACA-INICIO",
        "K-PLACA-META",
        "K-PLACA-ESCUCHA",
        "K-PLACA-RECEPTOR",
        "K-PLACA-FRONTAL",
        "K-PLACA-NIVEL",
        "K-PLACA-JARDIN",
    ]
    pilares = [f"S3-PIL-{n}-G" for n in range(1, 7)]
    resonadores = [
        f"S2-RES-{color}-E-{letra}"
        for color in ("AZU", "AMA", "ROJ")
        for letra in ("A", "B", "C")
    ]
    probetas = [
        f"P1-{sexo}-{escala}-{marca}"
        for escala in ("G", "E")
        for marca in ("015", "020", "025")
        for sexo in ("MAC", "HEM")
    ]
    return {
        "P1-probeta-encaje": probetas,
        "S0-kit-lua": [
            "K-TRONCO-G",
            "K-LOMO-G",
            "K-PATA-DEL-G",
            "K-PATA-TRA-G",
            "K-COLA-G",
            "K-PATIN-G",
            "K-ZOCALO-G",
            *placas,
        ],
        "S2-estacion-sonido": [
            "K-ZOCALO-G",
            "K-PLACA-ESCUCHA",
            "S2-BAL-BASE-E",
            "S2-BAL-BRAZO-E",
            *resonadores,
            "S2-RAS-E",
            "S2-ESP-E",
            *pilares,
        ],
        "S3-laboratorio-rampas": [
            "S3-BIS-G",
            "S3-RAM-G",
            *pilares,
            "S3-FRI-G",
            "S3-CUR-PER-G",
            "S3-REC-G",
            "K-ZOCALO-G",
            "K-PLACA-RECEPTOR",
            "S3-ESF-LIS-G",
            "S3-ESF-RUG-G",
        ],
        "S4-maquina-soplo": [
            "S4-CAN-E",
            "S4-COD-E",
            "S4-ROT-JAULA-E",
            "S4-ROT-ASPAS-E",
            "S4-COM-LIG-E",
            "S4-COM-PES-E",
            "S4-MOL-JAULA-G",
            "S4-MOL-ASPAS-G",
            "K-ZOCALO-G",
            "K-PLACA-FRONTAL",
        ],
        "S5-puente-equilibrio": [
            "S5-FUL-G",
            "S5-VIG-G",
            "S5-MAS-20",
            "S5-MAS-40",
            "S5-MAS-60",
            "S5-PAS-G",
            *pilares,
            "K-ZOCALO-G",
            "K-PLACA-NIVEL",
        ],
        "S6-jardin": [
            "S6-TIE-G",
            "S6-SEM-G",
            "S6-TAL-G",
            "S6-FLO-G",
            "S6-COP-G",
            "S6-FRU-MAN",
            "S6-FRU-NAR",
            "S6-FRU-MANZ",
            "S6-PRI-AZU",
            "S6-PRI-AMA",
            "S6-SIL-ARB",
            "S6-SIL-LUN",
            "K-ZOCALO-G",
            "K-PLACA-JARDIN",
        ],
    }


TEXTOS = {
    "P1-probeta-encaje": {
        "titulo": "Probeta de encaje",
        "fase": "Fase 1 del plan de impresión",
        "es": "Se imprime antes que los sets. Cada pareja con el mismo sufijo se encaja a mano. No es un juguete y no entra en el kit del niño.",
        "gl": "Imprímese antes que os sets. Cada parella co mesmo sufixo encaixa á man. Non é un xoguete e non entra no kit do neno.",
        "pasos": [
            ("Imprime una pareja del mismo sufijo.", "Imprime unha parella do mesmo sufixo."),
            ("Baja el macho sobre el pozo, sin forzar.", "Baixa o macho sobre o pozo, sen forzar."),
            ("Anota qué holgura agarra en el PLA de Masque3D y cuál queda floja.", "Anota que folgura agarra no PLA de Masque3D e cal queda frouxa."),
        ],
        "orientacion": "No interviene Lúa.",
    },
    "S0-kit-lua": {
        "titulo": "Kit Lúa",
        "fase": "Fase 2 del plan de impresión",
        "es": "El tronco recibe las patas, el lomo y la cola. La placa se elige según el mundo y baja al zócalo.",
        "gl": "O tronco recibe as patas, o lombo e a cola. A placa elíxese segundo o mundo e baixa ao zócalo.",
        "pasos": [
            ("Encaja primero las patas traseras, de espiga redonda.", "Encaixa primeiro as patas traseiras, de espiga redonda."),
            ("Encaja después las delanteras. La llave no entra en el pozo redondo.", "Encaixa despois as dianteiras. A chave non entra no pozo redondo."),
            ("Coloca el lomo y la cola en la cara de atrás.", "Coloca o lombo e a cola na cara de atrás."),
            ("Elige una placa y bájala al zócalo hasta oír el snap.", "Elixe unha placa e báixaa ao zócalo ata oír o snap."),
        ],
        "orientacion": "La izquierda y la derecha son las de Lúa. En los sets 1, 5 y 6 el niño la mira desde atrás.",
    },
    "S2-estacion-sonido": {
        "titulo": "La Estación de Sonido y Eco",
        "fase": "Fase 7 del plan de impresión",
        "es": "Lúa mira de frente, con la placa Escucha. El niño pulsa el brazo sobre el resonador. La tableta no habla encima del sonido.",
        "gl": "Lúa mira de fronte, coa placa Escoita. O neno preme o brazo sobre o resonador. A tableta non fala enriba do son.",
        "pasos": [
            ("Baja la placa Escucha al zócalo.", "Baixa a placa Escoita ao zócalo."),
            ("Encaja el brazo en el banco. El eje es del propio brazo.", "Encaixa o brazo no banco. O eixe é do propio brazo."),
            ("Apoya un resonador en el rebaje. Prueba las tres variantes de cada color y quédate con la que suene distinta.", "Apoia un resonador no rebaixe. Proba as tres variantes de cada cor e queda coa que soe distinta."),
            ("El raspado se hace con la espátula sobre el raspador, después del golpe.", "O raspado faise coa espátula sobre o raspador, despois do golpe."),
        ],
        "orientacion": "Lúa está de frente al niño. No se le pide un giro en espejo.",
    },
    "S3-laboratorio-rampas": {
        "titulo": "El Laboratorio de Rampas y Gravedad",
        "fase": "Fase 5 del plan de impresión",
        "es": "La rampa se apoya en la torre. La esfera se detiene en la lengüeta, antes de Lúa.",
        "gl": "A rampa apóiase na torre. A esfera detense na lingüeta, antes de Lúa.",
        "pasos": [
            ("Coloca el bloque bisagra y baja el eje de la rampa a la boca en C.", "Coloca o bloque bisagra e baixa o eixe da rampa á boca en C."),
            ("Apila los pilares bajo el extremo alto. Dos pilares dejan la rampa baja; cuatro, la pronunciada.", "Apila os piares baixo o extremo alto. Dous piares deixan a rampa baixa; catro, a pronunciada."),
            ("Encadena el tramo de fricción y, si el reto lo pide, la curva peraltada.", "Encadea o tramo de fricción e, se o reto o pide, a curva peraltada."),
            ("Cierra con el receptor. La lengüeta mira hacia la rampa.", "Pecha co receptor. A lingüeta mira cara á rampa."),
            ("La placa Receptor baja al zócalo, detrás del receptor.", "A placa Receptor baixa ao zócalo, detrás do receptor."),
        ],
        "orientacion": "Lúa queda detrás del receptor y no recibe el golpe de la esfera.",
    },
    "S4-maquina-soplo": {
        "titulo": "La Máquina de Soplo y Viento",
        "fase": "Fase 8 del plan de impresión",
        "es": "Juego de soplo y de causa-efecto. No es un ejercicio de habla ni un tratamiento del velo.",
        "gl": "Xogo de sopro e de causa-efecto. Non é un exercicio de fala nin un tratamento do veo.",
        "pasos": [
            ("Baja la placa Frontal al zócalo. Lúa mira al niño. Las luces quedan apagadas.", "Baixa a placa Frontal ao zócalo. Lúa mira ao neno. As luces quedan apagadas."),
            ("Acopla el canal y, si el reto dobla el aire, el codo.", "Acopla a canle e, se o reto dobra o aire, o cóbado."),
            ("Mete el rotor en la jaula por el cojinete. Las aspas no salen de la jaula.", "Mete o rotor na gaiola polo rodamento. As aspas non saen da gaiola."),
            ("Clava la compuerta ligera o la pesada en el pozo del canal.", "Crava a comporta lixeira ou a pesada no pozo da canle."),
            ("Con menores de 3 años solo se usa el molinete, y sopla el adulto.", "Con menores de 3 años só se usa o muiño, e sopra o adulto."),
        ],
        "orientacion": "Lúa está de frente. Cada niño usa su embocadura, que no está en esta carpeta.",
    },
    "S5-puente-equilibrio": {
        "titulo": "El Puente de Equilibrio y Fuerza",
        "fase": "Fase 4 del plan de impresión",
        "es": "Lúa está junto a la viga, con la placa Nivel, nunca encima del balancín suelto. Solo sube al puente cuando los clips lo dejan fijo.",
        "gl": "Lúa está xunto á viga, coa placa Nivel, nunca enriba do balancín solto. Só sobe á ponte cando os clips a deixan fixa.",
        "pasos": [
            ("Apoya la viga en el lomo redondeado del fulcro.", "Apoia a viga no lombo redondeado do fulcro."),
            ("Coloca las masas en las posiciones numeradas. La de 60 g en la posición 1 se equilibra con la de 20 g en la posición 3.", "Coloca as masas nas posicións numeradas. A de 60 g na posición 1 equilibra coa de 20 g na posición 3."),
            ("Para el puente fijo, apoya la viga en pilares y bájalos clips en U por encima de la viga.", "Para a ponte fixa, apoia a viga en piares e baixa os clips en U por riba da viga."),
            ("La placa Nivel baja al zócalo, al lado de la viga.", "A placa Nivel baixa ao zócalo, ao lado da viga."),
        ],
        "orientacion": "El niño mira a Lúa desde atrás cuando se trabaja la izquierda y la derecha.",
    },
    "S6-jardin": {
        "titulo": "El Jardín del Sol, la Sombra y la Semilla",
        "fase": "Fase 6 del plan de impresión",
        "es": "La semilla entra en la tierra. Los tallos se enroscan. La flor y la copa comparten la misma rosca.",
        "gl": "A semente entra na terra. Os talos enróscanse. A flor e a copa comparten a mesma rosca.",
        "pasos": [
            ("Baja la placa Jardín al zócalo y ponlo junto a la base, del lado en que el niño ve a Lúa desde atrás.", "Baixa a placa Xardín ao zócalo e pono xunto á base, do lado en que o neno ve a Lúa desde atrás."),
            ("Mete la semilla en el alvéolo, a ras.", "Mete a semente no alvéolo, a ras."),
            ("Enrosca un tallo en la semilla y el siguiente tallo en el anterior.", "Enrosca un talo na semente e o seguinte talo no anterior."),
            ("Corona con la flor o con la copa. Los frutos bajan a los pozos de la copa.", "Coroa coa flor ou coa copa. Os froitos baixan aos pozos da copa."),
            ("El prisma azul va al pozo del agua y el amarillo al del sol. La linterna la sostiene el adulto.", "O prisma azul vai ao pozo da auga e o amarelo ao do sol. A lanterna sostena o adulto."),
            ("La pantalla de la luna entra en la ranura de noche.", "A pantalla da lúa entra na rañura de noite."),
        ],
        "orientacion": "El niño ve a Lúa desde atrás. La linterna no la usa el niño.",
    },
}
