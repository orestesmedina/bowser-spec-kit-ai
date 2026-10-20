"""Actualizar un proyecto: desde la versión anterior publicada, con cambios locales y con archivos retirados."""
import json

from apoyo import SUBMODULO, Omitida, afirmar, contiene, prueba


@prueba("actualización desde la versión anterior, con el Makefile viejo del proyecto")
def desde_la_anterior(e):
    anterior = e.version_anterior()
    kit = e.kit("anterior")
    p = e.proyecto(kit)
    version_vieja = json.loads(p.leer(".kit-manifest.json"))["version"]
    afirmar(version_vieja != e.version, f"la versión anterior ({anterior}) es la misma que se prueba")
    p.escribir("proyecto.mk", "e2e: ## Pruebas end-to-end del proyecto\n\t@echo e2e-del-proyecto\n")
    config_antes = p.leer("equipo/config.json")
    ci_antes = p.leer(".github/workflows/ci.yml") if p.existe(".github/workflows/ci.yml") else None
    constitucion_entera = not p.existe("equipo/principios.md")   # la anterior traía la constitución en un solo archivo
    # La versión anterior traía reglas de Go y Node en su bloque de .gitignore. Una de ellas, además, ya era del proyecto.
    contiene(p.leer(".gitignore"), "frontend/node_modules/", "el bloque del kit anterior")
    p.escribir(".gitignore", "frontend/dist/\n\n" + p.leer(".gitignore") + "\n# Del proyecto\n*.log\n")
    p.commit("chore: comando propio")

    e.pasar_kit_a(kit, "actual")
    r = p.make("actualizar-kit")     # make ya leyó el Makefile viejo: el nuevo queda instalado al terminar
    contiene(r.salida, f"Kit {e.version}")
    contiene(r.salida, f"Novedades del kit de {version_vieja} a {e.version}")
    contiene(r.salida, f"[{e.version}]")

    afirmar(json.loads(p.leer(".kit-manifest.json"))["version"] == e.version, "el manifiesto no quedó en la versión nueva")
    p.verificar_kit()
    p.correr("python3", "scripts/sincronizar.py", "--verificar")
    afirmar(p.leer("equipo/config.json") == config_antes, "la actualización tocó equipo/config.json, que es del proyecto")
    contiene(p.make("e2e").salida, "e2e-del-proyecto")
    contiene(p.make("help").salida, "e2e")

    # Las reglas que el bloque ya no trae no se pierden: quedan debajo, como del proyecto, y sin repetir las que ya tenía.
    contiene(r.salida, "Se conservaron debajo del bloque: ahora son del proyecto.")
    gitignore = p.leer(".gitignore")
    antes, resto = gitignore.split("# >>> bowser-spec-kit-ai", 1)
    bloque, despues = resto.split("# <<< bowser-spec-kit-ai", 1)
    afirmar("node_modules" not in bloque and "backend" not in bloque, "el bloque del kit sigue trayendo tecnología")
    for regla in ("frontend/node_modules/", "backend/bin/", "*.test"):
        contiene(despues, f"\n{regla}\n", "lo que quedó debajo del bloque del kit")
    afirmar(gitignore.count("frontend/dist/") == 1, "repitió una regla que el proyecto ya tenía fuera del bloque")
    afirmar(gitignore.count("\n.env\n") == 1, "pasó al proyecto una regla que el bloque sigue trayendo")
    afirmar(antes == "frontend/dist/\n\n" and despues.endswith("\n# Del proyecto\n*.log\n"),
            "la actualización cambió lo que el proyecto tenía escrito en su .gitignore")
    # La integración continua que el kit traía pasa a ser del proyecto: no se borra, y deja de estar en el manifiesto.
    if ci_antes is not None:
        contiene(r.salida, ".github/workflows/ci.yml ya no viene del kit")
        afirmar(p.leer(".github/workflows/ci.yml") == ci_antes, "la actualización borró o cambió el ci.yml del proyecto")
    manifiesto = json.loads(p.leer(".kit-manifest.json"))["archivos"]
    afirmar(".github/workflows/ci.yml" not in manifiesto, "ci.yml sigue figurando como archivo del kit")
    afirmar(".github/workflows/bowser.yml" in manifiesto, "el workflow del kit (bowser.yml) no llegó al actualizar")
    # La constitución se parte en dos: los principios llegan del kit y las reglas de tecnología que traía quedan en el proyecto.
    if constitucion_entera:
        contiene(r.salida, "Las reglas de tecnología que traía quedaron en equipo/reglas.md")
        generada = p.leer(".specify/memory/constitution.md")
        afirmar(generada.startswith("<!-- GENERADO"), "la constitución del proyecto no se regeneró al actualizar")
        for texto in ("principios del kit", "salvo que las reglas del proyecto digan otro alcance", "`handler → service → repository`",
                      "cobertura mínima DEBE ser 80%", "`pgx` / `sqlc`", "`docker compose up`"):
            contiene(generada, texto, "la constitución generada después de actualizar")
        contiene(p.leer("equipo/reglas.md"), "cobertura mínima DEBE ser 80%", "las reglas que quedaron en el proyecto")
    afirmar(".specify/memory/constitution.md" not in manifiesto and "equipo/reglas.md" not in manifiesto,
            "la constitución generada o las reglas del proyecto figuran como archivos del kit")
    afirmar("equipo/principios.md" in manifiesto, "los principios no llegaron al actualizar")
    # El hook que formateaba al editar se retira, y la configuración de Claude Code deja de llamarlo.
    afirmar(not p.existe("equipo/adaptadores/claude/hooks/formatear.sh"), "el hook de formateo no se retiró al actualizar")
    afirmar("formatear.sh" not in p.leer(".claude/settings.json"), ".claude/settings.json sigue llamando al hook de formateo")
    p.escribir("frontend/node_modules/x/index.js", "x\n")
    afirmar(all("node_modules" not in l for l in p.pendientes()),
            "git empezó a ver frontend/node_modules/ después de actualizar")
    p.commit(f"chore: actualiza kit a {e.version}")
    afirmar(not p.pendientes(), f"quedaron archivos sin commit después de actualizar: {p.pendientes()}")
    contiene(p.make("install-kit").salida, "Sin cambios: el proyecto ya estaba al día.")


