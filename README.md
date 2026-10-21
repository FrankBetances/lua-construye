# 🧱 Lúa Construye

> **Sistema modular tangible de construcción y robótica manipulativa educativa-clínica.**  
> Basado en el estándar mecánico Duplo (paso de 31,80 mm), modelado proceduralmente en Blender (*Python `bpy`*) para impresión 3D FDM/resina y sincronizado con software pedagógico offline (*Descubre con Lúa*) y terapéutico (*Ecosistema Valeria*).

---

## 🧭 Visión y Arquitectura del Ecosistema

**Lúa Construye** unifica la manipulación física tangible con el pensamiento computacional y la estimulación neurofuncional en la primera infancia (0 a 6 años). El sistema establece una frontera estricta entre dos mundos:

1. **Entorno 3D Físico (Blender Headless / Python `bpy`):** Generación algorítmica de geometría poligonal, tolerancias mecánicas milimétricas y exportación directa a STL/3MF sin dependencia de suites CAD privativas.
2. **Entorno de Software (Flutter en *Descubre con Lúa*):** Catálogo declarativo estructurado en JSON, trazado vectorial directo en `CustomPainter` (cero emojis, cero fuentes externas), audio TPR pregrabado en inglés con verificación criptográfica SHA-256 y arquitectura **Zero-Network / Zero-PHI**.

```
                   ESTÁNDAR MECÁNICO DUPLO (31,80 mm)
 ┌───────────────────────────────────────────────────────────────────┐
 │        Piezas Núcleo (Core): Placas 8x8, bloques 2x2, 2x4,        │
 │         rampas continuas 15°/30° y ejes de giro modular           │
 └─────────────────────────────────┬─────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
 GAMA «DESCUBRE CON LÚA»                               GAMA «VALERIA»
 (Escuela / LOMLOE / STEAM)                      (Hogar / Clínica / Estimulación)
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│ • Baldosas de dirección plana   │                 │ • Relieves hápticos/sensoriales │
│ • Ranuras de guiado de esferas  │ ◄─ Intercambio ─► │ • Cilindros de prensión gradual │
│ • Bloques huecos resonadores    │      mecánico   │ • Canales para praxias de soplo │
│ • Fichas algorítmicas de giro   │   (31,8 mm)     │ • Pesos calibrados propiocepción│
└────────────────┬────────────────┘                 └────────────────┬────────────────┘
                 │                                                   │
                 ▼                                                   ▼
       App Descubre con Lúa                                 Ecosistema Valeria
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│ • assets/content/steam/*.json   │                 │ • Plataforma clínica / web      │
│ • CustomPainter (cero emojis)   │                 │ • Registro longitudinal de hitos│
│ • TPR English (SHA pregrabado)  │                 │ • Cribado neurodesarrollo       │
│ • Zero Network / Zero PHI       │                 │ • Cumplimiento MDR / RGPD salud │
└─────────────────────────────────┘                 └─────────────────────────────────┘
```

---

## 📐 1. Especificación Mecánica en Blender (Métrica Real)

Toda la matriz física se diseña en milímetros reales. En Blender la escena se configura con escala métrica estricta:
```python
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'MILLIMETERS'
scene.unit_settings.scale_length = 0.001
```

### Cotas Críticas del Estándar

```
          ┌─── 9.40 mm ───┐
          │    (Tetón)    │  ▲ 4.50 mm
     ─────┴───────────────┴─────
    │                          │  ▲ 19.20 mm (altura base del bloque)
    │                          │  │
    └──────────────────────────┘  ▼
    ◄──────── 31.80 mm ────────► (Paso modular entre centros de tetón)
```

| Parámetro Mecánico | Valor Nominal | Tolerancia / Observación |
| :--- | :--- | :--- |
| **Paso modular (*stud pitch*)** | `31,80 mm` | Distancia entre centros de tetones contiguos en ejes X e Y. |
| **Diámetro del tetón (*stud*)** | `9,40 mm` | Cilindro superior de inserción por fricción. |
| **Altura del tetón (*stud height*)** | `4,50 mm` | Altura efectiva del conector superior. |
| **Altura base del bloque** | `19,20 mm` | Altura estándar de bloque (sin incluir tetón superior). |
| **Grosor de pared exterior** | `1,50 - 1,60 mm` | Rigidez estructural y ajuste por fricción sin riesgo de fractura. |
| **Tubo interior de retención** | `Øext 13,20 mm` | Cilindros huecos interiores (*clutch power*) para bloques 2×2 y 2×4. |
| **Offset de encaje (Impresión 3D)** | `Δ = 0,15 - 0,20 mm` | Compensación diametral radial según contracción térmica de PLA/PETG. |
| **Seguridad Infantil (EN 71-1)** | `> 31,75 mm` | Todas las piezas superan el cilindro de partes pequeñas para < 36 meses. |

