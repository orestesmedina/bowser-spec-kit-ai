#!/usr/bin/env python3
"""Instala o actualiza el kit (submódulo, por defecto en .bowser-spec-kit-ai/) en la raíz del proyecto.

Las herramientas (Claude Code, Codex, OpenCode, Spec Kit, GitHub Actions) leen sus archivos
en la raíz del proyecto, no dentro del submódulo. Este script:

  1. Copia a la raíz los archivos GESTIONADOS por el kit (se reemplazan en cada actualización).
  2. Copia del catálogo (catalogo/skills/) a .agents/skills/ solo las skills de tecnología que nombra el perfil
     del proyecto (equipo/perfil.json); sin perfil, las tres de siempre. También quedan gestionadas.
  3. Copia las SEMILLAS solo si no existen (después son del proyecto: config.json, CODEOWNERS…).
  4. Mantiene un bloque del kit dentro de .gitignore.
  5. Registra en .kit-manifest.json qué archivos vienen del kit y su hash, para:
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
import os
import re
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
    "equipo/comandos/",
    "equipo/adaptadores/",
    "equipo/orquestador.md",
    "scripts/",
    "docs/plantillas/",
]
# La documentación (docs/*.md) no se copia: en los proyectos se lee desde el submódulo, siempre en la versión instalada.
# Nunca se copian (solo tienen sentido dentro del kit).
NUNCA = {"scripts/instalar_kit.py", ".github/workflows/kit.yml"}
# Tampoco se copian los comandos que sincronizar.py genera para Codex dentro de .agents/skills/:
# cada proyecto genera los suyos según las herramientas que tenga activas.
sys.path.insert(0, str(KIT / "scripts"))
from sincronizar import COMANDOS_CODEX as GENERADO_EN_FUENTES  # noqa: E402
import catalogo  # noqa: E402
import perfil as perfil_proyecto  # noqa: E402
sys.path.pop(0)
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
            if rel in NUNCA or rel.startswith(GENERADO_EN_FUENTES) or es_ignorable(rel) or excluido(rel, excluir):
                continue
            resultado[rel] = p
    return resultado


def skill_de(rel: str) -> str | None:
    """El nombre de la skill a la que pertenece un archivo de .agents/skills/, o None si no es de una skill."""
    partes = rel.split("/")
    return partes[2] if rel.startswith(catalogo.INSTALADAS + "/") and len(partes) > 3 else None


def archivos_del_catalogo(excluir: list[str], anterior: dict) -> tuple[dict[str, Path], list[str]]:
    """Las skills del catálogo que le tocan a este proyecto (ruta en el proyecto -> archivo de origen) y avisos.
    Con perfil, las que nombra; sin perfil, las de siempre."""
    disponibles, _ = catalogo.leer(KIT / catalogo.CARPETA)
    avisos: list[str] = []
    try:
        perfil = perfil_proyecto.cargar(DESTINO)
    except perfil_proyecto.ErrorPerfil:
        # No se sabe qué pide el proyecto: ni se agregan ni se retiran skills hasta que el perfil se pueda leer.
        pedidas = sorted({skill_de(rel) for rel in anterior} & set(disponibles))
        avisos.append(f"{perfil_proyecto.RUTA} no se puede leer: las skills del catálogo se dejan como estaban. "
                      "Corrígelo (make profile) y repite make instalar-kit.")
    else:
        pedidas = list(catalogo.SIN_PERFIL) if perfil is None else perfil_proyecto.skills_nombradas(perfil)
        for s in pedidas:
            if s not in disponibles and not (DESTINO / catalogo.INSTALADAS / s / "SKILL.md").exists():
                avisos.append(f"El perfil pide la skill «{s}», que no está en el catálogo del kit ni en "
                              f"{catalogo.INSTALADAS}/: los agentes trabajarán sin ella (catálogo: make skills).")
    resultado: dict[str, Path] = {}
    for nombre in pedidas:
        if nombre not in disponibles:
            continue
        origen = disponibles[nombre]["carpeta"]
        for p in origen.rglob("*"):
            rel = f"{catalogo.INSTALADAS}/{nombre}/{p.relative_to(origen).as_posix()}"
            if p.is_file() and not es_ignorable(rel) and not excluido(rel, excluir):
                resultado[rel] = p
    return resultado, avisos


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


def commit_kit() -> str:
    try:
        r = subprocess.run(["git", "-C", str(KIT), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "desconocido"
    except OSError:
        return "desconocido"


def version_kit() -> str:
    """Versión semántica del archivo VERSION del kit (ej. 1.6.0)."""
    archivo = KIT / "VERSION"
    return archivo.read_text(encoding="utf-8").strip() if archivo.exists() else ""


def nombre_version(version: str | None, commit: str | None) -> str:
    if version and commit:
        return f"{version} ({commit})"
    return version or commit or "desconocida"


# ---------------------------------------------------------------- novedades (CHANGELOG.md del kit)

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def clave_version(v: str) -> tuple[int, int, int] | None:
    m = SEMVER.match(v or "")
    return tuple(int(x) for x in m.groups()) if m else None  # type: ignore[return-value]


def entradas_changelog() -> list[tuple[str, str, str]]:
    """[(version, fecha, cuerpo)] en el orden del archivo (la más nueva primero)."""
    archivo = KIT / "CHANGELOG.md"
    if not archivo.exists():
        return []
    texto = archivo.read_text(encoding="utf-8")
    partes = re.split(r"^## \[([^\]]+)\](?:\s*-\s*(\S+))?\s*$", texto, flags=re.M)
    entradas = []
    for i in range(1, len(partes) - 2, 3):
        version, fecha, cuerpo = partes[i], partes[i + 1] or "", partes[i + 2].strip()
        if clave_version(version):
            entradas.append((version, fecha, cuerpo))
    return entradas


def mostrar_novedades(desde: str | None, hasta: str | None, limite_sin_desde: int = 1) -> None:
    """Imprime las entradas con desde < versión <= hasta. Sin 'desde' conocido, muestra las últimas."""
    entradas = entradas_changelog()
    if not entradas:
        return
    k_desde, k_hasta = clave_version(desde or ""), clave_version(hasta or "")
    if k_desde and k_hasta and k_desde >= k_hasta:
        return
    if k_desde:
        elegidas = [e for e in entradas if k_desde < clave_version(e[0]) and (not k_hasta or clave_version(e[0]) <= k_hasta)]
        titulo = f"Novedades del kit de {desde} a {hasta or entradas[0][0]}"
    else:
        elegidas = [e for e in entradas if not k_hasta or clave_version(e[0]) <= k_hasta][:limite_sin_desde]
        titulo = "Novedades de la versión instalada del kit" if limite_sin_desde == 1 else "Historial de cambios del kit"
    if not elegidas:
        return
    print()
    print(f"=== {titulo} ===")
    pasos = []
    for version, fecha, cuerpo in elegidas:
        print(f"\n[{version}] {fecha}")
        seccion = ""
        for linea in cuerpo.splitlines():
            if linea.startswith("### "):
                seccion = linea[4:].strip()
                if seccion.lower() != "al actualizar":
                    print(f"  {seccion}:")
                continue
            if not linea.strip():
                continue
            if seccion.lower() == "al actualizar":
                pasos.append((clave_version(version), len(pasos), f"{linea.strip().lstrip('-').strip()}  ({version})"))
            else:
                print(f"    {linea.strip()}")
    if pasos:
        print("\n⚠ PASOS MANUALES AL ACTUALIZAR:")
        for _, _, p in sorted(pasos):  # de la versión más antigua a la más nueva, en el orden escrito
            print(f"  - {p}")
    print(f"\nDetalle completo: {RUTA_KIT}/CHANGELOG.md")


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
    del_catalogo, avisos = archivos_del_catalogo(excluir, anterior)
    kit.update(del_catalogo)
    r = {"kit": kit, "nuevos": [], "actualizar": [], "iguales": [], "conflictos": [],
         "previos": [], "eliminar": [], "eliminar_modificados": [], "catalogo": set(del_catalogo), "avisos": avisos}

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
    previo = leer_manifiesto()
    version_previa = previo.get("version") if clave_version(previo.get("version") or "") else None
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

    # Hooks y scripts de shell deben ser ejecutables: si no, git y Claude Code los ignoran sin avisar.
    # Se revisan todos (no solo los copiados) para reparar instalaciones anteriores.
    for rel in a["kit"]:
        if rel.startswith(".githooks/") or rel.endswith(".sh"):
            ruta = DESTINO / rel
            ruta.chmod(ruta.stat().st_mode | 0o111)

    eliminados =a["eliminar"] + (a["eliminar_modificados"] if forzar else [])
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
        "version": version_kit() or commit_kit(),
        "commit": commit_kit(),
        "ruta_kit": RUTA_KIT,
        "archivos": {rel: sha256(DESTINO / rel) for rel in sorted(a["kit"])},
    }
    MANIFIESTO.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Resumen
    print(f"Kit {nombre_version(manifiesto['version'], manifiesto['commit'])} instalado en {DESTINO.name}/")
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
    # Skills del catálogo: lo que el perfil pide y no hay, y las que llegan por primera vez sin estar probadas.
    for aviso in a["avisos"]:
        print(f"  ! {aviso}")
    disponibles, _ = catalogo.leer(KIT / catalogo.CARPETA)
    for nombre in sorted({skill_de(rel) for rel in a["nuevos"] if rel in a["catalogo"]}):
        if disponibles[nombre]["madurez"] != "probada":
            print(f"  ! La skill «{nombre}» está {catalogo.MADUREZ[disponibles[nombre]['madurez']]}. "
                  "Revisa con más cuidado lo que los agentes hagan con ella.")
    if not (a["nuevos"] or a["actualizar"] or a["previos"] or eliminados or semillas or (forzar and a["conflictos"])):
        print("  Sin cambios: el proyecto ya estaba al día.")
    # El Makefile del kit muestra las novedades al final (--resumen-novedades). Un Makefile anterior no lo hace:
    # en ese caso se muestran aquí.
    if not os.environ.get("NOVEDADES_AL_FINAL"):
        resumen_novedades(version_previa if previo.get("archivos") else "NUEVO", previo.get("version"))
    return 0


def version_instalada() -> str:
    """Para el Makefile: versión instalada antes de actualizar ('NUEVO' si el kit no estaba instalado)."""
    m = leer_manifiesto()
    return (m.get("version") or "desconocida") if m.get("archivos") else "NUEVO"


def resumen_novedades(previa: str | None, previa_cruda: str | None = None) -> None:
    nueva = version_kit()
    if not nueva or previa == "NUEVO" or previa == nueva:
        return
    if clave_version(previa or ""):
        mostrar_novedades(previa, nueva)
    else:
        # Instalado antes de que el kit tuviera VERSION: no se sabe desde cuál viene, se muestra todo.
        print("\n(Este proyecto tenía una versión del kit anterior al historial de cambios: se muestran todas las novedades.)")
        mostrar_novedades(None, nueva, limite_sin_desde=1000)
    if not any(v == nueva for v, _, _ in entradas_changelog()):
        print(f"! La versión {nueva} no tiene entrada en {RUTA_KIT}/CHANGELOG.md (avísale a quien mantiene el kit).")


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
    disponibles, _ = catalogo.leer(KIT / catalogo.CARPETA)
    if pendientes and anterior.get("version") == version_kit() and all(skill_de(rel) in disponibles for rel in pendientes):
        # Misma versión del kit y solo cambian skills del catálogo: lo que cambió es el perfil del proyecto.
        problemas += 1
        print(f"✗ Las skills instaladas no son las que pide el perfil ({perfil_proyecto.RUTA}). Ejecuta: make instalar-kit",
              file=sys.stderr)
        for nombre in sorted({skill_de(rel) for rel in pendientes}):
            print(f"    {nombre}: {'sobra' if not any(skill_de(rel) == nombre for rel in a['kit']) else 'falta'}", file=sys.stderr)
    elif pendientes:
        problemas += 1
        print(f"✗ El submódulo {RUTA_KIT}/ está en {nombre_version(version_kit(), commit_kit())} pero se instaló "
              f"{nombre_version(anterior.get('version'), anterior.get('commit'))}. Ejecuta: make instalar-kit", file=sys.stderr)
        for rel in pendientes:
            print(f"    {rel}", file=sys.stderr)
    if problemas:
        return 1
    print(f"OK: kit {nombre_version(anterior.get('version'), anterior.get('commit'))} instalado y sin cambios locales.")
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
    if "--version-instalada" in sys.argv[1:]:
        print(version_instalada())
        return 0
    if "--resumen-novedades" in sys.argv[1:]:
        args = sys.argv[1:]
        i = args.index("--resumen-novedades")
        resumen_novedades(args[i + 1] if i + 1 < len(args) else None)
        return 0
    if "--novedades" in sys.argv[1:]:
        args = sys.argv[1:]
        desde = args[args.index("--desde") + 1] if "--desde" in args and args.index("--desde") + 1 < len(args) else None
        if desde and not clave_version(desde):
            print(f"Versión no válida: {desde} (formato 1.4.0)", file=sys.stderr)
            return 1
        instalada = leer_manifiesto().get("version")
        print(f"Kit instalado: {nombre_version(instalada, leer_manifiesto().get('commit'))} · en el submódulo: {nombre_version(version_kit(), commit_kit())}")
        mostrar_novedades(desde, version_kit() or None, limite_sin_desde=1000)
        return 0
    return instalar(forzar="--forzar" in sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
