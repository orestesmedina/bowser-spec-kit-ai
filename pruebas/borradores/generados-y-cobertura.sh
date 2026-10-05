#!/usr/bin/env bash
# Prueba de la 1.7.0: actualización desde 1.6.4, make generar / verificar-generados / cobertura.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/go/bin:$PATH"
ORIGEN=${ORIGEN:-$(git rev-parse --show-toplevel)}
export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=protocol.file.allow GIT_CONFIG_VALUE_0=always \
       GIT_CONFIG_KEY_1=safe.directory GIT_CONFIG_VALUE_1='*'
export GIT_AUTHOR_NAME=prueba GIT_AUTHOR_EMAIL=prueba@example.com GIT_COMMITTER_NAME=prueba GIT_COMMITTER_EMAIL=prueba@example.com
T=$(mktemp -d); FALLOS=0
espera() { # espera <0|1> <descripción> <comando...>
  local quiere=$1 desc=$2; shift 2
  "$@" >"$T/salida.txt" 2>&1; local dio=$?
  if { [ "$quiere" = 0 ] && [ $dio = 0 ]; } || { [ "$quiere" = 1 ] && [ $dio != 0 ]; }; then echo "  ✓ $desc"
  else echo "  ✗ $desc (salida $dio)"; sed 's/^/      /' "$T/salida.txt" | tail -8; FALLOS=$((FALLOS+1)); fi
}

echo "== 1. proyecto con el kit 1.6.4 (HEAD) y actualización a 1.7.0"
mkdir "$T/kit"; git -C "$ORIGEN" archive HEAD | tar -x -C "$T/kit"
(cd "$T/kit" && git init -q && git add -A && git commit -qm "kit 1.6.4" --no-verify)
mkdir "$T/proy" && cd "$T/proy" && git init -q
git submodule add -q "$T/kit" .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit >/dev/null
git add -A && git commit -qm "chore: instala kit"
cp "$ORIGEN/.git/index" "$T/indice"
ARBOL=$(cd "$ORIGEN" && GIT_INDEX_FILE="$T/indice" git add -A 2>/dev/null && GIT_INDEX_FILE="$T/indice" git write-tree)
git -C "$ORIGEN" archive "$ARBOL" | tar -x -C "$T/kit"
(cd "$T/kit" && git add -A && git commit -qm "kit 1.7.0" --no-verify)
make actualizar-kit 2>&1 | grep -E "Kit 1\.|actualizados|nuevos|scripts/(generar|cobertura)|PASOS"
ls -l scripts/generar.sh scripts/cobertura.py | cut -c1-11,40-
espera 0 "kit verificado" python3 .bowser-spec-kit-ai/scripts/instalar_kit.py --verificar
git add -A; espera 0 "commit de la actualización pasa los hooks" git commit -m "chore: actualiza kit a 1.7.0"
make help | grep -E "generar|cobertura"

echo "== 2. proyecto sin backend ni frontend: todo se omite"
espera 0 "make generar" make generar
espera 0 "make verificar-generados" make verificar-generados
cat "$T/salida.txt" | sed 's/^/      /'

echo "== 3. backend con sqlc ($(sqlc version 2>&1))"
mkdir -p backend/internal/db/queries backend/migrations backend/internal/users
cat > backend/go.mod <<'EOF'
module ejemplo/backend

go 1.26
EOF
cat > backend/sqlc.yaml <<'EOF'
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
EOF
echo "CREATE TABLE users (id BIGSERIAL PRIMARY KEY, email TEXT NOT NULL);" > backend/migrations/000001_create_users.up.sql
echo "DROP TABLE users;" > backend/migrations/000001_create_users.down.sql
git add -A && git commit -qm "feat: base del backend"
espera 0 "sin consultas: verificar-generados pasa (sqlc se omite)" make verificar-generados
printf -- "-- name: GetUser :one\nSELECT id, email FROM users WHERE id = \$1;\n" > backend/internal/db/queries/users.sql
git add -A && git commit -qm "feat: consulta de usuarios (sin generar)"
espera 1 "consulta nueva sin generar: verificar-generados FALLA" make verificar-generados
tail -5 "$T/salida.txt" | sed 's/^/      /'
ls backend/internal/db | tr '\n' ' '; echo
git add -A && git commit -qm "feat: código generado de sqlc"
espera 0 "con el generado en git: verificar-generados pasa" make verificar-generados
printf -- "\n-- name: ListUsers :many\nSELECT id, email FROM users ORDER BY id;\n" >> backend/internal/db/queries/users.sql
git add -A && git commit -qm "feat: otra consulta (sin regenerar)"
espera 1 "consulta cambiada sin regenerar: FALLA" make verificar-generados
git add -A && git commit -qm "chore: regenera sqlc"
espera 0 "solo backend (como en el CI)" bash scripts/generar.sh --verificar backend

