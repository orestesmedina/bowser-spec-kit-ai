"""Los controles que no dependen de que el agente obedezca: hooks de git y hook de Claude Code."""
import json
import os
import re
import shutil
import subprocess

from apoyo import afirmar, contiene, prueba

CONSTITUCION = ".specify/memory/constitution.md"
PRINCIPIOS, REGLAS = "equipo/principios.md", "equipo/reglas.md"


@prueba("el mensaje de commit debe seguir Conventional Commits")
def mensaje_de_commit(e):
    p = e.proyecto()
    p.escribir("nota.txt", "x\n")
    for malo in ("mensaje malo", "Feat: con mayúscula", "feat: x", "arreglo: tipo inventado"):
        contiene(p.commit(malo, espera=1).salida, "Mensaje de commit inválido")
    afirmar(p.commits() == 1, "un commit con mensaje inválido entró al historial")
    p.commit("feat(notas): agrega una nota")
    p.escribir("nota.txt", "y\n")
    p.commit("fix!: cambio incompatible en la nota")
    afirmar(p.commits() == 3, "un commit con mensaje válido fue rechazado")


@prueba("no se pueden subir archivos que suelen tener secretos, aunque se fuerce el git add")
def secretos(e):
    p = e.proyecto()
    for rel in (".env", "backend/.env.local", "certificado.pem", "llave.key", "secrets/token.txt"):
        p.escribir(rel, "contenido de prueba\n")
        afirmar(rel not in p.git("status", "--short", "--untracked-files=all").salida, f"{rel} no está ignorado por git")
        p.git("add", "-f", rel)
        r = p.git("commit", "-m", "chore: agrega configuración", espera=1)
        contiene(r.salida, f"No se permite commitear '{rel}'")
        p.git("rm", "-q", "--cached", rel)
    p.agregar(".env.example", "\n# variable nueva, sin valor\nNUEVA=\n")
    p.commit("docs: documenta una variable de entorno")


@prueba("la constitución se genera con los principios del kit y las reglas del proyecto, y no nombra ninguna tecnología")
def constitucion_en_dos_partes(e):
    p = e.proyecto()
    generada, principios, reglas = p.leer(CONSTITUCION), p.leer(PRINCIPIOS).strip(), p.leer(REGLAS).strip()
    afirmar(generada.startswith("<!-- GENERADO"), "la constitución no avisa de que es un archivo generado")
    contiene(generada, principios, "la constitución generada")
    contiene(generada, reglas, "la constitución generada")
    afirmar(generada.index(principios) < generada.index(reglas), "las reglas del proyecto deben ir después de los principios")
    manifiesto = json.loads(p.leer(".kit-manifest.json"))["archivos"]
    afirmar(PRINCIPIOS in manifiesto, "los principios deben ser un archivo del kit")
    afirmar(REGLAS not in manifiesto and CONSTITUCION not in manifiesto,
            "las reglas son del proyecto y la constitución se genera: ninguna de las dos es un archivo del kit")
    for palabra in ("Go", "React", "TypeScript", "PostgreSQL", "sqlc", "pgx", "gofmt", "golangci-lint", "govulncheck", "npm",
                    "Vitest", "Playwright", "docker", "slog", "handler", "backend", "frontend", "PHP", "MySQL", "OpenAPI"):
        afirmar(not re.search(rf"\b{re.escape(palabra)}\b", generada), f"la constitución de un proyecto nuevo nombra «{palabra}»")
    # Sin reglas, la constitución son solo los principios.
    p.archivo(REGLAS).unlink()
    p.make("sync")
    contiene(p.leer(CONSTITUCION), principios, "la constitución sin reglas del proyecto")
    afirmar("Constitución: reglas del proyecto" not in p.leer(CONSTITUCION), "la constitución conserva unas reglas que ya no existen")


@prueba("las reglas del proyecto no cambian sin aprobación, y la constitución generada tiene que ir al día")
def reglas_del_proyecto(e):
    p = e.proyecto()
    aprobado = {"APPROVED_CONSTITUTION": "1"}
    p.agregar(REGLAS, "\n- La cobertura mínima DEBE ser 70 %.\n")
    contiene(p.commit("docs: agrega una regla", espera=1).salida, "La constitución cambió: las reglas del proyecto")
    # Con la aprobación, falta regenerar: lo que leen los agentes seguiría sin la regla.
    contiene(p.commit("docs: agrega una regla", espera=1, extra=aprobado).salida, "la constitución generada están desactualizadas")
    p.make("sync")
    contiene(p.leer(CONSTITUCION), "La cobertura mínima DEBE ser 70 %.", "la constitución generada")
    p.commit("docs: agrega una regla", extra=aprobado)

    # El archivo generado no se edita a mano, ni con la aprobación: se cambia la fuente.
    p.agregar(CONSTITUCION, "\n- regla escrita en el archivo generado\n")
    contiene(p.commit("docs: cambia la constitución", espera=1, extra=aprobado).salida, "la constitución generada están desactualizadas")
    p.git("checkout", "-q", "HEAD", "--", CONSTITUCION)

    # Borrar las reglas también es cambiarlas.
    p.git("rm", "-q", REGLAS)
    contiene(p.git("commit", "-m", "chore: quita las reglas", espera=1).salida, "La constitución cambió: las reglas del proyecto")
    afirmar(p.commits() == 2, "un cambio de las reglas sin aprobación entró al historial")


