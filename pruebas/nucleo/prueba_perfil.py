"""Perfil del proyecto y verbos: equipo/perfil.json declara las partes y el comando de cada verbo."""
import json

from apoyo import afirmar, contiene, prueba

PERFIL = "equipo/perfil.json"
APROBADO = {"APROBADO_PERFIL": "1"}


def base() -> dict:
    return {"partes": [
        {"nombre": "api", "carpeta": "servidor", "rol": "dev-backend", "terceros": ["ajeno"],
         "inmutables": ["cambios/*.sql"], "verbos": {"probar": "pwd", "cobertura": None}},
        {"nombre": "panel", "carpeta": "web/panel"},
    ]}


def escribir_perfil(p, perfil) -> None:
    texto = perfil if isinstance(perfil, str) else json.dumps(perfil, ensure_ascii=False, indent=2) + "\n"
    p.escribir(PERFIL, texto)


def con_perfil(e, perfil: dict | None = None):
    """Proyecto con el kit instalado y un perfil ya aprobado."""
    p = e.proyecto()
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir("web/panel/index.html", "<html></html>\n")
    escribir_perfil(p, perfil or base())
    p.commit("chore: perfil del proyecto", extra=APROBADO)
    return p


@prueba("sin perfil los comandos son los de siempre; con perfil, make ejecuta los verbos de cada parte en su carpeta")
def verbos_del_perfil(e):
    p = e.proyecto()
    contiene(p.make("-n", "test").salida, "go test", "make test sin perfil")
    contiene(p.make("-n", "lint").salida, "golangci-lint", "make lint sin perfil")
    contiene(p.make("profile").salida, "no tiene perfil")
    p.correr("python3", "scripts/verbos.py", "probar", espera=1)

    p = con_perfil(e)
    afirmar("go test" not in p.make("-n", "test").salida, "con perfil, make test sigue llamando a go test")
    r = p.make("test")
    contiene(r.salida, "▶ probar · api (servidor): pwd")
    contiene(r.salida, f"{p.ruta}/servidor\n", "la carpeta donde corrió el verbo")
    contiene(r.salida, "La parte «panel» no define el verbo «probar»: se omite.")

    # Un verbo que nadie define avisa y no falla: el proyecto todavía no lo tiene.
    contiene(p.make("security").salida, "Ninguna parte define «auditar»")
    contiene(p.make("cobertura").salida, "Ninguna parte define «cobertura»")
    contiene(p.make("test", "PARTE=panel").salida, "Ninguna parte define «probar»")
    contiene(p.make("test", "PARTE=nada", espera=1).salida, "No hay ninguna parte llamada «nada»")

    contiene(p.make("profile").salida, "OK: perfil válido (2 partes).")
    contiene(p.make("profile").salida, "cobertura  — sin definir")

    # Un comando que falla hace fallar a make, y los demás verbos y partes se ejecutan igual.
    perfil = base()
    perfil["partes"][0]["verbos"].update({"formato": "echo formato-api", "revisar": "exit 3"})
    perfil["partes"][1]["verbos"] = {"revisar": "echo revisar-panel"}
    escribir_perfil(p, perfil)
    r = p.make("lint", espera=1)
    contiene(r.salida, "formato-api")
    contiene(r.salida, "revisar falló en la parte «api» (código 3)")
    contiene(r.salida, "revisar-panel")

    # El perfil es del proyecto: instalar el kit otra vez no lo toca.
    p.commit("chore: verbos de revisión", extra=APROBADO)
    p.make("instalar-kit")
    p.verificar_kit()
    afirmar(json.loads(p.leer(PERFIL)) == perfil, "instalar el kit cambió el perfil del proyecto")
    afirmar(PERFIL not in json.loads(p.leer(".kit-manifest.json"))["archivos"], "el perfil quedó registrado como archivo del kit")