echo "== 4. frontend con api:gen"
mkdir -p backend/api frontend/src/api frontend/node_modules
echo "openapi: 3.1.0" > backend/api/openapi.yaml
cat > frontend/package.json <<'EOF'
{"name": "f", "private": true, "scripts": {
  "api:gen": "node -e \"const fs=require('fs');fs.writeFileSync('src/api/schema.d.ts','// '+fs.readFileSync('../backend/api/openapi.yaml','utf8').length+'\\n')\""}}
EOF
git add -A && git commit -qm "feat: base del frontend (sin tipos)"
espera 1 "tipos sin generar: FALLA" make verificar-generados
git add -A && git commit -qm "feat: tipos de la API"
espera 0 "tipos en git: pasa" make verificar-generados
echo "info: {title: x}" >> backend/api/openapi.yaml; git add -A && git commit -qm "feat: cambia el contrato (sin regenerar)"
espera 1 "contrato cambiado sin regenerar: FALLA" bash scripts/generar.sh --verificar frontend
git add -A && git commit -qm "chore: regenera tipos"
espera 0 "make generar no deja cambios" bash -c 'make generar && test -z "$(git status --porcelain)"'
rm -rf frontend/node_modules
espera 1 "sin node_modules: error claro" make generar; tail -1 "$T/salida.txt" | sed 's/^/      /'
mkdir frontend/node_modules

echo "== 5. make cobertura ($(go version | cut -d' ' -f3))"
rm -f backend/internal/db/*.go   # el módulo de ejemplo no tiene pgx: sin esto no compila
cat > backend/internal/users/service.go <<'EOF'
package users

func Suma(a, b int) int { return a + b }

func Signo(n int) string {
	if n < 0 {
		return "negativo"
	}
	if n == 0 {
		return "cero"
	}
	return "positivo"
}
EOF
cat > backend/internal/users/service_test.go <<'EOF'
package users

import "testing"

func TestSuma(t *testing.T) {
	if Suma(1, 2) != 3 {
		t.Fatal("suma")
	}
}
EOF
espera 1 "cobertura baja (solo Suma probada): FALLA" make cobertura; tail -7 "$T/salida.txt" | sed 's/^/      /'
cat >> backend/internal/users/service_test.go <<'EOF'

func TestSigno(t *testing.T) {
	for n, quiere := range map[int]string{-1: "negativo", 0: "cero", 1: "positivo"} {
		if Signo(n) != quiere {
			t.Fatalf("signo %d", n)
		}
	}
}
EOF
espera 0 "cobertura completa: pasa" make cobertura; tail -5 "$T/salida.txt" | sed 's/^/      /'
espera 0 "coverage.out ignorado por git" bash -c 'test -z "$(git status --porcelain backend/coverage.out)"'

echo "== 6. proyecto real (clon limpio de simiente_santa, como lo vería el CI)"
REAL=${PROYECTO_REAL:-/no/definido}   # opcional: ruta de un proyecto real para probar contra un clon limpio
if [ -d "$REAL/frontend/node_modules" ]; then
  git clone -q "$REAL" "$T/real" 2>/dev/null && cd "$T/real"
  echo "  commit: $(git log -1 --format='%h %s' | cut -c1-70)"
  ln -s "$REAL/frontend/node_modules" frontend/node_modules
  mkdir -p scripts && cp "$ORIGEN/scripts/generar.sh" "$ORIGEN/scripts/cobertura.py" scripts/
  bash scripts/generar.sh --verificar 2>&1 | sed 's/^/      /' ; echo "  salida de verificar-generados: ${PIPESTATUS[0]}"
  git status --porcelain -- frontend/src backend | head -5
else echo "  (sin node_modules en el proyecto real: se omite)"; fi

cd /; rm -rf "$T"
echo "== FIN · fallos: $FALLOS"
exit $FALLOS
