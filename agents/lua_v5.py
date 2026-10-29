"""Lo que lua-construye copia de Lúa V5 (lua-firmware), y el gate que compara la copia.

    python3 -m agents.lua_v5 --check ../lua-firmware   # rojo si el fondo no es el de allí

La fuente es lua-firmware (`tools/blender/lua_v5_uniones.py` y
`lua_v5_cuerpo.py`, en Blender). Aquí hay una copia en `lua-v5/`:

- `interfaz-construye.json`: el fondo del cubo de Lúa V5 (108 × 108 × 5) y
  las cotas del patín (bandeja). De aquí salen la cuna del zócalo y el patín.
  El gate compara el fondo con `FONDO` de lua_v5_uniones.py.

Si la copia se edita aquí, el zócalo deja de casar con la Lúa que se imprime.
Sin el vecino, el gate se salta y lo dice: ese verde no ha comparado nada.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
COPIA = RAIZ / "lua-v5"


def interfaz() -> dict:
    return json.loads((COPIA / "interfaz-construye.json").read_text(encoding="utf-8"))


def _dict_fw(fw: Path, nombre: str) -> dict:
    texto = (fw / "tools" / "blender" / "lua_v5_uniones.py").read_text(encoding="utf-8")
    m = re.search(rf"^{nombre} = dict\((.*?)\)\n", texto, re.S | re.M)
    if not m:
        raise SystemExit(f"✗ no encuentro {nombre} en lua_v5_uniones.py")
    sin_comentarios = re.sub(r"#.*", "", m.group(1))
    return {k.strip(): ast.literal_eval(v.strip()) for k, v in
            (par.split("=") for par in sin_comentarios.split(",") if "=" in par)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", metavar="LUA_FIRMWARE", required=True)
    a = ap.parse_args(argv)
    fw = Path(a.check)
    if not (fw / "tools" / "blender" / "lua_v5_uniones.py").exists():
        print(f"· lua_v5: no hay lua-firmware en {fw}: la interfaz NO se compara")
        return 0
    F = _dict_fw(fw, "FONDO")
    mio = interfaz()["fondo"]
    fallos = [f"fondo.{k}: aquí {mio[k]}, en lua-firmware {F.get(k)}" for k in mio if mio[k] != F.get(k)]
    for f in fallos:
        print(f"  ✗ {f}")
    if not fallos:
        print("✓ lua-v5/interfaz-construye.json: el fondo del cubo es el de lua-firmware")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