@prueba("un perfil mal escrito se rechaza con un mensaje que dice qué corregir, y no se ejecuta nada")
def perfil_invalido(e):
    p = con_perfil(e)

    def cambiar(**campos) -> dict:
        perfil = base()
        perfil["partes"][0].update(campos)
        return perfil

    repetido = base()
    repetido["partes"][1]["nombre"] = "api"
    misma = base()
    misma["partes"][1]["carpeta"] = "servidor/"
    malos = [
        ("{ esto no es json", "no es un JSON válido"),
        ({"partes": []}, "debe ser una lista con al menos una parte"),
        (cambiar(carpeta="no-existe"), "la carpeta «no-existe» no existe"),
        (cambiar(carpeta="../afuera"), "debe ser una ruta relativa dentro del proyecto"),
        (cambiar(nombre="Api Rest"), "solo admite minúsculas, números y guiones"),
        (repetido, "hay dos partes con el nombre «api»"),
        (misma, "ya pertenece a otra parte"),
        (cambiar(rol="dev-inventado"), "el rol «dev-inventado» no existe"),
        (cambiar(verbos={"compilar": "make"}), "verbo desconocido «compilar»"),
        (cambiar(verbos={"probar": ""}), "debe ser un comando (texto) o null"),
        (cambiar(comandos={}), "campo desconocido «comandos»"),
        (cambiar(inmutables="cambios/*.sql"), "\"inmutables\" debe ser una lista"),
    ]
    for perfil, mensaje in malos:
        escribir_perfil(p, perfil)
        contiene(p.make("profile", espera=1).salida, mensaje)
        r = p.make("test", espera=1)
        contiene(r.salida, mensaje, "make test con un perfil inválido")
        afirmar("▶" not in r.salida, f"se ejecutó un verbo con un perfil inválido ({mensaje})")
        contiene(p.commit("chore: cambia el perfil", espera=1, extra=APROBADO).salida, mensaje, "el commit con un perfil inválido")

    # Una skill que falta es un aviso, no un error: el agente trabaja sin ella.
    escribir_perfil(p, cambiar(skills=["php", "go-backend"]))
    r = p.make("profile")
    contiene(r.salida, "la skill «php» no está en .agents/skills/")
    afirmar("«go-backend»" not in r.salida, "avisó de una skill que sí existe")


@prueba("commit: el perfil se confirma con APROBADO_PERFIL, sus inmutables no se modifican y el formato corre solo en la parte tocada")
def controles_del_commit(e):
    p = e.proyecto()
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir("web/panel/index.html", "<html></html>\n")
    perfil = base()
    perfil["partes"][0]["verbos"]["formato"] = "touch ../formato-corrio; ! grep -rIlq --exclude-dir=ajeno SIN_FORMATO ."
    escribir_perfil(p, perfil)
    contiene(p.commit("chore: perfil del proyecto", espera=1).salida, "El perfil del proyecto (equipo/perfil.json) cambió")
    afirmar(p.commits() == 1, "el perfil entró al historial sin la confirmación de una persona")
    p.commit("chore: perfil del proyecto", extra=APROBADO)
    marca = p.archivo("formato-corrio")
    marca.unlink()

    # Inmutables: los declara el perfil, no el kit.
    p.escribir("servidor/cambios/001_inicio.sql", "CREATE TABLE a (id int);\n")
    p.escribir("backend/migrations/000001_inicio.up.sql", "CREATE TABLE a (id int);\n")
    p.commit("feat(db): primer cambio de esquema")
    marca.unlink()
    p.agregar("servidor/cambios/001_inicio.sql", "ALTER TABLE a ADD b int;\n")
    contiene(p.commit("fix(db): edita el cambio", espera=1).salida, "no se modifican una vez versionados")
    p.git("checkout", "-q", "HEAD", "--", "servidor/cambios/001_inicio.sql")
    p.git("mv", "servidor/cambios/001_inicio.sql", "servidor/cambios/001_otro.sql")
    contiene(p.git("commit", "-m", "chore(db): renombra", espera=1).salida, "no se modifican una vez versionados")
    p.git("mv", "servidor/cambios/001_otro.sql", "servidor/cambios/001_inicio.sql")
    p.escribir("servidor/cambios/002_columna.sql", "ALTER TABLE a ADD b int;\n")
    p.agregar("backend/migrations/000001_inicio.up.sql", "-- con perfil, esta carpeta ya no es especial\n")
    p.commit("feat(db): agrega una columna")
    marca.unlink()

    # Formato: no corre si el commit no toca la parte, ni si solo toca código de terceros.
    p.escribir("nota.txt", "x\n")
    p.escribir("web/panel/index.html", "<html><body></body></html>\n")
    p.escribir("servidor/ajeno/biblioteca.php", "<?php // SIN_FORMATO\n")
    p.commit("docs: nota, panel y una biblioteca de terceros")
    afirmar(not marca.exists(), "el formato de «api» corrió en un commit que no tocaba código propio de esa parte")
    p.escribir("servidor/index.php", "<?php // SIN_FORMATO\n")
    contiene(p.commit("feat: cambia la api", espera=1).salida, "La parte «api» no pasa la revisión de formato")
    afirmar(marca.exists(), "el formato de «api» no corrió en un commit que la tocaba")
    marca.unlink()
    p.escribir("servidor/index.php", "<?php // bien\n")
    p.commit("feat: cambia la api")
    marca.unlink()

    # Quitar el perfil también lo confirma una persona; sin él vuelven los controles de siempre.
    p.git("rm", "-q", PERFIL)
    contiene(p.git("commit", "-m", "chore: quita el perfil", espera=1).salida, "El perfil del proyecto (equipo/perfil.json) cambió")
    p.git("commit", "-m", "chore: quita el perfil", extra=APROBADO)
    p.agregar("backend/migrations/000001_inicio.up.sql", "-- otra edición\n")
    contiene(p.commit("fix(db): edita la migración", espera=1).salida, "No modifiques migraciones existentes")


