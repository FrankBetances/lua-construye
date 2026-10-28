#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= La Estación de Sonido y Eco
Fase 7 del plan de impresión. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
Lúa mira de frente, con la placa Escucha. El niño pulsa el brazo sobre el resonador. La tableta no habla encima del sonido.

#text(fill: rgb("#555555"))[Lúa mira de fronte, coa placa Escoita. O neno preme o brazo sobre o resonador. A tableta non fala enriba do son.]

Lúa está de frente al niño. No se le pide un giro en espejo.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [K-ZOCALO-G], [Zócalo universal], [1],
  [K-PLACA-ESCUCHA], [Placa Escucha], [1],
  [S2-BAL-BASE-E], [Banco del martillo], [1],
  [S2-BAL-BRAZO-E], [Brazo del martillo con eje], [1],
  [S2-RES-AZU-E-A], [Resonador grave variante A], [1],
  [S2-RES-AZU-E-B], [Resonador grave variante B], [1],
  [S2-RES-AZU-E-C], [Resonador grave variante C], [1],
  [S2-RES-AMA-E-A], [Resonador medio variante A], [1],
  [S2-RES-AMA-E-B], [Resonador medio variante B], [1],
  [S2-RES-AMA-E-C], [Resonador medio variante C], [1],
  [S2-RES-ROJ-E-A], [Resonador agudo variante A], [1],
  [S2-RES-ROJ-E-B], [Resonador agudo variante B], [1],
  [S2-RES-ROJ-E-C], [Resonador agudo variante C], [1],
  [S2-RAS-E], [Raspador estriado], [2],
  [S2-ESP-E], [Espátula sin filo], [1],
  [S3-PIL-1-G], [Pilar con marca táctil 1], [1],
  [S3-PIL-2-G], [Pilar con marca táctil 2], [1],
  [S3-PIL-3-G], [Pilar con marca táctil 3], [1],
  [S3-PIL-4-G], [Pilar con marca táctil 4], [1],
  [S3-PIL-5-G], [Pilar con marca táctil 5], [1],
  [S3-PIL-6-G], [Pilar con marca táctil 6], [1],
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
  [Baja la placa Escucha al zócalo.\ #text(size: 9pt, fill: rgb("#555555"))[Baixa a placa Escoita ao zócalo.]],
  [Encaja el brazo en el banco. El eje es del propio brazo.\ #text(size: 9pt, fill: rgb("#555555"))[Encaixa o brazo no banco. O eixe é do propio brazo.]],
  [Apoya un resonador en el rebaje. Prueba las tres variantes de cada color y quédate con la que suene distinta.\ #text(size: 9pt, fill: rgb("#555555"))[Apoia un resonador no rebaixe. Proba as tres variantes de cada cor e queda coa que soe distinta.]],
  [El raspado se hace con la espátula sobre el raspador, después del golpe.\ #text(size: 9pt, fill: rgb("#555555"))[O raspado faise coa espátula sobre o raspador, despois do golpe.]],
)

== Qué no va en esta carpeta
#list(
  [S2-RES-ROJ con pared de 1,5 mm no se imprime: incumple el mínimo de 3,2 mm.],
  [Las nueve piezas S2-RES-\*-E-A/B/C mantienen pared de 8 mm y cambian la cavidad. El tono no se ha medido.],
  [S2-BAL-E se entrega como banco y brazo. El eje va unido al brazo; no hay pasador suelto.],
)

== Comprobación de diseño
21 de 21 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
