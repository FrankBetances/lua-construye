# Carpetas de impresión

Una carpeta por envío a Masque3D. El Set 1 ya estaba y no se ha regenerado.
Generadas con `python3 -m agents.pipeline_todos`.

| Carpeta | Piezas | Auditoría | PDF |
|---|---|---|---|
| `sets/P1-probeta-encaje` | 12 | apta | sí |
| `sets/S0-kit-lua` | 14 | apta | sí |
| `sets/S2-estacion-sonido` | 21 | apta | sí |
| `sets/S3-laboratorio-rampas` | 15 | apta | sí |
| `sets/S4-maquina-soplo` | 10 | apta | sí |
| `sets/S5-puente-equilibrio` | 14 | apta | sí |
| `sets/S6-jardin` | 14 | apta | sí |

## Qué no cupo

### P1-probeta-encaje
- No es una pieza del juguete. Sirve para elegir la holgura en el PLA de Masque3D.

### S0-kit-lua
- K-CUELLO no se imprime: es la unidad sellada del fabricante y queda fuera del alcance del niño.

### S2-estacion-sonido
- S2-RES-ROJ con pared de 1,5 mm no se imprime: incumple el mínimo de 3,2 mm.
- Las nueve piezas S2-RES-*-E-A/B/C mantienen pared de 8 mm y cambian la cavidad. El tono no se ha medido.
- S2-BAL-E se entrega como banco y brazo. El eje va unido al brazo; no hay pasador suelto.

### S3-laboratorio-rampas
- La esfera E de 38 mm no se genera: SETS la marca por verificar para menores de 36 meses y no llega a 44,5 mm.
- Con H = 31,80 mm la rampa mediría 254,40 mm y no cabe en la cama. H queda en 19,20 mm.

### S4-maquina-soplo
- S4-BOQ no se imprime en PLA por FDM. Cada niño necesita embocadura de otro proveedor, sin compartirla.
- S4-ROT-E y S4-MOL-G se parten en jaula y aspas. El eje es integral al rotor.
- El contrapeso de las compuertas es volumen de PLA, no un lastre suelto. Los gramos no se han pesado.

### S5-puente-equilibrio
- La viga de 10 × 31,80 mm mediría 318 mm y no cabe en la cama. Esta viga mide 186 mm.
- S5-PAS-G es un clip en U. Un pasador pequeño entraría en el cilindro de piezas pequeñas.
- 20, 40 y 60 g son un objetivo a 1,24 g/cm³. No hay báscula en esta máquina y la tolerancia de ±0,5 g no está verificada.

### S6-jardin
- Los prismas son geometría opaca de PLA. El azul y el amarillo translúcidos piden PETG o resina, que aquí no se fabrican.
- El macro-escenario del apartado 7 no tiene carpeta: no condiciona estos STL.

### Común a todas
- No hay impresora Masque3D en esta máquina: los STL no se han impreso.
- No hay ensayo de laboratorio EN 71-1. La auditoría es un criterio de diseño sobre la malla.
- D1 (paso de 8 mm o de 16 mm) sigue abierta. La planta usa el módulo de 31,80 mm.
- El apartado 7 de SETS, el macro-escenario, no tiene STL propio.
