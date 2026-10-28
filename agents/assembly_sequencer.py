"""AssemblySequencerAgent. Ordena el montaje deshaciendo el árbol de encajes."""

from __future__ import annotations

import json
from pathlib import Path


def ejecutar(raiz: Path) -> dict:
    dag = json.loads((raiz / "sets" / "S1-camino" / "pruebas" / "dag.json").read_text(encoding="utf-8"))
    tarjetas = {}
    for nombre, tarjeta in dag["tarjetas"].items():
        tarjetas[nombre] = _secuenciar(tarjeta)
    documento = {
        "metodo": (
            "Desensamblaje inverso del árbol de encajes. "
            "En cada paso se retira una hoja: una pieza que ya no tiene otra encajada en ella. "
            "Si hay varias, sale primero la que tapa a su soporte (placa o patín) "
            "y, a igualdad, la de mayor X. El montaje es el reverso. "
            "La cola de milano no tapa el desmontaje del vecino; la placa y el patín sí."
        ),
        "tarjetas": tarjetas,
    }
    ruta = raiz / "sets" / "S1-camino" / "pruebas" / "secuencia.json"
    ruta.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return documento


def _comprobar_padres(montaje: list[str], nodos: dict) -> None:
    puestos: set[str] = set()
    for ident in montaje:
        padre = nodos[ident]["requiere"]
        if padre is not None and padre not in puestos:
            raise RuntimeError(f"{ident} se montaría antes que {padre}")
        puestos.add(ident)


def _secuenciar(tarjeta: dict) -> dict:
    nodos = {n["id"]: n for n in tarjeta["nodos"]}
    hijos: dict[str, list[str]] = {ident: [] for ident in nodos}
    for nodo in tarjeta["nodos"]:
        padre = nodo["requiere"]
        if padre is not None:
            if padre not in nodos:
                raise RuntimeError(f"{nodo['id']} pide {padre}, que no está en la tarjeta")
            hijos[padre].append(nodo["id"])
    restantes = set(nodos)
    retiro = []
    while restantes:
        hojas = [ident for ident in restantes if all(h not in restantes for h in hijos[ident])]
        if not hojas:
            raise RuntimeError(f"ciclo al desmontar {tarjeta['titulo']}")
        # Primero lo que tapa a su soporte (placa, patín); después el extremo libre.
        hojas.sort(
            key=lambda ident: (
                0 if nodos[ident]["bloquea_al_padre"] else 1,
                -nodos[ident]["origen_mm"][0],
                -nodos[ident]["origen_mm"][1],
                ident,
            )
        )
        retiro.append(hojas[0])
        restantes.remove(hojas[0])
    montaje = list(reversed(retiro))
    _comprobar_padres(montaje, nodos)
    pasos = []
    for indice, ident in enumerate(montaje):
        nodo = nodos[ident]
        pasos.append(
            {
                "orden": indice + 1,
                "id": ident,
                "codigo": nodo["codigo"],
                "u_insercion": nodo["u_insercion"],
                "origen_mm": nodo["origen_mm"],
                "rot_z_grados": nodo["rot_z_grados"],
                "desplazamiento_despiece_mm": [round(16.0 * indice, 2), 0.0, round(28.0 * indice, 2)],
                "bloquea_al_padre": nodo["bloquea_al_padre"],
                "rol": nodo["rol"],
            }
        )
    return {"titulo": tarjeta["titulo"], "retiro": retiro, "montaje": pasos}
