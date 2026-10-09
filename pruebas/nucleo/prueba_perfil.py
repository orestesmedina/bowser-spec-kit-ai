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
    p.make("instalar-kit")      # las skills del proyecto pasan a ser las que nombra el perfil
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
    p.escribir(".agents/skills/propia/SKILL.md", "---\nname: propia\ndescription: Del proyecto.\n---\n")
    escribir_perfil(p, cambiar(skills=["php", "propia"]))
    r = p.make("profile")
    contiene(r.salida, "la skill «php» no está en .agents/skills/")
    afirmar("«propia»" not in r.salida, "avisó de una skill que sí existe")


@prueba("una parte puede tener varios roles, cada uno con las skills de la parte más las suyas; el «rol» único sigue valiendo")
def roles_de_la_parte(e):
    p = con_perfil(e)
    contiene(p.make("profile").salida, "    roles:      dev-backend\n", "el perfil con «rol» (formato de la entrega A)")

    def con_roles(roles, **campos) -> dict:
        perfil = base()
        del perfil["partes"][0]["rol"]
        perfil["partes"][0].update(roles=roles, **campos)
        return perfil

    escribir_perfil(p, con_roles(["dev-backend", {"rol": "dev-frontend", "skills": ["react-frontend", "go-backend"]}, "qa-tester"],
                                 skills=["go-backend"]))
    r = p.make("profile")
    contiene(r.salida, "    roles:      dev-backend (go-backend)  ·  dev-frontend (go-backend, react-frontend)  ·  qa-tester (go-backend)\n")
    contiene(r.salida, "OK: perfil válido (2 partes).")

    # Skills sin ningún rol: se dice, porque nadie las recibe.
    sin_rol = base()
    del sin_rol["partes"][0]["rol"]
    sin_rol["partes"][0]["skills"] = ["go-backend"]
    escribir_perfil(p, sin_rol)
    contiene(p.make("profile").salida, "skills:     go-backend (ningún rol las recibe")

    # La skill que falta también se avisa cuando es de un solo rol.
    escribir_perfil(p, con_roles([{"rol": "dev-backend", "skills": ["php"]}]))
    contiene(p.make("profile").salida, "la skill «php» no está en .agents/skills/")

    ambos = base()
    ambos["partes"][0]["roles"] = ["dev-backend"]
    malos = [
        (ambos, "usa \"roles\" (lista) o \"rol\" (uno solo), no los dos"),
        (con_roles("dev-backend"), "\"roles\" debe ser una lista de roles"),
        (con_roles(["dev-backend", "dev-inventado"]), "el rol «dev-inventado» no existe"),
        (con_roles([{"skills": ["go-backend"]}]), "el rol «None» no existe"),
        (con_roles(["dev-backend", {"rol": "dev-backend"}]), "el rol «dev-backend» está dos veces"),
        (con_roles([{"rol": "dev-backend", "skill": ["go-backend"]}]), "un rol solo admite \"rol\" y \"skills\" (sobra «skill»)"),
        (con_roles([{"rol": "dev-backend", "skills": "go-backend"}]), "las \"skills\" del rol «dev-backend» deben ser una lista"),
    ]
    for perfil, mensaje in malos:
        escribir_perfil(p, perfil)
        contiene(p.make("profile", espera=1).salida, mensaje)
        afirmar("▶" not in p.make("test", espera=1).salida, f"se ejecutó un verbo con un perfil inválido ({mensaje})")


