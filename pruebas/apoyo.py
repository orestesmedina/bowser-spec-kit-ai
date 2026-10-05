"""Apoyo para las pruebas del kit: registro de pruebas, copias del kit y proyectos temporales.

Cada prueba es una función decorada con @prueba que recibe un Entorno. Con él pide copias del kit
(la versión que se está probando o la anterior publicada) y crea proyectos temporales donde lo instala.
Una prueba falla cuando lanza Fallo (o cualquier otra excepción) y se omite cuando lanza Omitida.

Solo usa la biblioteca estándar de Python 3.9+.
"""
from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SUBMODULO = ".bowser-spec-kit-ai"


class Fallo(AssertionError):
    """La prueba encontró algo que no cuadra."""


class Omitida(Exception):
    """La prueba no se puede ejecutar en esta máquina (falta una herramienta o una versión anterior)."""


PRUEBAS: list[dict] = []


def prueba(descripcion: str, requiere: tuple[str, ...] = ()):
    """Registra una prueba. 'requiere' son los programas que deben estar en el PATH; si falta uno, se omite."""
    def registrar(funcion):
        PRUEBAS.append({"grupo": funcion.__module__, "nombre": funcion.__name__, "descripcion": descripcion,
                        "requiere": requiere, "funcion": funcion})
        return funcion
    return registrar


# ---------------------------------------------------------------- afirmaciones

def afirmar(condicion, mensaje: str) -> None:
    if not condicion:
        raise Fallo(mensaje)


def contiene(texto: str, esperado: str, que: str = "la salida") -> None:
    if esperado not in texto:
        raise Fallo(f"{que} no contiene «{esperado}». Se obtuvo:\n{recortar(texto)}")


def recortar(texto: str, lineas: int = 25) -> str:
    partes = texto.strip().splitlines()
    if len(partes) > lineas:
        partes = [f"… ({len(partes) - lineas} líneas antes)"] + partes[-lineas:]
    return "\n".join(partes)


# ---------------------------------------------------------------- ejecución de comandos