@prueba("los principios llegan con la actualización del kit sin pedir aprobación; si el proyecto los hace suyos, sí la piden")
def principios_del_kit(e):
    kit = e.kit()
    p = e.proyecto(kit)

    p.agregar(PRINCIPIOS, "\n- principio agregado a mano\n")
    p.make("sync")
    r = p.commit("docs: cambia los principios", espera=1)
    contiene(r.salida, "La constitución cambió: los principios")
    contiene(r.salida, "Los archivos del kit no coinciden")
    p.git("checkout", "-q", "HEAD", "--", PRINCIPIOS, CONSTITUCION)

    # El proyecto los declara suyos (kit.excluir): desde entonces cada cambio necesita la aprobación.
    config = json.loads(p.leer("equipo/config.json"))
    config.setdefault("kit", {})["excluir"] = [PRINCIPIOS]
    p.escribir("equipo/config.json", json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    p.make("install-kit")
    p.commit("chore: principios propios del proyecto")
    p.agregar(PRINCIPIOS, "\n- principio propio del proyecto\n")
    p.make("sync")
    contiene(p.commit("docs: ajusta los principios", espera=1).salida, "La constitución cambió: los principios")
    p.commit("docs: ajusta los principios", extra={"APPROVED_CONSTITUTION": "1"})

    # Otro proyecto, sin exclusión: los principios cambian en el kit y llegan con la actualización.
    q = e.proyecto(kit)
    with open(kit / PRINCIPIOS, "a", encoding="utf-8") as f:
        f.write("\n- principio nuevo aprobado en el kit\n")
    e.commit_kit(kit, "cambia los principios")
    q.make("update-kit")
    contiene(q.leer(CONSTITUCION), "principio nuevo aprobado en el kit", "la constitución generada del proyecto")
    q.commit("chore: actualiza kit")


@prueba("una migración ya versionada no se modifica; una nueva sí se puede agregar")
def migraciones(e):
    p = e.proyecto()
    p.escribir("backend/migrations/000001_inicio.up.sql", "CREATE TABLE a (id int);\n")
    p.commit("feat(db): primera migración")
    p.agregar("backend/migrations/000001_inicio.up.sql", "ALTER TABLE a ADD b int;\n")
    contiene(p.commit("fix(db): cambia la migración", espera=1).salida, "No modifiques migraciones existentes")
    p.git("checkout", "-q", "HEAD", "--", "backend/migrations/000001_inicio.up.sql")
    # Eliminarla también es modificarla, aunque el commit no traiga nada más.
    p.git("rm", "-q", "backend/migrations/000001_inicio.up.sql")
    contiene(p.git("commit", "-m", "chore(db): elimina la migración", espera=1).salida, "No modifiques migraciones existentes")
    p.git("reset", "-q", "HEAD", "--", "backend/migrations/000001_inicio.up.sql")
    p.git("checkout", "-q", "HEAD", "--", "backend/migrations/000001_inicio.up.sql")
    p.escribir("backend/migrations/000002_columna.up.sql", "ALTER TABLE a ADD b int;\n")
    p.commit("feat(db): agrega una columna")


@prueba("sin python3, el commit se bloquea y el mensaje explica cómo resolverlo")
def sin_python(e):
    p = e.proyecto()
    limitado = e.tmp / f"sin-python-{p.ruta.name}"
    limitado.mkdir()
    for programa in ("git", "bash", "sh", "env", "grep", "sed", "awk", "cat", "head", "dirname", "basename", "sort", "xargs", "tr", "cut"):
        real = shutil.which(programa)
        if real:
            os.symlink(real, limitado / programa)
    p.escribir("nota.txt", "x\n")
    p.git("add", "-A")
    r = p.git("commit", "-m", "docs: nota", espera=1, extra={"PATH": str(limitado)})
    contiene(r.salida, "No se encontró python3")
    contiene(r.salida, "docs/windows-wsl.md")
    afirmar(p.commits() == 1, "el commit entró sin que corrieran los controles")


def intento_de_editar(e, p, rel: str) -> subprocess.CompletedProcess:
    """Lo que Claude Code le pasa al hook antes de editar un archivo."""
    return subprocess.run(["bash", "equipo/adaptadores/claude/hooks/proteger-archivos.sh"], cwd=p.ruta,
                          input=json.dumps({"tool_input": {"file_path": str(p.ruta / rel)}}).encode(),
                          env=dict(e.entorno, CLAUDE_PROJECT_DIR=str(p.ruta)), capture_output=True)


def se_bloquea(e, p, rel: str) -> str:
    r = intento_de_editar(e, p, rel)
    afirmar(r.returncode == 2, f"editar {rel} debía bloquearse (código 2) y dio {r.returncode}")
    motivo = r.stderr.decode("utf-8", "replace")
    contiene(motivo, "Bloqueado", f"el motivo al bloquear {rel}")
    return motivo


def se_permite(e, p, rel: str) -> None:
    r = intento_de_editar(e, p, rel)
    afirmar(r.returncode == 0, f"editar {rel} debía permitirse y se bloqueó: {r.stderr.decode('utf-8', 'replace')}")


@prueba("Claude Code: el hook bloquea secretos, constitución, archivos del kit y costos, y deja pasar el resto",
        requiere=("jq",))
def hook_de_claude(e):
    p = e.proyecto()
    p.escribir("backend/migrations/000001_inicio.up.sql", "CREATE TABLE a (id int);\n")
    p.commit("feat(db): primera migración")

    # Sin perfil, los inmutables son los de la estructura supuesta: las migraciones de backend/.
    for rel in (".env", "secrets/clave.txt", "certificado.pem", CONSTITUCION, PRINCIPIOS, REGLAS, "AGENTS.md", "equipo/orquestador.md",
                ".bowser-spec-kit-ai/README.md", "backend/migrations/000001_inicio.up.sql", "specs/001-x/costos.json"):
        se_bloquea(e, p, rel)
    for rel in (".env.example", "src/app.go", "equipo/config.json", "backend/migrations/000002_nueva.up.sql", "specs/001-x/spec.md"):
        se_permite(e, p, rel)


@prueba("Claude Code: con perfil, el hook protege los inmutables que el perfil declara, y solo los ya versionados",
        requiere=("jq",))
def hook_de_claude_con_perfil(e):
    p = e.proyecto()
    perfil = {"partes": [
        {"nombre": "datos", "carpeta": "base", "roles": ["dev-dba"], "inmutables": ["cambios/*.sql"]},
        {"nombre": "api", "carpeta": "backend", "roles": ["dev-backend"]},
    ]}
    p.escribir("equipo/perfil.json", json.dumps(perfil, ensure_ascii=False, indent=2) + "\n")
    p.escribir("base/cambios/001_inicio.sql", "CREATE TABLE a (id int);\n")
    p.escribir("base/consultas/listar.sql", "SELECT 1;\n")
    p.escribir("backend/migrations/000001_inicio.up.sql", "CREATE TABLE a (id int);\n")
    p.make("install-kit")
    p.commit("feat(db): primer cambio de esquema", extra={"APPROVED_PROFILE": "1"})

    motivo = se_bloquea(e, p, "base/cambios/001_inicio.sql")
    contiene(motivo, "«datos»", "el motivo del bloqueo")
    contiene(motivo, "crea uno nuevo", "el motivo del bloqueo")
    # Uno nuevo se puede escribir y corregir mientras no esté en git, aunque ya exista en el disco.
    se_permite(e, p, "base/cambios/002_columna.sql")
    p.escribir("base/cambios/002_columna.sql", "ALTER TABLE a ADD b int;\n")
    se_permite(e, p, "base/cambios/002_columna.sql")
    # Lo que el perfil no declara no se protege: ni otros archivos de la parte ni la carpeta de la estructura original.
    se_permite(e, p, "base/consultas/listar.sql")
    se_permite(e, p, "backend/migrations/000001_inicio.up.sql")

    # Con un perfil mal escrito no se bloquea nada (el commit lo rechaza): si no, no se podría ni corregir.
    p.escribir("equipo/perfil.json", "{ esto no es JSON\n")
    se_permite(e, p, "base/cambios/001_inicio.sql")
    se_bloquea(e, p, ".env")


@prueba("Claude Code: los permisos y los hooks que el kit instala no nombran ninguna tecnología ni formatean al editar")
def ajustes_de_claude(e):
    p = e.proyecto(commit=False)
    for rel in ("equipo/adaptadores/claude/settings.json", ".claude/settings.json"):
        ajustes = json.loads(p.leer(rel))
        afirmar("PostToolUse" not in ajustes.get("hooks", {}), f"{rel} ejecuta un hook después de cada edición")
        permisos = [regla for grupo in ajustes["permissions"].values() for regla in grupo]
        for palabra in ("go ", "gofmt", "golangci", "govulncheck", "npm", "npx", "playwright", "php", "composer"):
            malos = [regla for regla in permisos if palabra in regla.lower()]
            afirmar(not malos, f"{rel} nombra una tecnología en sus permisos: {malos}")
        for regla in ("Bash(make:*)", "Read(./.env)", "Bash(git push:*)"):
            afirmar(regla in permisos, f"{rel} perdió el permiso {regla}")
    afirmar(not p.existe("equipo/adaptadores/claude/hooks/formatear.sh"), "el hook de formateo sigue llegando a los proyectos")
    hook = p.leer("equipo/adaptadores/claude/hooks/proteger-archivos.sh")
    for palabra in ("backend", "migrations", "gofmt", "prettier"):
        afirmar(palabra not in hook, f"el hook de Claude Code nombra «{palabra}»")
