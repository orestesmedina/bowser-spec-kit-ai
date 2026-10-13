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
    contiene(p.make("instalar-kit").salida, "Sin cambios: el proyecto ya estaba al día.")


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
    contiene(p.make("instalar-kit").salida, "Sin cambios: el proyecto ya estaba al día.")
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

    r = p.make("instalar-kit", espera=1)
    contiene(r.salida, "fueron modificados en este proyecto")
    contiene(r.salida, "equipo/orquestador.md")
    contiene(r.salida, "kit.excluir")
    contiene(r.salida, "FORZAR=1")
    contiene(p.leer("equipo/orquestador.md"), "Regla agregada a mano", "el archivo editado")

    r = p.make("instalar-kit", "FORZAR=1")
    contiene(r.salida, "Respaldo de lo reemplazado: .kit-respaldo/")
    afirmar("Regla agregada a mano" not in p.leer("equipo/orquestador.md"), "FORZAR=1 no restauró el archivo del kit")
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
    p.make("instalar-kit")
    p.verificar_kit()
    p.commit("chore: orquestador propio del proyecto")

    (kit / "equipo/orquestador.md").write_text("# Orquestador nuevo del kit\n", encoding="utf-8")
    (kit / "AGENTS.md").write_text((kit / "AGENTS.md").read_text(encoding="utf-8") + "\nLínea nueva del kit.\n", encoding="utf-8")
    e.commit_kit(kit, "cambia orquestador y AGENTS")
    p.make("actualizar-kit")
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

    r = p.make("actualizar-kit")
    afirmar(not p.existe("docs/plantillas/retirado-limpio.md"), "el archivo retirado sigue en el proyecto")
    afirmar(p.existe("docs/plantillas/retirado-editado.md"), "se borró un archivo retirado que tenía cambios locales")
    contiene(r.salida, "tienen cambios locales; se conservaron")
    afirmar(p.existe("docs/plantillas/estado.md"), "se borró una plantilla que el kit no retiró")


@prueba("make novedades muestra el historial y los pasos manuales de la versión instalada")
def novedades(e):
    p = e.proyecto()
    r = p.make("novedades")
    contiene(r.salida, f"Kit instalado: {e.version}")
    contiene(r.salida, f"[{e.version}]")
    contiene(p.make("novedades", "DESDE=no-es-version", espera=1).salida, "Versión no válida")


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

    r = p.make("instalar-kit")
    contiene(r.salida, f"{ci} ya no viene del kit: se conservó tal como estaba y desde ahora es del proyecto.")
    contiene(p.leer(ci), "un paso que agregó el proyecto", "el ci.yml del proyecto")
    afirmar(ci not in json.loads(p.leer(".kit-manifest.json"))["archivos"], "ci.yml sigue en el manifiesto")
    p.verificar_kit()
    # Ya es un archivo cualquiera del proyecto: se edita y entra al historial sin que el kit se queje.
    p.agregar(ci, "# otro cambio\n")
    p.commit("ci: integración continua del proyecto")
    contiene(p.make("instalar-kit").salida, "Sin cambios: el proyecto ya estaba al día.")
