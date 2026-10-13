"""Nombres en inglés: los comandos de make, sus opciones y las confirmaciones, con los nombres anteriores aceptados."""
import json

from apoyo import afirmar, contiene, prueba

ANTERIORES = {
    "estado": "status", "costos": "costs", "novedades": "news", "modelos": "models", "actualizar-kit": "update-kit",
    "instalar-kit": "install-kit", "verificar-kit": "check-kit", "actualizar-modelos": "update-models",
    "sincronizar": "sync", "verificar-agentes": "check-agents", "instalar-hooks": "install-hooks",
    "generar": "generate", "verificar-generados": "check-generated", "cobertura": "coverage",
}
PERFIL = "equipo/perfil.json"
REGLAS = "equipo/reglas.md"


@prueba("cada comando de make con nombre anterior sigue funcionando, ejecuta el nuevo y avisa de cómo se llama ahora")
def comandos_anteriores(e):
    p = e.proyecto()
    ayuda = p.make("help").salida
    listados = {linea.split()[0] for linea in ayuda.splitlines() if linea.strip()}
    for viejo, nuevo in ANTERIORES.items():
        afirmar(nuevo in listados, f"make help no muestra «{nuevo}»")
        afirmar(viejo not in listados, f"make help sigue mostrando el nombre anterior «{viejo}»")
        # Sin ejecutar: el nombre anterior depende del nuevo y termina con el aviso.
        r = p.make("-n", viejo)
        contiene(r.salida, f"'make {viejo}' ahora se llama 'make {nuevo}'", f"make {viejo}")
        afirmar(r.salida.strip() != p.make("-n", nuevo).salida.strip(), f"make {nuevo} también muestra el aviso")
    # Ejecutados de verdad: dan lo mismo que el nombre nuevo, y el aviso va al final.
    for viejo in ("estado", "novedades", "modelos", "verificar-kit", "sincronizar"):
        r, nuevo = p.make(viejo), p.make(ANTERIORES[viejo])
        aviso = f"Aviso: 'make {viejo}' ahora se llama 'make {ANTERIORES[viejo]}'."
        afirmar(r.salida.startswith(nuevo.salida), f"make {viejo} no dio lo mismo que make {ANTERIORES[viejo]}")
        contiene(r.salida[len(nuevo.salida):], aviso, f"el final de make {viejo}")
        afirmar("Aviso: 'make" not in nuevo.salida, f"make {ANTERIORES[viejo]} avisa de un nombre anterior")


@prueba("las opciones de los comandos se aceptan con el nombre nuevo y con el anterior")
def opciones_anteriores(e):
    p = e.proyecto()
    for orden, nuevas, viejas, espera in (
        ("costs", ("ALL=1", "CLOSE=1", "PRICES=today"), ("TODO=1", "CERRAR=1", "PRECIOS=hoy"), "--todo --cerrar --hoy"),
        ("install-kit", ("FORCE=1",), ("FORZAR=1",), "--forzar"),
        ("news", ("SINCE=1.4.0",), ("DESDE=1.4.0",), "--desde 1.4.0"),
        ("update-models", ("YES=1",), ("SI=1",), "--si"),
        ("profile", ("DETECT=1",), ("DETECTAR=1",), "--detectar"),
    ):
        afirmar(espera not in p.make("-n", orden).salida, f"make {orden} lleva «{espera}» sin pedirlo")
        contiene(p.make("-n", orden, *nuevas).salida, espera, f"make {orden} {' '.join(nuevas)}")
        contiene(p.make("-n", orden, *viejas).salida, espera, f"make {orden} {' '.join(viejas)}")
    # La parte: solo cuenta con perfil.
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir(PERFIL, json.dumps({"partes": [{"nombre": "api", "carpeta": "servidor"}]}) + "\n")
    for opcion in ("PART=api", "PARTE=api"):
        contiene(p.make("-n", "test", opcion).salida, "--parte api", f"make test {opcion}")
    # Y ejecutadas de verdad, una de cada.
    contiene(p.make("news", "DESDE=no-es-version", espera=1).salida, "Versión no válida")
    contiene(p.make("test", "PARTE=nada", espera=1).salida, "No hay ninguna parte llamada «nada»")