@prueba("make verificar-generados con perfil: falla si el verbo generar deja cambios sin commit")
def generados_con_perfil(e):
    perfil = base()
    perfil["partes"][0]["verbos"]["generar"] = "echo generado > salida.gen"
    p = con_perfil(e, perfil)
    r = p.make("verificar-generados", espera=1)
    contiene(r.salida, "El código generado de la parte «api» no estaba al día")
    contiene(r.salida, "servidor/salida.gen")
    p.commit("chore: código generado")
    contiene(p.make("verificar-generados").salida, "Código generado al día en la parte «api»")
    p.make("generar")
    afirmar(not p.pendientes(), f"generar dos veces dejó cambios: {p.pendientes()}")


@prueba("make profile DETECTAR=1 describe el proyecto sin escribir nada y sin contar el kit ni el código de terceros")
def detectar(e):
    p = e.proyecto()
    p.escribir("api/index.php", "<?php\n")
    p.escribir("api/modelo/Usuario.php", "<?php\n")
    p.escribir("api/vendor/alguien/paquete/a.php", "<?php\n")
    p.escribir("api/libraries/Hojas/Hoja.php", "<?php\n")
    p.escribir("api/libraries/Hojas/composer.json", json.dumps({"require": {"php": ">=5.0"}}))
    p.escribir("api/composer.json", json.dumps({"require": {"php": ">=8.2"}, "scripts": {"test": "phpunit"}}))
    p.escribir("datos/esquema.sql",
               "CREATE TABLE `a` (`id` int NOT NULL AUTO_INCREMENT) ENGINE=InnoDB;\n"
               "DELIMITER ;;\nCREATE DEFINER=`root`@`%` PROCEDURE `sp_a`() BEGIN SELECT 1; END ;;\n")
    p.escribir("web/package.json", json.dumps({"scripts": {"test": "vitest", "lint": "eslint ."},
                                               "dependencies": {"react": "^19"}, "devDependencies": {"vitest": "^3"}}))
    p.escribir("web/src/App.tsx", "export const App = () => null;\n")
    p.git("add", "-A")
    antes = p.pendientes()

    d = json.loads(p.make("profile", "DETECTAR=1").salida)
    afirmar(p.pendientes() == antes and not p.existe(PERFIL), "detectar escribió archivos en el proyecto")
    carpetas = {c["carpeta"]: c for c in d["carpetas_con_codigo"]}
    afirmar(set(carpetas) == {"api", "datos", "web"}, f"carpetas con código inesperadas (¿contó el kit?): {sorted(carpetas)}")
    afirmar(carpetas["api"]["lenguajes"] == {"PHP": 3}, f"contó mal el PHP propio (vendor no cuenta): {carpetas['api']}")
    afirmar(d["carpetas_de_terceros"] == ["api/vendor"], f"terceros: {d['carpetas_de_terceros']}")
    afirmar(d["carpetas_a_confirmar_si_son_de_terceros"] == [{"carpeta": "api/libraries/Hojas", "archivos": 2}],
            f"carpetas a confirmar: {d['carpetas_a_confirmar_si_son_de_terceros']}")
    marcas = {m["archivo"]: m for m in d["archivos_que_indican_tecnologia"]}
    afirmar(set(marcas) == {"api/composer.json", "api/libraries/Hojas/composer.json", "web/package.json"},
            f"marcadores: {sorted(marcas)}")
    afirmar(marcas["api/libraries/Hojas/composer.json"].get("dentro_de_carpeta_a_confirmar") == "api/libraries/Hojas"
            and "dentro_de_carpeta_a_confirmar" not in marcas["api/composer.json"],
            f"no distingue el composer.json de una biblioteca copiada del propio: {marcas}")
    afirmar(marcas["web/package.json"]["paquetes_conocidos"] == ["react", "vitest"], f"paquetes: {marcas['web/package.json']}")
    afirmar(marcas["web/package.json"]["scripts"] == ["lint", "test"], f"scripts: {marcas['web/package.json']}")
    afirmar(marcas["api/composer.json"]["scripts"] == ["test"], f"scripts de Composer: {marcas['api/composer.json']}")
    afirmar(d["archivos_sql"] == [{"archivo": "datos/esquema.sql", "motor_probable": "MySQL o MariaDB", "tablas": 1,
                                   "procedimientos_y_funciones": 1, "disparadores": 0}], f"SQL: {d['archivos_sql']}")
    afirmar("arquitecto" in d["roles_disponibles"] and "go-backend" in d["skills_disponibles"], "faltan roles o skills disponibles")
    afirmar(not [s for s in d["skills_disponibles"] if s.startswith(("bowser-", "equipo-", "perfil-"))],
            f"ofreció como skill de tecnología una que no lo es: {d['skills_disponibles']}")
    afirmar(d["repositorio_git"] is True and d["perfil_actual"] is None, "estado del repositorio o del perfil mal informado")
