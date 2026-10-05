"""make generar y make verificar-generados: código de sqlc y tipos de la API."""
import json

from apoyo import afirmar, contiene, prueba

SQLC_YAML = """\
version: "2"
sql:
  - schema: "migrations"
    queries: "internal/db/queries"
    engine: "postgresql"
    gen:
      go:
        package: "db"
        out: "internal/db"
        sql_package: "pgx/v5"
"""
CONSULTAS = "backend/internal/db/queries/users.sql"
CONTRATO = "backend/api/openapi.yaml"
# Un "generador" mínimo: escribe en los tipos el tamaño del contrato, así cambia cuando cambia el contrato.
API_GEN = ("node -e \"const fs=require('fs');fs.writeFileSync('src/api/schema.d.ts',"
           "'// '+fs.readFileSync('../backend/api/openapi.yaml','utf8').length+'\\n')\"")
DESACTUALIZADO = "El código generado no está al día"
AL_DIA = "✓ Código generado al día."


def con_backend(e):
    """Proyecto con la base de un backend con sqlc, todavía sin consultas."""
    p = e.proyecto()
    p.escribir("backend/go.mod", "module ejemplo/backend\n\ngo 1.26\n")
    p.escribir("backend/sqlc.yaml", SQLC_YAML)
    p.escribir("backend/migrations/000001_create_users.up.sql",
               "CREATE TABLE users (id BIGSERIAL PRIMARY KEY, email TEXT NOT NULL);\n")
    p.escribir("backend/migrations/000001_create_users.down.sql", "DROP TABLE users;\n")
    p.commit("feat: base del backend")
    return p


def con_frontend(e):
    """Proyecto con un contrato de API y un frontend con el script api:gen, todavía sin tipos generados."""
    p = e.proyecto()
    p.escribir(CONTRATO, "openapi: 3.1.0\n")
    p.escribir("frontend/package.json",
               json.dumps({"name": "f", "private": True, "scripts": {"api:gen": API_GEN}}, indent=2) + "\n")
    p.escribir("frontend/src/api/.gitkeep", "")
    p.commit("feat: base del frontend (sin tipos)")
    return p


@prueba("proyecto sin backend ni frontend: make generar y make verificar-generados se omiten y terminan bien")
def sin_nada_que_generar(e):
    p = e.proyecto()
    for orden in ("generar", "verificar-generados"):
        r = p.make(orden)
        contiene(r.salida, "sqlc: sin backend/sqlc.yaml, se omite", f"la salida de make {orden}")
        contiene(r.salida, 'sin script "api:gen" en frontend/package.json, se omite', f"la salida de make {orden}")
    afirmar(not p.pendientes(), f"make generar dejó cambios en un proyecto sin nada que generar: {p.pendientes()}")


@prueba("backend sin ninguna consulta: sqlc se omite en vez de fallar")
def sin_consultas(e):
    p = con_backend(e)
    contiene(p.make("verificar-generados").salida, "sin consultas en backend/internal/db/queries/, se omite")


@prueba("sqlc: una consulta nueva o cambiada sin regenerar hace fallar verificar-generados", requiere=("sqlc",))
def sqlc_desactualizado(e):
    p = con_backend(e)
    p.escribir(CONSULTAS, "-- name: GetUser :one\nSELECT id, email FROM users WHERE id = $1;\n")
    p.commit("feat: consulta de usuarios (sin generar)")
    contiene(p.make("verificar-generados", espera=1).salida, DESACTUALIZADO)
    afirmar(p.existe("backend/internal/db/users.sql.go"), "sqlc no generó backend/internal/db/users.sql.go")

    p.commit("feat: código generado de sqlc")
    contiene(p.make("verificar-generados").salida, AL_DIA)

    p.agregar(CONSULTAS, "\n-- name: ListUsers :many\nSELECT id, email FROM users ORDER BY id;\n")
    p.commit("feat: otra consulta (sin regenerar)")
    r = p.make("verificar-generados", espera=1)
    contiene(r.salida, DESACTUALIZADO)
    contiene(r.salida, "backend/internal/db/users.sql.go")

    p.commit("chore: regenera sqlc")
    # Así lo llama la integración continua: una sola parte.
    contiene(p.correr("bash", "scripts/generar.sh", "--verificar", "backend").salida, AL_DIA)
    p.make("generar")
    afirmar(not p.pendientes(), f"make generar cambió archivos que ya estaban al día: {p.pendientes()}")


@prueba("tipos de la API: un contrato cambiado sin regenerar hace fallar verificar-generados", requiere=("node", "npm"))
def tipos_desactualizados(e):
    p = con_frontend(e)
    p.archivo("frontend/node_modules").mkdir()
    contiene(p.make("verificar-generados", espera=1).salida, DESACTUALIZADO)
    afirmar(p.existe("frontend/src/api/schema.d.ts"), "api:gen no generó frontend/src/api/schema.d.ts")

    p.commit("feat: tipos de la API")
    contiene(p.make("verificar-generados").salida, AL_DIA)

    p.agregar(CONTRATO, "info: {title: x}\n")
    p.commit("feat: cambia el contrato (sin regenerar)")
    contiene(p.correr("bash", "scripts/generar.sh", "--verificar", "frontend", espera=1).salida, DESACTUALIZADO)

    p.commit("chore: regenera tipos")
    p.make("generar")
    afirmar(not p.pendientes(), f"make generar cambió archivos que ya estaban al día: {p.pendientes()}")


@prueba("frontend sin dependencias instaladas: make generar falla y dice qué ejecutar")
def sin_dependencias(e):
    p = con_frontend(e)
    contiene(p.make("generar", espera=1).salida, "Faltan las dependencias del frontend. Ejecuta: cd frontend && npm ci")


@prueba("argumento desconocido: generar.sh muestra cómo se usa")
def argumento_desconocido(e):
    p = e.proyecto()
    r = p.correr("bash", "scripts/generar.sh", "--otra-cosa", espera=1)
    contiene(r.salida, "Uso: scripts/generar.sh [--verificar] [backend|frontend]")
