"""Comprobaciones sobre el propio repositorio del kit, sin instalarlo en ningún proyecto."""
import re
import sys

from apoyo import afirmar, correr, prueba


@prueba("los archivos generados del kit (CLAUDE.md, .claude/, .codex/, .opencode/) están al día")
def generados_al_dia(e):
    kit = e.kit()
    correr(["python3", "scripts/sincronizar.py", "--verificar"], kit, e.entorno)
    correr(["python3", "scripts/sincronizar.py"], kit, e.entorno)
    pendientes = correr(["git", "status", "--short"], kit, e.entorno).salida.strip()
    afirmar(not pendientes, f"make sincronizar cambia archivos que deberían estar ya generados:\n{pendientes}")


@prueba("VERSION tiene su entrada en el CHANGELOG y es la más reciente")
def version_y_changelog(e):
    kit = e.kit()
    afirmar(re.fullmatch(r"\d+\.\d+\.\d+", e.version), f"VERSION no es una versión válida: «{e.version}»")
    entradas = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", (kit / "CHANGELOG.md").read_text(encoding="utf-8"), flags=re.M)
    afirmar(entradas, "el CHANGELOG no tiene ninguna versión")
    afirmar(entradas[0] == e.version, f"VERSION dice {e.version} y la entrada más reciente del CHANGELOG es {entradas[0]}")
    claves = [tuple(int(x) for x in v.split(".")) for v in entradas]
    afirmar(claves == sorted(claves, reverse=True), "las versiones del CHANGELOG no están de la más nueva a la más antigua")
    afirmar(len(set(entradas)) == len(entradas), "hay versiones repetidas en el CHANGELOG")


@prueba("todo lo que el instalador dice copiar existe en el kit")
def lista_del_instalador(e):
    kit = e.kit()
    sys.path.insert(0, str(kit / "scripts"))
    try:
        sys.modules.pop("instalar_kit", None)
        import instalar_kit
    finally:
        sys.path.pop(0)
    for rel in instalar_kit.GESTIONADOS + instalar_kit.SEMILLAS + sorted(instalar_kit.NUNCA):
        afirmar((kit / rel).exists(), f"scripts/instalar_kit.py nombra {rel}, que no existe en el kit")


@prueba("los enlaces internos de la documentación apuntan a archivos y títulos que existen")
def enlaces_internos(e):
    import enlaces
    internos, rotos, _ = enlaces.revisar(e.kit())
    afirmar(internos > 50, f"solo se encontraron {internos} enlaces internos: ¿se movió la documentación?")
    afirmar(not rotos, "enlaces rotos:\n" + "\n".join(f"  {origen} → {url}: {motivo}" for origen, url, motivo in rotos))
