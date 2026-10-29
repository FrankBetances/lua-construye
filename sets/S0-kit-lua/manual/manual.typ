#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= Kit Lúa
Fase 2 del plan de impresión. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
El cuerpo de Lúa es el de Lúa V5 y se imprime con su propio paquete. Aquí van el zócalo, el patín y las placas. La placa se elige según el mundo y baja al zócalo.

#text(fill: rgb("#555555"))[O corpo de Lúa é o de Lúa V5 e imprímese co seu propio paquete. Aquí van o zócalo, o patín e as placas. A placa elíxese segundo o mundo e baixa ao zócalo.]

La izquierda y la derecha son las de Lúa. En los sets 1, 5 y 6 el niño la mira desde atrás.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [K-PATIN-G], [Patín guía], [1],
  [K-ZOCALO-G], [Zócalo universal], [1],
  [K-PLACA-INICIO], [Placa Inicio], [1],
  [K-PLACA-META], [Placa Meta], [1],
  [K-PLACA-ESCUCHA], [Placa Escucha], [1],
  [K-PLACA-RECEPTOR], [Placa Receptor], [1],
  [K-PLACA-FRONTAL], [Placa Frontal], [1],
  [K-PLACA-NIVEL], [Placa Nivel], [1],
  [K-PLACA-JARDIN], [Placa Jardín], [1],
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
  [Para el Set 1, engancha el patín bajo la base de Lúa: dos clics.\ #text(size: 9pt, fill: rgb("#555555"))[Para o Set 1, engancha o patín baixo a base de Lúa: dous clics.]],
  [Pon a Lúa en la cuna del zócalo mirando hacia el camino. Al revés, sus patas no caben.\ #text(size: 9pt, fill: rgb("#555555"))[Pon a Lúa no berce do zócalo mirando cara ao camiño. Ao revés, as súas patas non caben.]],
  [Elige una placa y bájala al zócalo hasta oír el snap.\ #text(size: 9pt, fill: rgb("#555555"))[Elixe unha placa e báixaa ao zócalo ata oír o snap.]],
  [Fuera del Set 1, quita el patín tirando fuerte y recto: Lúa se sostiene sobre su base.\ #text(size: 9pt, fill: rgb("#555555"))[Fóra do Set 1, quita o patín tirando forte e recto: Lúa sostense sobre a súa base.]],
)

== Qué no va en esta carpeta
#list(
  [K-CUELLO no se imprime: es la unidad sellada del fabricante y queda fuera del alcance del niño.],
  [K-TRONCO-G, K-LOMO-G, K-PATA-DEL-G, K-PATA-TRA-G y K-COLA-G ya no se imprimen: el cuerpo de Lúa es el de Lúa V5 (lua-firmware), con su propio paquete.],
  [Sin K-LOMO-G, Lúa V5 no lleva marcador de rumbo en el lomo: D2 sigue abierta y el adulto confirma con un toque.],
)

== Comprobación de diseño
9 de 9 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
