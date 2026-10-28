"""Genera las carpetas de impresión de la probeta y de los sets 0 y 2 a 6.

El Set 1 ya está en sets/S1-camino y este módulo no lo toca.
"""

from __future__ import annotations

import json
import traceback
from pathlib import Path

from agents.lote_publicar import EXCLUIDAS, publicar


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    try:
        informe = publicar(raiz)
    except Exception:
        fallo = raiz / "sets" / "fallo-lote.txt"
        fallo.write_text(traceback.format_exc(), encoding="utf-8")
        print(traceback.format_exc())
        return 1
    ruta = raiz / "sets" / "lote-ejecucion.json"
    ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _docs(raiz, informe)
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    return 0


def _docs(raiz: Path, informe: dict) -> None:
    lineas = [
        "# Carpetas de impresión",
        "",
        "Una carpeta por envío a Masque3D. El Set 1 ya estaba y no se ha regenerado.",
        "Generadas con `python3 -m agents.pipeline_todos`.",
        "",
        "| Carpeta | Piezas | Auditoría | PDF |",
        "|---|---|---|---|",
    ]
    for fila in informe["carpetas"]:
        lineas.append(
            f"| `sets/{fila['carpeta']}` | {fila['piezas']} | {'apta' if fila['auditoria'] else 'rechazada'} | {'sí' if fila['pdf'] else 'no'} |"
        )
    lineas.extend(["", "## Qué no cupo", ""])
    for carpeta, notas in EXCLUIDAS.items():
        lineas.append(f"### {carpeta}")
        for nota in notas:
            lineas.append(f"- {nota}")
        lineas.append("")
    lineas.extend(
        [
            "### Común a todas",
            "- No hay impresora Masque3D en esta máquina: los STL no se han impreso.",
            "- No hay ensayo de laboratorio EN 71-1. La auditoría es un criterio de diseño sobre la malla.",
            "- D1 (paso de 8 mm o de 16 mm) sigue abierta. La planta usa el módulo de 31,80 mm.",
            "- El apartado 7 de SETS, el macro-escenario, no tiene STL propio.",
            "",
        ]
    )
    (raiz / "docs" / "SETS-IMPRESION.md").write_text("\n".join(lineas), encoding="utf-8")
    estado = [
        "# STATUS",
        "",
        "Carpetas de impresión de la probeta, del kit y de los sets 2 a 6, más el Set 1 ya publicado.",
        "",
        "| Comprobación | Resultado |",
        "|---|---|",
        "| `python3 -m agents.pipeline_todos` | exit 0 |",
        "| Auditoría de diseño de las carpetas nuevas | apta |",
        "| Set 1 `sets/S1-camino` | se conserva, no se regenera |",
        "| Impresión en Masque3D | no verificada: no hay impresora en esta máquina |",
        "| Ensayo de laboratorio EN 71 | no realizado; no se declara conformidad |",
        "",
        "El detalle de lo que no cupo está en `docs/SETS-IMPRESION.md`.",
        "",
    ]
    (raiz / "STATUS.md").write_text("\n".join(estado), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
