"""Instalar el kit en un proyecto nuevo y en uno que ya tenía archivos propios."""
import json
import os

from apoyo import SUBMODULO, afirmar, contiene, correr, prueba


@prueba("instalación en un proyecto nuevo: queda verificada, sincronizada y el commit pasa los hooks")
def instalacion_nueva(e):
    p = e.proyecto(commit=False)
    p.verificar_kit()
    p.correr("python3", "scripts/sincronizar.py", "--verificar")
    afirmar(p.git("config", "core.hooksPath").salida.strip() == ".githooks", "los hooks de git no quedaron activados")
    p.commit("chore: instala kit")
    afirmar(p.commits() == 1, "el commit de la instalación no se hizo")
    afirmar(not p.pendientes(), f"quedaron archivos sin commit después de instalar: {p.pendientes()}")

    manifiesto = json.loads(p.leer(".kit-manifest.json"))
    afirmar(manifiesto["version"] == e.version, f"el manifiesto dice {manifiesto['version']} y el kit es {e.version}")
    afirmar(manifiesto["ruta_kit"] == SUBMODULO, f"ruta del kit inesperada: {manifiesto['ruta_kit']}")
    contiene(p.leer(".gitignore"), ".kit-respaldo/", "el .gitignore del proyecto")


@prueba("lo que es solo del repositorio del kit no llega a la raíz del proyecto")
def solo_del_kit(e):
    p = e.proyecto(commit=False)
    for rel in ("README.md", "CHANGELOG.md", "VERSION", "LICENSE", "MANTENER-KIT.md", "HOJA-DE-RUTA.md",
                "kit.mk", "pruebas", "scripts/instalar_kit.py", "docs/README.md", ".github/workflows/kit.yml"):
        afirmar(not p.existe(rel), f"{rel} se copió al proyecto y es solo del kit")
    afirmar(sorted(x.name for x in p.archivo("docs").iterdir()) == ["plantillas"],
            "en docs/ del proyecto solo debe estar plantillas/")
    afirmar(p.existe(f"{SUBMODULO}/docs/aprobaciones.md"), "la documentación debe leerse desde el submódulo")
    # Las semillas sí llegan, una sola vez.
    for rel in ("equipo/config.json", "equipo/reglas.md", ".github/CODEOWNERS", ".env.example"):
        afirmar(p.existe(rel), f"falta la semilla {rel}")


@prueba("lo que llega a un proyecto nuevo no trae tecnología: ni servicios, ni variables, ni reglas de .gitignore")
def semillas_sin_tecnologia(e):
    p = e.proyecto(commit=False)
    for rel in ("docker-compose.yml", "compose.yaml"):
        afirmar(not p.existe(rel), f"{rel} llegó al proyecto: el entorno local es del proyecto, no del kit")
    gitignore = p.leer(".gitignore")
    for regla in (".env", "secrets/", ".claude/settings.local.json", "__pycache__/", ".kit-respaldo/"):
        contiene(gitignore, f"\n{regla}\n", "el bloque del kit en .gitignore")
    for palabra in ("backend", "frontend", "node_modules", "Go", "Node", "React", "*.test"):
        afirmar(palabra not in gitignore, f"el bloque del kit en .gitignore nombra «{palabra}»")
    # Sin archivo de Docker Compose, make up lo dice en vez de dejar que Docker falle.
    for orden in ("up", "down"):
        contiene(p.make(orden, espera=1).salida, "todavía no tiene entorno local")
    variables = [l for l in p.leer(".env.example").splitlines() if l.strip() and not l.lstrip().startswith("#")]
    afirmar(not variables, f".env.example trae variables de una tecnología: {variables}")
    r = p.make("test-kit", espera=1)
    contiene(r.salida, "test-kit", "el error de make")
    afirmar("test-kit" not in p.make("help").salida, "make help ofrece test-kit en un proyecto")


@prueba("la plantilla de constitución que deja Spec Kit no se toma por reglas del proyecto; una escrita a mano, sí")
def constitucion_que_ya_existia(e):
    constitucion, reglas = ".specify/memory/constitution.md", "equipo/reglas.md"
    p = e.proyecto_vacio()
    p.escribir(constitucion, "# [PROJECT_NAME] Constitution\n\n## Core Principles\n\n### [PRINCIPLE_1_NAME]\n[PRINCIPLE_1_DESCRIPTION]\n")
    p.git("submodule", "add", "-q", str(e.kit()), SUBMODULO)
    p.instalar_kit()
    contiene(p.leer(reglas), "todavía no tiene reglas propias", "las reglas de un proyecto nuevo")
    afirmar("PRINCIPLE_1_NAME" not in p.leer(reglas) + p.leer(constitucion), "la plantilla de Spec Kit quedó en la constitución")
    afirmar(p.leer(constitucion).startswith("<!-- GENERADO"), "la constitución no se generó sobre la plantilla de Spec Kit")
    p.commit("chore: instala kit")

    q = e.proyecto_vacio()
    q.escribir(constitucion, "# Constitución de mi equipo\n\n- Los informes DEBEN salir en PDF.\n")
    q.git("submodule", "add", "-q", str(e.kit()), SUBMODULO)
    contiene(q.instalar_kit().salida, f"quedó completa en {reglas}")
    contiene(q.leer(reglas), "Los informes DEBEN salir en PDF.", "las reglas del proyecto")
    contiene(q.leer(constitucion), "Los informes DEBEN salir en PDF.", "la constitución generada")
    contiene(q.leer(constitucion), "principios del kit", "la constitución generada")
    q.commit("chore: instala kit")
    # Las reglas ya son del proyecto: instalar de nuevo no las toca.
    q.agregar(reglas, "\n- Otra regla.\n")
    q.make("install-kit")
    contiene(q.leer(reglas), "Otra regla.", "las reglas del proyecto después de instalar otra vez")


