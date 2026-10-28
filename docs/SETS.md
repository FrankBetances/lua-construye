# Construye con Lúa · Especificación de los mundos

Base de trabajo para los STL (masque3d) y para la integración de RA. Cada set sigue la misma estructura. Primero el fenómeno y la escena. Después las piezas, con código, escala, parámetros, notas de impresión y marcador RA. Luego el contrato de interacción con Lúa, los retos, el uso en cada contexto y los puntos abiertos.

Convenciones:

- **[hecho]**: sale de los documentos fuente. **[propuesta]**: diseño nuevo, reversible. **[por verificar]**: depende de ensayo, norma o decisión.
- Las medidas se expresan en **módulos** (P = paso estándar; escala G = 2P) y solo en milímetros cuando el dato es de origen.
- Las reacciones de Lúa usan los opcodes existentes (`MOOD`, `PICTO`, `CELEBRATE`, `AWARD`, `PHASE`, `RELAX`, `ACCESSORY`, `VERDICT`) y los propuestos para V5 (`LIGHT`, y `HAPTIC` solo en Ronroneo). Los argumentos entre paréntesis son **entradas de catálogo propuestas**. Las que no existen hoy se recogen al final de cada set y pasan por la puerta clínica.
- Los eventos se nombran `S<n>.<EVENTO>` y forman el catálogo único de `CONTRATO-EVENTOS.md`.

---

## 0. Reglas comunes a todos los sets

### 0.1 Detección [propuesta]

| Método | Qué detecta | Herramienta | Uso |
|---|---|---|---|
| A · Marcador de pieza | Presencia, posición, rumbo y ángulo de un bloque | ARCore (imágenes aumentadas) o fiducial propio, según D2 | Baldosas, viga, rotor, compuertas, zócalos |
| B · Oclusión de marcador | Algo tapa un marcador fijo | Igual que A | Semilla en alvéolo, pieza en ranura |
| C · Mano | Gesto, contacto, rotación de muñeca | MediaPipe Hands | Percusión, raspado, enroscado |
| D · Cara | Protrusión labial, mofletes inflados | MediaPipe Face (blendshapes; nombres exactos **por verificar** en la versión integrada) | Solo en el modo de praxias del Set 4 |
| E · Objeto en movimiento | Trayectoria y tiempo | Segmentación por color en la imagen | Esferas del Set 3 |
| F · Toque del adulto | Cualquier evento | Botón en la app | **Siempre disponible** |

Para dar un evento por bueno [propuesta], la detección debe mantenerse estable unos 10 fotogramas (≈ 0,33 s a 30 fps), y la reacción de Lúa debe llegar en menos de 300 ms desde la confirmación. Ambos valores se ajustan en la fase 5.

Todo marcador va en una cara que **no tapen** ni Lúa ni la mano del niño en el uso normal. Esta regla condiciona la geometría desde el primer STL.

### 0.2 Capas de RA visible [propuesta]

Cada set tiene una capa que hace visible lo invisible (aire, fuerza, sonido, luz). Solo aparece en la fase de ampliación, con la tableta en su soporte, y es el adulto quien la muestra. Las mallas pesan menos de 100 KB [hecho] y se derivan del STL master con el mismo código de pieza.

### 0.3 Mecánica transversal: tarjetas de modelo [propuesta]

Cada set incluye de dos a cuatro tarjetas en papel con una construcción objetivo que el niño copia. Es juego estructurado, la modalidad que en Gilligan-Lee *et al.* (2023) se asocia con la numeración a los 4 años. La asociación no es causal. La app puede reconocer la tarjeta (marcador) y comparar la construcción con el modelo.

### 0.4 Vocabulario espacial para el adulto [propuesta]

La app sugiere al adulto palabras de las ocho categorías de lenguaje espacial que usa BrickSmart: dimensiones, formas, posición y dirección, orientación y transformación, cantidad, deícticos, propiedades y patrón. Cada set indica sus categorías prioritarias. El niño nunca recibe listas: las palabras aparecen ligadas a lo que acaba de pasar.

### 0.5 Reglas de luz y vibración [hecho]

Rigen las del README de Lúa. Luz: brillo bajo, ≤ 3 destellos/s, nunca como error, apagada en escucha, captura de voz y turno de respuesta, y apagada en VIA+. Vibración: opcional, la activa el adulto, empieza en nivel mínimo, nunca en turno de respuesta ni como error, nunca en VIA+.

---

## SET 0 · Kit Lúa (común)

Define el cuerpo de Lúa y la forma en que Lúa se ancla a cualquier mundo. **Se diseña primero** y depende de B1, porque el volumen del bloque-cuello fija la base de la cabeza.

| Código | Pieza | Escala | Parámetros / función | Notas STL | Marcador RA |
|---|---|---|---|---|---|
| `K-CUELLO` | Unidad sellada cabeza + cuello | Fabricante | Anti-espigas de bloque grande debajo [hecho]. Cuatro luces direccionales [propuesta V5] | La imprime e integra masque3d [hecho]. Fuera del alcance del niño | No necesita: la pose se toma del lomo |
| `K-TRONCO-G` | Tronco | G | Recibe el cuello con **orientación forzada** (llave asimétrica) [hecho] | Llave visible y táctil: el niño entiende la posición sin instrucciones | — |
| `K-LOMO-G` | Bloque dorsal | G | Lleva el marcador que da posición y **rumbo** de Lúa en todos los sets | Cara superior plana, mate | Sí, cara superior |
| `K-PATA-G` ×4 | Patas | G | Encajan en el tronco. Las delanteras llevan la llave del zócalo | Sin subpiezas | — |
| `K-PATIN-G` | Patín guía | G | Pieza bajo el tronco que corre por la ranura de 12 mm del Set 1 | Tolerancia de deslizamiento por probeta | — |
| `K-COLA-G` | Cola | G | Marca visualmente la parte de atrás de Lúa | Indica el rumbo al niño | — |
| `K-ZOCALO-G` | Zócalo universal | G | Ancla a Lúa en una sola orientación y acepta una placa de identidad | Un único STL para todos los sets | — |
| `K-PLACA-*` | Placas de identidad | G | INICIO, META, ESCUCHA, RECEPTOR, FRONTAL, NIVEL, JARDÍN | Relieve con icono para lectura táctil | Sí: identifican el contexto |

