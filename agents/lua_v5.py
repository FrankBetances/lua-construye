"""Lo que lua-construye copia de Lúa V5 (lua-firmware), y el gate que compara la copia.

    python3 -m agents.lua_v5 --copiar ../lua-firmware   # trae la copia
    python3 -m agents.lua_v5 --check  ../lua-firmware   # rojo si la copia no es la de allí

La fuente es lua-firmware (`tools/blender/lua_v5_uniones.py` y
`lua_v5_cuerpo.py`, en Blender). Aquí hay una copia en `lua-v5/`:

- `interfaz-construye.json`: la huella de la base, las patas, la cola y las
  cotas del patín. De aquí sale la cuna del zócalo.
- `patin-montaje.stl`: el patín en el marco de Lúa montada (z = 0 en la cara
  de abajo de la base, el frente hacia −Y). Es K-PATIN-G.
- `patin-imprimir.stl`: el mismo, en la cama y con su sostén. Es el que va a
  masque3d.

Si la copia se edita aquí, el zócalo deja de casar con la Lúa que se imprime.
Sin el vecino, el gate se salta y lo dice: ese verde no ha comparado nada.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
COPIA = RAIZ / "lua-v5"
FICHEROS = {
    "interfaz-construye.json": "cad/lua-v5/interfaz-construye.json",
    "patin-montaje.stl": "cad/lua-v5/montaje/patin.stl",
    "patin-imprimir.stl": "cad/lua-v5/imprimir/patin.stl",
}


def interfaz() -> dict:
    return json.loads((COPIA / "interfaz-construye.json").read_text(encoding="utf-8"))


def _sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--copiar", metavar="LUA_FIRMWARE")
    g.add_argument("--check", metavar="LUA_FIRMWARE")
    a = ap.parse_args(argv)
    fw = Path(a.copiar or a.check)
    if not (fw / "cad" / "lua-v5").is_dir():
        print(f"· lua_v5: no hay lua-firmware en {fw}: la copia de lua-v5/ NO se compara")
        return 0 if a.check else 1
    fallos = []
    for local, remoto in FICHEROS.items():
        src, dst = fw / remoto, COPIA / local
        if a.copiar:
            COPIA.mkdir(exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"  copiado {remoto} → lua-v5/{local}")
        elif not dst.exists() or _sha(src) != _sha(dst):
            fallos.append(f"lua-v5/{local} no es {remoto} de lua-firmware")
    for f in fallos:
        print(f"  ✗ {f}")
    if a.check and not fallos:
        print(f"✓ lua-v5/: {len(FICHEROS)} ficheros iguales a los de lua-firmware")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