def entorno_base(datos: Path) -> dict[str, str]:
    """Variables para que git y los scripts se comporten igual en cualquier máquina."""
    e = dict(os.environ)
    for sobra in ("APROBADO_CONSTITUCION", "APROBADO_COSTOS", "NOVEDADES_AL_FINAL", "KIT", "FORZAR",
                  "MAKEFLAGS", "MAKELEVEL", "MFLAGS", "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        e.pop(sobra, None)
    e.update({
        # Sin la configuración personal de git (hooks globales, firma de commits, plantillas…).
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        # Submódulos desde una carpeta local, y repositorios en discos de Windows vistos desde WSL.
        "GIT_CONFIG_COUNT": "3",
        "GIT_CONFIG_KEY_0": "protocol.file.allow", "GIT_CONFIG_VALUE_0": "always",
        "GIT_CONFIG_KEY_1": "safe.directory", "GIT_CONFIG_VALUE_1": "*",
        "GIT_CONFIG_KEY_2": "init.defaultBranch", "GIT_CONFIG_VALUE_2": "main",
        "GIT_AUTHOR_NAME": "prueba", "GIT_AUTHOR_EMAIL": "prueba@example.com",
        "GIT_COMMITTER_NAME": "prueba", "GIT_COMMITTER_EMAIL": "prueba@example.com",
        "XDG_DATA_HOME": str(datos),   # el registro local de make costos no toca el de la persona
        "LC_ALL": "C.UTF-8", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1",
    })
    return e


class Resultado:
    def __init__(self, orden: list[str], codigo: int, salida: str):
        self.orden, self.codigo, self.salida = orden, codigo, salida


def correr(orden: list[str], carpeta: Path, entorno: dict[str, str], espera: int | None = 0,
           extra: dict[str, str] | None = None) -> Resultado:
    """Ejecuta un comando y junta stdout y stderr. espera=0: debe terminar bien; espera=1: debe fallar;
    espera=None: no se comprueba."""
    env = dict(entorno, **(extra or {}))
    try:
        p = subprocess.run(orden, cwd=carpeta, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=300)
    except FileNotFoundError:
        raise Fallo(f"no se encontró el programa «{orden[0]}»")
    except subprocess.TimeoutExpired:
        raise Fallo(f"«{' '.join(orden)}» no terminó en 5 minutos")
    r = Resultado(orden, p.returncode, p.stdout.decode("utf-8", "replace"))
    texto = " ".join(orden)
    if espera == 0 and r.codigo != 0:
        raise Fallo(f"«{texto}» debía terminar bien y falló (código {r.codigo}):\n{recortar(r.salida)}")
    if espera == 1 and r.codigo == 0:
        raise Fallo(f"«{texto}» debía fallar y terminó bien:\n{recortar(r.salida)}")
    return r


# ---------------------------------------------------------------- copias del kit y proyectos

class Proyecto:
    """Un repositorio temporal con el kit como submódulo."""

    def __init__(self, ruta: Path, entorno: dict[str, str]):
        self.ruta, self.entorno = ruta, entorno

    def correr(self, *orden: str, espera: int | None = 0, extra: dict[str, str] | None = None) -> Resultado:
        return correr(list(orden), self.ruta, self.entorno, espera, extra)

    def make(self, *args: str, espera: int | None = 0, extra: dict[str, str] | None = None) -> Resultado:
        return self.correr("make", "--no-print-directory", *args, espera=espera, extra=extra)

    def git(self, *args: str, espera: int | None = 0, extra: dict[str, str] | None = None) -> Resultado:
        return self.correr("git", *args, espera=espera, extra=extra)

    def commit(self, mensaje: str, espera: int | None = 0, extra: dict[str, str] | None = None) -> Resultado:
        """git add -A y commit, con los hooks del proyecto."""
        self.git("add", "-A")
        return self.git("commit", "-m", mensaje, espera=espera, extra=extra)

    def commits(self) -> int:
        r = self.git("rev-list", "--count", "HEAD", espera=None)
        return int(r.salida.strip()) if r.codigo == 0 else 0

    def pendientes(self) -> list[str]:
        return [l for l in self.git("status", "--short").salida.splitlines() if l.strip()]

    def archivo(self, rel: str) -> Path:
        return self.ruta / rel

    def existe(self, rel: str) -> bool:
        return (self.ruta / rel).exists()

    def leer(self, rel: str) -> str:
        return (self.ruta / rel).read_text(encoding="utf-8")

    def escribir(self, rel: str, texto: str) -> None:
        destino = self.ruta / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8", newline="\n")

    def agregar(self, rel: str, texto: str) -> None:
        self.escribir(rel, self.leer(rel) + texto)

    def instalar_kit(self, **kw) -> Resultado:
        """La instalación de la primera vez: con el Makefile del submódulo."""
        return self.make("-f", f"{SUBMODULO}/Makefile", "instalar-kit", **kw)

    def verificar_kit(self, espera: int | None = 0) -> Resultado:
        return self.correr("python3", f"{SUBMODULO}/scripts/instalar_kit.py", "--verificar", espera=espera)


class Entorno:
    """Lo que comparten las pruebas de una ejecución: carpeta temporal, copias del kit y versión anterior."""

    def __init__(self, tmp: Path, desde: str | None = None):
        self.tmp = tmp
        self.entorno = entorno_base(tmp / "datos")
        self.version = (RAIZ / "VERSION").read_text(encoding="utf-8").strip()
        self._desde_pedido = desde
        self._desde: str | None = None
        self._arboles: dict[str, str] = {}
        self._plantillas: dict[str, Path] = {}
        self._n = 0

    # -- versiones

    def _git_origen(self, *args: str, extra: dict[str, str] | None = None, binario: bool = False):
        p = subprocess.run(["git", *args], cwd=RAIZ, env=dict(self.entorno, **(extra or {})),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise Fallo(f"git {' '.join(args)} falló en el repositorio del kit: {p.stderr.decode('utf-8', 'replace').strip()}")
        return p.stdout if binario else p.stdout.decode("utf-8", "replace").strip()

    def version_anterior(self) -> str:
        """El tag publicado más reciente cuya versión es distinta de la que se está probando."""
        if self._desde:
            return self._desde
        if self._desde_pedido:
            try:
                self._git_origen("rev-parse", "--verify", "--quiet", f"{self._desde_pedido}^{{commit}}")
            except Fallo:
                raise Fallo(f"no existe el tag o commit «{self._desde_pedido}» (los tags se ven con: git tag)")
            self._desde = self._desde_pedido
            return self._desde
        tags = [t for t in self._git_origen("tag", "--list", "v*", "--sort=-v:refname").splitlines()
                if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
        for t in tags:
            if self._git_origen("show", f"{t}:VERSION") != self.version:
                self._desde = t
                return t
        raise Omitida("no hay un tag de una versión anterior (¿clon sin tags? prueba: git fetch --tags)")

    def _arbol(self, cual: str) -> str:
        """Identificador de git del contenido a probar. 'actual' es la carpeta de trabajo tal como está,
        con los cambios sin commit, y con los permisos que git tiene registrados."""
        if cual not in self._arboles:
            if cual == "actual":
                indice = self.tmp / "indice-actual"
                real = Path(self._git_origen("rev-parse", "--git-path", "index"))
                real = real if real.is_absolute() else RAIZ / real
                if real.exists():
                    shutil.copy2(real, indice)
                extra = {"GIT_INDEX_FILE": str(indice)}
                self._git_origen("add", "-A", extra=extra)
                self._arboles[cual] = self._git_origen("write-tree", extra=extra)
            else:
                self._arboles[cual] = self._git_origen("rev-parse", f"{self.version_anterior()}^{{tree}}")
        return self._arboles[cual]

    def _extraer(self, cual: str, destino: Path) -> None:
        datos = self._git_origen("archive", "--format=tar", self._arbol(cual), binario=True)
        with tarfile.open(fileobj=io.BytesIO(datos)) as tar:
            try:
                tar.extractall(destino, filter="fully_trusted")
            except TypeError:           # Python sin el parámetro filter
                tar.extractall(destino)

    # -- copias del kit

    def kit(self, cual: str = "actual") -> Path:
        """Un repositorio git con el kit ('actual' o 'anterior'). Cada llamada devuelve una copia propia,
        que la prueba puede modificar o actualizar sin afectar a las demás."""
        if cual not in self._plantillas:
            plantilla = self.tmp / f"plantilla-kit-{cual}"
            plantilla.mkdir()
            self._extraer(cual, plantilla)
            correr(["git", "init", "-q"], plantilla, self.entorno)
            correr(["git", "add", "-A"], plantilla, self.entorno)
            correr(["git", "commit", "-qm", f"kit {cual}", "--no-verify"], plantilla, self.entorno)
            self._plantillas[cual] = plantilla
        self._n += 1
        copia = self.tmp / f"kit-{self._n}"
        shutil.copytree(self._plantillas[cual], copia, symlinks=True)
        return copia

    def pasar_kit_a(self, kit: Path, cual: str = "actual", mensaje: str = "kit nuevo") -> None:
        """Reemplaza el contenido de una copia del kit por otra versión y hace el commit (una 'publicación')."""
        correr(["git", "rm", "-rqf", "."], kit, self.entorno)
        self._extraer(cual, kit)
        self.commit_kit(kit, mensaje)

    def commit_kit(self, kit: Path, mensaje: str) -> None:
        correr(["git", "add", "-A"], kit, self.entorno)
        correr(["git", "commit", "-qm", mensaje, "--no-verify"], kit, self.entorno)

    # -- proyectos

    def proyecto_vacio(self) -> Proyecto:
        self._n += 1
        ruta = self.tmp / f"proyecto-{self._n}"
        ruta.mkdir()
        p = Proyecto(ruta, self.entorno)
        p.git("init", "-q")
        return p

    def proyecto(self, kit: Path | None = None, commit: bool = True) -> Proyecto:
        """Proyecto nuevo con el kit instalado (por defecto, la versión que se está probando)."""
        p = self.proyecto_vacio()
        p.git("submodule", "add", "-q", str(kit or self.kit()), SUBMODULO)
        p.instalar_kit()
        if commit:
            p.commit("chore: instala kit")
        return p