@prueba("los comandos de los verbos reciben PERFIL_RAIZ y PERFIL_TERCEROS, también en el commit, y pueden usar scripts de tools/")
def variables_de_los_verbos(e):
    perfil = base()
    perfil["partes"][0]["terceros"] = ["ajeno", "libs/con espacio/"]
    perfil["partes"][0]["verbos"] = {"probar": "bash \"$PERFIL_RAIZ/tools/mostrar.sh\"",
                                     "formato": "test -f \"$PERFIL_RAIZ/equipo/perfil.json\" && test -n \"$PERFIL_TERCEROS\""}
    perfil["partes"][1]["verbos"] = {"probar": "test -z \"$PERFIL_TERCEROS\" && echo panel-sin-terceros"}
    p = e.proyecto()
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir("web/panel/index.html", "<html></html>\n")
    p.escribir("tools/mostrar.sh",
               "echo \"raiz=$PERFIL_RAIZ en=$PWD\"\n"
               "while IFS= read -r t; do echo \"tercero=<$t>\"; done <<< \"$PERFIL_TERCEROS\"\n")
    escribir_perfil(p, perfil)
    p.make("instalar-kit")
    # El commit toca la parte «api»: su verbo formato corre en el hook y necesita las dos variables.
    p.commit("chore: perfil del proyecto", extra=APROBADO)

    r = p.make("test")
    contiene(r.salida, f"raiz={p.ruta} en={p.ruta}/servidor\n")
    contiene(r.salida, "tercero=<ajeno>\ntercero=<libs/con espacio>\n")
    afirmar(r.salida.count("tercero=<") == 2, f"PERFIL_TERCEROS no trae una carpeta por línea:\n{r.salida}")
    contiene(r.salida, "panel-sin-terceros")

    # tools/ es del proyecto: instalar el kit otra vez no la toca ni la registra como suya.
    p.make("instalar-kit")
    p.verificar_kit()
    afirmar(p.existe("tools/mostrar.sh") and not p.pendientes(), f"instalar el kit tocó el proyecto: {p.pendientes()}")
    afirmar(not [a for a in json.loads(p.leer(".kit-manifest.json"))["archivos"] if a.startswith("tools/")],
            "tools/ quedó registrada como carpeta del kit")


@prueba("make ci con perfil ejecuta todos los verbos aunque uno falle y termina con un resumen de lo comprobado y lo que no")
def resumen_de_ci(e):
    contiene(e.proyecto().make("-n", "ci").salida, "go test", "make ci sin perfil")

    p = con_perfil(e)
    r = p.make("ci")
    contiene(r.salida, "Resumen de lo comprobado")
    contiene(r.salida, "  probar     bien: api  ·  sin definir: panel\n")
    contiene(r.salida, "  cobertura  sin definir en ninguna parte\n")
    contiene(r.salida, "⚠ Pasó lo que se comprobó: 1 de 12 comprobaciones. Las otras 11 no existen")
    afirmar("Resumen" not in p.make("test").salida, "make test mostró el resumen, que es de make ci")

    # Un fallo no corta lo que sigue, y el resumen dice dónde fue.
    perfil = base()
    perfil["partes"][0]["verbos"].update({"revisar": "exit 3", "generar": "echo generado > salida.gen"})
    perfil["partes"][1]["verbos"] = {"revisar": "echo revisar-panel"}
    escribir_perfil(p, perfil)
    r = p.make("ci", espera=1)
    contiene(r.salida, "  revisar    FALLÓ: api  ·  bien: panel\n")
    contiene(r.salida, "  generar    FALLÓ: api  ·  sin definir: panel\n", "el código generado sin commit")
    contiene(r.salida, "▶ probar · api", "los verbos que siguen a un fallo")
    afirmar("Pasó lo que se comprobó" not in r.salida and "Todo comprobado" not in r.salida, "un ci con fallos dijo que pasó")
    contiene(r.salida, "✗ Falló: revisar en «api»; código generado de «api».")

    # Con todo definido y sin fallos, lo dice. PARTE limita el resumen a esa parte.
    completo = {"partes": [{"nombre": "todo", "carpeta": "servidor", "verbos": {v: f"echo {v}-ok" for v in
                                                                                 ("formato", "revisar", "probar", "cobertura", "auditar", "generar")}}]}
    escribir_perfil(p, completo)
    p.commit("chore: perfil completo", extra=APROBADO)
    contiene(p.make("ci").salida, "✓ Todo comprobado y sin fallos (6 comprobaciones).")
    escribir_perfil(p, base())
    contiene(p.make("ci", "PARTE=api").salida, "1 de 6 comprobaciones")


@prueba("commit: el perfil se confirma con APROBADO_PERFIL, sus inmutables no se modifican y el formato corre solo en la parte tocada")
def controles_del_commit(e):
    p = e.proyecto()
    p.escribir("servidor/index.php", "<?php\n")
    p.escribir("web/panel/index.html", "<html></html>\n")
    perfil = base()
    perfil["partes"][0]["verbos"]["formato"] = "touch ../formato-corrio; ! grep -rIlq --exclude-dir=ajeno SIN_FORMATO ."
    escribir_perfil(p, perfil)
    p.make("instalar-kit")
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
    p.make("instalar-kit")      # sin perfil, vuelven las tres skills de siempre
    p.git("add", "-A")
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
