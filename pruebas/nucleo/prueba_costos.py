"""make costos con un OpenCode simulado, en los formatos 1.x y 2.x."""
import json
import os
import shutil
import time
from pathlib import Path

from apoyo import afirmar, contiene, prueba

SIMULADO = Path(__file__).resolve().parent.parent / "opencode_simulado.py"
PRECIOS = {"opencode-go": {"models": {
    "deepseek-v4.1-flash": {"cost": {"input": 0.15, "output": 0.60, "cache_read": 0.003}},
    "glm-5.3": {"cost": {"input": 1.0, "output": 3.0, "cache_read": 0.1}}}}}
RAMA = "001-prueba"
TOKENS = 89100            # suma de entrada, salida, razonamiento y caché de las tres respuestas simuladas
COSTO_OPENCODE = 0.08     # suma del campo cost de las tres respuestas


def preparar(e, version: str):
    """Proyecto en una rama de funcionalidad, con el OpenCode simulado primero en el PATH."""
    p = e.proyecto()
    carpeta = e.tmp / f"simulado-{p.ruta.name}"
    (carpeta / "bin").mkdir(parents=True)
    shutil.copy2(SIMULADO, carpeta / "bin/opencode")
    (carpeta / "bin/opencode").chmod(0o755)
    (carpeta / "precios.json").write_text(json.dumps(PRECIOS), encoding="utf-8")
    p.git("checkout", "-q", "-b", RAMA)
    p.escribir(f"specs/{RAMA}/spec.md", "# spec\n")
    extra = {
        "PATH": f"{carpeta / 'bin'}{os.pathsep}{e.entorno['PATH']}",
        "COSTOS_FUENTE_PRECIOS": str(carpeta / "precios.json"),
        "XDG_DATA_HOME": str(carpeta / "datos"),
        "FALSO_VERSION": version,
        # Un minuto adelante: las respuestas simuladas deben ser posteriores a la creación de la rama.
        "FALSO_AHORA": str(int(time.time() * 1000) + 60000),
    }
    return p, extra


def registrar(e, version: str) -> dict:
    p, extra = preparar(e, version)
    r = p.make("costos", extra=extra)
    contiene(r.salida, "Registradas 2 sesión(es) nuevas o continuadas")
    costos = json.loads(p.leer(f"specs/{RAMA}/costos.json"))
    t = costos["totales"]
    afirmar(len(costos["sesiones"]) == 2, f"se esperaban 2 sesiones (raíz y subagente), hay {len(costos['sesiones'])}")
    afirmar(sorted(str(s["padre"]) for s in costos["sesiones"]) == ["None", "ses_raiz"],
            "el subagente no quedó enlazado a su sesión raíz")
    afirmar(t["tokens"] == TOKENS, f"tokens: se esperaban {TOKENS}, hay {t['tokens']}")
    afirmar(abs(t["costo_opencode"] - COSTO_OPENCODE) < 1e-9, f"costo según OpenCode: {t['costo_opencode']}")
    afirmar(t["costo"] and t["costo"] > 0, f"el costo equivalente no se calculó: {t['costo']}")

    antes = p.leer(f"specs/{RAMA}/costos.json")
    r = p.make("costos", extra=extra)
    afirmar("Registradas" not in r.salida, "la segunda ejecución volvió a registrar el mismo consumo")
    afirmar(p.leer(f"specs/{RAMA}/costos.json") == antes, "la segunda ejecución modificó costos.json")
    return {"tokens": t["tokens"], "costo": t["costo"], "agentes": sorted(f["agente"] for s in costos["sesiones"] for f in s["consumo"])}


@prueba("make costos con OpenCode 1.x y 2.x: mismos totales, subagente enlazado y sin duplicar al repetir")
def dos_versiones(e):
    uno, dos = registrar(e, "1"), registrar(e, "2")
    afirmar(uno == dos, f"los totales cambian según la versión de OpenCode:\n  1.x: {uno}\n  2.x: {dos}")
    afirmar(uno["agentes"] == ["orquestador", "seguridad"], f"agentes inesperados: {uno['agentes']}")


@prueba("make costos avisa cuando OpenCode no devuelve sesiones y cuando se está en la rama principal")
def avisos(e):
    for version in ("1", "2"):
        p, extra = preparar(e, version)
        r = p.make("costos", extra=dict(extra, FALSO_SIN_SESIONES="1"))
        contiene(r.salida, "OpenCode no devolvió ninguna sesión de este proyecto")
        afirmar(not p.existe(f"specs/{RAMA}/costos.json"), "se creó costos.json sin consumo que registrar")
    p.git("checkout", "-q", "main")
    contiene(p.make("costos", extra=extra).salida, "Estás en la rama principal")


@prueba("un costo cerrado no se vuelve a registrar ni se puede modificar sin aprobación")
def cerrado(e):
    p, extra = preparar(e, "2")
    contiene(p.make("costos", "CERRAR=1", extra=extra).salida, "Costo de la tarea CERRADO")
    p.commit("docs: cierra el costo de la tarea")
    contiene(p.make("costos", extra=extra).salida, "El costo de esta tarea está cerrado")
    afirmar(not p.pendientes(), "make costos modificó un costo cerrado")

    ruta = f"specs/{RAMA}/costos.json"
    costos = json.loads(p.leer(ruta))
    costos["totales"]["costo"] = 0
    p.escribir(ruta, json.dumps(costos, indent=2, ensure_ascii=False) + "\n")
    contiene(p.commit("fix: ajusta el costo", espera=1).salida, "ya está cerrado y no se modifica")
    p.commit("fix: ajusta el costo", extra={"APROBADO_COSTOS": "1"})
