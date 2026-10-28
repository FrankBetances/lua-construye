# Construye con Lúa

Bloques pedagógicos que forman mundos de juguete STEAM. El niño construye y manipula, la tableta del adulto detecta el resultado físico, la app decide y Lúa reacciona en su pantalla.

> **La app decide. Lúa reacciona. Los bloques los mueve el niño. El adulto media siempre.**

Estado: diseño activo · versión de prueba V5 · octubre 2026.
Especificación detallada de los seis mundos: [`docs/SETS.md`](docs/SETS.md).

---

## 1. Qué es

Construye con Lúa es un sistema modular de bloques físicos para niños de 0 a 6 años. Con los bloques se montan seis mundos (caminos, estaciones, laboratorios y máquinas simples) donde ocurre un fenómeno observable que el niño provoca con las manos o con la boca. Ese fenómeno manda: después se le asignan objetivos de lenguaje, de inglés L2 mediante TPR y, cuando corresponde, de práctica de rehabilitación.

Hay dos puertas de entrada al mismo sistema de bloques, ambas offline:

| Puerta | Contexto | Quién opera la tableta |
|---|---|---|
| **Valeria+** | Hogar y sesión, participación familiar | Familia o profesional |
| **Descubre con Lúa** | Escuela infantil 0–6, inglés L2 y STEAM | Docente |

Valeria+ es una aplicación educativa y Descubre con Lúa un recurso escolar. Ninguno diagnostica ni trata.

## 2. Qué hace Lúa y qué no hace

Esta tabla corrige la versión anterior de este README, que atribuía a Lúa avanzar, hablar y sonar. Eso no es posible en ninguna versión del hardware.

| Lúa **sí** | Lúa **no** |
|---|---|
| Muestra expresiones, pictogramas, insignias y niveles en una pantalla circular de 240×240 px | Habla, suena ni escucha: no tiene altavoz ni micrófono |
| Enciende cuatro luces direccionales en el bloque-cuello (propuesta V5) | Se mueve sola: no tiene motores. **El niño la desplaza** |
| Ejecuta índices de catálogos flasheados que le envía la app por BLE | Mide, puntúa, decide ni guarda nada |

La voz está **solo** en la tableta del adulto. La vibración, si se aprueba, está **solo** en el bloque independiente Ronroneo (≥ 3 años, nunca en VIA+).

## 3. Arquitectura

```
  NIÑO ── mueve ──► BLOQUES PASIVOS (cuerpo de Lúa + mundos)
                          │  la cámara de la tableta ve el resultado físico
                          ▼
  TABLETA DEL ADULTO: sensor ciego local (ARCore + MediaPipe) ─► APP decide
                          │                                   │
             BLE: índice de catálogo                    voz y sugerencias
                          ▼                                   ▼ al adulto
  LÚA (cabeza V4 + placa V1 + cuello sellado)        ADULTO media y amplía
  pantalla · 4 luces direccionales (propuesta)
                          │
  RONRONEO (opcional, ≥3 años): bloque háptico independiente, BLE propio
```

Topología BLE en estrella: la app es el único central. Lúa y Ronroneo no se hablan entre sí. Cero vídeo, cero red, cero datos de los niños.

## 4. El contrato de interacción

Todo set se especifica con la misma cadena de cinco eslabones. Es la frontera entre el equipo de bloques (STL), el de RA y el de la app:

```
1. EVENTO FÍSICO      el niño coloca, desliza, sopla, golpea, equilibra, enrosca
2. DETECCIÓN          RA de la tableta (marcador, mano, cara, objeto)  ó  toque del adulto
3. DECISIÓN           la app compara con el objetivo del reto
4. REACCIÓN           Lúa (opcode) · luz (opcional) · Ronroneo (opcional)
5. PALABRA            voz de la tableta o frase sugerida al adulto
```

Reglas del contrato (**propuesta**, pendientes de la puerta clínica B3):

