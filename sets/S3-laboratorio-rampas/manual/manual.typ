#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= El Laboratorio de Rampas y Gravedad
Fase 5 del plan de impresión. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
La rampa se apoya en la torre. La esfera se detiene en la lengüeta, antes de Lúa.

#text(fill: rgb("#555555"))[A rampa apóiase na torre. A esfera detense na lingüeta, antes de Lúa.]

Lúa queda detrás del receptor y no recibe el golpe de la esfera.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [S3-BIS-G], [Bloque bisagra], [1],
  [S3-RAM-G], [Rampa articulada], [1],
  [S3-PIL-1-G], [Pilar con marca táctil 1], [1],
  [S3-PIL-2-G], [Pilar con marca táctil 2], [1],
  [S3-PIL-3-G], [Pilar con marca táctil 3], [1],
  [S3-PIL-4-G], [Pilar con marca táctil 4], [1],
  [S3-PIL-5-G], [Pilar con marca táctil 5], [1],
  [S3-PIL-6-G], [Pilar con marca táctil 6], [1],
  [S3-FRI-G], [Tramo de fricción reversible], [1],
  [S3-CUR-PER-G], [Curva peraltada], [1],
  [S3-REC-G], [Receptor con lengüeta], [1],
  [K-ZOCALO-G], [Zócalo universal], [1],
  [K-PLACA-RECEPTOR], [Placa Receptor], [1],
  [S3-ESF-LIS-G], [Esfera lisa], [2],
  [S3-ESF-RUG-G], [Esfera rugosa], [2],
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
  [Coloca el bloque bisagra y baja el eje de la rampa a la boca en C.\ #text(size: 9pt, fill: rgb("#555555"))[Coloca o bloque bisagra e baixa o eixe da rampa á boca en C.]],
  [Apila los pilares bajo el extremo alto. Dos pilares dejan la rampa baja; cuatro, la pronunciada.\ #text(size: 9pt, fill: rgb("#555555"))[Apila os piares baixo o extremo alto. Dous piares deixan a rampa baixa; catro, a pronunciada.]],
  [Encadena el tramo de fricción y, si el reto lo pide, la curva peraltada.\ #text(size: 9pt, fill: rgb("#555555"))[Encadea o tramo de fricción e, se o reto o pide, a curva peraltada.]],
  [Cierra con el receptor. La lengüeta mira hacia la rampa.\ #text(size: 9pt, fill: rgb("#555555"))[Pecha co receptor. A lingüeta mira cara á rampa.]],
  [La placa Receptor baja al zócalo, detrás del receptor.\ #text(size: 9pt, fill: rgb("#555555"))[A placa Receptor baixa ao zócalo, detrás do receptor.]],
)

== Qué no va en esta carpeta
#list(
  [La esfera E de 38 mm no se genera: SETS la marca por verificar para menores de 36 meses y no llega a 44,5 mm.],
  [Con H = 31,80 mm la rampa mediría 254,40 mm y no cabe en la cama. H queda en 19,20 mm.],
)

== Comprobación de diseño
15 de 15 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
