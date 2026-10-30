# Construye con Lúa · sets v1 · STL sin soportes para masque3d · 30/10/2026 · NO PROBADO

**Nada de esto se ha impreso.** Cada STL va **limpio, sin soportes dibujados dentro del fichero** (por indicación de Masque3D del 30/10/2026 para no encarecer la impresión), cerrado (2-manifold en `float32`), apoyado en `z = 0`, en milímetros sin escalar y con paredes de 3,2 mm o más fuera de los dientes de rosca. **El taller aplica los soportes directamente en el laminador** donde hagan falta. Eso dice que se puede laminar e imprimir según el fichero; **no dice que encaje, que gire ni que aguante.**

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
6. **Cantidad de PLA: unos 17,8 kg en los sets 0 a 6 (más 2,5 kg en las 4 maquetas S8–S11) con relleno al 100 %.**
   Es una cota superior maciza, no el peso real: con relleno del 30–40 % pesa bastante menos.
7. **Sets 8 a 11 (policía, bomberos, hospital, trenes): van ESCALADOS** a la
   cama (policía, bomberos y hospital al 60 %; trenes al 33 %), en una pieza
   cada uno y **sin soportes modelados** (el taller los añade en el laminador).
   Son maquetas decorativas: no casan con Lúa V5.

## Cómo imprimir en Masque3D

| Parámetro | Indicación para el taller |
| :--- | :--- |
| **Material** | PLA |
| **Orientación** | Cada STL va ya en su postura de cama (`z = 0`), en mm, sin escalar. |
| **Soportes (Laminador)** | **Ningún STL lleva soporte dibujado dentro (`sosten_cm3 = 0.0`).** El taller genera los soportes necesarios en su laminador (carriles inferiores de `K-PATIN-G`, ejes de `S2-BAL-BRAZO-E`, `S3-RAM-G`, `S4-ROT-ASPAS-E` y `S4-MOL-ASPAS-G`, esferas `S3-ESF-*`, codo `S4-COD-E`, frutos `S6-FRU-*`, pétalos de `S6-FLO-G` y maquetas `S8..S11`). |
| **Precaución en roscas (Set 6)** | **Bloquear soportes dentro de las roscas** de `S6-SEM-G`, `S6-TAL-G`, `S6-FLO-G` y `S6-COP-G` (sus flancos a 51° se imprimen en vertical sin soporte; un soporte dentro del filete impide enroscarlas). |
| **Perímetros** | 6 como mínimo |
| **Relleno** | 100 % en piezas pequeñas (fichas, placas, patín, aspas, pasadores); 30–40 % en baldosas, zócalos y bloques grandes |
| **Cama** | Todas caben en 200 × 200 × 200 mm |

## Qué hay en la carpeta (87 STL · 0 soportes modelados)

`piezas.csv` lista cada STL con su carpeta, **cuántas copias imprimir**, en qué
sets se usa, sus gramos a relleno 100 % (`sosten_cm3 = 0.0` en todas) y el estado.

| Carpeta | Qué es |
| :--- | :--- |
| `00-comun` | Lo que comparten los sets: el zócalo con la cuna de Lúa V5 (**2 copias**: INICIO y META del Set 1), el patín de Lúa, las placas de identidad y los seis pilares |
| `P1-probeta-encaje` | Probetas de holgura (6 parejas G y 6 parejas E). No son juguete |
| `S1-camino` | Baldosas, curvas, T, fichas de comando y placas de destino |
| `S2-estacion-sonido` | Resonadores (9 variantes), banco y brazo del martillo, raspador, espátula |
| `S3-laboratorio-rampas` | Rampa, bisagra, tramo de fricción, curva peraltada, receptor y esferas de Ø45 |
| `S4-maquina-soplo` | Canal, codo, rotor y molinete (jaula + aspas), compuertas |
| `S5-puente-equilibrio` | Fulcro, viga, masas de 20, 40 y 60 g (objetivo volumétrico), clip |
| `S6-jardin` | Tierra, semilla, tallos (5), flor, copa, frutos, prismas y pantallas |
| `S8-policia` .. `S11-trenes` | Maquetas de una pieza escaladas a 190 mm de cama (60 % en S8–S10; 33 % en S11), limpias sin soporte modelado |

Cómo se generó y qué se cambió respecto a la v1: `docs/ANALISIS-SETS-V1-LUA.md`
del repositorio `lua-construye`.