1. **Ningún evento depende solo de la RA.** El adulto siempre puede confirmar con un toque. La RA facilita, no condiciona la sesión.
2. **El orden importa:** primero el fenómeno físico, luego una pausa breve, después Lúa y al final la palabra. La voz nunca tapa el sonido o el movimiento que el niño acaba de provocar.
3. **Turno verbal frente a turno motor.** Durante el turno verbal (el niño debe contestar o vocalizar) todo queda quieto: Lúa estática, luces apagadas, sin vibración. Durante el turno motor, Lúa puede reaccionar al *resultado* con animaciones suaves. Esta distinción es nueva y necesita aprobación clínica.
4. **Error neutro:** el mundo muestra su consecuencia natural y Lúa queda serena, atenta o de aliento. Nunca expresión de reproche, nunca luz ni vibración como señal de error.
5. **La RA explica, no distrae.** Las capas visibles de RA en la tableta solo aparecen en la fase de ampliación, después de la acción. Durante la acción, la mirada del niño va a sus manos y a Lúa.
6. **Diseño universal (UDL):** ningún reto exige hablar para que Lúa reaccione. Señalar, gestos o pictogramas de CAA cuentan como respuesta.

## 5. Los seis mundos

| Set | Fenómeno (manda) | Gesto principal | Evento clave detectado | Reacción de Lúa | Tamaños |
|---|---|---|---|---|---|
| 1 · El Camino de Lúa | Orientación espacial, algoritmo tangible | Colocar baldosas, deslizar a Lúa | Camino continuo / interrumpido, llegada a meta | Atención, ánimo, luz del giro, celebración | Grande y estándar |
| 2 · Estación de Sonido y Eco | El sonido es vibración | Percutir, raspar | Golpe fuerte/débil, duración del raspado, ritmo | Calma o alegría tras el sonido, metrónomo visual | Estándar (≥ 3) |
| 3 · Laboratorio de Rampas y Gravedad | Gravedad y fricción | Esperar y soltar | Salida, llegada, tiempo de recorrido | Espera expectante, «rápido» o «caracol» | Grande y estándar |
| 4 · Máquina de Soplo y Viento | Flujo de aire | Soplar | Giro del rotor, compuerta abatida, soplo sostenido | Remolino, insignia, aro de progreso en pantalla | Estándar (≥ 3) |
| 5 · Puente de Equilibrio y Fuerza | Palanca y centro de gravedad | Colocar masas | Ángulo de la viga, equilibrio | Sorpresa, alivio, luz del lado que baja | Grande y estándar |
| 6 · Jardín del Sol, la Sombra y la Semilla | Crecimiento vegetal, luz y sombra | Sembrar, enroscar, interponer | Semilla, agua, sol, altura, noche | Ternura, esperanza, celebración, descanso | Grande y estándar |

Además hay un **Kit Lúa (Set 0)**, común a todos: cuerpo de bloques, bloque dorsal con marcador y zócalo universal. Define la geometría que heredan los demás.

## 6. Sistema de encaje y tamaños

Hay dos escalas con relación 2:1 y encaje cruzado sin adaptadores:

| Escala | Edad | Paso modular | Uso |
|---|---|---|---|
| Bloque grande (G) | 0–3 años | 2P | Todo lo que vaya a manos de menores de 36 meses |
| Bloque estándar (E) | 3–6 años | P | Piezas de precisión, masas pequeñas, canales de soplo |

El valor de P está pendiente de la decisión **D1** (ver §12). Hasta entonces, todo STL se modela **paramétrico en P** y nunca en milímetros fijos. La nomenclatura pública describe los bloques por su módulo de encaje y nunca por marcas de terceros (B4).

## 7. Seguridad: lo afirmado y lo pendiente