@prueba("al partir la constitución, la que un proyecto había hecho suya queda completa en sus reglas")
def constitucion_propia(e):
    constitucion, reglas = ".specify/memory/constitution.md", "equipo/reglas.md"
    e.version_anterior()
    kit = e.kit("anterior")
    p = e.proyecto(kit)
    if p.existe("equipo/principios.md"):
        raise Omitida("la versión anterior ya traía la constitución en dos partes")
    config = json.loads(p.leer("equipo/config.json"))
    config.setdefault("kit", {})["excluir"] = [constitucion]
    p.escribir("equipo/config.json", json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    p.agregar(constitucion, "\n- Regla propia: los informes DEBEN salir en PDF.\n")
    p.make("instalar-kit")
    p.commit("docs: constitución propia del proyecto", extra={"APROBADO_CONSTITUCION": "1"})

    e.pasar_kit_a(kit, "actual")
    contiene(p.make("actualizar-kit").salida, f"quedó completa en {reglas}")
    for texto in ("Regla propia: los informes DEBEN salir en PDF.", "`handler → service → repository`"):
        contiene(p.leer(reglas), texto, "las reglas del proyecto")
        contiene(p.leer(constitucion), texto, "la constitución generada")
    contiene(p.leer(constitucion), "principios del kit", "la constitución generada")
    p.verificar_kit()
    p.commit(f"chore: actualiza kit a {e.version}")
    antes = p.leer(reglas)
    contiene(p.make("install-kit").salida, "Sin cambios: el proyecto ya estaba al día.")
    afirmar(p.leer(reglas) == antes, "instalar otra vez cambió las reglas del proyecto")


@prueba("un archivo del kit editado en el proyecto detiene la actualización y ofrece las tres salidas")
def cambio_local(e):
    kit = e.kit()
    p = e.proyecto(kit)
    p.agregar("equipo/orquestador.md", "\nRegla agregada a mano en el proyecto.\n")
    contiene(p.verificar_kit(espera=1).salida, "equipo/orquestador.md")
    p.git("add", "-A")
    r = p.git("commit", "-m", "docs: cambia el orquestador", espera=1)
    contiene(r.salida, "Los archivos del kit no coinciden")

    r = p.make("install-kit", espera=1)
    contiene(r.salida, "fueron modificados en este proyecto")
    contiene(r.salida, "equipo/orquestador.md")
    contiene(r.salida, "kit.excluir")
    contiene(r.salida, "FORCE=1")
    contiene(p.leer("equipo/orquestador.md"), "Regla agregada a mano", "el archivo editado")

    r = p.make("install-kit", "FORCE=1")
    contiene(r.salida, "Respaldo de lo reemplazado: .kit-respaldo/")
    afirmar("Regla agregada a mano" not in p.leer("equipo/orquestador.md"), "FORCE=1 no restauró el archivo del kit")
    respaldo = next(p.archivo(".kit-respaldo").iterdir()) / "equipo/orquestador.md"
    contiene(respaldo.read_text(encoding="utf-8"), "Regla agregada a mano", "el respaldo")
    p.verificar_kit()


@prueba("kit.excluir: el proyecto se queda con su versión de un archivo y las actualizaciones no lo pisan")
def excluir(e):
    kit = e.kit()
    p = e.proyecto(kit)
    config = json.loads(p.leer("equipo/config.json"))
    config.setdefault("kit", {})["excluir"] = ["equipo/orquestador.md"]
    p.escribir("equipo/config.json", json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    p.agregar("equipo/orquestador.md", "\nRegla propia de este proyecto.\n")
    p.make("install-kit")
    p.verificar_kit()
    p.commit("chore: orquestador propio del proyecto")

    (kit / "equipo/orquestador.md").write_text("# Orquestador nuevo del kit\n", encoding="utf-8")
    (kit / "AGENTS.md").write_text((kit / "AGENTS.md").read_text(encoding="utf-8") + "\nLínea nueva del kit.\n", encoding="utf-8")
    e.commit_kit(kit, "cambia orquestador y AGENTS")
    p.make("update-kit")
    contiene(p.leer("equipo/orquestador.md"), "Regla propia de este proyecto.", "el archivo excluido")
    contiene(p.leer("AGENTS.md"), "Línea nueva del kit.", "un archivo no excluido")
    p.commit("chore: actualiza kit")


@prueba("un archivo que el kit retira se borra del proyecto; si tenía cambios locales, se conserva y se avisa")
def retirados(e):
    kit = e.kit()
    for nombre in ("retirado-limpio.md", "retirado-editado.md"):
        (kit / "docs/plantillas" / nombre).write_text("plantilla\n", encoding="utf-8")
    e.commit_kit(kit, "dos plantillas más")
    p = e.proyecto(kit)
    afirmar(p.existe("docs/plantillas/retirado-limpio.md"), "la plantilla nueva no se instaló")
    for nombre in ("retirado-limpio.md", "retirado-editado.md"):
        (kit / "docs/plantillas" / nombre).unlink()
    e.commit_kit(kit, "retira las plantillas")
    p.agregar("docs/plantillas/retirado-editado.md", "cambio local\n")

    r = p.make("update-kit")
    afirmar(not p.existe("docs/plantillas/retirado-limpio.md"), "el archivo retirado sigue en el proyecto")
    afirmar(p.existe("docs/plantillas/retirado-editado.md"), "se borró un archivo retirado que tenía cambios locales")
    contiene(r.salida, "tienen cambios locales; se conservaron")
    afirmar(p.existe("docs/plantillas/estado.md"), "se borró una plantilla que el kit no retiró")


@prueba("make news muestra el historial y los pasos manuales de la versión instalada")
def novedades(e):
    p = e.proyecto()
    r = p.make("news")
    contiene(r.salida, f"Kit instalado: {e.version}")
    contiene(r.salida, f"[{e.version}]")
    contiene(p.make("news", "SINCE=no-es-version", espera=1).salida, "Versión no válida")


@prueba("desde una versión anterior a la 1.23.0, los pasos manuales de la 1.x se resumen en la guía de migración")
def pasos_de_la_1x(e):
    p = e.proyecto()
    # Desde la 1.6.4 (la de un proyecto real): un solo aviso en lugar de los pasos de cada versión intermedia.
    r = p.make("news", "SINCE=1.6.4")
    contiene(r.salida, "Vienes de la 1.6.4, anterior a la 2.0.")
    contiene(r.salida, "docs/migrar-a-2.md")
    afirmar("Instala sqlc en local" not in r.salida, "muestra un paso de la 1.7.0 que la 2.0 dejó sin efecto")
    afirmar("Tu proyecto sigue funcionando igual sin perfil" not in r.salida, "muestra un paso de la 1.12.0 que ya es falso")
    contiene(r.salida, "=== Novedades del kit de 1.6.4", "las novedades se siguen mostrando")
    # Desde la 1.23.0 en adelante, los pasos se muestran uno por uno, como siempre.
    r = p.make("news", "SINCE=1.23.0")
    afirmar("Vienes de la" not in r.salida, "resume los pasos de un proyecto que ya pasó el cambio que rompe")
    contiene(r.salida, "Ejecuta `make upgrade`", "el paso manual de la 1.24.0")


@prueba("un archivo que el kit entrega al proyecto (ci.yml) no se borra al actualizar, aunque tenga cambios locales")
def entregados(e):
    p = e.proyecto()
    ci = ".github/workflows/ci.yml"
    afirmar(not p.existe(ci), "el kit sigue instalando un ci.yml: la integración continua es del proyecto")
    # Como lo dejó una versión anterior: el archivo en el proyecto y su hash en el manifiesto.
    p.escribir(ci, "name: CI\n# con un paso que agregó el proyecto\n")
    manifiesto = json.loads(p.leer(".kit-manifest.json"))
    manifiesto["archivos"][ci] = "0" * 64
    p.escribir(".kit-manifest.json", json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n")
    contiene(p.verificar_kit(espera=1).salida, ci)

    r = p.make("install-kit")
    contiene(r.salida, f"{ci} ya no viene del kit: se conservó tal como estaba y desde ahora es del proyecto.")
    contiene(p.leer(ci), "un paso que agregó el proyecto", "el ci.yml del proyecto")
    afirmar(ci not in json.loads(p.leer(".kit-manifest.json"))["archivos"], "ci.yml sigue en el manifiesto")
    p.verificar_kit()
    # Ya es un archivo cualquiera del proyecto: se edita y entra al historial sin que el kit se queje.
    p.agregar(ci, "# otro cambio\n")
    p.commit("ci: integración continua del proyecto")
    contiene(p.make("install-kit").salida, "Sin cambios: el proyecto ya estaba al día.")


@prueba("un archivo que el kit retira y el proyecto todavía nombra (perfil, proyecto.mk o un workflow) se le entrega en vez de borrarlo")
def retirados_en_uso(e):
    kit = e.kit()
    nombres = ("en-el-perfil.sh", "en-proyecto-mk.sh", "en-workflow.sh", "sin-uso.sh")
    for nombre in nombres:
        (kit / "scripts" / nombre).write_text("echo hola\n", encoding="utf-8")
    e.commit_kit(kit, "cuatro scripts más")
    p = e.proyecto(kit)
    p.escribir("servidor/index.php", "<?php\n")
    perfil = {"partes": [{"nombre": "api", "carpeta": "servidor", "verbos": {"cobertura": "bash ../scripts/en-el-perfil.sh"}}]}
    p.escribir("equipo/perfil.json", json.dumps(perfil, ensure_ascii=False, indent=2) + "\n")
    p.escribir("proyecto.mk", "propio:\n\tbash scripts/en-proyecto-mk.sh\n")
    p.escribir(".github/workflows/ci.yml", "jobs:\n  pruebas:\n    steps:\n      - run: bash scripts/en-workflow.sh\n")
    p.make("install-kit")
    p.commit("chore: perfil y comandos propios", extra={"APPROVED_PROFILE": "1"})
    for nombre in nombres:
        (kit / "scripts" / nombre).unlink()
    e.commit_kit(kit, "retira los scripts")

    r = p.make("update-kit")
    for nombre, quien in (("en-el-perfil.sh", "equipo/perfil.json"), ("en-proyecto-mk.sh", "proyecto.mk"),
                          ("en-workflow.sh", ".github/workflows/ci.yml")):
        afirmar(p.existe(f"scripts/{nombre}"), f"se borró scripts/{nombre}, que {quien} todavía usa")
        contiene(r.salida, f"scripts/{nombre} ya no viene del kit, pero {quien} lo usa")
    afirmar(not p.existe("scripts/sin-uso.sh"), "un archivo retirado que nadie usa sigue en el proyecto")
    manifiesto = json.loads(p.leer(".kit-manifest.json"))["archivos"]
    afirmar(not [n for n in nombres if f"scripts/{n}" in manifiesto], "un script retirado sigue en el manifiesto")
    p.verificar_kit()
    contiene(p.make("coverage").salida, "hola", "el verbo que usa el script entregado")


@prueba("los scripts retirados que usa el ci.yml que instalaba el kit se entregan: el ci.yml pasa a ser del proyecto en la misma actualización")
def retirados_en_el_ci_heredado(e):
    e.version_anterior()
    kit = e.kit("anterior")
    p = e.proyecto(kit)
    ci = ".github/workflows/ci.yml"
    if ci not in json.loads(p.leer(".kit-manifest.json"))["archivos"]:
        raise Omitida("la versión anterior ya no gestionaba el ci.yml")
    usados = [s for s in ("scripts/generar.sh", "scripts/cobertura.py") if s in p.leer(ci)]
    if not usados:
        raise Omitida("el ci.yml de la versión anterior no usa scripts que el kit retire")
    # Con perfil, para que la actualización no se detenga (el proyecto tiene backend/).
    p.escribir("backend/main.go", "package main\n")
    perfil = {"partes": [{"nombre": "backend", "carpeta": "backend", "verbos": {"probar": "true"}}]}
    p.escribir("equipo/perfil.json", json.dumps(perfil, ensure_ascii=False, indent=2) + "\n")
    p.commit("chore: perfil", extra={"APROBADO_PERFIL": "1"})
    e.pasar_kit_a(kit, "actual")

    r = p.make("actualizar-kit")
    for script in usados:
        afirmar(p.existe(script), f"se borró {script}, que el ci.yml heredado todavía usa")
        contiene(r.salida, f"{script} ya no viene del kit, pero {ci} lo usa")
    p.verificar_kit()


def con_backend_desde_la_anterior(e):
    """Un proyecto instalado con la versión anterior publicada, sin perfil y con la estructura que esta suponía."""
    e.version_anterior()
    kit = e.kit("anterior")
    p = e.proyecto(kit)
    p.escribir("backend/main.go", "package main\n")
    p.commit("feat: primer código del backend")
    e.pasar_kit_a(kit, "actual")
    return p


@prueba("un proyecto que viene de la 1.x sin perfil y con backend/ o frontend/ no se actualiza hasta crear el perfil")
def sin_perfil_desde_la_anterior(e):
    p = con_backend_desde_la_anterior(e)
    antes = p.leer(".kit-manifest.json")
    r = p.make("actualizar-kit", espera=1)
    contiene(r.salida, "Este proyecto no tiene perfil (equipo/perfil.json)")
    contiene(r.salida, "aquí hay backend/")
    contiene(r.salida, "No se cambió nada en el proyecto.")
    # Nombra los comandos que entiende el Makefile que el proyecto tiene todavía.
    contiene(r.salida, "Sin hacer commit todavía, repite: make instalar-kit\n")
    contiene(r.salida, "make instalar-kit FORZAR=1")
    afirmar(p.leer(".kit-manifest.json") == antes, "la actualización detenida cambió el manifiesto")
    afirmar(p.existe(".agents/skills/go-backend/SKILL.md"), "la actualización detenida retiró una skill")

    # Con el perfil escrito (todavía sin commit: el submódulo ya cambió y el control del commit no lo dejaría pasar),
    # la actualización sigue, y después todo entra en un solo commit.
    perfil = {"partes": [{"nombre": "backend", "carpeta": "backend", "rol": "dev-backend"}]}
    p.escribir("equipo/perfil.json", json.dumps(perfil, ensure_ascii=False, indent=2) + "\n")
    p.make("instalar-kit")
    p.verificar_kit()
    p.commit("chore: actualiza el kit y crea el perfil", extra={"APPROVED_PROFILE": "1"})
    contiene(p.leer(".claude/agents/dev-backend.md"), "- **backend**, en `backend`", "el rol dev-backend")


@prueba("si la versión instalada no tiene /bowser-profile, la parada sin perfil no lo recomienda: solo ofrece forzar")
def sin_perfil_antes_del_comando(e):
    p = con_backend_desde_la_anterior(e)
    # Simula un proyecto instalado con una versión anterior a la 1.12.0, como el 1.6.4 de un proyecto real.
    manifiesto = json.loads(p.leer(".kit-manifest.json"))
    manifiesto["version"] = "1.6.4"
    p.escribir(".kit-manifest.json", json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n")
    r = p.make("actualizar-kit", espera=1)
    contiene(r.salida, "Tu versión (1.6.4) no tiene /bowser-profile")
    contiene(r.salida, "make instalar-kit FORZAR=1")
    contiene(r.salida, "docs/migrar-a-2.md")
    afirmar("Recomendado" not in r.salida, "recomienda /bowser-profile a una versión que no lo tiene")


@prueba("forzando, un proyecto de la 1.x sin perfil se actualiza y se le avisa de lo que deja de funcionar")
def sin_perfil_forzando(e):
    p = con_backend_desde_la_anterior(e)
    r = p.make("actualizar-kit", "FORZAR=1")
    contiene(r.salida, "Este proyecto no tiene perfil: make test, make lint, make ci y los demás verbos no funcionan")
    p.verificar_kit()
    afirmar(not p.existe(".agents/skills/go-backend"), "sin perfil no debe quedar ninguna skill de tecnología")
    # Ya instalada la versión nueva, una actualización posterior sin perfil no se detiene.
    contiene(p.make("install-kit").salida, "instalado")
