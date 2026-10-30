# STATUS

Sets v1 compatibles con Lúa V5 (29/10/2026) y carpeta para masque3d en `entrega/masque3d-sets-v1/`. NO PROBADO: nada impreso.

| Comprobación | Resultado |
|---|---|
| `python3 -m agents.pipeline_todos` | exit 0 |
| Auditoría de diseño de las carpetas nuevas | apta |
| Set 1 `sets/S1-camino` | regenerado el 29/10 (zócalo, patín, iconos) con `python3 -m agents.pipeline` |
| Lúa V5 sobre el camino (`make check`) | ver `docs/ANALISIS-SETS-V1-LUA.md` §3 |
| Paquete masque3d (`agents.paquete_masque3d`) | 83 piezas medidas con check-v3-piezas de lua-firmware |
| Manual IKEA de ensamblaje (11 sets) | generado (18 páginas A4 + HTML con 31 renders 3D de Blender Cycles en `docs/cad/manual/`, `docs/MANUAL-ENSAMBLAJE-IKEA-11-SETS.pdf` y `entrega/masque3d-sets-v1/MANUAL-ENSAMBLAJE-IKEA.pdf`, revisado visualmente página a página) |
| Sets 8 a 11 | escalados al 60 % (S8, S9, S10) y 33 % (S11) con sostén en `entrega/masque3d-sets-v1/` (maquetas de una pieza, no despiezadas en bloques) |
| Impresión en Masque3D | no verificada: no hay impresora en esta máquina |
| Ensayo de laboratorio EN 71 | no realizado; no se declara conformidad |

Lo que no se cumple: `docs/ANALISIS-SETS-V1-LUA.md` §0. Lo que no cupo: `docs/SETS-IMPRESION.md`.
