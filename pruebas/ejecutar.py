#!/usr/bin/env python3
"""Pruebas automáticas del kit: instala el kit en proyectos temporales y comprueba que todo cuadre.

Uso (desde la raíz del repositorio del kit, en Linux o WSL):
  python3 pruebas/ejecutar.py                  todas las pruebas
  python3 pruebas/ejecutar.py --solo costos    solo las que tengan "costos" en el grupo, el nombre o la descripción
  python3 pruebas/ejecutar.py --lista          las muestra sin ejecutarlas
  python3 pruebas/ejecutar.py --desde v1.7.0   versión anterior desde la que se prueba la actualización
  python3 pruebas/ejecutar.py --estricto       una prueba omitida cuenta como fallo (para la integración continua)
  python3 pruebas/ejecutar.py --conservar      no borra la carpeta temporal (para investigar un fallo)

Termina con código 0 si todo pasó y 1 si algo falló. Solo usa la biblioteca estándar de Python 3.9+.
"""
from __future__ import annotations

import argparse
import importlib
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.dont_write_bytecode = True

import apoyo  # noqa: E402

GRUPOS = ["nucleo", "go"]
# Orden de lectura: primero lo más básico. Un archivo que no esté aquí se ejecuta al final.
ORDEN = ["repositorio", "instalacion", "actualizacion", "controles", "costos", "generados", "cobertura"]


def posicion(archivo: Path) -> tuple[int, str]:
    tema = archivo.stem[len("prueba_"):]
    return (ORDEN.index(tema) if tema in ORDEN else len(ORDEN), tema)


def cargar() -> None:
    for grupo in GRUPOS:
        sys.path.insert(0, str(AQUI / grupo))
        for archivo in sorted((AQUI / grupo).glob("prueba_*.py"), key=posicion):
            modulo = importlib.import_module(archivo.stem)
            for p in apoyo.PRUEBAS:
                if p["grupo"] == modulo.__name__:
                    p["grupo"] = f"{grupo}/{archivo.stem[len('prueba_'):]}"


def sangrar(texto: str) -> str:
    return "\n".join("      " + linea for linea in texto.splitlines())


def main() -> int:
    ap = argparse.ArgumentParser(description="Pruebas automáticas del kit.")
    ap.add_argument("--solo", metavar="TEXTO", help="ejecuta solo las pruebas que contengan este texto")
    ap.add_argument("--lista", action="store_true", help="muestra las pruebas sin ejecutarlas")
    ap.add_argument("--desde", metavar="TAG", help="versión anterior para la prueba de actualización (por defecto, el último tag)")
    ap.add_argument("--estricto", action="store_true", help="una prueba omitida cuenta como fallo")
    ap.add_argument("--conservar", action="store_true", help="no borra la carpeta temporal")
    args = ap.parse_args()

    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")

    cargar()
    elegidas = [p for p in apoyo.PRUEBAS
                if not args.solo or args.solo.lower() in f"{p['grupo']} {p['nombre']} {p['descripcion']}".lower()]
    if not elegidas:
        print(f"Ninguna prueba coincide con «{args.solo}».", file=sys.stderr)
        return 1
    if args.lista:
        grupo = None
        for p in elegidas:
            if p["grupo"] != grupo:
                grupo = p["grupo"]
                print(grupo)
            print(f"  {p['descripcion']}" + (f"   [necesita: {', '.join(p['requiere'])}]" if p["requiere"] else ""))
        print(f"\n{len(elegidas)} pruebas")
        return 0

    faltan = [h for h in ("git", "make", "bash") if shutil.which(h) is None]
    if faltan or sys.platform == "win32":
        motivo = f"faltan: {', '.join(faltan)}" if faltan else "esto es Windows"
        print(f"✗ Las pruebas del kit se ejecutan en Linux o WSL, con git, make y bash ({motivo}).", file=sys.stderr)
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="pruebas-kit-"))
    e = apoyo.Entorno(tmp, args.desde)
    try:
        anterior = e.version_anterior()
    except (apoyo.Omitida, apoyo.Fallo) as error:
        if args.desde:
            print(f"✗ No se puede usar --desde {args.desde}: {error}", file=sys.stderr)
            return 1
        anterior = None
    print(f"Pruebas del kit {e.version}" + (f" · actualización desde {anterior}" if anterior else " · sin versión anterior"))

    pasaron, fallaron, omitidas = 0, [], []
    inicio, grupo = time.time(), None
    try:
        for p in elegidas:
            if p["grupo"] != grupo:
                grupo = p["grupo"]
                print(f"\n{grupo}")
            t0 = time.time()
            try:
                falta = [h for h in p["requiere"] if shutil.which(h) is None]
                if falta:
                    raise apoyo.Omitida(f"falta {', '.join(falta)} en esta máquina")
                p["funcion"](e)
            except apoyo.Omitida as error:
                omitidas.append(p)
                print(f"  – {p['descripcion']}\n      omitida: {error}")
            except apoyo.Fallo as error:
                fallaron.append(p)
                print(f"  ✗ {p['descripcion']}\n{sangrar(str(error))}")
            except Exception:   # un error de la propia prueba también es un fallo, con su traza
                fallaron.append(p)
                print(f"  ✗ {p['descripcion']}\n{sangrar(traceback.format_exc())}")
            else:
                pasaron += 1
                print(f"  ✓ {p['descripcion']}  ({time.time() - t0:.1f} s)")
            sys.stdout.flush()
    finally:
        if args.conservar:
            print(f"\nCarpeta temporal conservada: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nResultado: {pasaron} pasaron, {len(fallaron)} fallaron, {len(omitidas)} omitidas · {time.time() - inicio:.0f} s")
    if fallaron:
        print("✗ Fallaron:")
        for p in fallaron:
            print(f"    {p['grupo']}: {p['descripcion']}")
    if omitidas and args.estricto:
        print("✗ Modo estricto: no puede quedar ninguna prueba omitida.")
    if fallaron or (omitidas and args.estricto):
        return 1
    print("✓ Todo pasó." if not omitidas else "✓ Pasó todo lo que se pudo ejecutar en esta máquina.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
