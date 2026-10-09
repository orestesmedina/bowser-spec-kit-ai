#!/usr/bin/env python3
"""Ejecuta los verbos del perfil del proyecto (equipo/perfil.json).

El núcleo del kit solo sabe pedir verbos (formato, revisar, probar, cobertura, auditar, generar). Qué comando
corresponde a cada uno lo declara cada parte del proyecto en su perfil. Este script lo busca y lo ejecuta
dentro de la carpeta de la parte. Una parte que no define un verbo se omite con un aviso: no es un error.

Uso:
  python3 scripts/verbos.py probar                 el verbo en todas las partes
  python3 scripts/verbos.py formato revisar        varios verbos, en orden
  python3 scripts/verbos.py probar --parte api     solo en una parte
  python3 scripts/verbos.py generar --verificar    además falla si la parte quedó con cambios sin commit
  python3 scripts/verbos.py --pre-commit           controles del perfil en cada commit (lo llama el hook de git)

Solo usa la biblioteca estándar de Python 3.9+.
"""
from __future__ import annotations

import fnmatch
import os
import subprocess
import sys

from perfil import RAIZ, RUTA, VERBOS, ErrorPerfil, cargar, comando_de, perfil_valido, validar


def correr(comando: str, carpeta: str) -> int:
    sys.stdout.flush()
    sys.stderr.flush()
    return subprocess.run(["bash", "-o", "pipefail", "-c", comando], cwd=RAIZ / carpeta).returncode


def git(*args: str) -> list[str]:
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True)
    return [l for l in r.stdout.decode("utf-8", "replace").splitlines() if l]


def dentro_de(archivo: str, carpeta: str) -> str | None:
    """La ruta del archivo relativa a la carpeta de la parte, o None si no le pertenece."""
    carpeta = os.path.normpath(carpeta).replace("\\", "/")
    if carpeta == ".":
        return archivo
    return archivo[len(carpeta) + 1:] if archivo.startswith(carpeta + "/") else None


def es_de_terceros(rel: str, parte: dict) -> bool:
    return any(rel == t.rstrip("/") or rel.startswith(t.rstrip("/") + "/") for t in parte.get("terceros", []))


# ---------------------------------------------------------------- ejecutar verbos

