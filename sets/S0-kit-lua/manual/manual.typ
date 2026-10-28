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
El tronco recibe las patas, el lomo y la cola. La placa se elige según el mundo y baja al zócalo.

#text(fill: rgb("#555555"))[O tronco recibe as patas, o lombo e a cola. A placa elíxese segundo o mundo e baixa ao zócalo.]

La izquierda y la derecha son las de Lúa. En los sets 1, 5 y 6 el niño la mira desde atrás.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [K-TRONCO-G], [Tronco con llave de cuello], [1],
  [K-LOMO-G], [Bloque dorsal], [1],
  [K-PATA-DEL-G], [Pata delantera con llave], [2],
  [K-PATA-TRA-G], [Pata trasera], [2],
  [K-COLA-G], [Cola], [1],
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
  [Encaja primero las patas traseras, de espiga redonda.\ #text(size: 9pt, fill: rgb("#555555"))[Encaixa primeiro as patas traseiras, de espiga redonda.]],
  [Encaja después las delanteras. La llave no entra en el pozo redondo.\ #text(size: 9pt, fill: rgb("#555555"))[Encaixa despois as dianteiras. A chave non entra no pozo redondo.]],
  [Coloca el lomo y la cola en la cara de atrás.\ #text(size: 9pt, fill: rgb("#555555"))[Coloca o lombo e a cola na cara de atrás.]],
  [Elige una placa y bájala al zócalo hasta oír el snap.\ #text(size: 9pt, fill: rgb("#555555"))[Elixe unha placa e báixaa ao zócalo ata oír o snap.]],
)

== Qué no va en esta carpeta
#list(
  [K-CUELLO no se imprime: es la unidad sellada del fabricante y queda fuera del alcance del niño.],
)

== Comprobación de diseño
14 de 14 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
