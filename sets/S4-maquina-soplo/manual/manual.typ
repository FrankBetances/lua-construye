#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")

= La Máquina de Soplo y Viento
Fase 8 del plan de impresión. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  El niño mueve las piezas. El adulto sostiene la tableta. La criatura no toca la pantalla.
  #linebreak()
  O neno move as pezas. O adulto sostén a tableta. A criatura non toca a pantalla.
]

== Escena
Juego de soplo y de causa-efecto. No es un ejercicio de habla ni un tratamiento del velo.

#text(fill: rgb("#555555"))[Xogo de sopro e de causa-efecto. Non é un exercicio de fala nin un tratamento do veo.]

Lúa está de frente. Cada niño usa su embocadura, que no está en esta carpeta.

El reconocimiento es para el adulto que acompaña, no para el niño.

== Piezas
#table(
  columns: (1.5fr, 2.2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cant.*],
  [S4-CAN-E], [Cuerpo del canal], [2],
  [S4-COD-E], [Codo de 90 grados], [1],
  [S4-ROT-JAULA-E], [Jaula del rotor], [1],
  [S4-ROT-ASPAS-E], [Rotor de aspas], [1],
  [S4-COM-LIG-E], [Compuerta ligera], [1],
  [S4-COM-PES-E], [Compuerta pesada], [1],
  [S4-MOL-JAULA-G], [Jaula del molinete], [1],
  [S4-MOL-ASPAS-G], [Aspas anchas del molinete], [1],
  [K-ZOCALO-G], [Zócalo universal], [1],
  [K-PLACA-FRONTAL], [Placa Frontal], [1],
)

== Orden
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/despiece.svg", width: 100%)

#enum(
  [Baja la placa Frontal al zócalo. Lúa mira al niño. Las luces quedan apagadas.\ #text(size: 9pt, fill: rgb("#555555"))[Baixa a placa Frontal ao zócalo. Lúa mira ao neno. As luces quedan apagadas.]],
  [Acopla el canal y, si el reto dobla el aire, el codo.\ #text(size: 9pt, fill: rgb("#555555"))[Acopla a canle e, se o reto dobra o aire, o cóbado.]],
  [Mete el rotor en la jaula por el cojinete. Las aspas no salen de la jaula.\ #text(size: 9pt, fill: rgb("#555555"))[Mete o rotor na gaiola polo rodamento. As aspas non saen da gaiola.]],
  [Clava la compuerta ligera o la pesada en el pozo del canal.\ #text(size: 9pt, fill: rgb("#555555"))[Crava a comporta lixeira ou a pesada no pozo da canle.]],
  [Con menores de 3 años solo se usa el molinete, y sopla el adulto.\ #text(size: 9pt, fill: rgb("#555555"))[Con menores de 3 años só se usa o muiño, e sopra o adulto.]],
)

== Qué no va en esta carpeta
#list(
  [S4-BOQ no se imprime en PLA por FDM. Cada niño necesita embocadura de otro proveedor, sin compartirla.],
  [S4-ROT-E y S4-MOL-G se parten en jaula y aspas. El eje es integral al rotor.],
  [El contrapeso de las compuertas es volumen de PLA, no un lastre suelto. Los gramos no se han pesado.],
)

== Comprobación de diseño
10 de 10 mallas pasan el criterio de diseño (pared, cilindro, cama). No es un ensayo de laboratorio ni una impresión en Masque3D.

La planta del kit está en `tarjetas/planta.svg`.