---

## ⚙️ 2. Automatización Procedural: Script Headless (`tools/blender/generar_sets.py`)

Para garantizar reproducibilidad absoluta sin depender de ajustes manuales en interfaz gráfica, las piezas base se generan desde terminal ejecutando Blender en segundo plano:

```bash
blender -b -P tools/blender/generar_sets.py -- --tipo lua_caminos --offset 0.15
```

### Código Fuente de Generación Paramétrica

```python
"""
Generador procedural de bloques compatibles Duplo para Blender 4.x.
Ejecución:
    blender -b -P tools/blender/generar_sets.py -- --tipo lua_caminos
"""

import math
import sys
import bpy

# Constantes estándar Duplo (metros en Blender con scale_length = 0.001)
UNIT_MM = 0.001
STUD_PITCH = 31.8 * UNIT_MM
STUD_DIAMETER = 9.4 * UNIT_MM
STUD_HEIGHT = 4.5 * UNIT_MM
BLOCK_HEIGHT = 19.2 * UNIT_MM
WALL_THICKNESS = 1.5 * UNIT_MM


def limpiar_escena():
    """Limpia todos los objetos y colecciones de la escena."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def crear_bloque_base(nombre: str, studs_x: int, studs_y: int):
    """Genera un bloque sólido con tetones superiores estandarizados."""
    ancho = studs_x * STUD_PITCH
    largo = studs_y * STUD_PITCH

    # Cuerpo principal
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(ancho / 2, largo / 2, BLOCK_HEIGHT / 2)
    )
    bloque = bpy.context.active_object
    bloque.name = nombre
    bloque.scale = (ancho, largo, BLOCK_HEIGHT)
    bpy.ops.object.transform_apply(scale=True)

    # Generación paramétrica de studs superiores
    for ix in range(studs_x):
        for iy in range(studs_y):
            cx = (ix + 0.5) * STUD_PITCH
            cy = (iy + 0.5) * STUD_PITCH
            cz = BLOCK_HEIGHT + (STUD_HEIGHT / 2)

            bpy.ops.mesh.primitive_cylinder_add(
                radius=STUD_DIAMETER / 2,
                depth=STUD_HEIGHT,
                location=(cx, cy, cz)
            )
            stud = bpy.context.active_object

            # Unión booleana
            mod = bloque.modifiers.new(type="BOOLEAN", name=f"stud_{ix}_{iy}")
            mod.operation = "UNION"
            mod.object = stud
            bpy.context.view_layer.objects.active = bloque
            bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(stud, do_unlink=True)

    return bloque


def aplicar_ranura_camino(bloque, tipo="recta"):
    """Añade ranura algorítmica para Lúa Camiños (ancho 12 mm, profundidad 4 mm)."""
    ancho_ranura = 12.0 * UNIT_MM
    profundidad = 4.0 * UNIT_MM

    if tipo == "recta":
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(
                bloque.dimensions.x / 2,
                bloque.dimensions.y / 2,
                BLOCK_HEIGHT - (profundidad / 2),
            ),
        )
        cortador = bpy.context.active_object
        cortador.scale = (ancho_ranura, bloque.dimensions.y + 0.002, profundidad)
        bpy.ops.object.transform_apply(scale=True)

        mod = bloque.modifiers.new(type="BOOLEAN", name="corte_camino")
        mod.operation = "DIFFERENCE"
        mod.object = cortador
        bpy.context.view_layer.objects.active = bloque
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cortador, do_unlink=True)


def exportar_stl(objeto, filepath: str):
    """Exporta el objeto seleccionado a STL con escala y triangulación validada."""
    bpy.ops.object.select_all(action="DESELECT")
    objeto.select_set(True)
    bpy.ops.wm.stl_export(filepath=filepath)


if __name__ == "__main__":
    limpiar_escena()
    # Generación de baldosa 2x2 para Lúa Camiños
    pieza = crear_bloque_base("lua_baldosa_recta_2x2", 2, 2)
    aplicar_ranura_camino(pieza, "recta")
    exportar_stl(pieza, "build/stl/lua_baldosa_recta.stl")
```

---

## 🔀 3. Matriz de Compatibilidad: Gama Lúa vs. Gama Valeria

Ambas familias comparten el plano de anclaje inferior y superior (100% interoperables mecánicamente). Difieren en su **cara funcional superior**:

| Gama | Pieza en Blender | Característica Física | Uso Pedagógico / Clínico |
| :--- | :--- | :--- | :--- |
| **Lúa** | `lua_camino_recta_2x2` | Ranura plana de paso de 12 mm continuo. | Algoritmos tangibles, secuenciación espacial. |
| **Lúa** | `lua_camino_curva_2x2` | Arco cuadrante con radio de curvatura de 31,8 mm. | Cambio de dirección ortogonal, lateralidad. |
| **Lúa** | `lua_marcador_gata` | Zócalo con el perfil de la gata Lúa en relieve 2 mm. | Objeto agente tangible (posición inicial/objetivo). |
| **Valeria** | `val_textura_estriada` | Modificador `Displace` con patrón de estrías ±1,5 mm. | Estimulación táctil, propiocepción palmar. |
| **Valeria** | `val_cilindro_presion` | Cilindro de inserción con pestaña de resistencia calibrada. | Fuerza de prensión bimanual, pinza digital. |
| **Valeria** | `val_resonador_acustico` | Cavidad interna resonante amortiguada (bloque hueco). | Discriminación acústica manual (percusión sorda/aguda). |

---

## 📱 4. Arquitectura de Software en Flutter (*Descubre con Lúa*)

La app de soporte opera bajo **principios de máxima austeridad técnica**:
* 🚫 Cero paquetes externos en `pubspec.yaml` para renderizado.
* 🚫 Cero llamadas de red / telemetría (**Zero-Network**).
* 🚫 Cero emojis o tipografías de iconos volátiles.
* 🚫 Cero inferencia de IA en el dispositivo (**Zero-PHI**).

### Estructura de Archivos

```
assets/content/steam/
  └── sets_construccion.json       <-- Datos de retos e inventario (bilingüe gl/es)
lib/data/models/
  └── steam_set.dart               <-- Modelo inmutable y tipado confromJson
lib/features/juega/
  └── steam_silueta_painter.dart   <-- Trazado vectorial de piezas en Canvas
tools/
  └── check_steam_sets.py          <-- Gate que valida hashes SHA-256 de audios TPR
```

### Esquema de Datos Declarativo (`assets/content/steam/sets_construccion.json`)

```json
{
  "sets": [
    {
      "id": "lua_caminos_algoritmos",
      "curso": "3-4",
      "titulo": {
        "gl": "Lúa Camiños: Algoritmos na alfombra",
        "es": "Lúa Caminos: Algoritmos en la alfombra"
      },
      "obxectivo": {
        "gl": "Descubrir que as ordes van paso a paso e que un xiro cambia a dirección.",
        "es": "Descubrir que las órdenes van paso a paso y que un giro cambia la dirección."
      },
      "aviso_seguridade": {
        "gl": "Supervisión continuada da persoa adulta. Pezas maiores de 31 mm.",
        "es": "Supervisión continuada de la persona adulta. Piezas mayores de 31 mm."
      },
      "inventario": [
        { "id": "lua_recta", "cantidade": 4, "silueta": "ranura_recta" },
        { "id": "lua_curva", "cantidade": 4, "silueta": "ranura_curva" },
        { "id": "val_textura", "cantidade": 2, "silueta": "relieve_ondas", "orixe": "valeria" }
      ],
      "retos": [
        {
          "fase": 1,
          "consigna": {
            "gl": "Colocade dúas pezas rectas e pasade a gata con dous pasos.",
            "es": "Colocad dos piezas rectas y pasad a la gata con dos pasos."
          },
          "tpr": {
            "texto": "Step forward",
            "audio_sha": "sha256_b2938a192847cdef482910482910482910482910482910482910482910482910"
          }
        }
      ]
    }
  ]
}
```

### Renderizado Vectorial Autónomo (`lib/features/juega/steam_silueta_painter.dart`)

Cada pieza del inventario se dibuja vectorialmente mediante primitivas matemáticas de Flutter Canvas:

```dart
import 'package:flutter/material.dart';

/// Dibuja vectorialmente las siluetas del inventario sin fuentes ni imágenes externas.
class SteamSiluetaPainter extends CustomPainter {
  final String silueta;
  final Color color;

  const SteamSiluetaPainter({
    required this.silueta,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    final w = size.width;
    final h = size.height;

    switch (silueta) {
      case 'ranura_recta':
        // Bloque con canal central recto
        canvas.drawRect(Rect.fromLTWH(0, 0, w, h), paint);
        paint.strokeWidth = 3.0;
        canvas.drawLine(Offset(w / 2, 0), Offset(w / 2, h), paint);
        break;

      case 'ranura_curva':
        // Bloque con canal en arco cuadrante
        canvas.drawRect(Rect.fromLTWH(0, 0, w, h), paint);
        final path = Path()
          ..moveTo(0, h / 2)
          ..quadraticBezierTo(w / 2, h / 2, w / 2, h);
        canvas.drawPath(path, paint);
        break;

      case 'relieve_ondas':
        // Pieza sensorial tipo Valeria: estrías táctiles
        canvas.drawRect(Rect.fromLTWH(0, 0, w, h), paint);
        for (var i = 1; i <= 3; i++) {
          final y = h * (i / 4.0);
          canvas.drawLine(Offset(w * 0.2, y), Offset(w * 0.8, y), paint);
        }
        break;

      default:
        // Contenedor modular neutro
        canvas.drawRect(Rect.fromLTWH(0, 0, w, h), paint);
    }
  }

  @override
  bool shouldRepaint(covariant SteamSiluetaPainter oldDelegate) {
    return oldDelegate.silueta != silueta || oldDelegate.color != color;
  }
}
```