Decisión de diseño [propuesta]: un solo zócalo con placas intercambiables evita seis zócalos distintos y permite que la app sepa, solo con ver la placa, en qué mundo está Lúa.

Regla de lateralidad [propuesta]: la izquierda y la derecha son **siempre las de Lúa**. En los sets donde importa la lateralidad (1, 5 y 6), el zócalo se orienta de forma que el niño vea a Lúa desde atrás. Así la izquierda de Lúa coincide con la del niño y no se le exige un giro mental en espejo a los 3–4 años.

---

## SET 1 · El Camino de Lúa (*Lúa's Stepping Trail*)

**Fenómeno:** un recorrido es una secuencia ordenada de pasos. Si falta un paso, no se llega (algoritmo tangible desconectado).
**Edad:** 0–6. Escala G hasta 3 años; las fichas de comando de escala E, a partir de 3.
**Ejes:** propiocepción y desensibilización táctil palmar, coordinación bimanual, planificación motriz y estructura temporal («primero, luego, al final») · *Step forward, Turn left/right, Stop, Jump, Rough, Smooth, Follow the path* · secuencias, giros de 90°, depuración.
**Vocabulario espacial prioritario:** posición y dirección, orientación, patrón, deícticos.

### Escena

Sobre la mesa o la alfombra, el niño une baldosas desde el zócalo INICIO hasta el zócalo META. Lúa va encajada por su patín en la ranura y el niño la desliza. Las fichas de comando se insertan en los laterales de las baldosas y dicen qué hace Lúa en ese tramo.

### Piezas

| Código | Pieza | Cant. | Escala | Parámetros | Notas STL | Marcador |
|---|---|---|---|---|---|---|
| `S1-REC-LIS-G` | Baldosa recta lisa (ondas suaves) | 3 | G | Ranura guía de 12 mm [hecho]. Ancho = ancho del cuerpo de Lúa + 2 módulos [propuesta] | Ranura con chaflán de entrada en ambos extremos | Esquina, fuera de la ranura |
| `S1-REC-RUG-G` | Baldosa recta rugosa (estriada) | 3 | G | Relieve ±1,5 mm [hecho] | Relieve redondeado, sin aristas vivas. Validar limpieza | Esquina |
| `S1-CUR-G` | Curva de 90° | 4 | G | Mantiene la continuidad de la ranura [hecho] | Radio de la ranura compatible con el patín | Esquina exterior |
| `S1-TEE-G` | Intersección en T | 2 | G | Bifurcación [hecho] | Las tres salidas con chaflán | Centro, fuera de la ranura |
| `S1-CMD-AVA/PAR/GIR/SAL` | Fichas de comando (avanza, para, gira, salta) | 4 | E, y versión G para < 3 | Icono háptico en relieve [hecho]. Encaje a presión en el lateral [hecho] | En escala G, dimensiones que no quepan en el cilindro de piezas pequeñas [por verificar] | Cara superior, con el icono |
| `S1-DEST-*` | Placas de destino (parque, cama) | 2 | G | Sustituyen la placa META en el reto 4 | Reutilizan `K-ZOCALO-G` | Sí |

### Contrato de interacción

| Evento | Qué hace el niño | Detección | Lúa | Luz | Tableta / adulto | Ronroneo |
|---|---|---|---|---|---|---|
| `S1.LUA_EN_INICIO` | Coloca a Lúa en el zócalo INICIO | Placa INICIO + lomo dentro del zócalo | `MOOD(atenta)` + `PICTO(destino)` | `LIGHT(DIR_DELANTE)` tenue | «Let's go to the park! Build the path.» | — |
| `S1.BALDOSA_CONECTADA` | Une una baldosa al camino | Nuevo marcador alineado con el grafo del camino | Parpadeo breve (`MOOD(atenta)`) | — | Solo en el reto 1: «Step!» | — |
| `S1.COMANDO_INSERTADO` | Mete una ficha en un lateral | Marcador de ficha junto a una baldosa | `PICTO(comando)` | Según el comando | Verbo TPR: «Turn left!» | — |
| `S1.LUA_AVANZA` | Desliza a Lúa un tramo | El lomo cruza el límite entre baldosas | `MOOD(ánimo)` | `LIGHT(DIR_DELANTE)` | «Step forward!» | — |
| `S1.LUA_GIRA` | Pasa por una curva | Cambio de rumbo del lomo de ±90° | `MOOD(ánimo)` | `LIGHT(DIR_IZQ/DCHA)` | «Turn left!» / «Turn right!» | — |
| `S1.CAMINO_ROTO` | Curva invertida o hueco por delante | Grafo discontinuo delante del lomo | `MOOD(espera_serena)` | `APAGADO` | Al adulto: «The road is blocked! Can we turn the block?» | — |
| `S1.LLEGA_META` | Encaja a Lúa en META | Lomo en el zócalo META | `CELEBRATE` (+ `AWARD` opcional) | Las cuatro tenues | «We arrived! Stop and rest.» | `CELEBRA_CORTO` opcional |

Capa de RA visible: el camino recorrido se dibuja como una línea de flechas sobre las baldosas, para que el adulto muestre «el programa» que el niño ha construido.

### Retos

