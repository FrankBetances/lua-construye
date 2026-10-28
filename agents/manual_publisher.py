"""ManualPublisherAgent. Compila el manual y la tarjeta de reto en Typst."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


def ejecutar(raiz: Path) -> dict:
    base = raiz / "sets" / "S1-camino"
    textos = json.loads((base / "manual" / "textos.json").read_text(encoding="utf-8"))
    bom = json.loads((base / "pruebas" / "bom.json").read_text(encoding="utf-8"))
    secuencia = json.loads((base / "pruebas" / "secuencia.json").read_text(encoding="utf-8"))
    auditoria = json.loads((base / "pruebas" / "auditoria.json").read_text(encoding="utf-8"))
    manual = base / "manual" / "manual.typ"
    tarjeta = base / "manual" / "tarjeta-recta.typ"
    manual.write_text(_manual(textos, bom, secuencia, auditoria), encoding="utf-8")
    tarjeta.write_text(_tarjeta(textos, secuencia), encoding="utf-8")
    typst = shutil.which("typst") or shutil.which("typst", path=str(Path.home() / ".local" / "bin"))
    resultados = []
    if typst is None:
        resultados.append({"comando": "typst compile sets/S1-camino/manual/manual.typ", "exit": 127, "nota": "typst no está en PATH"})
        return {"typst": None, "resultados": resultados, "pdf": False}
    entorno = os.environ.copy()
    entorno["PATH"] = str(Path.home() / ".local" / "bin") + os.pathsep + entorno.get("PATH", "")
    for fuente in (manual, tarjeta):
        pdf = fuente.with_suffix(".pdf")
        comando = [typst, "compile", "--root", str(raiz), str(fuente), str(pdf)]
        proc = subprocess.run(comando, cwd=raiz, env=entorno, capture_output=True, text=True)
        resultados.append(
            {
                "comando": " ".join(comando),
                "exit": proc.returncode,
                "stderr": proc.stderr.strip(),
            }
        )
        if proc.returncode != 0:
            raise RuntimeError(f"typst falló ({proc.returncode}): {proc.stderr.strip()}")
    return {"typst": typst, "resultados": resultados, "pdf": True}


def _manual(textos: dict, bom: dict, secuencia: dict, auditoria: dict) -> str:
    filas = []
    for pieza in bom["maestros"]:
        filas.append(f"  [{_t(pieza['codigo'])}], [{_t(pieza['nombre'])}], [{pieza['cantidad']}],")
    pasos = []
    for paso in textos["pasos_recta"]:
        pasos.append(
            "  ["
            + _t(paso["es"])
            + "\\ #text(size: 9pt, fill: rgb(\"#555555\"))["
            + _t(paso["gl"])
            + "]],"
        )
    otras = []
    for nombre in ("curva", "te"):
        orden = ", ".join(p["codigo"] for p in secuencia["tarjetas"][nombre]["montaje"])
        titulo = secuencia["tarjetas"][nombre]["titulo"]
        otras.append(f"  [{_t(titulo)}: {orden}],")
    return f"""#set page(paper: "a4", margin: 16mm)
#set text(size: 11pt, lang: "es")
#set heading(numbering: none)

= El Camino de Lúa
Tarjeta recta del Set 1. Manual para el adulto que media.

#rect(width: 100%, inset: 8pt, stroke: 0.6pt)[
  {_t(textos["advertencia"]["es"])}
  #linebreak()
  {_t(textos["advertencia"]["gl"])}
]

== Quién hace qué
{_t(textos["regla_pantalla"]["es"])}

{_t(textos["regla_pantalla"]["gl"])}

{_t(textos["lateralidad"]["es"])}

{_t(textos["premio"]["es"])}

== Piezas de este ejemplo
#table(
  columns: (1.4fr, 2fr, auto),
  inset: 4pt,
  stroke: 0.4pt,
  [*Código*], [*Pieza*], [*Cantidad*],
{chr(10).join(filas)}
)

La hipótesis de planta (4 × 31,80 mm) está declarada en el BOM: SETS no da el ancho del cuerpo de Lúa.

== Montaje
Cada pieza baja. El vector de inserción es (0, 0, −1).

#image("../tarjetas/recta-despiece.svg", width: 100%)

#enum(
{chr(10).join(pasos)}
)

{_t(textos["despues_de_montar"]["es"])}

#linebreak()
{_t(textos["despues_de_montar"]["gl"])}

== Lenguaje para el adulto
Categorías de BrickSmart en este set: posición y dirección, orientación, patrón, deícticos.

Castellano: {", ".join(textos["vocabulario_espacial"]["es"])}.

Galego: {", ".join(textos["vocabulario_espacial"]["gl"])}.

TPR, dicho por el adulto: {", ".join(textos["tpr"])}.

{_t(textos["error_neutro"]["es"])}

== Las otras dos tarjetas
Mismo gesto: bajar la pieza sobre la espiga. En la curva y en la rama de la T, el zócalo de llegada se gira 90 grados para que su hembra enfrente al macho.

#list(
{chr(10).join(otras)}
)

== Ficha de comando
{_t(textos["ficha_comando"]["es"])}

#linebreak()
{_t(textos["ficha_comando"]["gl"])}

== Revisión de diseño
Piezas aptas en esta máquina: {len(auditoria["piezas"])}. Rechazadas: {len(auditoria["rechazados"])}.
Cilindro de referencia: {auditoria["cilindro_mm"]["diametro"]} mm × {auditoria["cilindro_mm"]["profundidad"]} mm.
Pared mínima declarada: {auditoria["pared_min_mm"]} mm.
{auditoria["norma"]}
"""


def _tarjeta(textos: dict, secuencia: dict) -> str:
    lineas = []
    for paso in textos["pasos_recta"]:
        lineas.append(f"  [{_t(paso['es'])}],")
    return f"""#set page(paper: "a5", margin: 12mm)
#set text(size: 10pt, lang: "es")

= Tarjeta de reto · camino recto
Copia este recorrido. El adulto lee. El niño mueve las piezas.

#image("../tarjetas/recta-planta.svg", width: 100%)

#enum(
{chr(10).join(lineas)}
)

{_t(textos["despues_de_montar"]["es"])}

#v(4pt)
{_t(textos["regla_pantalla"]["es"])}
"""


def _t(texto: str) -> str:
    return (
        texto.replace("\\", "\\\\")
        .replace("#", "\\#")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("*", "\\*")
        .replace("_", "\\_")
    )
