#!/usr/bin/env bash
# Regenera el código que sale de otra fuente (no se escribe a mano):
#   backend:  consultas tipadas con sqlc     (backend/sqlc.yaml + backend/internal/db/queries/*.sql → backend/internal/db/)
#   frontend: tipos de la API desde OpenAPI  (script "api:gen" de frontend/package.json → frontend/src/api/)
#
# Uso: scripts/generar.sh [--verificar] [backend|frontend]
#   --verificar  además falla si la generación dejó cambios sin commit (alguien cambió la fuente y no regeneró).
# Cada parte se omite si el proyecto todavía no la tiene.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

VERIFICAR=0
PARTE=todo
for arg in "$@"; do
  case "$arg" in
    --verificar) VERIFICAR=1 ;;
    backend|frontend) PARTE=$arg ;;
    *) echo "Uso: scripts/generar.sh [--verificar] [backend|frontend]" >&2; exit 2 ;;
  esac
done

RUTAS=()

if [ "$PARTE" != frontend ]; then
  if [ ! -f backend/sqlc.yaml ] && [ ! -f backend/sqlc.yml ]; then
    echo "· sqlc: sin backend/sqlc.yaml, se omite"
  elif ! ls backend/internal/db/queries/*.sql >/dev/null 2>&1; then
    # sqlc falla si no hay ninguna consulta: mientras no exista la primera no hay nada que generar.
    echo "· sqlc: sin consultas en backend/internal/db/queries/, se omite"
  elif ! command -v sqlc >/dev/null 2>&1; then
    echo "✗ Falta sqlc. Instálalo con: go install github.com/sqlc-dev/sqlc/cmd/sqlc@v1.31.1" >&2
    exit 1
  else
    echo "· sqlc generate"
    (cd backend && sqlc generate)
    RUTAS+=(backend/internal/db)
  fi
fi

if [ "$PARTE" != backend ]; then
  if [ ! -f frontend/package.json ] || ! grep -q '"api:gen"' frontend/package.json; then
    echo "· tipos de la API: sin script \"api:gen\" en frontend/package.json, se omite"
  elif [ ! -d frontend/node_modules ]; then
    echo "✗ Faltan las dependencias del frontend. Ejecuta: cd frontend && npm ci" >&2
    exit 1
  else
    echo "· npm run api:gen"
    (cd frontend && npm run --silent api:gen)
    RUTAS+=(frontend/src/api)
  fi
fi

if [ "$VERIFICAR" = 1 ] && [ "${#RUTAS[@]}" -gt 0 ]; then
  CAMBIOS=$(git status --porcelain -- "${RUTAS[@]}")
  if [ -n "$CAMBIOS" ]; then
    echo "✗ El código generado no está al día (o tiene cambios sin commit):" >&2
    echo "$CAMBIOS" >&2
    echo "  Ejecuta 'make generar' y agrega el resultado al commit." >&2
    exit 1
  fi
  echo "✓ Código generado al día."
fi