1. **Un paso (0–2, causa-efecto 1:1).** Una baldosa junto al zócalo. El niño desliza a Lúa: `S1.LUA_AVANZA`. La tableta dice «Step!».
2. **Liso y rugoso (2–3, propiocepción).** Se alternan baldosas `LIS` y `RUG`. El niño palpa con las yemas antes de deslizar a Lúa y vocaliza «brrrr» en la rugosa. La vocalización es un turno verbal: Lúa queda quieta.
3. **Del cuerpo al bloque (3–4, TPR y secuencia).** El adulto modela «Step forward, step forward, stop!». El niño lo hace con su cuerpo, coloca tres piezas y repite el recorrido con Lúa.
4. **Encrucijada (4–5, lateralidad).** Una T con salida a la cama (`S1-DEST-CAMA`) y otra al parque. Lúa muestra `PICTO(cama)` y la tableta dice «I am sleepy! Turn right to the bed». Con la regla de lateralidad del Set 0, la derecha de Lúa es la del niño.
5. **Depuración en equipo (5–6).** El adulto coloca una baldosa errónea. Tres roles (guía, proveedor y constructor, inspirados en la terapia basada en bloques; evidencia de baja calidad según Narzisi *et al.* 2021) localizan el fallo, piden la pieza en inglés («Give me the straight block») y rehacen el algoritmo.

**Tarjetas de modelo:** tres recorridos dibujados (recto, una curva, una T) para copiar.

### Contextos

En **Valeria+**, se usa para rutinas de ordenación en cuatro pasos (mañana, comida, juego, sueño), para graduar la fuerza de pinza al insertar fichas y como exposición táctil gradual en niños con hipersensibilidad, sin presentarlo como tratamiento. En **Descubre con Lúa**, va en el centro del círculo de asamblea: dos delegados construyen y el grupo dice la orden siguiendo el metrónomo visual de Lúa.

### Puntos abiertos

La conexión mecánica entre baldosas debe resistir el empuje del niño al deslizar a Lúa sin separarse (probeta). La ranura de 12 mm y el patín se diseñan juntos. Hay que decidir si las fichas de comando de escala E entran en el kit 0–3 (recomendación: no). Entradas de catálogo nuevas: `PICTO(destino, parque, cama)`, `PICTO(avanza, para, gira, salta)`, `MOOD(ánimo)`, `MOOD(espera_serena)`.

---

## SET 2 · La Estación de Sonido y Eco (*Sound & Echo Station*)

**Fenómeno:** el sonido es vibración; la forma y el material del objeto cambian cómo suena.
**Edad:** 2–6, escala E [propuesta]: las paredes finas y la precisión acústica no encajan con la escala G.
**Ejes:** discriminación fuerte/débil, grave/agudo y largo/corto, ritmo silábico, apoyo a pares mínimos y autorregulación ante sobre-reactividad auditiva · *Listen, Loud, Quiet, Soft, Fast beat, Slow beat, Tap, Scrape* · acústica de cavidades y materiales.
**Vocabulario espacial prioritario:** dimensiones, propiedades, patrón.

### Escena

Una estación con un martillo balancín fijo. El niño pone debajo el resonador que quiere y pulsa el balancín con un dedo. Lúa está en su zócalo, de frente al niño, con la placa ESCUCHA.

Corrección respecto al documento base: Lúa **no recibe** la vibración de los bloques, porque no tiene sensor. La antigua «plataforma de escucha» pasa a ser simplemente el lugar desde donde Lúa mira.

### Piezas

| Código | Pieza | Cant. | Escala | Parámetros | Notas STL | Marcador |
|---|---|---|---|---|---|---|
| `S2-RES-AZU-E` | Resonador grave | 1 | E | Pared de 5,0 mm [hecho]. Volumen exterior igual al de los otros dos [hecho] | 100 % de relleno en paredes: el relleno cambia el sonido | Cara frontal |
| `S2-RES-AMA-E` | Resonador medio | 1 | E | Pared de 3,2 mm [hecho] | Igual | Cara frontal |
| `S2-RES-ROJ-E` | Resonador agudo | 1 | E | Pared de 1,5 mm con nervaduras [hecho] → **incumple el mínimo de 3,2 mm** | Ver puntos abiertos | Cara frontal |
| `S2-BAL-E` | Martillo balancín | 1 | E | Palanca de primer grado con tope, que estandariza el golpe [hecho] | Eje sin piezas sueltas. Tope que limita el ángulo máximo | Brazo: mide el ángulo |
| `S2-RAS-E` | Raspador estriado | 2 | E | Estrías transversales [hecho] | Estría redondeada | Extremo |
| `S2-ESP-E` | Espátula de raspar | 1 | E | Segura, sin filo [hecho] | Tamaño mínimo por norma [por verificar] | — |
| `S2-PIL` | Pilares (reto 5) | — | — | Se reutilizan `S3-PIL` | — | — |

### Contrato de interacción

Orden obligatorio [propuesta]: golpe → el sonido se apaga → pausa de ~1 s → Lúa → palabra. La tableta nunca habla encima del sonido físico.

| Evento | Qué hace el niño | Detección | Lúa | Luz | Tableta / adulto | Ronroneo |
|---|---|---|---|---|---|---|
| `S2.RESONADOR_COLOCADO` | Pone un resonador bajo el balancín | Marcador del resonador en la posición de golpeo | `MOOD(escucha)`, quieta | `APAGADO` | — | — |
| `S2.GOLPE_DEBIL` | Pulsa suave | Pico de velocidad del brazo con ángulo < θ₁ | Tras la pausa: `MOOD(calma)` | `APAGADO` | «Quiet… soft sound.» | — |
| `S2.GOLPE_FUERTE` | Pulsa con energía | Ángulo > θ₂ | Tras la pausa: onda de alegría | `APAGADO` | «Loud! Good beat!» | — |
| `S2.RASPADO` | Frota la espátula | La mano se desplaza a lo largo del raspador (duración) | `MOOD(atenta)` sostenida mientras dura | `APAGADO` | Al terminar: «Long sound!» | — |
| `S2.RITMO` | Repite el pulso de Lúa | Golpes dentro de una ventana alrededor de cada pulso | Metrónomo visual en el borde (`PHASE`) y destellos al acertar | `APAGADO` | «Slow beat!» / «Fast beat!» | Solo en la fase «sentir»: `METRONOMO_LENTO` |