@prueba("las confirmaciones del commit se aceptan con el nombre nuevo y con el anterior")
def confirmaciones_anteriores(e):
    p = e.proyecto()
    for n, (nombre, mensaje) in enumerate((("APPROVED_CONSTITUTION", "APPROVED_CONSTITUTION=1 git commit"),
                                           ("APROBADO_CONSTITUCION", "APPROVED_CONSTITUTION=1 git commit"))):
        p.agregar(REGLAS, f"\n- Regla número {n} del proyecto.\n")
        p.make("sync")
        contiene(p.commit("docs: agrega una regla", espera=1).salida, mensaje)
        p.commit("docs: agrega una regla", extra={nombre: "1"})

    p.escribir("servidor/index.php", "<?php\n")
    for n, nombre in enumerate(("APPROVED_PROFILE", "APROBADO_PERFIL")):
        p.escribir(PERFIL, json.dumps({"partes": [{"nombre": "api", "carpeta": "servidor",
                                                   "verbos": {"probar": f"echo {n}"}}]}) + "\n")
        p.make("install-kit")
        contiene(p.commit("chore: perfil", espera=1).salida, "APPROVED_PROFILE=1 git commit")
        p.commit("chore: perfil", extra={nombre: "1"})

    for n, nombre in enumerate(("APPROVED_COSTS", "APROBADO_COSTOS")):
        costos = f"specs/00{n}-algo/costos.json"
        p.escribir(costos, json.dumps({"estado": "cerrado", "total": 1}) + "\n")
        p.commit("chore: costo cerrado")
        p.escribir(costos, json.dumps({"estado": "cerrado", "total": 2}) + "\n")
        contiene(p.commit("chore: cambia el costo", espera=1).salida, "APPROVED_COSTS=1 git commit")
        p.commit("chore: cambia el costo", extra={nombre: "1"})


@prueba("make check-ci reconoce en los workflows los comandos y la opción con el nombre nuevo y con el anterior")
def workflows_anteriores(e):
    p = e.proyecto()
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir(PERFIL, json.dumps({"partes": [{"nombre": "api", "carpeta": "servidor",
                                               "verbos": {"cobertura": "true", "generar": "true"}}]}) + "\n")
    listo = "✓ La integración continua ejecuta los 2 verbos que el perfil define."
    for linea in ("make coverage PART=api && make check-generated PART=api",
                  "make cobertura PARTE=api && make verificar-generados PARTE=api"):
        p.escribir(".github/workflows/ci.yml", f"jobs:\n  ci:\n    steps:\n      - run: {linea}\n")
        contiene(p.make("check-ci").salida, listo, linea)
    # La opción anterior también limita a una parte: una que no existe no cubre nada.
    p.escribir(".github/workflows/ci.yml", "jobs:\n  ci:\n    steps:\n      - run: make cobertura PARTE=otra\n")
    contiene(p.make("check-ci").salida, "(api: cobertura, generar)")


@prueba("si la actualización se detiene, el comando para forzarla es el que entiende el Makefile viejo del proyecto")
def forzar_con_el_makefile_viejo(e):
    e.version_anterior()
    kit = e.kit("anterior")
    p = e.proyecto(kit)
    afirmar("\ninstall-kit:" not in p.leer("Makefile"), "la versión anterior ya traía los nombres en inglés")
    p.agregar("AGENTS.md", "\nLínea agregada a mano en el proyecto.\n")
    e.pasar_kit_a(kit, "actual")
    r = p.make("actualizar-kit", espera=1)
    contiene(r.salida, "make instalar-kit FORZAR=1")
    r = p.make("instalar-kit", "FORZAR=1")
    contiene(r.salida, "Respaldo de lo reemplazado: .kit-respaldo/")
    # Ya con el Makefile nuevo, el mensaje usa los nombres nuevos.
    p.agregar("AGENTS.md", "\nOtra línea agregada a mano.\n")
    contiene(p.make("install-kit", espera=1).salida, "make install-kit FORCE=1")
