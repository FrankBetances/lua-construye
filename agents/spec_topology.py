"""SpecTopologyAgent. Lee SETS.md y el README, valida los códigos y arma BOM y DAG."""

from __future__ import annotations

import json
import re
from pathlib import Path

PATRON = re.compile(r"^(K|S[0-9]+)-[A-Z0-9]+(-[A-Z0-9]+)*$")
FILA = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([^|]*)\|", re.M)


def ejecutar(raiz: Path) -> dict:
    sets = (raiz / "docs" / "SETS.md").read_text(encoding="utf-8")
    readme = (raiz / "README.md").read_text(encoding="utf-8")
    fuentes = {
        "docs/SETS.md": "leido",
        "README.md": "leido",
        "CCLREADME.md": "ausente" if not (raiz / "CCLREADME.md").exists() else "leido",
        "LCREADME.md": "ausente" if not (raiz / "LCREADME.md").exists() else "leido",
    }
    if "Empezar por el Set 1" not in readme:
        raise RuntimeError("El README ya no recomienda empezar por el Set 1")
    if "Set 1 completo" not in sets:
        raise RuntimeError("SETS.md ya no lista la fase «Set 1 completo»")

    set1 = _trozo(sets, "## SET 1", "## SET 2")
    set0 = _trozo(sets, "## SET 0", "## SET 1")
    maestros = _piezas_set1(set1)
    maestros.extend(_dependencias_set0(set0, set1))
    for pieza in maestros:
        if not PATRON.match(pieza["codigo"]):
            raise RuntimeError(f"código fuera de la taxonomía: {pieza['codigo']}")
    codigos = [p["codigo"] for p in maestros]
    if len(codigos) != len(set(codigos)):
        raise RuntimeError("código de pieza repetido en el BOM")

    dag = _dag(raiz)
    _aciclico(dag["tarjetas"]["recta"]["nodos"])
    documento = {
        "set": "S1",
        "nombre": "El Camino de Lúa",
        "plan": (
            "README §11: empezar por el Set 1. "
            "SETS §8 fase 3: imprimir el Set 1 completo. "
            "Este ejemplo modela los maestros G de esa tabla y las piezas del Set 0 "
            "que la escena nombra (zócalo, placas INICIO y META, patín)."
        ),
        "fuentes": fuentes,
        "hipotesis": (
            "Planta de baldosa y zócalo: 4 × 31,80 mm. "
            "SETS no da milímetros del cuerpo de Lúa; ancho = 2 módulos de cuerpo + 2 módulos."
        ),
        "excluidos": [
            {
                "codigo": "S1-CMD-*-E",
                "motivo": (
                    "El punto abierto del Set 1 recomienda no meter las fichas de escala E "
                    "en el kit de 0 a 3 años. No se genera ese STL."
                ),
            },
            {
                "codigo": "K-CUELLO",
                "motivo": "SET 0: lo imprime e integra el fabricante. Fuera de este ejemplo.",
            },
        ],
        "maestros": maestros,
    }
    pruebas = raiz / "sets" / "S1-camino" / "pruebas"
    pruebas.mkdir(parents=True, exist_ok=True)
    _escribir(pruebas / "bom.json", documento)
    _escribir(pruebas / "dag.json", dag)
    return {"bom": documento, "dag": dag}


def _trozo(texto: str, inicio: str, fin: str) -> str:
    i = texto.find(inicio)
    j = texto.find(fin, i + 1)
    if i < 0 or j < 0:
        raise RuntimeError(f"no está el tramo {inicio!r}")
    return texto[i:j]


