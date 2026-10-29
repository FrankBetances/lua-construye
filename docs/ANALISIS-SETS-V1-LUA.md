# Sets v1 · análisis, compatibilidad con Lúa V5 y carpeta para masque3d · 29/10/2026

> Frank, 29/10: «analiza la versión 1 de los 9 sets, intenta que sean
> compatibles con lua, revisa el modelo que está en el repositorio lua firmware,
> cuando acabes genera una carpeta con todos los stl para enviar a imprimir a
> masque3d». Preguntado qué son los sets: «ahí están todos» (`sets/` de `main`).
> Preguntado si se puede tocar la base de Lúa V5: «Sí, dos enchufes».

**Estado: dibujado y medido en el fichero. NO PROBADO: no se ha impreso nada.**

## 0. Lo que NO se cumple o no está comprobado, primero

1. **Sets 8 a 11 (30/10, orden de Frank: van todos): van escalados a la cama**
   (60 % y 33 %, `agents/paquete_escenas.py`); policía en verde, bomberos,
   hospital y trenes con un fallo de medida cada uno (ver el LEEME). Lo de
   abajo sigue valiendo para jugar con ellos:
   Cada uno es un único STL decorativo de 318 × 191 a 491 × 582 mm, con 1 a 12
   cuerpos sueltos y una gata de juguete fundida al suelo que no es Lúa V5. No
   caben en la cama y no tienen fuente (solo el STL), así que no se pueden
   corregir: hay que diseñarlos como piezas. Qué piezas lleva cada uno no está
   en `docs/SETS.md`; lo decide Frank.
2. **Las uniones de los sets no tienen medida de retención.** Colas de milano,
   nervios de snap y espigas siguen como en la v1, sin bloqueo medido. Solo
   están medidos el patín de Lúa (dos clics, en lua-firmware) y la rosca del
   jardín (que no sale tirando y sí desenroscando).
3. **Set 2: el banco del martillo no puede sostener un resonador.** Ya en la
   v1: el resonador (78 × 64 mm) no cabía en el rebaje de 34 × 34 y chocaba con
   las carrilleras del banco. He cambiado la espiga por un hueco (para que el
   resonador se imprima plano), pero dónde se apoya es una decisión de juego,
   no de impresión, y está sin tomar.
4. **Set 4: las jaulas van abiertas por arriba** y el eje de las aspas se apoya
   en dos cunas en U, sin nada que lo sujete arriba.
5. **El marcador del lomo (K-LOMO-G) desaparece con el cuerpo de la v1.** Lúa
   V5 no lleva cara para un marcador de rumbo: D2 sigue abierta y, hasta
   entonces, el adulto confirma con un toque (regla 1 del contrato).
6. **La placa de identidad queda tapada en parte por los brazos de Lúa** vista
   desde arriba: 645 de 4 032 mm² (lo mide `check_lua_camino`). Con la tableta
   en diagonal puede no tapar; no está probado.
7. **Sin probetas.** Si una holgura sale mal, se ve en la impresión completa.
   La carpeta `P1-probeta-encaje` va en el paquete; imprimirla antes lo decide
   Frank.
8. **17,8 kg de PLA con relleno al 100 %** para 104 piezas (cota, no medida).

## 1. Qué se encontró en la v1 (medido)

