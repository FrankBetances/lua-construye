"""Lúa V5 sobre el Set 1 y en el zócalo: la medida que faltaba (29/10/2026).

    python3 -m agents.check_lua_camino --firmware ../lua-firmware
    python3 -m agents.check_lua_camino --firmware ../lua-firmware --romper sin_patin
    python3 -m agents.check_lua_camino --firmware ../lua-firmware --romper al_reves

Por qué existe. La v1 de los sets se auditaba pieza a pieza y daba «apta», y
con la Lúa que se imprime (la V5 de lua-firmware) no se podía jugar: el patín no
se enganchaba a nada, su carril recto de 50 mm no pasaba por la curva de r 63,6,
la base de Lúa (Ø104) pisaba las fichas de comando, que sobresalen 4,4 mm, y el
zócalo no tenía nada que la sujetara ni la orientara. Ninguna medida montaba a
Lúa encima de una baldosa. Esta sí.

Lúa son los STL de montaje de lua-firmware (cad/lua-v5/montaje): base, vientre,
pecho, brazos, cola y el patín. La cabeza queda muy por encima y no se mira.
Da ROJO si:

  1 · RECTA      deslizando a Lúa por la baldosa rugosa con una ficha puesta,
                 Lúa pisa la baldosa o la ficha
  2 · CURVA      con los dos pivotes en el eje de la ranura curva, Lúa pisa la
                 baldosa o la ficha de la curva
  3 · TE         girando en la T (un pivote en cada brazo), Lúa pisa la baldosa
  4 · ZÓCALO     Lúa, con patín y sin él, no entra en la cuna mirando al camino,
                 o entra al revés (la llave son las patas delanteras), o no sale
                 deslizando hacia la primera baldosa

Y AVISA (no da rojo) de cuánto tapa Lúa la placa de identidad vista desde arriba.

Con --romper sin_patin (Lúa sin patín sobre la recta) y --romper al_reves (la
llave del zócalo) da rojo: es lo que la hace valer (CLAUDE.md 9.6 de
lua-firmware). Sin el vecino, se salta y lo dice.

LO QUE NO DICE: que Lúa deslice bien impresa, ni que la quilla no roce, ni que
el niño la empuje sin volcarla. Mide el fichero. NO PROBADO.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from manifold3d import Manifold

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "sets" / "S1-camino" / "cad"))

import geometria as G  # noqa: E402
import parametros as P  # noqa: E402

from agents.lua_v5 import interfaz  # noqa: E402
from agents.malla_io import leer_stl  # noqa: E402

LIBRE = 0.05  # mm³
SEG = 48
CUERPO = ("base", "vientre", "pecho", "brazo_izq", "brazo_der", "cola")


def _colocar(s: Manifold, x: float, y: float, rumbo: float, z: float) -> Manifold:
    """Del marco de Lúa (frente −Y) a la baldosa: el frente mira al rumbo (grados, 0 = +X)."""
    return s.rotate((0.0, 0.0, rumbo + 90.0)).translate((x, y, z))


def _lua(fw: Path, con_patin: bool) -> Manifold:
    piezas = [leer_stl(fw / "cad" / "lua-v5" / "montaje" / f"{n}.stl") for n in CUERPO]
    if con_patin:
        piezas.append(leer_stl(RAIZ / "lua-v5" / "patin-montaje.stl"))
    s = piezas[0]
    for p in piezas[1:]:
        s = s + p
    return s


def _ficha(x0: float, y0: float) -> Manifold:
    f = G.ficha("avanza", SEG)
    return f.translate((x0 + P.HOLGURA_MM, y0 + P.HOLGURA_MM, P.ALTURA_BASE_MM - P.POZO_PROF_MM))


def _choque(a: Manifold, b: Manifold) -> float:
    return (a ^ b).volume()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--firmware", default=str(RAIZ.parent / "lua-firmware"))
    ap.add_argument("--romper", choices=["sin_patin", "al_reves"], default=None)
    a = ap.parse_args(argv)
    fw = Path(a.firmware)
    if not (fw / "cad" / "lua-v5" / "montaje" / "base.stl").exists():
        print(f"· check_lua_camino: no hay lua-firmware en {fw}: Lúa sobre el camino NO se mide")
        return 0
    L = interfaz()
    z_patin = -L["patin"]["z_baldosa"]
    con = _lua(fw, True)
    sin = _lua(fw, False)
    lua = sin if a.romper == "sin_patin" else con
    alto = P.ALTURA_BASE_MM + (0.0 if a.romper == "sin_patin" else z_patin)
    w = P.BALDOSA_MM
    c = w / 2
    fallos = []
    print(f"· Lúa V5 ({fw}) · base a {alto - P.ALTURA_BASE_MM:.1f} mm sobre la baldosa"
          + (f" · ROMPER={a.romper}" if a.romper else ""))

    # 1 · recta rugosa con una ficha puesta en su pozo
    print("  1 recta rugosa + ficha")
    suelo = G.baldosa_recta(True, SEG) + _ficha(*P.POZO_RECTA_XY)
    peor = max((_choque(_colocar(lua, x, c, 0.0, alto), suelo), x) for x in np.arange(0.0, w + 0.1, 4.0))
    ok = peor[0] <= LIBRE
    print(f"      {'✓' if ok else '✗'} peor choque {peor[0]:.2f} mm³ (Lúa en x {peor[1]:.0f})")
    if not ok:
        fallos.append(f"recta: Lúa pisa la baldosa o la ficha {peor[0]:.2f} mm³")

    # 2 · curva: los dos pivotes sobre la circunferencia de r W/2 centrada en (0, W)
    print("  2 curva + ficha")
    suelo = G.baldosa_curva(SEG) + _ficha(*P.POZO_CURVA_XY)
    r = w / 2
    dt = 2 * math.asin(L["patin"]["y_pivote"] / r)
    peor = (0.0, 0.0)
    for t in np.linspace(-math.pi / 2 + dt / 2, -dt / 2, 12):
        p1 = np.array([r * math.cos(t - dt / 2), w + r * math.sin(t - dt / 2)])
        p2 = np.array([r * math.cos(t + dt / 2), w + r * math.sin(t + dt / 2)])
        m = (p1 + p2) / 2
        rumbo = math.degrees(math.atan2(*(p2 - p1)[::-1]))
        peor = max(peor, (_choque(_colocar(lua, m[0], m[1], rumbo, alto), suelo), math.degrees(t)))
    ok = peor[0] <= LIBRE
    print(f"      {'✓' if ok else '✗'} peor choque {peor[0]:.2f} mm³ (en {peor[1]:.0f}°)")
    if not ok:
        fallos.append(f"curva: Lúa pisa la baldosa o la ficha {peor[0]:.2f} mm³")

    # 3 · te: un pivote en la ranura recta, el otro en la rama (+Y)
    print("  3 te, girando")
    suelo = G.baldosa_te(SEG) + _ficha(*P.POZO_TE_XY)
    d = 2 * L["patin"]["y_pivote"]
    peor = (0.0, 0.0)
    for ax in np.linspace(d, 0.0, 9):
        by = math.sqrt(max(d * d - ax * ax, 0.0))
        p1, p2 = np.array([c - ax, c]), np.array([c, c + by])
        m = (p1 + p2) / 2
        rumbo = math.degrees(math.atan2(*(p2 - p1)[::-1]))
        peor = max(peor, (_choque(_colocar(lua, m[0], m[1], rumbo, alto), suelo), ax))
    ok = peor[0] <= LIBRE
    print(f"      {'✓' if ok else '✗'} peor choque {peor[0]:.2f} mm³")
    if not ok:
        fallos.append(f"te: Lúa pisa la baldosa {peor[0]:.2f} mm³")

    # 4 · zócalo
    print("  4 zócalo")
    z = G.zocalo(SEG)
    for nombre, s, h in (("con patín", con, P.ALTURA_BASE_MM + z_patin), ("sin patín", sin, P.ALTURA_BASE_MM)):
        rumbo = 180.0 if a.romper == "al_reves" else 0.0
        v = _choque(_colocar(s, c, c, rumbo, h), z)
        ok = v <= LIBRE
        print(f"      {'✓' if ok else '✗'} {nombre}, mirando al camino: {v:.2f} mm³")
        if not ok:
            fallos.append(f"zócalo, {nombre}: Lúa no entra en la cuna ({v:.2f} mm³)")
        v = _choque(_colocar(s, c, c, 180.0, h), z)
        ok = v > 10.0
        print(f"      {'✓' if ok else '✗'} {nombre}, al revés: las patas chocan {v:.0f} mm³ (la llave)")
        if not ok:
            fallos.append(f"zócalo, {nombre}: Lúa entra al revés")
    peor = max((_choque(_colocar(con, x, c, 0.0, P.ALTURA_BASE_MM + z_patin), z), x)
               for x in np.arange(c, w + 60.0, 4.0))
    ok = peor[0] <= LIBRE
    print(f"      {'✓' if ok else '✗'} sale deslizando hacia la primera baldosa: peor {peor[0]:.2f} mm³")
    if not ok:
        fallos.append(f"zócalo: Lúa no sale deslizando ({peor[0]:.2f} mm³ en x {peor[1]:.0f})")
    # aviso: cuánto tapa Lúa la placa, vista desde arriba
    x0, y0 = P.BOLSA_X0_MM, P.BOLSA_ZOCALO_Y0_MM
    placa = Manifold.cube((P.BOLSA_ANCHO_MM, P.BOLSA_FONDO_MM, 400.0)).translate((x0, y0, -100.0))
    sombra = _colocar(con, c, c, 0.0, 0.0).project()
    tapa = (Manifold.extrude(sombra, 400.0).translate((0.0, 0.0, -100.0)) ^ placa).volume() / 400.0
    print(f"      · aviso: vista desde arriba, Lúa (sin cabeza) tapa {tapa:.0f} de "
          f"{P.BOLSA_ANCHO_MM * P.BOLSA_FONDO_MM:.0f} mm² de la placa (los brazos)")

    if fallos:
        print(f"\n✗ {len(fallos)} fallo(s) con Lúa V5 sobre el Set 1:")
        for f in fallos:
            print(f"  · {f}")
        return 1
    print("\n✓ Lúa V5 corre por la recta, la curva y la T sin pisar baldosa ni fichas, y el zócalo la")
    print("  recibe solo mirando al camino. En el fichero: NO PROBADO impreso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
