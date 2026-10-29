"""Cotas del ejemplo Set 1 · El Camino de Lúa.

Todas las piezas de este ejemplo salen de docs/SETS.md (Set 1 y las
dependencias del Set 0 que la escena nombra). No se añaden piezas.

Unidad de planta: módulo Duplo del reglamento Earlify, 31,80 mm.
D1 del README (paso de 8 / 16 mm) sigue abierta; el generador no
la cierra. La planta se expresa en ese módulo para que cada maestro
quepa en la cama FDM 220 × 220 × 270 mm y no entre en el cilindro
de piezas pequeñas.

Ancho de la baldosa: SETS propone «ancho del cuerpo de Lúa + 2
módulos». El cuerpo no tiene milímetros en el documento. Se toma
cuerpo = 2 módulos y se suma 2 módulos: planta cuadrada de 4 módulos.
La hipótesis queda declarada en el BOM; no es una pieza nueva.
"""

from __future__ import annotations

# --- Reglamento de pieza (Earlify) ---
MODULO_MM = 31.80
ALTURA_BASE_MM = 19.20
TETON_DIAMETRO_MM = 9.40
TETON_ALTURA_MM = 4.50
HOLGURA_MM = 0.20
PARED_MIN_MM = 3.20
ROSCA_MIN_MM = 3.00

# Cama citada para FDM de sobremesa (Masque3D).
CAMA_MM = (220.0, 220.0, 270.0)

# EN 71-1. El umbral de 31,75 mm es el del reglamento del proyecto
# (el cilindro de la norma mide 31,7 mm de diámetro interior).
CILINDRO_DIAMETRO_MM = 31.75
CILINDRO_PROFUNDIDAD_MM = 57.1
ESFERA_G_MIN_MM = 44.5

# --- Set 1, datos de origen ---
RANURA_ANCHO_MM = 12.0
RELIEVE_MM = 1.5

# Profundidad de ranura: no está en SETS. Se fija para dejar suelo
# 19,20 − 8,00 = 11,20 mm, por encima de la pared mínima.
RANURA_PROF_MM = 8.0

# Chaflán de boca. SETS pide chaflán y no da el milímetro.
# Se usa la pared mínima para que el ensanche sea imprimible.
CHAFLAN_MM = 3.20
CHAFLAN_LARGO_MM = 8.0

# Planta. 4 × 31,80 = 127,20 mm. Cabe en 220 mm.
BALDOSA_MM = 4.0 * MODULO_MM  # 127.20

# Cola de milano (espiga). El punto abierto de SETS pide una unión
# que resista el empuje; el reglamento admite espiga, no fricción.
CUELLO_ANCHO_MM = 14.0
CUELLO_FONDO_MM = 4.80  # por encima de 3,20 para que la cintura no quede en el límite
BULBO_ANCHO_MM = 20.0
BULBO_FONDO_MM = 4.80  # profundidad total 9,60 mm
COLA_Y_MM = (30.0, BALDOSA_MM - 30.0)

# Pozo de la ficha de comando (encaje a presión, abierto hacia arriba).
POZO_ANCHO_MM = 48.40
POZO_FONDO_MM = 36.40
POZO_PROF_MM = 5.0
POZO_RECTA_XY = (40.0, 78.0)
POZO_CURVA_XY = (66.8, 8.0)
POZO_TE_XY = (40.0, 8.0)

# Ficha G. Dos dimensiones de planta > 31,75 mm.
FICHA_ANCHO_MM = 48.0
FICHA_FONDO_MM = 36.0
FICHA_ALTO_MM = 8.0
FICHA_LLAVE_MM = 10.20  # poste del pozo; la ficha se recorta 0,20 menos

# Nervio lateral del snap. Sección ≥ 3,20 mm.
SNAP_ANCHO_MM = 12.0
SNAP_SALIENTE_MM = 4.80
SNAP_RANURA_MM = 4.30  # interferencia 4,80 − 0,20 − 4,30 = 0,30 mm
SNAP_HOLGURA_RANURA_MM = 0.40  # ranura más ancha que el nervio

# Placa de identidad / destino. Entra en el zócalo.
BOLSA_X0_MM = 16.0
BOLSA_Y0_MM = 8.0  # deja 3,70 mm tras la ranura de snap de 4,30 mm
BOLSA_ANCHO_MM = 90.0
BOLSA_FONDO_MM = 44.80  # termina en y = 52,80; quedan 4,80 mm hasta la ranura (y = 57,60)
BOLSA_PROF_MM = 4.0
PLACA_ALTO_MM = 6.40
PLACA_LLAVE_MM = 14.20

# Patín. Carril más estrecho que la ranura por la holgura de impresión.
PATIN_PLANTA_MM = 2.0 * MODULO_MM  # 63,60 > 31,75
PATIN_ALTO_MM = 6.40
PATIN_CARRIL_ANCHO_MM = RANURA_ANCHO_MM - 2.0 * HOLGURA_MM  # 11,60
PATIN_CARRIL_ALTO_MM = RANURA_PROF_MM - 2.0 * HOLGURA_MM  # 7,60
PATIN_CARRIL_LARGO_MM = 50.0

ICONO_ALTO_MM = 1.40
ICONO_ENGROSE_MM = 0.40  # por lado: el trazo más fino (2,4) pasa a 3,2

# Segmentos de revolución.
SEGMENTOS_STL = 48
SEGMENTOS_AR = 12

# --- Zócalo para Lúa V5 (29/10/2026) ---
# La cuna sigue la huella de la base de Lúa V5 (lua-v5/interfaz-construye.json,
# copia de lua-firmware). Lúa mira a +X, que es el sentido del camino.
# Cerrada por detrás y por los lados, abierta por delante: en INICIO Lúa sale
# deslizando hacia la primera baldosa; en META se encaja desde arriba. Las patas
# delanteras solo caben delante: Lúa al revés no asienta.
ZOCALO_FONDO_MM = 6.0 * MODULO_MM  # 190,80: Lúa en 4 módulos + franja de la placa
CUNA_HOLGURA_MM = 0.6  # aire entre el patín de Lúa y la cuna
CUNA_PARED_MM = 4.0
CUNA_ALTO_MM = 21.6  # con el patín, abraza 8,4 mm de la base (13,2 sobre la baldosa)
CUNA_ABIERTA_X_MM = 0.0  # la cuna acaba en el centro de Lúa: delante de su parte más ancha no hay pared
COLA_HUECO_MM = 18.0  # medio ancho de la escotadura de la cola, detrás
# La placa, en la franja de y 127,2 a 190,8. Su ranura norte deja 3,2 mm de pared.
BOLSA_ZOCALO_Y0_MM = 138.50