@prueba("los hooks y los scripts de shell quedan ejecutables, en git y en el proyecto")
def permisos(e):
    kit = e.kit()
    listado = correr(["git", "ls-files", "-s"], kit, e.entorno).salida.splitlines()
    modos = {linea.split("\t", 1)[1]: linea.split()[0] for linea in listado}
    deben = [r for r in modos if r.startswith(".githooks/") or r.endswith(".sh")]
    afirmar(len(deben) >= 5, f"se esperaban varios hooks y scripts de shell, hay {len(deben)}")
    malos = [r for r in deben if modos[r] != "100755"]
    afirmar(not malos, f"guardados en git sin permiso de ejecución (git update-index --chmod=+x): {malos}")
    p = e.proyecto(kit, commit=False)
    for rel in (".githooks/pre-commit", ".githooks/commit-msg", "scripts/doctor.sh",
                "equipo/adaptadores/claude/hooks/proteger-archivos.sh"):
        afirmar(os.access(p.archivo(rel), os.X_OK), f"{rel} no es ejecutable en el proyecto")


@prueba("si el kit llega con los hooks sin permiso de ejecución, la instalación lo repara y los hooks corren")
def repara_permisos(e):
    # Pasa cuando alguien agrega un hook desde un clon de Windows: git lo guarda como 100644 y lo ignoraría.
    kit = e.kit()
    hooks = [".githooks/pre-commit", ".githooks/commit-msg"]
    correr(["git", "update-index", "--chmod=-x", *hooks], kit, e.entorno)
    for rel in hooks:
        (kit / rel).chmod(0o644)
    e.commit_kit(kit, "hooks sin permiso de ejecución")
    p = e.proyecto(kit)
    for rel in hooks:
        afirmar(not os.access(p.archivo(f"{SUBMODULO}/{rel}"), os.X_OK), f"la prueba no logró quitarle el permiso a {rel}")
        afirmar(os.access(p.archivo(rel), os.X_OK), f"{rel} quedó sin permiso de ejecución en el proyecto")
    p.escribir("nota.txt", "x\n")
    contiene(p.commit("mensaje malo", espera=1).salida, "Mensaje de commit inválido")


@prueba("instalar por segunda vez no cambia nada")
def instalar_dos_veces(e):
    p = e.proyecto()
    r = p.make("install-kit")
    contiene(r.salida, "Sin cambios: el proyecto ya estaba al día.")
    afirmar(not p.pendientes(), f"la segunda instalación dejó cambios: {p.pendientes()}")


@prueba("proyecto existente: reemplaza con respaldo lo que gestiona el kit y respeta lo demás")
def proyecto_existente(e):
    p = e.proyecto_vacio()
    propios = {
        "Makefile": "build:\n\t@echo mi build\n",
        "AGENTS.md": "mis instrucciones\n",
        ".github/workflows/ci.yml": "name: mi-ci\n",
        ".github/workflows/deploy.yml": "name: deploy\n",
        ".github/CODEOWNERS": "* @yo\n",
        "docker-compose.yml": "services: {}\n",
        "README.md": "# Mi proyecto\n",
        ".gitignore": "node_modules/\n",
        "docs/notas.md": "mi doc\n",
        "src/app.txt": "x\n",
    }
    for rel, texto in propios.items():
        p.escribir(rel, texto)
    p.commit("feat: proyecto existente")
    p.git("submodule", "add", "-q", str(e.kit()), SUBMODULO)
    r = p.instalar_kit()
    contiene(r.salida, "reemplazados (existían antes)")
    contiene(r.salida, "Respaldo de lo reemplazado: .kit-respaldo/")

    # La integración continua es del proyecto: su ci.yml no se toca, y el workflow del kit llega con otro nombre.
    afirmar(p.existe(".github/workflows/bowser.yml"), "no llegó el workflow del kit")
    reemplazados = ("Makefile", "AGENTS.md")
    respaldos = list(p.archivo(".kit-respaldo").iterdir())
    afirmar(len(respaldos) == 1, "debe haber una sola carpeta de respaldo")
    for rel in reemplazados:
        afirmar(p.leer(rel) != propios[rel], f"{rel} lo gestiona el kit y no se reemplazó")
        afirmar((respaldos[0] / rel).read_text(encoding="utf-8") == propios[rel], f"no hay respaldo fiel de {rel}")
    for rel in set(propios) - set(reemplazados) - {".gitignore"}:
        afirmar(p.leer(rel) == propios[rel], f"{rel} es del proyecto y se modificó")
    gitignore = p.leer(".gitignore")
    afirmar(gitignore.startswith("node_modules/\n"), "se perdió el contenido propio del .gitignore")
    contiene(gitignore, "# >>> bowser-spec-kit-ai", "el .gitignore")

    p.verificar_kit()
    p.commit("chore: instala kit")
    afirmar(not any(".kit-respaldo" in l for l in p.git("ls-files").salida.splitlines()),
            "el respaldo entró al commit y debería estar ignorado")