def _piezas_set1(set1: str) -> list[dict]:
    tabla = set1.split("### Contrato", 1)[0]
    filas = {codigo: (nombre.strip(), cant.strip()) for codigo, nombre, cant in FILA.findall(tabla)}
    requeridos = ("S1-REC-LIS-G", "S1-REC-RUG-G", "S1-CUR-G", "S1-TEE-G", "S1-CMD-AVA/PAR/GIR/SAL", "S1-DEST-*")
    for codigo in requeridos:
        if codigo not in filas:
            raise RuntimeError(f"SETS.md ya no lista {codigo}")
    if "S1-DEST-CAMA" not in set1 or "parque" not in set1.lower():
        raise RuntimeError("la escena del Set 1 ya no nombra parque y cama")
    piezas = []
    for codigo in ("S1-REC-LIS-G", "S1-REC-RUG-G", "S1-CUR-G", "S1-TEE-G"):
        nombre, cant = filas[codigo]
        piezas.append(_fila(codigo, nombre, int(cant), "tabla SET 1"))
    for token, verbo in (("AVA", "avanza"), ("PAR", "para"), ("GIR", "gira"), ("SAL", "salta")):
        piezas.append(
            _fila(
                f"S1-CMD-{token}-G",
                f"Ficha de comando {verbo}",
                1,
                "tabla SET 1, grupo S1-CMD-AVA/PAR/GIR/SAL, versión G",
            )
        )
    piezas.append(_fila("S1-DEST-PARQUE", "Placa de destino parque", 1, "tabla SET 1, S1-DEST-*"))
    piezas.append(_fila("S1-DEST-CAMA", "Placa de destino cama", 1, "tabla SET 1 y reto 4"))
    return piezas


def _dependencias_set0(set0: str, set1: str) -> list[dict]:
    for codigo in ("K-ZOCALO-G", "K-PATIN-G", "K-PLACA-*"):
        if codigo not in set0:
            raise RuntimeError(f"SET 0 ya no define {codigo}")
    if "K-ZOCALO-G" not in set1:
        raise RuntimeError("el Set 1 ya no reutiliza K-ZOCALO-G")
    if "patín" not in set1 and "patin" not in set1.lower():
        raise RuntimeError("la escena del Set 1 ya no usa el patín")
    if "INICIO" not in set0 or "META" not in set0:
        raise RuntimeError("el Set 0 ya no lista las placas INICIO y META")
    return [
        _fila("K-ZOCALO-G", "Zócalo universal", 1, "tabla SET 0; un STL, varias instancias en la escena"),
        _fila("K-PLACA-INICIO", "Placa de identidad INICIO", 1, "tabla SET 0, K-PLACA-*"),
        _fila("K-PLACA-META", "Placa de identidad META", 1, "tabla SET 0, K-PLACA-*"),
        _fila("K-PATIN-G", "Patín guía", 1, "tabla SET 0; corre por la ranura de 12 mm del Set 1"),
    ]


def _fila(codigo: str, nombre: str, cantidad: int, origen: str) -> dict:
    return {
        "codigo": codigo,
        "nombre": nombre,
        "cantidad": cantidad,
        "escala": "G",
        "origen": origen,
    }


