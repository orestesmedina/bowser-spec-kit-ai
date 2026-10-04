#!/usr/bin/env python3
"""Cobertura de la capa de servicio del backend (constitución III: mínimo 80 %).

Lee un perfil de cobertura de Go (go test -coverprofile=coverage.out ./...) y mide solo los
archivos de servicio: service*.go dentro de internal/ (sin los _test.go), sumando todos los
dominios. Falla (salida 1) si el total queda por debajo del mínimo.

Uso:
  python3 scripts/cobertura.py backend/coverage.out
"""
from __future__ import annotations

import re
import sys
from pathlib import PurePosixPath

sys.dont_write_bytecode = True

MINIMO = 80.0   # lo fija la constitución; no es configurable por proyecto
# archivo:líneaIni.colIni,líneaFin.colFin sentencias veces
BLOQUE = re.compile(r"^(?P<archivo>.+):(?P<rango>\d+\.\d+,\d+\.\d+) (?P<sentencias>\d+) (?P<veces>\d+)$")


def es_servicio(archivo: str) -> bool:
    ruta = PurePosixPath(archivo)
    return ("internal" in ruta.parts and ruta.name.startswith("service")
            and ruta.suffix == ".go" and not ruta.name.endswith("_test.go"))


def leer(perfil: str) -> dict[str, dict[str, tuple[int, int]]]:
    """archivo -> {rango: (sentencias, veces)}. Un bloque repetido (perfiles unidos) cuenta una vez."""
    archivos: dict[str, dict[str, tuple[int, int]]] = {}
    with open(perfil, encoding="utf-8") as f:
        for linea in f:
            m = BLOQUE.match(linea.strip())
            if not m or not es_servicio(m["archivo"]):
                continue
            bloques = archivos.setdefault(m["archivo"], {})
            previo = bloques.get(m["rango"], (0, 0))
            bloques[m["rango"]] = (int(m["sentencias"]), max(previo[1], int(m["veces"])))
    return archivos


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        archivos = leer(sys.argv[1])
    except OSError as e:
        print(f"✗ No se pudo leer {sys.argv[1]}: {e}. Genera el perfil con: go test -coverprofile=coverage.out ./...", file=sys.stderr)
        return 2

    print(f"COBERTURA DE LA CAPA DE SERVICIO · mínimo {MINIMO:.0f} %")
    total = cubiertas = 0
    for archivo in sorted(archivos):
        s = sum(n for n, _ in archivos[archivo].values())
        c = sum(n for n, veces in archivos[archivo].values() if veces > 0)
        total, cubiertas = total + s, cubiertas + c
        corto = archivo.split("/internal/", 1)[-1]
        print(f"  {corto:<50} {c:>4}/{s:<4} {100 * c / s if s else 100:>6.1f} %")
    if total == 0:
        print("  Sin archivos service*.go con código en internal/: nada que medir.")
        return 0

    porcentaje = 100 * cubiertas / total
    print(f"  {'Total':<50} {cubiertas:>4}/{total:<4} {porcentaje:>6.1f} %")
    if porcentaje < MINIMO:
        sys.stdout.flush()   # que la tabla salga antes que el error cuando la salida va a un archivo o al CI
        print(f"\n✗ Cobertura de servicio {porcentaje:.1f} % por debajo del mínimo {MINIMO:.0f} % (constitución, III). "
              "Agrega pruebas a la capa de servicio.", file=sys.stderr)
        return 1
    print("\n✓ Cumple el mínimo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
