#!/usr/bin/env python3
"""Instala o actualiza el kit (submódulo, por defecto en .bowser-spec-kit-ai/) en la raíz del proyecto.

Las herramientas (Claude Code, Codex, OpenCode, Spec Kit, GitHub Actions) leen sus archivos
en la raíz del proyecto, no dentro del submódulo. Este script:

  1. Copia a la raíz los archivos GESTIONADOS por el kit (se reemplazan en cada actualización).
  2. Copia las SEMILLAS solo si no existen (después son del proyecto: config.json, CODEOWNERS…).
  3. Mantiene un bloque del kit dentro de .gitignore.
  4. Registra en .kit-manifest.json qué archivos vienen del kit y su hash, para:
       - borrar los que el kit eliminó,
       - detectar si alguien modificó localmente un archivo del kit (y no pisarlo).

Uso (desde la raíz del proyecto):
  python3 .bowser-spec-kit-ai/scripts/instalar_kit.py              instala o actualiza
  python3 .bowser-spec-kit-ai/scripts/instalar_kit.py --forzar     pisa cambios locales (guarda respaldo)
  python3 .bowser-spec-kit-ai/scripts/instalar_kit.py --verificar  falla si la raíz no coincide con el kit (CI, hooks)

Un proyecto puede quedarse con su propia versión de un archivo del kit agregándolo a
"kit.excluir" en equipo/config.json. Solo usa la biblioteca estándar de Python 3.9+.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
DESTINO = Path.cwd().resolve()
MANIFIESTO = DESTINO / ".kit-manifest.json"
# Ruta del submódulo relativa al proyecto (se guarda en el manifiesto para hooks, CI y doctor).
try:
    RUTA_KIT = KIT.relative_to(DESTINO).as_posix()
except ValueError:
    RUTA_KIT = str(KIT)

# Archivos y carpetas del kit que se copian y se mantienen actualizados en el proyecto.
GESTIONADOS = [
    "AGENTS.md",
    "Makefile",
    ".agents/skills/",
    ".githooks/",
    ".github/workflows/",
    ".specify/memory/constitution.md",
    "equipo/agentes/",
    "equipo/adaptadores/",
    "equipo/MODELOS.md",
    "scripts/",
    "docs/GUIA-INICIO.md",
    "docs/plantillas/",
]
# Nunca se copian (solo tienen sentido dentro del kit).
NUNCA = {"scripts/instalar_kit.py"}
# Se copian una sola vez; después pertenecen al proyecto.
SEMILLAS = ["equipo/config.json", ".github/CODEOWNERS", ".env.example", "docker-compose.yml"]

INICIO_GITIGNORE = "# >>> bowser-spec-kit-ai (gestionado por make instalar-kit; no editar este bloque)"
FIN_GITIGNORE = "# <<< bowser-spec-kit-ai"


# ---------------------------------------------------------------- utilidades

def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def es_ignorable(rel: str) -> bool:
    partes = rel.split("/")
    return "__pycache__" in partes or rel.endswith((".pyc", ".DS_Store"))


def archivos_del_kit(excluir: list[str]) -> dict[str, Path]:
    """Mapa ruta relativa -> archivo de origen, para todo lo gestionado."""
    resultado: dict[str, Path] = {}
    for entrada in GESTIONADOS:
        origen = KIT / entrada
        if entrada.endswith("/"):
            if not origen.is_dir():
                continue
            candidatos = [p for p in origen.rglob("*") if p.is_file()]
        else:
            candidatos = [origen] if origen.is_file() else []
        for p in candidatos:
            rel = p.relative_to(KIT).as_posix()
            if rel in NUNCA or es_ignorable(rel) or excluido(rel, excluir):
                continue
            resultado[rel] = p
    return resultado


def excluido(rel: str, excluir: list[str]) -> bool:
    return any(rel == e or (e.endswith("/") and rel.startswith(e)) for e in excluir)


def leer_excluir() -> list[str]:
    cfg = DESTINO / "equipo/config.json"
    if not cfg.exists():
        return []
    try:
        return list(json.loads(cfg.read_text(encoding="utf-8")).get("kit", {}).get("excluir", []))
    except (json.JSONDecodeError, AttributeError):
        return []


def leer_manifiesto() -> dict:
    if MANIFIESTO.exists():
        return json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    return {"version": None, "archivos": {}}


def version_kit() -> str:
    try:
        r = subprocess.run(["git", "-C", str(KIT), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "desconocida"
    except OSError:
        return "desconocida"


def bloque_gitignore() -> str:
    lineas = (KIT / ".gitignore").read_text(encoding="utf-8").strip().splitlines() if (KIT / ".gitignore").exists() else []
    lineas += ["", "# Respaldos de make instalar-kit", ".kit-respaldo/"]
    return "\n".join([INICIO_GITIGNORE, *lineas, FIN_GITIGNORE]) + "\n"


def gitignore_con_bloque(actual: str) -> str:
    bloque = bloque_gitignore()
    if INICIO_GITIGNORE in actual and FIN_GITIGNORE in actual:
        antes, resto = actual.split(INICIO_GITIGNORE, 1)
        _, despues = resto.split(FIN_GITIGNORE, 1)
        return antes + bloque + despues.lstrip("\n")
    separador = "" if not actual or actual.endswith("\n\n") else ("\n" if actual.endswith("\n") else "\n\n")
    return actual + separador + bloque


# ---------------------------------------------------------------- análisis

def analizar(excluir: list[str]) -> dict:
    """Compara kit, manifiesto anterior y archivos actuales del proyecto."""
    kit = archivos_del_kit(excluir)
    anterior = leer_manifiesto()["archivos"]
    r = {"kit": kit, "nuevos": [], "actualizar": [], "iguales": [], "conflictos": [],
         "previos": [], "eliminar": [], "eliminar_modificados": []}

    for rel, origen in sorted(kit.items()):
        destino = DESTINO / rel
        hash_kit = sha256(origen)
        if not destino.exists():
            r["nuevos"].append(rel)
            continue
        hash_actual = sha256(destino)
        if hash_actual == hash_kit:
            r["iguales"].append(rel)
        elif rel not in anterior:
            r["previos"].append(rel)          # existía antes de gestionarlo el kit (ej. plantilla de Spec Kit)
        elif hash_actual == anterior[rel]:
            r["actualizar"].append(rel)       # no se tocó localmente: se puede actualizar
        else:
            r["conflictos"].append(rel)       # modificado localmente

    for rel, hash_anterior in sorted(anterior.items()):
        if rel in kit or excluido(rel, excluir):
            continue
        destino = DESTINO / rel
        if not destino.exists():
            continue
        (r["eliminar"] if sha256(destino) == hash_anterior else r["eliminar_modificados"]).append(rel)
    return r


# ---------------------------------------------------------------- acciones

def respaldar(rels: list[str]) -> Path | None:
    if not rels:
        return None
    carpeta = DESTINO / ".kit-respaldo" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for rel in rels:
        destino = carpeta / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DESTINO / rel, destino)
    return carpeta


def instalar(forzar: bool) -> int:
    excluir = leer_excluir()
    a = analizar(excluir)

    if a["conflictos"] and not forzar:
        print("✗ Estos archivos del kit fueron modificados en este proyecto:", file=sys.stderr)
        for rel in a["conflictos"]:
            print(f"    {rel}", file=sys.stderr)
        print("\nOpciones:", file=sys.stderr)
        print("  • Si el cambio sirve a todos los proyectos: llévalo al repositorio del kit y actualiza.", file=sys.stderr)
        print("  • Si es propio de este proyecto: agrégalo a \"kit.excluir\" en equipo/config.json.", file=sys.stderr)
        print("  • Para descartarlo (se guarda un respaldo): make instalar-kit FORZAR=1", file=sys.stderr)
        return 1

    respaldo = respaldar(a["previos"] + a["conflictos"] + a["eliminar_modificados"] if forzar else a["previos"])

    for rel in a["nuevos"] + a["actualizar"] + a["previos"] + (a["conflictos"] if forzar else []):
        destino = DESTINO / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(a["kit"][rel], destino)

    eliminados = a["eliminar"] + (a["eliminar_modificados"] if forzar else [])
    for rel in eliminados:
        (DESTINO / rel).unlink()
        padre = (DESTINO / rel).parent
        while padre != DESTINO and padre.exists() and not any(padre.iterdir()):
            padre.rmdir()
            padre = padre.parent

    semillas = []
    for rel in SEMILLAS:
        origen, destino = KIT / rel, DESTINO / rel
        if origen.exists() and not destino.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)
            semillas.append(rel)

    gi = DESTINO / ".gitignore"
    actual = gi.read_text(encoding="utf-8") if gi.exists() else ""
    nuevo = gitignore_con_bloque(actual)
    if nuevo != actual:
        gi.write_text(nuevo, encoding="utf-8")

    manifiesto = {
        "_comentario": f"Generado por make instalar-kit. Lista los archivos que vienen del kit ({RUTA_KIT}/) y su hash.",
        "version": version_kit(),
        "ruta_kit": RUTA_KIT,
        "archivos": {rel: sha256(DESTINO / rel) for rel in sorted(a["kit"])},
    }
    MANIFIESTO.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Resumen
    print(f"Kit {manifiesto['version']} instalado en {DESTINO.name}/")
    for titulo, lista in (("nuevos", a["nuevos"]), ("actualizados", a["actualizar"] + (a["conflictos"] if forzar else [])),
                          ("reemplazados (existían antes)", a["previos"]), ("eliminados", eliminados),
                          ("semillas (ahora son del proyecto)", semillas)):
        if lista:
            print(f"  {len(lista):>3} {titulo}")
            if titulo != "nuevos":
                for rel in lista:
                    print(f"        {rel}")
    if a["eliminar_modificados"] and not forzar:
        print("  ! El kit eliminó estos archivos, pero tienen cambios locales; se conservaron:")
        for rel in a["eliminar_modificados"]:
            print(f"        {rel}")
    if respaldo:
        print(f"  Respaldo de lo reemplazado: {respaldo.relative_to(DESTINO)}/")
    if not (a["nuevos"] or a["actualizar"] or a["previos"] or eliminados or semillas or (forzar and a["conflictos"])):
        print("  Sin cambios: el proyecto ya estaba al día.")
    return 0


def verificar() -> int:
    if not MANIFIESTO.exists():
        print(f"✗ El kit no está instalado en este proyecto (falta .kit-manifest.json). Ejecuta: make -f {RUTA_KIT}/Makefile instalar-kit", file=sys.stderr)
        return 1
    excluir = leer_excluir()
    a = analizar(excluir)
    anterior = leer_manifiesto()
    problemas = 0
    if a["conflictos"] or a["previos"]:
        problemas += 1
        print("✗ Archivos del kit modificados en el proyecto (llévalos al kit o agrégalos a kit.excluir):", file=sys.stderr)
        for rel in a["conflictos"] + a["previos"]:
            print(f"    {rel}", file=sys.stderr)
    pendientes = a["nuevos"] + a["actualizar"] + a["eliminar"]
    if pendientes:
        problemas += 1
        print(f"✗ El submódulo {RUTA_KIT}/ está en {version_kit()} pero se instaló {anterior.get('version')}. Ejecuta: make instalar-kit", file=sys.stderr)
        for rel in pendientes:
            print(f"    {rel}", file=sys.stderr)
    if problemas:
        return 1
    print(f"OK: kit {anterior.get('version')} instalado y sin cambios locales.")
    return 0


def main() -> int:
    if KIT == DESTINO:
        print("Este comando se ejecuta desde la raíz de un proyecto que tiene el kit como submódulo, no dentro del kit.", file=sys.stderr)
        return 1
    if not (DESTINO / ".git").exists():
        print("Ejecuta este comando desde la raíz del repositorio del proyecto.", file=sys.stderr)
        return 1
    if "--verificar" in sys.argv[1:]:
        return verificar()
    return instalar(forzar="--forzar" in sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