| Qué | Medido con | v1 | Ahora |
| :--- | :--- | :--- | :--- |
| El cuerpo de Lúa | comparación con `lua-firmware/cad/lua-v5` | el Set 0 dibujaba otro cuerpo (tronco 72 × 64, lomo, 4 patas, cola), incompatible con la Lúa V5 (base Ø104 × 96 + patas) | el cuerpo es el de Lúa V5; el de la v1 no va a la carpeta (sus funciones se conservan) |
| El patín del Set 1 | geometría | no se enganchaba a nada; su carril recto de 50 mm no pasa por la curva de r 63,6 (flecha 4,9 mm con 0,4 de holgura) | patín de Lúa V5: dos clics en la base y dos pivotes redondos (pasan por curva y T) |
| Lúa sobre el camino | `agents/check_lua_camino.py` | la base de Lúa pisaba las fichas de comando (sobresalen 4,4 mm): 6 808 mm³ de choque | 0 mm³ en recta, curva y T: el patín levanta la base 13,2 mm |
| El zócalo | geometría | una baldosa con bolsillo: nada sujetaba ni orientaba a Lúa, y la placa quedaba debajo de ella | cuna con la huella de Lúa (abierta por delante para salir deslizando); al revés, las patas chocan (1 228 mm³); placa en una franja aparte |
| Voladizos sin sostén | `check-v3-piezas.py` de lua-firmware | 70 de 114 STL (contando las copias que se repiten entre carpetas) | 0: el sostén va dibujado en el STL (`sosten.py`, Blender) |
| Paredes < 3,2 mm | ídem | 27 de 114 STL (7 son el mismo zócalo, con un filo de 0,5): iconos de 2,4, filos de 0,02 en fulcro, prismas, pantalla, jaula, curva peraltada… | 0 fuera de los dientes de rosca |
| La rosca del jardín | cuerpos del STL | 36 tacos cuadrados que no tocaban el núcleo: 37 cuerpos sueltos en la semilla, 38 en el tallo | hélice continua, flancos a 51°, diente de 3 × 8 mm; no sale tirando (200 mm³ de choque a 1 mm), sí desenroscando |
| Aspas del rotor y del molinete | cuerpos del STL | las 4 aspas sueltas del eje | nacen dentro del eje |
| Rotor y molinete en su jaula | choque montado | la jaula era una caja cerrada (las aspas no entraban) con el eje en Y, cruzado con el de las aspas (X) | jaula abierta con cunas en X: montado y girando, 0 mm³ |
| Resonadores | cuerpos del STL | en 5 de 9, la garganta no llegaba a la cavidad: hueco cerrado, no resuena | cavidad con techo a 45° que baja a la garganta |
| Esferas, codo, espátula | huella en la cama | apoyaban en un punto o en una línea | espátula plana; esferas y codo, sobre su sostén |

## 2. Lo que se ha cambiado

En **lua-firmware** (rama `claude/jolly-fermi-a7tpah`): el patín
(`lua_v5_uniones.PATIN`, `lua_v5_cuerpo.patin`), dos enchufes de clic en la
cara de abajo de la base, la medida del patín en `check-v5-montaje` y el
paquete V5 rehecho. Es la decisión 27 de su `CLAUDE.md`.

En **lua-construye**:

- `lua-v5/`: copia de la interfaz y del patín de Lúa V5. `agents/lua_v5.py` la
  trae (`make lua-v5`) y la compara (`make check`).
- `sets/S1-camino/cad/geometria.py`: zócalo nuevo con cuna, patín copiado de
  Lúa V5, iconos engrosados 0,4 mm por lado.
- `agents/lote_geometria.py`: rosca, resonadores, aspas, jaulas, curva
  peraltada, fulcro, prismas, pantalla, espátula, manzana y copa (cada cambio
  lleva su comentario con fecha y el porqué). El Set 0 ya no lleva el cuerpo de
  la v1.
- `agents/check_lua_camino.py`: Lúa V5 sobre la recta, la curva, la T y el
  zócalo.
- `agents/paquete_masque3d.py`: la carpeta para masque3d.
- `agents/render_lua_camino.py`: `docs/lua-v5-camino.png` y `-lado.png`.

## 3. Comprobado con

```bash
make check FIRMWARE=../lua-firmware                       # copia de lua-v5 y Lúa sobre el camino
python3 -m agents.check_lua_camino --romper sin_patin     # rojo: Lúa pisa las fichas
python3 -m agents.check_lua_camino --romper al_reves      # rojo: la llave del zócalo
python3 -m agents.paquete_masque3d --firmware ../lua-firmware   # 83 piezas, 0 en rojo
```

y en lua-firmware `make check-v5` (12 uniones, rojo con
`LUA_V5_ROMPER=sin_unas`) y `make check` en verde **sin** `VALERIA=` ni `VIA=`
(esos gates se saltaron; Lúa mini no se midió porque no tiene STL generados).

La medida del paquete se ha visto en rojo de verdad: dio 13 piezas en rojo
(resonadores, rosca) antes de los últimos arreglos.

La auditoría propia de lua-construye (`pruebas/auditoria.json`) es un
criterio de diseño de EN 71-1 (cilindro de piezas pequeñas, cama, núcleo); no
es un ensayo y no mide voladizos ni paredes.

## 4. Siguiente paso recomendado

1. Frank decide si imprime antes `P1-probeta-encaje` (unas horas y 1,3 kg) o
   todo de una vez.
2. Decidir dónde se apoya el resonador en el banco del Set 2.
3. Diseñar los sets 8 a 11 como piezas, con su lista en `docs/SETS.md`.
4. Una medida de retención para las uniones de los sets, como la de lua-firmware.