**Decisión de diseño [propuesta]:** la intensidad del golpe se mide **por el ángulo del balancín** y no por el micrófono de la tableta. Así la tableta se mantiene como sensor ciego visual, no se capta audio y se evitan los problemas del micrófono en un set pensado también para niños con audífono o implante. Los umbrales θ₁ y θ₂ se calibran en la fase 5.

**Fase «oír» frente a fase «sentir»:** con Ronroneo, el niño primero oye el ritmo y después lo siente en la mano, nunca a la vez [hecho, reglas hápticas].

Capa de RA visible: tras el golpe, ondas concéntricas sobre el resonador, más separadas en el grave y más juntas en el agudo.

### Retos

1. **Mi sonido es seguro (2–3).** El niño acciona el balancín. Lúa sonríe en calma: el sonido es predecible.
2. **Ratón y león (2–3).** «Tap quiet like a mouse» / «Tap loud like a lion!». Gradúa la fuerza de la muñeca.
3. **Corto y largo (3–4).** El golpe seco se asocia a /p/ y /t/; el raspado continuo, a /s/. Lúa mantiene la atención mientras dura el raspado.
4. **Pares mínimos (4–5).** El resonador grave se asocia a una imagen (*boca*) y el agudo a su par (*bota*). El adulto dice la palabra y el niño golpea el que corresponde. Es una actividad de práctica, no de evaluación.
5. **¿Dónde suena más? (5–6).** El resonador se apoya en la alfombra o se eleva sobre pilares. El niño compara y lo dice.

**Tarjetas de modelo:** secuencias rítmicas en dibujo (●●○, ●○●) para reproducir.

### Contextos

En **Valeria+**, sirve como material para desensibilización progresiva, preparación sensorial antes de la prueba de Ling y segmentación silábica por percusión. En **Descubre con Lúa**, acompaña canciones en inglés a pulso visual.

### Puntos abiertos

**Resonador rojo:** una pared de 1,5 mm no cumple el criterio de 3,2 mm. Hay dos salidas [propuesta]. La primera, una lámina interna de 1,5 mm dentro de un marco ≥ 3,2 mm e inaccesible, con ensayo de caída. La segunda, recomendada, es conseguir el agudo variando la **cavidad** (longitud y abertura) con paredes iguales. **Hay que verificar** que en PLA impreso la diferencia de tono sea audible y estable entre lotes: se imprimen tres variantes por resonador y se mide su frecuencia antes de fijar el STL. Entradas de catálogo nuevas: `MOOD(escucha)`, `MOOD(calma)`, animación de onda y metrónomo de borde.

---

## SET 3 · El Laboratorio de Rampas y Gravedad (*Motion & Gravity Lab*)

**Fenómeno:** cuanto más alto y más liso, más rápido; la rugosidad frena.
**Edad:** 0–6, con una esfera distinta en cada escala.
**Ejes:** seguimiento visual horizontal, control inhibitorio (esperar), prosodia ascendente y descendente, narración en tres tiempos · *Roll, Fast, Slow, High, Low, Steep, Wait, Go, Catch* · plano inclinado (15° frente a 30°) y fricción.
**Vocabulario espacial prioritario:** dimensiones (alto/bajo), cantidad (más/menos), orientación.

### Escena

Una torre de pilares sostiene el extremo alto de una rampa articulada. Al pie de la rampa, un tramo plano intercambiable lleva al receptor, y detrás del receptor está Lúa. La esfera **se detiene en una lengüeta antes de llegar a Lúa**: la unidad electrónica nunca recibe impactos.

### Geometría de la rampa [propuesta]

Si las rampas tienen un ángulo fijo y además se apoyan en una torre variable, la altura no cambia nada. Se resuelve con **una rampa articulada de longitud L = 8H**, siendo H la altura de un pilar. Pivota sobre un bloque bisagra a pie de mesa y apoya su extremo alto en la torre:

| Pilares | Ángulo | Uso |
|---|---|---|
| 2 | ≈ 14,5° | «Low», rampa suave (15° del documento base) |
| 3 | ≈ 22° | Intermedio |
| 4 | 30° | «Steep», rampa pronunciada |
| 5 | ≈ 38,7° | Máximo recomendado |
| 6 | ≈ 48,6° | Solo para contar y apilar, no para lanzar |

Con esto, los ángulos de 15° y 30° del documento base salen de 2 y 4 pilares, y el reto 3 (2 frente a 5 pilares) compara alturas reales.

### Piezas

| Código | Pieza | Cant. | Escala | Parámetros | Notas STL | Marcador |
|---|---|---|---|---|---|---|
| `S3-RAM-G` | Rampa articulada | 1 | G | L = 8H, canal con perfil en U | Rigidez: no debe flexar bajo la mano | Lateral, en el tercio alto |
| `S3-BIS-G` | Bloque bisagra | 1 | G | Pivote a presión, sin pasador suelto | Evitar bisagra impresa de una pieza en escala G | — |
| `S3-PIL-G` | Pilar | 6 | G | Altura H. Relieve táctil del 1 al 6 [hecho] | Se reutiliza en los Sets 2 y 5 | Cara frontal con el número |
| `S3-ESF-LIS` / `S3-ESF-RUG` | Esfera lisa y esfera rugosa | 2 + 2 | E: Ø 38 mm [hecho]. G: Ø ≥ 45 mm [propuesta, por verificar] | Colores muy distintos entre sí y del fondo | Maciza o de pared gruesa | Por color (método E) |
| `S3-FRI-G` | Tramo de fricción reversible | 1 | G | Una cara lisa y otra rugosa: un solo STL | El relieve no debe hacer rebotar la esfera | Una marca distinta en cada cara |
| `S3-CUR-PER-G` | Curva peraltada (reto 5) | 1 | G | Pieza citada en el reto 5 que faltaba en la lista | Peralte por prototipo | Esquina |
| `S3-REC-G` | Receptor con lengüeta | 1 | G | La esfera se para un módulo antes de Lúa | Integrado con `K-ZOCALO-G` + placa RECEPTOR | Placa |