**Criterio de diseño:** las piezas de escala G no caben en el cilindro de piezas pequeñas de EN 71-1, tienen paredes estructurales ≥ 3,2 mm y carecen de imanes, adhesivos o subpiezas desprendibles. Ninguna pieza tiene electrónica salvo la unidad sellada de Lúa y Ronroneo.

**No se declara ninguna conformidad hasta disponer de ensayo de laboratorio.** Faltan por verificar, como mínimo: EN 71-1/2/3; EN 62115 para la unidad de Lúa y Ronroneo; la Directiva de equipos radioeléctricos y sus actos delegados de ciberseguridad y privacidad; el calendario del nuevo Reglamento europeo de seguridad de juguetes; y la extraibilidad de baterías del Reglamento (UE) 2023/1542, que puede chocar con una batería sellada.

Alertas abiertas por el diseño de los sets, desarrolladas en [`docs/SETS.md`](docs/SETS.md):

- La esfera de Ø 38 mm (Set 3) supera el cilindro de piezas pequeñas, pero las esferas tienen requisitos propios para menores de 3 años. **Por verificar** antes de usarla en ese tramo.
- La pared de 1,5 mm del resonador rojo (Set 2) incumple el mínimo de 3,2 mm.
- Las embocaduras de soplo (Set 4) entran en la boca. No deben imprimirse en PLA por FDM, y cada niño debe tener la suya, también en el aula.
- Las masas lastradas (Set 5) y los frutos (Set 6) pueden liberar piezas pequeñas si se rompen.
- Las piezas de escala E acabarán en hogares con hermanos menores de 3 años. Hay que definir su etiquetado y su guía para familias.

## 8. Qué dice la evidencia y qué no

| Afirmación | Respaldo disponible | Cómo usarla |
|---|---|---|
| El juego de bloques guiado por un adulto aumenta el lenguaje espacial | BrickSmart (CHI 2025): 24 díadas, niños de 6–8 años, una sesión | Justifica que la app sugiera vocabulario espacial **al adulto**. No extrapolar resultados a 0–5 años |
| Construir copiando un modelo se asocia con la numeración | Gilligan-Lee *et al.* 2023: 116 niños de 4 años, explica ~5 % de la varianza (14,5 % en familias de menor renta) | Es asociación, no causalidad. Justifica incluir **tarjetas de modelo** en cada set |
| La terapia basada en bloques mejora la interacción social en TEA | Narzisi *et al.* 2021: 19 estudios, un solo ECA, calidad global baja | Los roles cooperativos (ingeniero/proveedor/constructor) son una inspiración, no un tratamiento validado |
| STEAM inclusivo con UDL en 0–8 años | Wade *et al.* 2023: artículo conceptual, sin datos | Marco de diseño (representación, implicación, expresión), no evidencia de eficacia |
| Los ejercicios de soplo mejoran el habla o el cierre velofaríngeo | **No respaldado** por la literatura de ejercicios oromotores no verbales | El Set 4 se presenta como juego de control respiratorio y causa-efecto, **no** como tratamiento del escape nasal ni de las dislalias |

Las hipótesis clínicas (Ronroneo como metrónomo táctil en hipoacusia o implante coclear, desensibilización táctil en TEA) se tratan como hipótesis por validar y nunca como beneficios.

## 9. Estructura del repositorio (propuesta)

```
construye-con-lua/
├── README.md                  este documento
├── docs/
│   ├── SETS.md                especificación de los seis mundos + Kit Lúa
│   ├── CONTRATO-EVENTOS.md    catálogo único de eventos y reacciones (a extraer de SETS.md)
│   ├── ENCAJE.md              parámetros del sistema modular, tolerancias, probetas
│   └── SEGURIDAD.md           matriz de requisitos y ensayos pendientes
├── sets/
│   └── S1-camino/             (igual para S0…S6)
│       ├── cad/               fuentes paramétricas (Blender bpy / CAD)
│       ├── stl/               masters de fabricación, uno por código de pieza
│       ├── ar/                mallas simplificadas para Filament (< 100 KB) + marcadores
│       ├── tarjetas/          tarjetas de modelo y de reto (impresión en papel)
│       └── pruebas/           informes de impresión, ajuste y detección
└── catalogos/                 índices de expresiones, pictogramas y patrones de luz
```

