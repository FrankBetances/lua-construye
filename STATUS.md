# STATUS

Sets v1 compatibles con Lúa V5 (29/10/2026) y carpeta para masque3d en `entrega/masque3d-sets-v1/`. NO PROBADO: nada impreso.

| Comprobación | Resultado |
|---|---|
| `python3 -m agents.pipeline_todos` | exit 0 |
| Auditoría de diseño de las carpetas nuevas | apta |
| Set 1 `sets/S1-camino` | regenerado el 29/10 (zócalo, patín, iconos) con `python3 -m agents.pipeline` |
| Lúa V5 sobre el camino (`make check`) | ver `docs/ANALISIS-SETS-V1-LUA.md` §3 |
| Paquete masque3d (`agents.paquete_masque3d`) | 83 piezas medidas con check-v3-piezas de lua-firmware |
| Manual IKEA de ensamblaje (11 sets) | generado (14 páginas A4, PDF en docs/ y entrega/) |
| Sets 8 a 11 | no van: una pieza decorativa cada uno, no caben en la cama |
| Impresión en Masque3D | no verificada: no hay impresora en esta máquina |
| Ensayo de laboratorio EN 71 | no realizado; no se declara conformidad |

Lo que no se cumple: `docs/ANALISIS-SETS-V1-LUA.md` §0. Lo que no cupo: `docs/SETS-IMPRESION.md`.