### Contrato de interacción

| Evento | Qué hace el niño | Detección | Lúa | Luz | Tableta / adulto | Ronroneo |
|---|---|---|---|---|---|---|
| `S3.ESFERA_ARRIBA` | Pone la esfera en la cima y aparta las manos | Esfera en la zona alta, sin mano en contacto | `MOOD(expectante)`, mirada hacia arriba | `LIGHT(lado_rampa)` tenue | «Ready… steady…» | — |
| `S3.SALIDA_ANTICIPADA` | La suelta antes de tiempo | La esfera sale antes del «go» | `MOOD(atenta)`, sin reproche | `APAGADO` | Al adulto: «Let's try waiting together» | — |
| `S3.SALIDA` | La suelta tras el «go» | La esfera abandona la zona alta | Sigue la bajada | `LIGHT(lado_rampa)` mientras baja [hecho] | «Go!» | — |
| `S3.LLEGADA_RAPIDA` | — | Llega al receptor en menos tiempo que el lanzamiento anterior | `CELEBRATE` de velocidad | Las cuatro tenues | «Whoa! Super fast!» | `CELEBRA_CORTO` opcional |
| `S3.LLEGADA_LENTA` | — | Llega en más tiempo | `PICTO(caracol)`, relajada | Las cuatro tenues | «Slow… rolling gentle.» | — |
| `S3.SE_PARA` | — | Esfera quieta más de 2 s fuera del receptor | `MOOD(curiosa)` | `APAGADO` | «It stopped! Let's build a taller tower!» | — |

**Decisión de diseño [propuesta]:** rápido y lento se deciden **por comparación con el lanzamiento anterior** y no con umbrales absolutos. Es más robusto frente a la luz y al montaje, y pedagógicamente es lo que se busca: comparar.

Capa de RA visible: la trayectoria de la esfera, con una flecha de velocidad que crece al bajar.

### Retos

1. **Mirar sin tocar (0–2).** Rampa baja montada por el adulto, esfera G. El niño sigue la esfera con la mirada.
2. **Sube la voz, baja la esfera (2–3).** Vocal ascendente al apilar pilares y descendente cuando baja la esfera. Mientras el niño vocaliza, Lúa queda quieta (turno verbal).
3. **Bajo o alto (3–4).** Torre de 2 frente a torre de 5: «Low» frente a «High». El niño deducela relación.
4. **Arena en el camino (4–5).** El tramo `FRI` por la cara rugosa frena la esfera. El niño lo resuelve con más altura o con la esfera lisa.
5. **Circuito completo (5–6).** Rampa empinada, tramo plano y curva peraltada. El niño dice su hipótesis en inglés antes de soltar.

**Tarjetas de modelo:** tres montajes (2, 4 y 5 pilares, con o sin tramo rugoso) para reproducir y predecir.

### Contextos

En **Valeria+**: autorregulación y espera estructurada, y fijación visual antes de la Pizarra Mágica. En **Descubre con Lúa**: unidad de planos inclinados, con hipótesis a mano alzada antes de cada lanzamiento.

### Puntos abiertos

La esfera de escala G debe pasar los requisitos aplicables a esferas para menores de 36 meses [por verificar]. El lastre de la esfera rugosa no debe ser accesible. Entradas de catálogo nuevas: `MOOD(expectante)`, `MOOD(curiosa)`, `PICTO(caracol)`, celebración de velocidad.

---

## SET 4 · La Máquina de Soplo y Viento (*Wind & Breath Engine*)

**Fenómeno:** el aire en movimiento empuja: hace girar un rotor y vence una compuerta.
**Edad:** 3–6, escala E [propuesta]. Para menores de 3 años: el adulto sopla y el niño observa la causa-efecto, con un molinete G protegido.
**Ejes:** dosificación y duración del soplo, redondeo labial como **juego motor oral**, control respiratorio · *Breathe in, Blow, Hard, Gentle, Wind, Breeze, Storm, Spin, Fly* · flujo de aire en conductos, energía eólica.
**Vocabulario espacial prioritario:** orientación (girar), cantidad (más fuerte/más suave), posición (a través de).

### Alerta clínica

El documento base presenta este set como fortalecimiento del cierre velar «para prevenir el escape nasal» y como «reemplazo de ejercicios de soplo clínico para dislalias». **La literatura no respalda** que los ejercicios de soplo mejoren el habla ni la función velofaríngea en el habla. El set se reformula como juego de control respiratorio, causa-efecto y motivación, y deja de presentarse como tratamiento. Esto protege la credibilidad clínica del ecosistema y evita alegaciones que no se pueden sostener ante un evaluador o un regulador.

### Escena

Lúa está de frente al niño (placa FRONTAL). El niño sopla por una embocadura personal. El canal lleva el aire, con o sin codo, hasta el rotor y las compuertas.

### Piezas

| Código | Pieza | Cant. | Escala | Parámetros | Notas STL | Marcador |
|---|---|---|---|---|---|---|
| `S4-CAN-E` | Cuerpo del canal | 2 | E | Conducto cónico con salida de 4 mm [hecho] | Interior liso. Sin contacto con la boca | Lateral |
| `S4-BOQ` | Embocadura extraíble | 1 **por niño** | — | Encaja en el canal | **No PLA por FDM** (D5). Material apto para contacto bucal y desinfectable [por verificar] | — |
| `S4-COD-E` | Codo de 90° | 1 | E | Desvía el flujo [hecho] | Radio interior suave para no perder caudal | Lateral |
| `S4-ROT-E` | Rotor de baja fricción | 1 | E | Eje horizontal [hecho]. Aspas dentro de una **jaula** [propuesta] | Eje y cojinete: la baja fricción no se consigue con PLA sobre PLA. Valorar un eje metálico encapsulado [por verificar] | Disco en el buje: mide las rps |
| `S4-COM-LIG-E` / `S4-COM-PES-E` | Compuertas ligera y pesada | 2 | E | Contrapeso graduado [hecho] | Contrapeso encapsulado (mismo criterio que D6) | En la hoja: mide el ángulo |
| `S4-MOL-G` | Molinete protegido (menores de 3) | 1 | G | Aspas anchas y blandas, dentro de una jaula | Uso solo con soplo del adulto | Buje |