---

## 🗓️ 5. Plan de Trabajo Técnico (4 Hitos / 8 Semanas)

```
Semanas:  [1 - 2]            [3 - 4]            [5 - 6]            [7 - 8]
        ┌───────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐
        │  HITO 1   │ ───► │  HITO 2   │ ───► │  HITO 3   │ ───► │  HITO 4   │
        └───────────┘      └───────────┘      └───────────┘      └───────────┘
         Pipeline 3D        Datos JSON         UI Canvas &         Testing,
          en Blender       Sets & Modelos       Voces TPR         CI (21 Gates)
```

- **Hito 1: Pipeline de Modelado en Blender (Semanas 1–2)**
  - Script `tools/blender/generar_sets.py` con generación paramétrica de bloques 2×2, 2×4 y bases 8×8.
  - Modelos de la Gama Lúa: `lua_recta.blend`, `lua_curva.blend`, `lua_interseccion.blend`.
  - Modelos de la Gama Valeria: `val_ondas.blend`, `val_puntos.blend`, `val_cilindro.blend`.
  - Exportación de STLs de prueba con offset de encaje de 0,15 mm para calibración en impresora 3D.
- **Hito 2: Integración de Datos en Flutter (Semanas 3–4)**
  - `assets/content/steam/sets_construccion.json` con los 5 sets curriculares.
  - `lib/data/models/steam_set.dart` con deserialización inmutable y tipada.
  - Validador `tools/check_steam_sets.py` integrado en `tools/gates.sh` para comprobar bilingüismo estricto (gl/es) y campos de seguridad.
- **Hito 3: UI, Trazado Vectorial y Cobertura de Voz (Semanas 5–6)**
  - Implementación de `SteamSiluetaPainter` para visualización limpia del inventario sin emojis.
  - Extracción de consignas y órdenes TPR en inglés hacia el corpus vocal.
  - Síntesis neuronal de locuciones pregrabadas (`export_voice_corpus.py` → `generate_voice_assets.py`).
  - Verificación de renderizado de audio condicionado a la existencia física del hash SHA en `assets/voice/`.
- **Hito 4: Verificación, Golden Tests y CI (Semanas 7–8)**
  - `test/features/steam_sets_test.dart`: comprobación offline del flujo de asamblea y ausencia total de sockets o peticiones de red.
  - `test/capturas_test.dart`: regeneración de capturas automáticas para el manual técnico.
  - Validación completa con los **21 gates en verde** en `tools/gates.sh`.

---

## ⚖️ 6. Evaluación de Viabilidad y Veredicto Arquitectónico

| Componente Evaluado | Descripción Técnica | Desafío Real Identificado | Veredicto |
| :--- | :--- | :--- | :---: |
| **Generación procedural en Blender headless vía Python (`bpy`)** | Modelar todo el sistema de bloques con scripts de terminal para exportar STLs idénticos y repetibles. | Curva de ajuste fino de tolerancias: cada impresora y filamento encoge diferente; exige calibrar el offset radial (0,15 mm vs 0,20 mm) en la primera tirada. | **APLICABLE YA** |
| **Renderizado de siluetas de piezas en Flutter con `CustomPainter`** | Dibujo procedural en canvas nativo dentro de la app para no inflar el bundle ni usar paquetes externos. | Mantenimiento manual del trazado si se añaden decenas de piezas complejas al catálogo. | **APLICABLE YA** |
| **Visor interactivo 3D embebido en la app para la docente** | Incorporar un renderizador WebGL/OpenGL en Flutter para ver e interactuar con los modelos 3D en tiempo real. | Requiere dependencias pesadas en `pubspec.yaml`, viola la directriz de cero librerías externas y distrae a la docente en una asamblea de 5 minutos donde solo necesita el inventario 2D. | **ESPECULATIVA (RECHAZADA)** |

---

## 🔒 Licencia y Cumplimiento Normativo

- **Seguridad en Juguetes:** Geometría conforme a la Directiva Europea 2009/48/CE y norma EN 71-1 (dimensiones mínimas superiores a 31,75 mm para prevención de asfixia en menores de 36 meses).
- **Protección de Datos:** Arquitectura conforme a RGPD y Directiva MDR (UE) 2017/745 para piezas de la Gama Valeria (cero recopilación de identificadores de salud infantil en el dispositivo).
