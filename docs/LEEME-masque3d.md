# Construye con Lúa · sets v1 · STL para masque3d · 29/10/2026 · NO PROBADO

**Nada de esto se ha impreso.** Cada STL pasa la medida de pieza de lua-firmware
(cerrada, apoyada en la cama, nada colgando a más de 45° sin su sostén, paredes
de 3,2 mm o más fuera de los dientes de rosca). Eso dice que se puede imprimir
según el fichero. **No dice que encaje, que gire ni que aguante.**

## Antes de imprimir: lo que falta o no está comprobado

1. **Sin probetas, un fallo de holgura aparece en la impresión completa.** La
   carpeta `P1-probeta-encaje` existe para evitarlo; imprimirla primero lo
   decide Frank.
2. **Las uniones de los sets (colas de milano, nervios de snap, espigas) no
   tienen medida de retención.** Solo la tienen el patín de Lúa (dos clics) y
   la rosca del jardín. El resto puede quedar flojo o duro.
3. **Set 2: el banco del martillo y los resonadores no casan.** El resonador
   (78 × 64 mm) no cabe en el banco: choca con sus dos carrilleras. Falta
   decidir dónde se apoya. Los resonadores se imprimen bien solos; el tono no
   se ha medido.
4. **Set 4: la jaula del rotor y la del molinete van abiertas por arriba.** El
   eje de las aspas se apoya en dos cunas en U, sin nada que lo sujete por
   arriba. La embocadura (S4-BOQ) no va: no es PLA por FDM.
5. **Lúa V5 no va aquí.** El cuerpo (el cubo con su fondo de 108 × 108) se
   imprime con su propio paquete, `lua-firmware/entrega/lua-v5/lua-v5-imprimir.zip`.
   No hay que cambiarle nada: el patín de esta carpeta es una **bandeja** donde
   apoya el fondo del cubo. Sujeta a Lúa por los lados; si se levanta a Lúa,
   el patín se queda en la ranura.
6. **Cantidad de PLA: unos 17,8 kg con el relleno al 100 %.** Es una cota,
   no una medida: con el relleno de abajo pesa bastante menos.
7. **Sets 8 a 11 (policía, bomberos, hospital, trenes): van ESCALADOS** a la
   cama (policía, bomberos y hospital al 60 %; trenes al 33 %), en una pieza
   cada uno y con su sostén dibujado. Son maquetas: no casan con Lúa V5. Medida:
   policía en verde; **bomberos** con un voladizo de 152 mm² sin sostén,
   **hospital** con pared fina y **trenes** con sostén pegado a la pieza. En
   esas tres el taller puede **añadir soporte automático** donde su programa lo
   pida (excepción a la regla de abajo).

## Cómo imprimir

| | |
| :--- | :--- |
| Material | PLA |
| Orientación | Cada STL va ya en su postura de cama, en mm, sin escalar. No girarlas. |
| Sostén | **Ya va dibujado dentro del STL** donde hace falta (tabiques finos que se quitan con la mano). **No añadir soportes automáticos.** Las roscas no llevan ninguno dentro. |
| Perímetros | 6 como mínimo |
| Relleno | 100 % en piezas pequeñas (fichas, placas, patín, aspas, pasadores); 30–40 % en baldosas, zócalos y bloques grandes |
| Cama | Todas caben en 200 × 200 × 200 mm |

## Qué hay

`piezas.csv` lista cada STL con su carpeta, **cuántas copias imprimir**, en qué
sets se usa, sus gramos a relleno 100 % y el resultado de la medida.

| Carpeta | Qué es |
| :--- | :--- |
| `00-comun` | Lo que comparten los sets: el zócalo con la cuna de Lúa V5 (**2 copias**: INICIO y META del Set 1), el patín de Lúa, las placas de identidad y los seis pilares |
| `P1-probeta-encaje` | Probetas de holgura. No son juguete |
| `S1-camino` | Baldosas, curvas, T, fichas de comando y placas de destino |
| `S2-estacion-sonido` | Resonadores (9 variantes), banco y brazo del martillo, raspador, espátula |
| `S3-laboratorio-rampas` | Rampa, bisagra, tramo de fricción, curva peraltada, receptor y dos esferas de Ø45 |
| `S4-maquina-soplo` | Canal, codo, rotor y molinete (jaula + aspas), compuertas |
| `S5-puente-equilibrio` | Fulcro, viga, masas de 20, 40 y 60 g (objetivo, sin pesar), clip |
| `S6-jardin` | Tierra, semilla, tallos (5), flor, copa, frutos, prismas y pantallas |

Cómo se generó y qué se cambió respecto a la v1: `docs/ANALISIS-SETS-V1-LUA.md`
del repositorio lua-construye.