### Contrato de interacción

**Cámaras (D4) [propuesta]:** la detección principal usa la cámara trasera, que mira el *resultado físico* (rotor y compuerta). El análisis facial es un modo aparte de Valeria+, con la cámara frontal, que no se activa a la vez.

| Evento | Qué hace el niño | Detección | Lúa | Luz | Tableta / adulto | Ronroneo |
|---|---|---|---|---|---|---|
| `S4.PREPARA` | Inspira por la nariz | Toque del adulto o inicio de fase | Animación de inhalación | `APAGADO` | «Breathe in through your nose… and blow!» | — |
| `S4.ROTOR_GIRA` | Sopla | rps del buje > umbral | Remolino animado, ojos de diversión | `APAGADO` | — durante el soplo | — |
| `S4.SOPLO_SOSTENIDO` | Mantiene el giro | rps > umbral durante t segundos | **Aro de progreso en el borde de la pantalla** | `APAGADO` | Al final: «Long wind!» | — |
| `S4.COMPUERTA_LIGERA` | Soplo suave | Ángulo de la compuerta ligera > umbral | `MOOD(alegre)` | `APAGADO` | «Gentle breeze!» | — |
| `S4.COMPUERTA_PESADA` | Soplo firme | Ángulo de la compuerta pesada > umbral | `AWARD` con destellos | `APAGADO` | «Strong wind! Fantastic blow!» | `CELEBRA_CORTO` opcional |
| `S4.FUGA` | El aire se escapa (labios abiertos) | Modo praxias: mofletes inflados con rotor quieto. Si no, toque del adulto | Mofletes en espejo | `APAGADO` | «Round your lips like an O.» | — |

Corrección respecto al documento base: el reto 5 usaba el «anillo luminoso» de Lúa para cronometrar el soplo, pero las reglas de luz lo impiden durante la acción del niño y a esa distancia de la cara. Se sustituye por un **aro de progreso en la pantalla**. En este set las luces quedan apagadas.

Capa de RA visible: partículas de aire que recorren el canal y el codo, para mostrar lo que no se ve.

### Retos

1. **El adulto sopla (menores de 3) / soplo libre (3).** Molinete G protegido; el niño ve cómo gira y Lúa se alegra.
2. **Labios en O (3–4).** Con la embocadura personal, sin fugas laterales.
3. **Brisa y tormenta (3–4).** «Gentle breeze»: el rotor gira sin tumbar la compuerta ligera. «Big storm!»: caen las dos.
4. **El aire dobla la esquina (4–5).** El codo lleva el aire hasta un rotor lateral: «Turn the wind left».
5. **Viento largo (5–6).** Se mantiene el rotor girando mientras se llena el aro de la pantalla. La duración objetivo la fija el equipo clínico: el documento base propone de 3 a 5 s [por verificar].

**Tarjetas de modelo:** recorridos del aire (recto, con codo a la izquierda, con codo a la derecha).

### Contextos

En **Valeria+**: juego motivador de control respiratorio y de redondeo labial, sin finalidad terapéutica sobre el habla. En **Descubre con Lúa**: energías renovables y soplo suave para relajarse al final de la jornada. **En el aula, cada niño usa su propia embocadura y nunca se comparten.**

### Puntos abiertos

Material de la embocadura y protocolo de desinfección (D5). Jaula del rotor. Cojinete. Umbrales de rps y ángulo. Pendiente de clínica: validar con el equipo qué esfuerzo de soplo es adecuado por edad, para que la compuerta pesada no exija un esfuerzo excesivo. Entradas de catálogo nuevas: animación de inhalación, remolino, aro de progreso, mofletes en espejo.

---

## SET 5 · El Puente de Equilibrio y Fuerza (*Bridge & Balance Studio*)

**Fenómeno:** una palanca se equilibra cuando masa × distancia es igual a ambos lados.
**Edad:** 0–6. Las masas del reto 1 son de escala G.
**Ejes:** tono postural, percepción del peso, pinza digital, comparativos y condicionales («si pongo esto, se cae») · *Heavy, Light, Balance, Fall, On top of, Under, Between, Same weight* · palanca de primer grado, centro de gravedad.
**Vocabulario espacial prioritario:** posición (encima/debajo/entre), cantidad (igual/más), dimensiones.

### Escena

Un fulcro con una viga balancín. Lúa está en un zócalo con placa NIVEL **junto a** la viga, mirando hacia ella, y **nunca encima del balancín** [propuesta]. Encima de una unidad electrónica que se inclina hay riesgo de caída y de golpe a la cabeza. Lúa solo se sube al **puente fijo** (pasadores puestos), y solo si el puente soporta su peso, que depende de B1.

### Piezas

| Código | Pieza | Cant. | Escala | Parámetros | Notas STL | Marcador |
|---|---|---|---|---|---|---|
| `S5-FUL-G` | Fulcro triangular | 1 | G | Arista de apoyo de baja fricción [hecho] | Desgaste de la arista: probar PETG | — |
| `S5-VIG-G` | Viga balancín | 1 | G | 2×10 módulos [hecho]. **Posiciones 1–5 a cada lado del eje**, numeradas en relieve [propuesta] | Simetría de masa de la viga: imprimir con el mismo patrón a ambos lados | Centro de la viga: mide el ángulo |
| `S5-MAS-20` ×2 / `S5-MAS-40` / `S5-MAS-60` | Masas calibradas | 4 | G | 20, 40 y 60 g [hecho]. Celeste con nube, verde con hoja y gris facetado [hecho]. Tolerancia ±0,5 g [propuesta] | La carcasa de la masa de 20 g debe pesar ≤ 20 g sin lastre. Lastre único encapsulado (D6) | Cara superior: identifica la masa |
| `S5-PAS-G` | Pasadores de anclaje | 4 | G | Bloquean la viga como puente fijo [hecho] | Tamaño mínimo por norma [por verificar] | — |
| `S5-PIL` | Pilares | — | — | Se reutilizan `S3-PIL-G` | — | — |

