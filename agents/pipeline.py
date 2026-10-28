"""Ejecuta los siete agentes del Set 1, en el orden del contrato."""

from __future__ import annotations

import json
import traceback
from pathlib import Path

from agents import (
    assembly_sequencer,
    manifold_cad,
    manual_publisher,
    pedagogy_manual,
    safety_norms,
    spec_topology,
    technical_illustration,
)

AGENTES = (
    ("SpecTopologyAgent", spec_topology.ejecutar),
    ("ManifoldCadAgent", manifold_cad.ejecutar),
    ("SafetyNormsAuditor", safety_norms.ejecutar),
    ("AssemblySequencerAgent", assembly_sequencer.ejecutar),
    ("TechnicalIllustrationAgent", technical_illustration.ejecutar),
    ("PedagogyManualAgent", pedagogy_manual.ejecutar),
    ("ManualPublisherAgent", manual_publisher.ejecutar),
)


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    registro = []
    fallo = None
    for nombre, funcion in AGENTES:
        try:
            funcion(raiz)
            registro.append({"agente": nombre, "exit": 0})
        except Exception as exc:  # noqa: BLE001 — el registro tiene que conservar el fallo real
            registro.append({"agente": nombre, "exit": 1, "error": f"{type(exc).__name__}: {exc}"})
            fallo = traceback.format_exc()
            break
    pruebas = raiz / "sets" / "S1-camino" / "pruebas"
    pruebas.mkdir(parents=True, exist_ok=True)
    ejecucion = {
        "comando": "python3 -m agents.pipeline",
        "agentes": registro,
        "exit": 0 if fallo is None else 1,
    }
    if fallo is None:
        editor = json.loads((pruebas / "auditoria.json").read_text(encoding="utf-8"))
        ejecucion["auditoria_apta"] = editor["apto"]
    (pruebas / "ejecucion.json").write_text(
        json.dumps(ejecucion, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if fallo is not None:
        (pruebas / "fallo.txt").write_text(fallo, encoding="utf-8")
    else:
        fallo_txt = pruebas / "fallo.txt"
        if fallo_txt.exists():
            fallo_txt.unlink()
        _documentar(raiz, ejecucion)
    return 0 if fallo is None else 1


def _documentar(raiz: Path, ejecucion: dict) -> None:
    bom = json.loads((raiz / "sets" / "S1-camino" / "pruebas" / "bom.json").read_text(encoding="utf-8"))
    maestros = json.loads((raiz / "sets" / "S1-camino" / "pruebas" / "maestros.json").read_text(encoding="utf-8"))
    auditoria = json.loads((raiz / "sets" / "S1-camino" / "pruebas" / "auditoria.json").read_text(encoding="utf-8"))
    lineas_stl = "\n".join(f"- `{m['stl']}` ({m['triangulos_stl']} triángulos, {m['volumen_mm3']} mm³)" for m in maestros["maestros"])
    lineas_glb = "\n".join(f"- `{m['glb']}` ({m['glb_bytes']} bytes)" for m in maestros["maestros"])
    agentes = "\n".join(f"- {a['agente']}: exit {a['exit']}" for a in ejecucion["agentes"])
    texto = f"""# Ejemplo Set 1 · El Camino de Lúa

Set elegido: **Set 1, El Camino de Lúa**, el primero del plan (README, «Empezar por el Set 1»; SETS.md, fase 3, «Set 1 completo»). Es el mundo de geometría más simple que el propio documento manda imprimir primero.

No se modeló el cuerpo de Lúa. `K-CUELLO` lo imprime el fabricante. Las fichas de escala E no se generan: el punto abierto del Set 1 recomienda dejarlas fuera del kit de 0 a 3 años.

## Qué salió en esta máquina

{agentes}

Auditoría de diseño: {"apta" if auditoria["apto"] else "rechazada"}. No es un ensayo EN 71-1 de laboratorio y no declara conformidad.

## STL

{lineas_stl}

## GLB (menos de 100 KB)

{lineas_glb}

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

{bom["hipotesis"]}

La ranura mide 12 mm de ancho, como dice SETS, y 8 mm de fondo para dejar 11,20 mm de suelo. La unión entre baldosas es una cola de milano vertical: SETS deja abierta la probeta de encaje y el reglamento admite espiga, no fricción ni adhesivo.

## Qué no se verificó aquí

- No hay impresora Masque3D en esta máquina: no se imprimió ninguna pieza.
- No hay ensayo de laboratorio EN 71-1, EN 71-2 ni EN 71-3.
- No se comprobó el ajuste real de la cola de milano ni el deslizamiento del patín en PLA.
- D1 (el valor de P) sigue abierta. La planta usa el módulo de 31,80 mm del reglamento de piezas.
- `CCLREADME.md` no está en el repositorio. Se leyeron `docs/SETS.md` y `README.md`.
"""
    (raiz / "docs" / "EJEMPLO-SET-1.md").write_text(texto, encoding="utf-8")
    estado = f"""# STATUS

Ejemplo ejecutable del Set 1 (El Camino de Lúa), rama de trabajo sobre `sets`.

| Comprobación | Resultado |
|---|---|
| `python3 -m agents.pipeline` | exit {ejecucion["exit"]} |
| Auditoría de diseño (malla, cilindro, pared) | {"apta" if auditoria["apto"] else "rechazada"} |
| Impresión en Masque3D | no verificada: no hay impresora en esta máquina |
| Ensayo de laboratorio EN 71 | no realizado; no se declara conformidad |

El detalle está en `docs/EJEMPLO-SET-1.md`.
"""
    (raiz / "STATUS.md").write_text(estado, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
