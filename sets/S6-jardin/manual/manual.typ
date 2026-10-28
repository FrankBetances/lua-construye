#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= El Jardín del Sol, la Sombra y la Semilla
Fase 6 del plan de impresión. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
La semilla entra en la tierra. Los tallos se enroscan. La flor y la copa comparten la misma rosca.

#text(fill: rgb("#555555"))[A semente entra na terra. Os talos enróscanse. A flor e a copa comparten a mesma rosca.]

El niño ve a Lúa desde atrás. La linterna no la usa el niño.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [S6-TIE-G], [Base de tierra], [1],
  [S6-SEM-G], [Semilla], [1],
  [S6-TAL-G], [Tallo de rosca gruesa], [5],
  [S6-FLO-G], [Corona floral], [1],
  [S6-COP-G], [Copa de árbol], [1],
  [S6-FRU-MAN], [Fruto mango], [1],
  [S6-FRU-NAR], [Fruto naranja], [1],
  [S6-FRU-MANZ], [Fruto manzana], [1],
  [S6-PRI-AZU], [Prisma de agua], [1],
  [S6-PRI-AMA], [Prisma de sol], [1],
  [S6-SIL-ARB], [Pantalla opaca del árbol], [1],
  [S6-SIL-LUN], [Pantalla opaca de la luna], [1],
  [K-ZOCALO-G], [Zócalo universal], [1],
  [K-PLACA-JARDIN], [Placa Jardín], [1],
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
  [Baja la placa Jardín al zócalo y ponlo junto a la base, del lado en que el niño ve a Lúa desde atrás.\ #text(size: 9pt, fill: rgb("#555555"))[Baixa a placa Xardín ao zócalo e pono xunto á base, do lado en que o neno ve a Lúa desde atrás.]],
  [Mete la semilla en el alvéolo, a ras.\ #text(size: 9pt, fill: rgb("#555555"))[Mete a semente no alvéolo, a ras.]],
  [Enrosca un tallo en la semilla y el siguiente tallo en el anterior.\ #text(size: 9pt, fill: rgb("#555555"))[Enrosca un talo na semente e o seguinte talo no anterior.]],
  [Corona con la flor o con la copa. Los frutos bajan a los pozos de la copa.\ #text(size: 9pt, fill: rgb("#555555"))[Coroa coa flor ou coa copa. Os froitos baixan aos pozos da copa.]],
  [El prisma azul va al pozo del agua y el amarillo al del sol. La linterna la sostiene el adulto.\ #text(size: 9pt, fill: rgb("#555555"))[O prisma azul vai ao pozo da auga e o amarelo ao do sol. A lanterna sostena o adulto.]],
  [La pantalla de la luna entra en la ranura de noche.\ #text(size: 9pt, fill: rgb("#555555"))[A pantalla da lúa entra na rañura de noite.]],
)

== Qué no va en esta carpeta
#list(
  [Los prismas son geometría opaca de PLA. El azul y el amarillo translúcidos piden PETG o resina, que aquí no se fabrican.],
  [El macro-escenario del apartado 7 no tiene carpeta: no condiciona estos STL.],
)

== Comprobación de diseño
14 de 14 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