**Corrección física del reto 5 del documento base.** La roca de 60 g junto al fulcro (posición 1) se equilibra con la pluma de 20 g en la **posición 3**, no en el último tetón: 60 × 1 = 20 × 3. En la posición 5, la pluma vence a la roca (100 > 60) y la viga cae hacia la pluma. Combinaciones válidas con el kit: 40 en 1 ↔ 20 en 2; 60 en 2 ↔ 40 en 3; 60 en 1 ↔ 20 en 3.

### Contrato de interacción

| Evento | Qué hace el niño | Detección | Lúa | Luz | Tableta / adulto | Ronroneo |
|---|---|---|---|---|---|---|
| `S5.MASA_COLOCADA` | Pone una masa en una posición | Marcador de la masa y su posición sobre la viga | `MOOD(atenta)` | — | Al adulto: palabra de peso («Heavy rock!») | — |
| `S5.INCLINA` | — | Ángulo de la viga > umbral hacia un lado | `MOOD(sorpresa_inclinada)` | `LIGHT(DIR_IZQ/DCHA)`, lado que baja [hecho] | «Whoa! The bridge tilted down.» | — |
| `S5.EQUILIBRIO` | Compensa | \|ángulo\| < 2° sostenido 1 s [propuesta] | `MOOD(alivio)` + `AWARD(constructora)` | Las cuatro tenues [hecho] | «Balanced! Strong and steady bridge!» | `CELEBRA_CORTO` opcional |
| `S5.PREDICCION` (5–6) | Dice qué va a pasar antes de soltar | Toque del adulto que registra la predicción | `MOOD(expectante)` | `APAGADO` | «What will happen?» | — |

**Propuesta para 5–6 años:** como la app conoce las masas y sus posiciones, puede calcular el resultado. No lo enseña: el niño predice, suelta y comprueba, y la app solo confirma si el mundo coincidió con la predicción. Es indagación, no examen.

Capa de RA visible: flechas de peso proporcionales a masa × distancia sobre cada lado de la viga.

### Retos

1. **¿Cuál pesa? (0–2).** Con los ojos cerrados, en cada mano una masa G de 20 y otra de 60 g. Le da a Lúa la pesada.
2. **Encima, debajo, entre (2–3).** Puente fijo con pasadores: «Put Lúa on top of / under / between». Solo si el puente soporta a Lúa; si no, se usa una figura de bloques.
3. **El espejo (3–4).** Con el eje como línea de simetría, replicar a la derecha la torre de la izquierda.
4. **Sumar sin números (4–5).** 60 a un lado; 40 + 20 en la misma posición del otro lado.
5. **La palanca (5–6).** 60 en la posición 1; ¿dónde pongo la de 20? Predicción, prueba y la respuesta correcta: la posición 3.

**Tarjetas de modelo:** cuatro configuraciones de viga para reproducir y decir si se equilibran.

### Contextos

En **Valeria+**: graduación de la fuerza y de la pinza, y conceptos opuestos en expansión semántica. En **Descubre con Lúa**: trabajo por parejas para mantener a Lúa «nivelada» colocando masas a la vez.

### Puntos abiertos

Lastre (D6) y presupuesto de masa de la carcasa. Rozamiento del fulcro: con demasiada fricción, la viga no detecta 20 g de diferencia en posiciones cercanas. Hay que verificarlo con prototipo. Entradas de catálogo nuevas: `MOOD(sorpresa_inclinada)`, `MOOD(alivio)`, `AWARD(constructora)`.

---

## SET 6 · El Jardín del Sol, la Sombra y la Semilla (*Sun, Shadow & Growth Garden*)

**Fenómeno:** una planta necesita tierra, agua y luz; un objeto opaco proyecta una sombra que cambia con la distancia a la luz.
**Edad:** 0–6. Linterna solo a partir de 4 años y en manos del adulto.
**Ejes:** secuencia narrativa en 3–4 actos, ampliación morfosintáctica, rotación de muñeca · *Seed, Sprout, Plant, Flower, Tree, Water, Sun, Shadow, Grow tall, Night, Rest* · biología vegetal y óptica.
**Vocabulario espacial prioritario:** patrón y secuencia (antes/después), dimensiones (alto, grande/pequeña), posición.

### Escena

Una base de tierra con un alvéolo para la semilla y, al lado, el zócalo de Lúa (placa JARDÍN), visto desde atrás por el niño. La planta crece enroscando tallos y se corona con una flor o una copa con frutos.

### Piezas

| Código | Pieza | Cant. | Escala | Parámetros | Notas STL | Marcador |
|---|---|---|---|---|---|---|
| `S6-TIE-G` | Base tierra fértil | 1 | G | Alvéolo concéntrico para la semilla [hecho]. Ranura de noche junto al zócalo [propuesta] | — | **Marcador en el fondo del alvéolo** (método B) y otro en la ranura de noche |
| `S6-SEM-G` | Semilla | 1 | G | Encaja a ras del suelo [hecho] | Tamaño mínimo por norma [por verificar] | — |
| `S6-TAL-G` | Tallo con rosca gruesa | 3 (+2 para el reto 5) | G | Rosca de paso grueso, pocas vueltas [hecho] | Rosca impresa en vertical; probar el paso con niños de 2–3 años | Anillo superior: cuenta las alturas |
| `S6-FLO-G` / `S6-COP-G` | Corona floral y copa de árbol | 1 + 1 | G | Intercambiables [hecho] | — | Cara superior |
| `S6-FRU-*` | Frutos (mango, naranja, manzana) | 3 | G | Se acoplan a la copa [hecho] | **Riesgo de pieza pequeña**: tamaño mínimo por norma o integrarlos en la copa [por verificar] | — |
| `S6-PRI-AZU` / `S6-PRI-AMA` | Prismas translúcidos (agua y sol) | 2 | G | Tiñen la luz [hecho] | PETG translúcido o resina; el FDM da translucidez, no transparencia | Por color |
| `S6-SIL-ARB` / `S6-SIL-LUN` | Pantallas opacas de silueta | 2 | G | Recortes nítidos [hecho] | Grosor ≥ 3,2 mm | Base de la pantalla |

