#!/usr/bin/env python3
"""Revisa los enlaces de la documentación del kit.

Los internos (archivo y ancla, con las reglas de GitHub) los revisa siempre y forman parte de `make test-kit`.
Los externos (HTTP) solo con --externos: dependen de la red y de sitios ajenos, así que se revisan a mano.

Uso (desde cualquier carpeta):
  python3 pruebas/enlaces.py              enlaces internos
  python3 pruebas/enlaces.py --externos   también los enlaces a otros sitios

Solo usa la biblioteca estándar de Python 3.9+.
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SUELTAS = ["README.md", "MANTENER-KIT.md", "CHANGELOG.md", "HOJA-DE-RUTA.md", "pruebas/README.md", "pruebas/borradores/README.md"]


def paginas(raiz: Path = RAIZ) -> list[Path]:
    return sorted(raiz.glob("docs/*.md")) + [raiz / p for p in SUELTAS if (raiz / p).exists()]


def sin_codigo(texto: str) -> str:
    texto = re.sub(r"^(```|~~~).*?^\1\s*$", "", texto, flags=re.S | re.M)   # bloques
    return re.sub(r"`[^`\n]*`", "", texto)                                  # código en línea


def slug_github(titulo: str) -> str:
    """Regla de GitHub: minúsculas; se quita todo lo que no sea letra, número, espacio, guion o guion bajo; espacios → guiones."""
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", titulo)          # enlaces dentro del título: queda el texto
    t = t.replace("`", "").replace("*", "").strip().lower()
    t = "".join(c for c in t if c.isalnum() or c in " -_")
    return t.replace(" ", "-")


def anclas(p: Path) -> set[str]:
    en_codigo, vistas, r = False, {}, set()
    for linea in p.read_text(encoding="utf-8").splitlines():
        if re.match(r"\s*(```|~~~)", linea):
            en_codigo = not en_codigo
        m = None if en_codigo else re.match(r"(#{1,6})\s+(.*?)\s*#*\s*$", linea)
        if m:
            s = slug_github(m.group(2))
            n = vistas.get(s, 0)
            vistas[s] = n + 1
            r.add(s if n == 0 else f"{s}-{n}")
    return r


def revisar(raiz: Path = RAIZ) -> tuple[int, list[tuple[str, str, str]], dict[str, list[str]]]:
    """Devuelve (enlaces internos revisados, [(página, enlace, problema)], {dirección externa: [páginas]})."""
    internos, externos, rotos = 0, {}, []
    for p in paginas(raiz):
        origen = p.relative_to(raiz).as_posix()
        texto = sin_codigo(p.read_text(encoding="utf-8"))
        for m in re.finditer(r"(?<!\!)\[([^\]]*)\]\(\s*<?([^)\s>]+)>?[^)]*\)", texto):
            url = m.group(2)
            if url.startswith(("http://", "https://")):
                externos.setdefault(url, []).append(origen)
                continue
            if url.startswith("mailto:"):
                continue
            internos += 1
            archivo, _, ancla = url.partition("#")
            destino = (p.parent / archivo) if archivo else p
            if not destino.exists():
                rotos.append((origen, url, "el archivo no existe"))
            elif destino.is_dir():
                rotos.append((origen, url, "apunta a una carpeta"))
            elif ancla and destino.suffix == ".md" and ancla not in anclas(destino):
                cercanas = sorted(a for a in anclas(destino) if a[:6] == ancla[:6])
                rotos.append((origen, url, f"el ancla no existe (parecidas: {cercanas[:3]})"))
            elif archivo and "\\" in archivo:
                rotos.append((origen, url, "ruta con barras invertidas"))
            elif archivo and not any(q.name == Path(archivo).name for q in destino.parent.iterdir()):
                rotos.append((origen, url, "mayúsculas/minúsculas distintas al archivo real"))
    return internos, rotos, externos


def probar(url: str) -> tuple[str, str]:
    limpio = url.split("#")[0]
    for metodo in ("HEAD", "GET"):
        try:
            pedido = urllib.request.Request(limpio, method=metodo, headers={"User-Agent": "Mozilla/5.0 (verificador de enlaces del kit)"})
            with urllib.request.urlopen(pedido, timeout=25) as r:
                final = r.geturl()
                return url, f"{r.status}" + (f" → {final}" if final.rstrip("/") != limpio.rstrip("/") else "")
        except urllib.error.HTTPError as e:
            if metodo == "GET" or e.code not in (403, 405, 501):
                return url, f"HTTP {e.code}"
        except Exception as e:
            if metodo == "GET":
                return url, f"ERROR {type(e).__name__}: {str(e)[:60]}"
    return url, "?"


def main() -> int:
    internos, rotos, externos = revisar()
    print(f"INTERNOS: {internos} revisados, {len(rotos)} con problema")
    for origen, url, motivo in rotos:
        print(f"  ✗ {origen} → {url}: {motivo}")
    if "--externos" in sys.argv:
        print(f"\nEXTERNOS: {len(externos)} direcciones distintas")
        with ThreadPoolExecutor(8) as ex:
            for url, estado in sorted(ex.map(probar, externos)):
                marca = "✓" if estado.startswith("200") and "→" not in estado else ("~" if estado.startswith("200") else "✗")
                print(f"  {marca} {estado:<10.70} {url}   [{', '.join(sorted(set(q.split('/')[-1] for q in externos[url])))[:60]}]")
    return 1 if rotos else 0


if __name__ == "__main__":
    sys.exit(main())