def _dag(raiz: Path) -> dict:
    import importlib.util

    ruta = raiz / "sets" / "S1-camino" / "cad" / "parametros.py"
    spec = importlib.util.spec_from_file_location("parametros_s1", ruta)
    if spec is None or spec.loader is None:
        raise RuntimeError("no se pudo cargar parametros.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    w = float(modulo.BALDOSA_MM)
    z_placa = float(modulo.ALTURA_BASE_MM - modulo.BOLSA_PROF_MM)
    inset_x = float(modulo.BOLSA_X0_MM + modulo.HOLGURA_MM)
    inset_y = float(modulo.BOLSA_Y0_MM + modulo.HOLGURA_MM)
    patin = float(modulo.PATIN_PLANTA_MM)
    alto = float(modulo.ALTURA_BASE_MM)

    def nodo(ident, codigo, x, y, z, padre, bloquea, rol):
        return {
            "id": ident,
            "codigo": codigo,
            "origen_mm": [round(x, 2), round(y, 2), round(z, 2)],
            "rot_z_grados": 0,
            "requiere": padre,
            "bloquea_al_padre": bloquea,
            "u_insercion": [0, 0, -1],
            "rol": rol,
        }

    def placa(ident, codigo, zx, zy, padre):
        return nodo(ident, codigo, zx + inset_x, zy + inset_y, z_placa, padre, True, "placa")

    recta = [
        nodo("z0", "K-ZOCALO-G", 0, 0, 0, None, False, "ancla"),
        nodo("b1", "S1-REC-LIS-G", w, 0, 0, "z0", False, "baldosa"),
        nodo("b2", "S1-REC-LIS-G", 2 * w, 0, 0, "b1", False, "baldosa"),
        nodo("b3", "S1-REC-LIS-G", 3 * w, 0, 0, "b2", False, "baldosa"),
        nodo("zM", "K-ZOCALO-G", 4 * w, 0, 0, "b3", False, "ancla"),
        placa("pI", "K-PLACA-INICIO", 0, 0, "z0"),
        placa("pM", "K-PLACA-META", 4 * w, 0, "zM"),
        nodo(
            "pat",
            "K-PATIN-G",
            2 * w + (w - patin) / 2,
            (w - patin) / 2,
            alto,
            "b2",
            True,
            "patin",
        ),
    ]
    curva = [
        nodo("z0", "K-ZOCALO-G", 0, 0, 0, None, False, "ancla"),
        nodo("c1", "S1-CUR-G", w, 0, 0, "z0", False, "baldosa"),
        nodo("zM", "K-ZOCALO-G", w, w, 0, "c1", False, "ancla"),
        placa("pI", "K-PLACA-INICIO", 0, 0, "z0"),
        placa("pM", "K-PLACA-META", w, w, "zM"),
    ]
    te = [
        nodo("z0", "K-ZOCALO-G", 0, 0, 0, None, False, "ancla"),
        nodo("t1", "S1-TEE-G", w, 0, 0, "z0", False, "baldosa"),
        nodo("zR", "K-ZOCALO-G", 2 * w, 0, 0, "t1", False, "ancla"),
        nodo("zB", "K-ZOCALO-G", w, w, 0, "t1", False, "ancla"),
        placa("pI", "K-PLACA-INICIO", 0, 0, "z0"),
        placa("pP", "S1-DEST-PARQUE", 2 * w, 0, "zR"),
        placa("pC", "S1-DEST-CAMA", w, w, "zB"),
    ]
    # La curva y la rama de la T se documentan con el zócalo en la celda siguiente.
    # El STL del zócalo tiene la hembra en −X; hay que girarlo 90° para enfrentar el macho +Y.
    for pieza in (curva[2], te[3]):
        pieza["rot_z_grados"] = 90
        pieza["nota_giro"] = "La hembra local −X queda contra el macho +Y de la pieza anterior."
    return {
        "paso_mm": round(w, 2),
        "u_comun": [0, 0, -1],
        "nota": (
            "La espiga es una cola de milano vertical: la pieza baja (u = −Z). "
            "La placa y el patín sí tapan el desmontaje de su soporte; "
            "la cola de milano no, porque sale hacia arriba."
        ),
        "tarjetas": {
            "recta": {"titulo": "Recorrido recto", "nodos": recta},
            "curva": {"titulo": "Una curva", "nodos": curva},
            "te": {"titulo": "Una T", "nodos": te},
        },
    }


def _aciclico(nodos: list[dict]) -> None:
    pendientes = {n["id"]: n["requiere"] for n in nodos}
    vistos: set[str] = set()
    for ident in list(pendientes):
        camino = []
        cursor = ident
        while cursor is not None:
            if cursor in vistos:
                break
            if cursor in camino:
                raise RuntimeError(f"ciclo en el DAG: {' -> '.join(camino)}")
            camino.append(cursor)
            cursor = pendientes.get(cursor)
        vistos.update(camino)


def _escribir(ruta: Path, documento: dict) -> None:
    ruta.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
