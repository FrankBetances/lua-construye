# Ejemplo Set 1 · El Camino de Lúa

Set elegido: **Set 1, El Camino de Lúa**, el primero del plan (README, «Empezar por el Set 1»; SETS.md, fase 3, «Set 1 completo»). Es el mundo de geometría más simple que el propio documento manda imprimir primero.

No se modeló el cuerpo de Lúa. `K-CUELLO` lo imprime el fabricante. Las fichas de escala E no se generan: el punto abierto del Set 1 recomienda dejarlas fuera del kit de 0 a 3 años.

## Qué salió en esta máquina

- SpecTopologyAgent: exit 0
- ManifoldCadAgent: exit 0
- SafetyNormsAuditor: exit 0
- AssemblySequencerAgent: exit 0
- TechnicalIllustrationAgent: exit 0
- PedagogyManualAgent: exit 0
- ManualPublisherAgent: exit 0

Auditoría de diseño: apta. No es un ensayo EN 71-1 de laboratorio y no declara conformidad.

## STL

- `sets/S1-camino/stl/S1-REC-LIS-G.stl` (236 triángulos, 288749.5 mm³)
- `sets/S1-camino/stl/S1-REC-RUG-G.stl` (652 triángulos, 291768.6 mm³)
- `sets/S1-camino/stl/S1-CUR-G.stl` (304 triángulos, 291568.0 mm³)
- `sets/S1-camino/stl/S1-TEE-G.stl` (334 triángulos, 289287.0 mm³)
- `sets/S1-camino/stl/S1-CMD-AVA-G.stl` (232 triángulos, 14121.9 mm³)
- `sets/S1-camino/stl/S1-CMD-PAR-G.stl` (168 triángulos, 14142.5 mm³)
- `sets/S1-camino/stl/S1-CMD-GIR-G.stl` (332 triángulos, 14010.5 mm³)
- `sets/S1-camino/stl/S1-CMD-SAL-G.stl` (296 triángulos, 14020.1 mm³)
- `sets/S1-camino/stl/S1-DEST-PARQUE.stl` (248 triángulos, 25059.0 mm³)
- `sets/S1-camino/stl/S1-DEST-CAMA.stl` (200 triángulos, 25106.7 mm³)
- `sets/S1-camino/stl/K-ZOCALO-G.stl` (568 triángulos, 450740.9 mm³)
- `sets/S1-camino/stl/K-PLACA-INICIO.stl` (232 triángulos, 25073.9 mm³)
- `sets/S1-camino/stl/K-PLACA-META.stl` (344 triángulos, 25080.7 mm³)
- `sets/S1-camino/stl/K-PATIN-G.stl` (3192 triángulos, 25778.5 mm³)

## GLB (menos de 100 KB)

- `sets/S1-camino/ar/S1-REC-LIS-G.glb` (3644 bytes)
- `sets/S1-camino/ar/S1-REC-RUG-G.glb` (6336 bytes)
- `sets/S1-camino/ar/S1-CUR-G.glb` (3448 bytes)
- `sets/S1-camino/ar/S1-TEE-G.glb` (4864 bytes)
- `sets/S1-camino/ar/S1-CMD-AVA-G.glb` (2876 bytes)
- `sets/S1-camino/ar/S1-CMD-PAR-G.glb` (2296 bytes)
- `sets/S1-camino/ar/S1-CMD-GIR-G.glb` (3740 bytes)
- `sets/S1-camino/ar/S1-CMD-SAL-G.glb` (3452 bytes)
- `sets/S1-camino/ar/S1-DEST-PARQUE.glb` (3084 bytes)
- `sets/S1-camino/ar/S1-DEST-CAMA.glb` (2596 bytes)
- `sets/S1-camino/ar/K-ZOCALO-G.glb` (6380 bytes)
- `sets/S1-camino/ar/K-PLACA-INICIO.glb` (2892 bytes)
- `sets/S1-camino/ar/K-PLACA-META.glb` (3752 bytes)
- `sets/S1-camino/ar/K-PATIN-G.glb` (39024 bytes)

## Documentación de montaje

- `sets/S1-camino/pruebas/bom.json`
- `sets/S1-camino/pruebas/dag.json`
- `sets/S1-camino/pruebas/secuencia.json`
- `sets/S1-camino/pruebas/auditoria.json`
- `sets/S1-camino/tarjetas/recta-despiece.svg` y `.png`
- `sets/S1-camino/tarjetas/recta-planta.svg`, `curva-planta.svg`, `te-planta.svg`
- `sets/S1-camino/manual/manual.typ` y `manual.pdf`
- `sets/S1-camino/manual/tarjeta-recta.typ` y `tarjeta-recta.pdf`
- `sets/S1-camino/manual/textos.json`

## Hipótesis que el documento no cierra

Planta de baldosa y zócalo: 4 × 31,80 mm. SETS no da milímetros del cuerpo de Lúa; ancho = 2 módulos de cuerpo + 2 módulos.

La ranura mide 12 mm de ancho, como dice SETS, y 8 mm de fondo para dejar 11,20 mm de suelo. La unión entre baldosas es una cola de milano vertical: SETS deja abierta la probeta de encaje y el reglamento admite espiga, no fricción ni adhesivo.

## Qué no se verificó aquí

- No hay impresora Masque3D en esta máquina: no se imprimió ninguna pieza.
- No hay ensayo de laboratorio EN 71-1, EN 71-2 ni EN 71-3.
- No se comprobó el ajuste real de la cola de milano ni el deslizamiento del patín en PLA.
- D1 (el valor de P) sigue abierta. La planta usa el módulo de 31,80 mm del reglamento de piezas.
- `CCLREADME.md` no está en el repositorio. Se leyeron `docs/SETS.md` y `README.md`.
