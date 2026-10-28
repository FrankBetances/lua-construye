#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= Probeta de encaje
Fase 1 del plan de impresión. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
Se imprime antes que los sets. Cada pareja con el mismo sufijo se encaja a mano. No es un juguete y no entra en el kit del niño.

#text(fill: rgb("#555555"))[Imprímese antes que os sets. Cada parella co mesmo sufixo encaixa á man. Non é un xoguete e non entra no kit do neno.]

No interviene Lúa.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [P1-MAC-G-015], [Probeta macho G holgura 0.15 mm], [1],
  [P1-HEM-G-015], [Probeta hembra G holgura 0.15 mm], [1],
  [P1-MAC-G-020], [Probeta macho G holgura 0.20 mm], [1],
  [P1-HEM-G-020], [Probeta hembra G holgura 0.20 mm], [1],
  [P1-MAC-G-025], [Probeta macho G holgura 0.25 mm], [1],
  [P1-HEM-G-025], [Probeta hembra G holgura 0.25 mm], [1],
  [P1-MAC-E-015], [Probeta macho E holgura 0.15 mm], [1],
  [P1-HEM-E-015], [Probeta hembra E holgura 0.15 mm], [1],
  [P1-MAC-E-020], [Probeta macho E holgura 0.20 mm], [1],
  [P1-HEM-E-020], [Probeta hembra E holgura 0.20 mm], [1],
  [P1-MAC-E-025], [Probeta macho E holgura 0.25 mm], [1],
  [P1-HEM-E-025], [Probeta hembra E holgura 0.25 mm], [1],
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
  [Imprime una pareja del mismo sufijo.\ #text(size: 9pt, fill: rgb("#555555"))[Imprime unha parella do mesmo sufixo.]],
  [Baja el macho sobre el pozo, sin forzar.\ #text(size: 9pt, fill: rgb("#555555"))[Baixa o macho sobre o pozo, sen forzar.]],
  [Anota qué holgura agarra en el PLA de Masque3D y cuál queda floja.\ #text(size: 9pt, fill: rgb("#555555"))[Anota que folgura agarra no PLA de Masque3D e cal queda frouxa.]],
)

== Qué no va en esta carpeta
#list(
  [No es una pieza del juguete. Sirve para elegir la holgura en el PLA de Masque3D.],
)

== Comprobación de diseño
12 de 12 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