Regla de nombres: **un código de pieza = un STL = una malla RA = un marcador**. Ejemplo: `S1-REC-RUG-G` es la baldosa recta rugosa de escala grande.

## 10. De la idea al prototipo: las puertas de cada set

| Fase | Producto | Puerta para avanzar |
|---|---|---|
| 1. Experiencia | Ficha del set en `SETS.md` | Un adulto la entiende en menos de dos minutos |
| 2. Contrato | Tabla evento → detección → reacción cerrada | Cada evento tiene alternativa por toque del adulto |
| 3. Geometría | CAD paramétrico + STL de prueba | Probeta de encaje validada con masque3d |
| 4. Impresión | Piezas físicas | Revisión de seguridad de diseño (§7) |
| 5. Detección | Prueba de RA con piezas reales | Tasa de detección aceptable con la luz de un aula real (umbral por definir) |
| 6. Integración | App + Lúa + piezas | Latencia y orden de reacción conformes al contrato |
| 7. Puerta clínica | Revisión de opcodes, luz y vibración (B3) | Aprobación |
| 8. Piloto | Sesiones con familias o aula | Comprensión del adulto, implicación, incidencias |

## 11. Orden de desarrollo recomendado

**Empezar por el Set 1.** Tiene la geometría más simple, obliga a cerrar el sistema de encaje, el zócalo universal y el marcador del lomo de Lúa, y su detección es discreta (está o no está la baldosa), la más fácil de validar. Además usa las cuatro luces direccionales con un significado inequívoco. Todo lo que se aprenda ahí lo heredan los demás sets.

Orden propuesto: **S0 + S1 → S5 → S3 → S6 → S2 → S4.** El Set 5 reutiliza los pilares y valida la detección de ángulos. El Set 3 añade el seguimiento de objetos en movimiento. El Set 6 introduce la rosca y la óptica. El Set 2 exige resolver la acústica del material impreso. El Set 4 va el último porque concentra los problemas de higiene, la detección facial y el ajuste de su planteamiento clínico.

## 12. Decisiones abiertas

Heredadas del README de Lúa: **B1** (ubicación de la batería), **B2** (integración electrónica de Ronroneo), **B3** (aprobación clínica de luz, vibración y opcodes), **B4** (denominación pública), **B5** (pin libre para el anillo de luz).

Nuevas, que surgen de este diseño:

| Código | Decisión | Recomendación |
|---|---|---|
| **D1** | Valor del paso P: compatible de hecho con los bloques que las familias ya tienen, o propio e incompatible | Compatible de hecho (P = 8 mm en E, 16 mm en G), con revisión previa de propiedad industrial. Sin nombrar marcas |
| **D2** | Tipo de marcador RA: imagen texturada (imágenes aumentadas de ARCore) o fiduciales en relieve/impresos | Probar ambos en el Set 1 con piezas reales antes de fijarlo para el resto |
| **D3** | Distinción entre turno verbal y turno motor (contrato, regla 3) | Llevarla a la puerta clínica junto con B3 |
| **D4** | Cámara trasera (bloques) y frontal (cara) en el Set 4: uso simultáneo o por fases | Por fases. El análisis facial solo en un modo de praxias de Valeria+ |
| **D5** | Material de embocaduras y de piezas en contacto con la boca | Pieza extraíble de material apto para contacto bucal y desinfectable, de un proveedor distinto a la impresión FDM |
| **D6** | Lastre de las masas del Set 5 | Inserto metálico único encapsulado, con ensayo de caída. Nunca perdigones ni granalla |

---

*Todo el apoyo digital es offline. No hay red ni datos de los niños.*
