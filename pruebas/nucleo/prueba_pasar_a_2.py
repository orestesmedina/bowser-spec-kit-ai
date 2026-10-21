"""make upgrade: lo que le falta a un proyecto para aprovechar la 2.0 del kit, y los arreglos mecánicos."""
import json

from apoyo import afirmar, contiene, prueba

PERFIL = "equipo/perfil.json"
CI = ".github/workflows/ci.yml"
# Lo esencial del ci.yml que instalaba el kit hasta la 1.17, con los nombres anteriores y los comandos retirados.
CI_HEREDADO = """name: CI
jobs:
  agentes:
    name: Kit y configuración de agentes al día
  secretos:
    name: Búsqueda de secretos
  backend:
    steps:
      - run: make cobertura PARTE=backend
      - run: make test-backend
      - run: make db-migrate
      - run: python3 scripts/cobertura.py coverage.out
"""
PROYECTO_MK = "propio: ## Un comando del proyecto\n\t$(MAKE) verificar-generados FORZAR=1\n\t@echo APROBADO_PERFIL\n"


def escribir_json(p, rel: str, datos: dict) -> None:
    p.escribir(rel, json.dumps(datos, ensure_ascii=False, indent=2) + "\n")


@prueba("make upgrade: junta lo pendiente según quién lo resuelve, muestra los arreglos mecánicos y no cambia nada sin confirmar")
def pendientes(e):
    p = e.proyecto()
    # El proyecto se quedó con su propia versión de un script del kit: no es un script heredado.
    config = json.loads(p.leer("equipo/config.json"))
    config["kit"]["excluir"] = [".specify/memory/constitution.md", "scripts/doctor.sh"]
    escribir_json(p, "equipo/config.json", config)
    p.agregar("scripts/doctor.sh", "\n# versión propia del proyecto\n")
    p.escribir("servidor/index.php", "<?php\n")
    escribir_json(p, PERFIL, {"partes": [{"nombre": "backend", "carpeta": "servidor", "rol": "dev-backend",
                                          "verbos": {"cobertura": "python3 ../scripts/cobertura.py"}}]})
    p.make("install-kit")
    # Lo que dejó una actualización desde la 1.x: un script que el kit retiró, el ci.yml que instalaba, reglas heredadas.
    p.escribir("scripts/cobertura.py", "print('cobertura medida')\n")
    p.escribir(CI, CI_HEREDADO)
    p.escribir("proyecto.mk", PROYECTO_MK)
    # Otro archivo que nombra el script fuera de una llamada (en simiente-santa-webside, un comentario del OpenAPI).
    OPENAPI = "servidor/openapi.yaml"
    p.escribir(OPENAPI, "openapi: 3.1.0\n# Lo une scripts/cobertura.py; no confundir con otros_scripts/cobertura.py\n")
    p.escribir("equipo/reglas.md", "# Constitución: reglas del proyecto\n\nEstas reglas venían en la constitución que el "
                                   "kit instalaba antes (versión 1.0.0).\n\n- El backend DEBE estar en Go.\n")
    p.agregar(".gitignore", "\n# Estas líneas venían en el bloque del kit; desde ahora son del proyecto: edítalas o bórralas.\n"
                            "frontend/node_modules/\n")
    p.make("sync")
    afirmar("pendientes para aprovechar el kit: make upgrade" in p.make("install-kit").salida,
            "make install-kit no avisa de los pendientes")

    antes = {rel: p.leer(rel) for rel in (PERFIL, CI, "proyecto.mk", "scripts/cobertura.py", OPENAPI)}
    s = p.make("upgrade").salida
    for texto in ("Lo resuelve un agente", "El perfil no declara `requisitos`",
                  "ci.yml es el que instalaba el kit: repite lo que ya hace bowser.yml",
                  "Lo resuelve una persona", "equipo/reglas.md todavía tiene las reglas",
                  ".gitignore tiene, debajo del bloque del kit, reglas",
                  "`kit.excluir` nombra .specify/memory/constitution.md, que ya no es del kit",
                  "Recomendado: la parte backend no tiene convenciones propias",
                  "ci.yml usa `make db-migrate`, que se retiró en la 1.23.0",
                  "scripts/cobertura.py → tools/cobertura.py",
                  f"{OPENAPI} (línea 2) nombra scripts/cobertura.py, que pasa a tools/cobertura.py: corrígelo a mano",
                  "+      - run: make coverage PART=backend", "+      - run: make test PART=backend",
                  "+      - run: python3 tools/cobertura.py coverage.out",
                  "+\t$(MAKE) check-generated FORCE=1", "+\t@echo APPROVED_PROFILE",
                  '+        "cobertura": "python3 ../tools/cobertura.py"',
                  "Para aplicarlos: make upgrade YES=1"):
        contiene(s, texto, "la salida de make upgrade")
    afirmar("scripts/doctor.sh →" not in s, "propone mover un script que el proyecto excluyó a propósito")
    afirmar("db-migrate\n+" not in s and "+      - run: make db-migrate" not in s, "cambió un comando retirado sin reemplazo")
    for rel, texto in antes.items():
        afirmar(p.existe(rel) and p.leer(rel) == texto, f"make upgrade cambió {rel} sin confirmación")

    r = p.make("upgrade", "YES=1")
    contiene(r.salida, "Arreglos aplicados.")
    contiene(r.salida, "Cambió el perfil: el commit pide confirmarlo con APPROVED_PROFILE=1.")
    afirmar(p.existe("tools/cobertura.py") and not p.existe("scripts/cobertura.py"), "el script no pasó a tools/")
    afirmar(p.existe("scripts/doctor.sh"), "se movió un script que el proyecto excluyó a propósito")
    contiene(p.leer(PERFIL), '"cobertura": "python3 ../tools/cobertura.py"', "el perfil")
    ci = p.leer(CI)
    for texto in ("make coverage PART=backend", "make test PART=backend", "make db-migrate", "python3 tools/cobertura.py"):
        contiene(ci, texto, "el ci.yml")
    contiene(p.leer("proyecto.mk"), "$(MAKE) check-generated FORCE=1\n\t@echo APPROVED_PROFILE", "proyecto.mk")
    afirmar(p.leer(OPENAPI) == antes[OPENAPI], "make upgrade corrigió una mención que solo debía avisar")
    contiene(p.make("coverage").salida, "cobertura medida", "el verbo con el script ya en tools/")
    p.verificar_kit()
    p.correr("python3", "scripts/sincronizar.py", "--verificar")

    # Lo mecánico ya está; lo demás sigue pendiente hasta que lo resuelva quien corresponde.
    s = p.make("upgrade").salida
    afirmar("Arreglos mecánicos" not in s, f"quedaron arreglos mecánicos después de aplicarlos:\n{s}")
    contiene(s, "equipo/reglas.md todavía tiene las reglas")
    afirmar("nombra scripts/cobertura.py" not in s, "el aviso de la mención sigue después de mover el script")


@prueba("make upgrade: un proyecto sin pendientes lo dice, y make install-kit no avisa de nada")
def sin_pendientes(e):
    p = e.proyecto()
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir(".agents/skills/convenciones-de-api/SKILL.md",
               "---\nname: convenciones-de-api\ndescription: Convenciones de la API. Usar al tocar la API.\n---\n# API\n")
    escribir_json(p, PERFIL, {"partes": [{"nombre": "api", "carpeta": "servidor", "rol": "dev-backend",
                                          "skills": ["convenciones-de-api"], "verbos": {"probar": "true"}}],
                              "requisitos": ["git"]})
    p.escribir(CI, "name: CI\njobs:\n  api:\n    steps:\n      - run: make ci PART=api\n")
    r = p.make("install-kit")
    afirmar("make upgrade" not in r.salida, f"make install-kit avisa de pendientes que no hay:\n{r.salida}")
    contiene(p.make("upgrade").salida, "✓ Nada pendiente")


@prueba("make upgrade sin perfil: lo primero que pide es crearlo")
def sin_perfil(e):
    p = e.proyecto()
    contiene(p.make("upgrade").salida, "El proyecto no tiene perfil")
    contiene(p.make("upgrade").salida, "/bowser-profile")