### Contrato de interacción

| Evento | Qué hace el niño | Detección | Lúa | Luz | Tableta / adulto | Ronroneo |
|---|---|---|---|---|---|---|
| `S6.SIEMBRA` | Mete la semilla | Deja de verse el marcador del fondo del alvéolo | `MOOD(ternura)`, mira abajo, `PICTO(semilla)` | — | «A little seed in the soil. What does it need?» | — |
| `S6.AGUA` | Pone el prisma azul | Prisma azul sobre la tierra | `PICTO(gota)` | — | «Give it water.» | — |
| `S6.BROTE` | Enrosca un tallo | Anillo de tallo a la altura 1. Opcional: rotación de muñeca con MediaPipe Hands | `MOOD(esperanza)`, mira arriba | — | «Look! A green sprout is growing!» | — |
| `S6.SOL` | Acerca el prisma amarillo | Prisma amarillo a un lado de Lúa | `PICTO(sol)` | `LIGHT` del lado del sol [hecho] | «Give it sun.» | — |
| `S6.FLORECE` | Corona con la flor | Marcador de la flor en lo alto del tallo | `CELEBRATE` con destellos dorados | Lado del sol | «The sun is shining! A beautiful, tall flower!» | `CELEBRA_CORTO` opcional |
| `S6.NOCHE` | Mete la silueta de la Luna en la ranura de noche | Deja de verse el marcador de la ranura | `RELAX` | `APAGADO` | «Night in the garden. Time to sleep, Lúa.» | `RONRONEO` opcional |

Corrección respecto al documento base: la «sombra de la Luna sobre Lúa» no se puede detectar, porque Lúa no tiene sensor de luz y la sombra depende de la linterna. Se sustituye por un gesto mecánico inequívoco, meter la silueta en la ranura de noche, con detección por oclusión.

Capa de RA visible: rayos desde la linterna (posición indicada por el adulto) que muestran por qué la sombra crece al acercar la luz.

### Retos

1. **¿Dónde está la semilla? (0–2).** Se esconde la semilla y se pone la flor encima. Lúa parpadea al descubrirla.
2. **Agua y sol (2–3).** Enroscar el tallo girando la muñeca. Azul es lluvia, amarillo es sol.
3. **Cuatro pasos (3–4).** Ordenar en la mesa semilla → agua → brote → flor con fruto y contar la secuencia **antes** de montarla.
4. **Sombras (4–5).** El adulto sostiene la linterna. Al alejarla, «Small shadow»; al acercarla, «Big shadow!».
5. **Jardín ampliado (5–6).** Una planta corta y un árbol de cinco alturas, regados por un camino del Set 1, y la historia contada en inglés.

**Tarjetas de modelo:** secuencias ilustradas del ciclo y siluetas para emparejar con su pieza.

### Contextos

En **Valeria+**: estructura sintáctica de relatos cronológicos, donde cada bloque añadido apoya una frase. En **Descubre con Lúa**: proyecto del huerto escolar y «Grow tall like a tree!» con el cuerpo.

### Puntos abiertos

Hay una incoherencia entre los tres tallos del kit y el árbol de cinco alturas del reto 5: o se amplía el kit, o se admiten bloques del Set 0 como tronco. Faltan por resolver los frutos (tamaño) y el material translúcido. Entradas de catálogo nuevas: `MOOD(ternura)`, `MOOD(esperanza)`, `PICTO(semilla, gota, sol)`, celebración dorada.

---

## 7. Macro-escenario interoperable

| Inicio | Transición | Destino |
|---|---|---|
| Set 4: el soplo… | …empuja una esfera en el tramo de salida de la rampa (Set 3)… | …que golpea un resonador (Set 2) |
| Set 6: Lúa llega al jardín… | …tras cruzar el puente **fijo** (Set 5)… | …recorriendo el camino táctil (Set 1) |

Viabilidad [por verificar]: un chorro de 4 mm no mueve una esfera de 38 mm en pendiente. Solo puede ponerla en marcha en un tramo plano de salida. El macro-escenario se prototipa cuando cada set funcione por separado y no condiciona los STL individuales, más allá de compartir el sistema de encaje.

## 8. Resumen de STL por fase de desarrollo

| Fase | Piezas a imprimir primero | Qué se valida |
|---|---|---|
| 1 | Probeta de encaje G y E (varias tolerancias) | Valor de P (D1), ajuste en el PLA de masque3d |
| 2 | Kit Lúa completo + zócalo + 3 placas | Orientación forzada, marcador del lomo (D2) |
| 3 | Set 1 completo | Grafo del camino, lateralidad, luces direccionales |
| 4 | Viga, fulcro y masas (Set 5) | Detección de ángulo, lastre, rozamiento |
| 5 | Rampa articulada, pilares y esferas (Set 3) | Ángulos reales, seguimiento de objetos |
| 6 | Set 6 | Rosca, oclusión de marcador |
| 7 | Tres variantes de cada resonador (Set 2) | Diferencia de tono audible y estable |
| 8 | Canal, codo, rotor y compuertas (Set 4), con embocadura de otro proveedor | Higiene, cojinete, umbrales |