def ejecutar(perfil: dict, verbos: list[str], solo: str | None, verificar: bool) -> int:
    partes = [p for p in perfil["partes"] if solo in (None, p["nombre"])]
    if not partes:
        nombres = ", ".join(p["nombre"] for p in perfil["partes"])
        print(f"✗ No hay ninguna parte llamada «{solo}» en {RUTA} (partes: {nombres}).", file=sys.stderr)
        return 2

    fallos: list[str] = []
    for verbo in verbos:
        definido = False
        for parte in partes:
            comando = comando_de(parte, verbo)
            if not comando:
                print(f"⚠ La parte «{parte['nombre']}» no define el verbo «{verbo}»: se omite.")
                continue
            definido = True
            print(f"▶ {verbo} · {parte['nombre']} ({parte['carpeta']}): {comando}")
            codigo = correr(comando, parte["carpeta"])
            if codigo != 0:
                print(f"✗ {verbo} falló en la parte «{parte['nombre']}» (código {codigo}).", file=sys.stderr)
                fallos.append(f"{verbo} en «{parte['nombre']}»")
                continue
            if verificar and verbo == "generar":
                cambios = git("status", "--porcelain", "--", parte["carpeta"])
                if cambios:
                    print(f"✗ El código generado de la parte «{parte['nombre']}» no estaba al día (o hay cambios sin commit):",
                          file=sys.stderr)
                    for c in cambios:
                        print(f"  {c}", file=sys.stderr)
                    print("  Ejecuta 'make generar' y agrega el resultado al commit.", file=sys.stderr)
                    fallos.append(f"código generado de «{parte['nombre']}»")
                else:
                    print(f"✓ Código generado al día en la parte «{parte['nombre']}».")
        if not definido:
            print(f"⚠ Ninguna parte define «{verbo}» ({VERBOS[verbo]}). Se agrega en {RUTA}.")

    if fallos:
        print(f"\n✗ Falló: {'; '.join(fallos)}.", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------- controles del commit

def pre_commit() -> int:
    """Controles del perfil en cada commit. Escribe un «✗» por problema y termina con 1 si hay alguno."""
    errores = 0

    def fallar(mensaje: str) -> None:
        nonlocal errores
        print(f"✗ {mensaje}", file=sys.stderr)
        errores += 1

    # 1. Los comandos del perfil se ejecutan en la máquina de cada persona y en la integración continua:
    #    un cambio en él lo confirma una persona.
    if RUTA in git("diff", "--cached", "--name-only", "--no-renames") and os.environ.get("APROBADO_PERFIL") != "1":
        fallar(f"El perfil del proyecto ({RUTA}) cambió. Sus comandos se ejecutan en tu máquina y en la integración "
               "continua: revísalo (make profile) y confirma con: APROBADO_PERFIL=1 git commit ...")

    try:
        perfil = cargar()
    except ErrorPerfil as e:
        fallar(str(e))
        return 1
    if perfil is None:          # el commit lo está eliminando
        return 1 if errores else 0
    problemas, _ = validar(perfil)
    for p in problemas:
        fallar(f"{RUTA}: {p}")
    if problemas:
        return 1

    # 2. Archivos que no se modifican una vez versionados (ej. migraciones): se crea uno nuevo.
    tocados = git("diff", "--cached", "--name-only", "--no-renames", "--diff-filter=MD")
    for parte in perfil["partes"]:
        patrones = parte.get("inmutables", [])
        violan = []
        for archivo in tocados:
            rel = dentro_de(archivo, parte["carpeta"])
            if rel is not None and any(fnmatch.fnmatchcase(rel, patron) for patron in patrones):
                violan.append(archivo)
        if violan:
            fallar(f"Estos archivos de la parte «{parte['nombre']}» no se modifican una vez versionados; crea uno nuevo: "
                   + " ".join(violan))

    # 3. Formato, solo en las partes que el commit toca.
    nuevos = git("diff", "--cached", "--name-only", "--no-renames", "--diff-filter=ACM")
    for parte in perfil["partes"]:
        comando = comando_de(parte, "formato")
        if not comando:
            continue
        propios = [rel for rel in (dentro_de(a, parte["carpeta"]) for a in nuevos)
                   if rel is not None and not es_de_terceros(rel, parte)]
        if propios and correr(comando, parte["carpeta"]) != 0:
            fallar(f"La parte «{parte['nombre']}» no pasa la revisión de formato ({comando}).")

    return 1 if errores else 0


# ---------------------------------------------------------------- principal

def main() -> int:
    args = sys.argv[1:]
    if "--pre-commit" in args:
        return pre_commit()

    solo = None
    if "--parte" in args:
        i = args.index("--parte")
        if i + 1 >= len(args):
            print("Uso: scripts/verbos.py <verbo>... [--parte <nombre>] [--verificar]", file=sys.stderr)
            return 2
        solo = args[i + 1]
        del args[i:i + 2]
    verificar = "--verificar" in args
    verbos = [a for a in args if not a.startswith("--")]
    desconocidos = [v for v in verbos if v not in VERBOS]
    if not verbos or desconocidos:
        if desconocidos:
            print(f"✗ Verbo desconocido: {', '.join(desconocidos)}.", file=sys.stderr)
        print("Uso: scripts/verbos.py <verbo>... [--parte <nombre>] [--verificar]", file=sys.stderr)
        print("Verbos:", file=sys.stderr)
        for verbo, que in VERBOS.items():
            print(f"  {verbo:<10} {que}", file=sys.stderr)
        return 2

    perfil = perfil_valido()
    if perfil is None:
        print(f"✗ Este proyecto no tiene perfil ({RUTA}). Para crearlo, escribe en el chat: /bowser-profile", file=sys.stderr)
        return 1
    return ejecutar(perfil, verbos, solo, verificar)


if __name__ == "__main__":
    sys.exit(main())
