"""PedagogyManualAgent. Textos del adulto que media, en castellano y en gallego."""

from __future__ import annotations

import json
from pathlib import Path

PASOS = {
    "z0": {
        "es": "Coloca el zócalo de salida en la mesa. La espiga queda hacia el lado por donde seguirá el camino.",
        "gl": "Coloca o zócalo de saída na mesa. A espiga queda cara ao lado por onde seguirá o camiño.",
    },
    "b1": {
        "es": "Baja la primera baldosa lisa sobre esa espiga. La ranura de 12 mm tiene que seguir sin escalón.",
        "gl": "Baixa a primeira baldosa lisa sobre esa espiga. A rañura de 12 mm ten que seguir sen banzo.",
    },
    "b2": {
        "es": "Baja la segunda baldosa del mismo modo. Di, si quieres: «Step forward».",
        "gl": "Baixa a segunda baldosa do mesmo xeito. Di, se queres: «Step forward».",
    },
    "b3": {
        "es": "Baja la tercera baldosa. El camino recto de la tarjeta ya está tendido.",
        "gl": "Baixa a terceira baldosa. O camiño recto da tarxeta xa está tendido.",
    },
    "zM": {
        "es": "Baja el zócalo de llegada sobre la espiga de la última baldosa.",
        "gl": "Baixa o zócalo de chegada sobre a espiga da última baldosa.",
    },
    "pI": {
        "es": "Encaja la placa INICIO. La esquina cortada solo entra de una forma. Si no entra, gírala: no la fuerces.",
        "gl": "Encaixa a placa INICIO. A esquina cortada só entra dunha forma. Se non entra, víraa: non a forces.",
    },
    "pM": {
        "es": "Encaja la placa META en el zócalo de llegada, con la misma llave.",
        "gl": "Encaixa a placa META no zócalo de chegada, coa mesma chave.",
    },
    "pat": {
        "es": "Da la vuelta al patín para que el carril mire hacia abajo e introdúcelo en la ranura. Tiene que deslizar.",
        "gl": "Dálle a volta ao patín para que o carril mire cara abaixo e introdúceo na rañura. Ten que esvarar.",
    },
}


def ejecutar(raiz: Path) -> dict:
    secuencia = json.loads(
        (raiz / "sets" / "S1-camino" / "pruebas" / "secuencia.json").read_text(encoding="utf-8")
    )
    ids = [p["id"] for p in secuencia["tarjetas"]["recta"]["montaje"]]
    faltan = [i for i in ids if i not in PASOS]
    if faltan:
        raise RuntimeError("faltan textos de los pasos: " + ", ".join(faltan))
    documento = {
        "audiencia": "adulto que media",
        "regla_pantalla": {
            "es": "El niño mueve los bloques. El adulto sostiene la tableta. La criatura no toca la pantalla.",
            "gl": "O neno move os bloques. O adulto sostén a tableta. A criatura non toca a pantalla.",
        },
        "lateralidad": {
            "es": "La izquierda y la derecha son las de Lúa, la gata negra. El niño la mira desde atrás, así no tiene que hacer un giro en espejo.",
            "gl": "A esquerda e a dereita son as de Lúa, a gata negra. O neno míraa desde atrás, así non ten que facer un xiro en espello.",
        },
        "vocabulario_espacial": {
            "categorias": ["posicion y direccion", "orientacion", "patron", "deicticos"],
            "es": ["delante", "detrás", "al lado", "recto", "giro", "primero", "luego", "al final", "este", "aquel"],
            "gl": ["diante", "detrás", "ao lado", "recto", "xiro", "primeiro", "logo", "ao final", "este", "aquel"],
        },
        "tpr": ["Step forward", "Turn left", "Turn right", "Stop", "Jump", "Follow the path"],
        "premio": {
            "es": "Si hay un reconocimiento al terminar, es para el adulto que acompañó. Nunca es un premio para el niño.",
            "gl": "Se hai un recoñecemento ao rematar, é para o adulto que acompañou. Nunca é un premio para o neno.",
        },
        "error_neutro": {
            "es": "Si el camino se corta, el mundo lo enseña. Se le dice al adulto que el camino está cortado y se pregunta si se puede girar la pieza. Sin reproche, sin usarlo como fallo del niño.",
            "gl": "Se o camiño se corta, o mundo ensínao. Díxeselle ao adulto que o camiño está cortado e pregúntase se se pode virar a peza. Sen reproche, sen usalo como fallo do neno.",
        },
        "advertencia": {
            "es": "Esto no es un diagnóstico ni un tratamiento. La revisión de medidas no es un certificado EN 71-1 de laboratorio. No se declara conformidad.",
            "gl": "Isto non é un diagnóstico nin un tratamento. A revisión de medidas non é un certificado EN 71-1 de laboratorio. Non se declara conformidade.",
        },
        "despues_de_montar": {
            "es": "El niño desliza a Lúa por la ranura. El adulto puede decir «Step forward». Durante ese recorrido la tableta no se le acerca al niño.",
            "gl": "O neno fai esvarar a Lúa pola rañura. O adulto pode dicir «Step forward». Durante ese percorrido a tableta non se lle achega ao neno.",
        },
        "ficha_comando": {
            "es": "La ficha de comando baja al pozo de la baldosa, con el relieve hacia arriba. La esquina cortada impide ponerla al revés. No forma parte de la tarjeta recta; el kit sí la incluye.",
            "gl": "A ficha de comando baixa ao pozo da baldosa, co relevo cara arriba. A esquina cortada impide poñela ao revés. Non forma parte da tarxeta recta; o kit si a inclúe.",
        },
        "pasos_recta": [{"id": i, **PASOS[i]} for i in ids],
    }
    ruta = raiz / "sets" / "S1-camino" / "manual" / "textos.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return documento
