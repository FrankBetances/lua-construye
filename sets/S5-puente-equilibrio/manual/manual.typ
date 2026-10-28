#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= El Puente de Equilibrio y Fuerza
Fase 4 del plan de impresión. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
Lúa está junto a la viga, con la placa Nivel, nunca encima del balancín suelto. Solo sube al puente cuando los clips lo dejan fijo.

#text(fill: rgb("#555555"))[Lúa está xunto á viga, coa placa Nivel, nunca enriba do balancín solto. Só sobe á ponte cando os clips a deixan fixa.]

El niño mira a Lúa desde atrás cuando se trabaja la izquierda y la derecha.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [S5-FUL-G], [Fulcro de arista redondeada], [1],
  [S5-VIG-G], [Viga balancín], [1],
  [S5-MAS-20], [Masa de referencia 20 g], [2],
  [S5-MAS-40], [Masa de referencia 40 g], [1],
  [S5-MAS-60], [Masa de referencia 60 g], [1],
  [S5-PAS-G], [Clip de puente], [4],
  [S3-PIL-1-G], [Pilar con marca táctil 1], [1],
  [S3-PIL-2-G], [Pilar con marca táctil 2], [1],
  [S3-PIL-3-G], [Pilar con marca táctil 3], [1],
  [S3-PIL-4-G], [Pilar con marca táctil 4], [1],
  [S3-PIL-5-G], [Pilar con marca táctil 5], [1],
  [S3-PIL-6-G], [Pilar con marca táctil 6], [1],
  [K-ZOCALO-G], [Zócalo universal], [1],
  [K-PLACA-NIVEL], [Placa Nivel], [1],
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
  [Apoya la viga en el lomo redondeado del fulcro.\ #text(size: 9pt, fill: rgb("#555555"))[Apoia a viga no lombo redondeado do fulcro.]],
  [Coloca las masas en las posiciones numeradas. La de 60 g en la posición 1 se equilibra con la de 20 g en la posición 3.\ #text(size: 9pt, fill: rgb("#555555"))[Coloca as masas nas posicións numeradas. A de 60 g na posición 1 equilibra coa de 20 g na posición 3.]],
  [Para el puente fijo, apoya la viga en pilares y bájalos clips en U por encima de la viga.\ #text(size: 9pt, fill: rgb("#555555"))[Para a ponte fixa, apoia a viga en piares e baixa os clips en U por riba da viga.]],
  [La placa Nivel baja al zócalo, al lado de la viga.\ #text(size: 9pt, fill: rgb("#555555"))[A placa Nivel baixa ao zócalo, ao lado da viga.]],
)

== Qué no va en esta carpeta
#list(
  [La viga de 10 × 31,80 mm mediría 318 mm y no cabe en la cama. Esta viga mide 186 mm.],
  [S5-PAS-G es un clip en U. Un pasador pequeño entraría en el cilindro de piezas pequeñas.],
  [20, 40 y 60 g son un objetivo a 1,24 g/cm³. No hay báscula en esta máquina y la tolerancia de ±0,5 g no está verificada.],
)

== Comprobación de diseño
14 de 14 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
