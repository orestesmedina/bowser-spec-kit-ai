#!/usr/bin/env bash
# Prueba de punta a punta de la 1.6.2: instala la 1.6.1 en un proyecto temporal y actualiza a la 1.6.2.
set -euo pipefail
ORIGEN=${ORIGEN:-$(git rev-parse --show-toplevel)}
export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=protocol.file.allow GIT_CONFIG_VALUE_0=always \
       GIT_CONFIG_KEY_1=safe.directory GIT_CONFIG_VALUE_1='*'
export GIT_AUTHOR_NAME=prueba GIT_AUTHOR_EMAIL=prueba@example.com GIT_COMMITTER_NAME=prueba GIT_COMMITTER_EMAIL=prueba@example.com
T=$(mktemp -d)
echo "== carpeta: $T"

echo "== 1. kit en 1.6.1 (HEAD)"
mkdir "$T/kit"
git -C "$ORIGEN" archive HEAD | tar -x -C "$T/kit"
(cd "$T/kit" && git init -q && git add -A && git commit -qm "kit 1.6.1" --no-verify)
cat "$T/kit/VERSION"

echo "== 2. proyecto nuevo con la 1.6.1"
mkdir "$T/proy" && cd "$T/proy" && git init -q
git submodule add -q "$T/kit" .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit >/dev/null
git add -A && git commit -qm "chore: instala kit" && echo "commit con hooks: OK"
printf 'e2e: ## Pruebas end-to-end\n\t@echo e2e\n' > proyecto.mk
echo "-- make help | grep e2e (1.6.1, se espera vacío):"; make help | grep e2e || echo "(no aparece)"

echo "== 3. kit pasa a 1.6.2 (árbol de trabajo)"
# Árbol de trabajo con los permisos del índice de git (en /mnt/d todo aparece como ejecutable).
cp "$ORIGEN/.git/index" "$T/indice"
ARBOL=$(cd "$ORIGEN" && GIT_INDEX_FILE="$T/indice" git add -A 2>/dev/null && GIT_INDEX_FILE="$T/indice" git write-tree)
git -C "$ORIGEN" archive "$ARBOL" | tar -x -C "$T/kit"
ls -l "$T/kit/.githooks"
(cd "$T/kit" && git add -A && git commit -qm "kit 1.6.2" --no-verify && git status --short | wc -l)
cat "$T/kit/VERSION"

echo "== 4. make actualizar-kit (con el Makefile viejo)"
cd "$T/proy"
make actualizar-kit 2>&1 | tail -45

echo "== 5. comprobaciones"
grep -c "golangci-lint-action@v9" .github/workflows/ci.yml
grep -n "latest" .github/workflows/ci.yml || true
grep -n "postgres:" .github/workflows/ci.yml docker-compose.yml
echo "-- make help | grep e2e (1.6.2):"; make help | grep e2e
python3 .bowser-spec-kit-ai/scripts/instalar_kit.py --verificar
python3 scripts/sincronizar.py --verificar
python3 - <<'EOF'
try:
    import yaml
    d = yaml.safe_load(open(".github/workflows/ci.yml"))
    print("YAML válido; jobs:", ", ".join(d["jobs"]), "| env:", d["env"])
except ImportError:
    print("PyYAML no instalado: YAML sin validar")
EOF
ls -l .githooks equipo/adaptadores/claude/hooks
bash scripts/doctor.sh 2>&1 | grep -i "hooks" || true
git add -A
echo "-- mensaje inválido (se espera rechazo):"
if git commit -qm "mensaje malo" 2>&1 | tail -4; [ "$(git log --oneline | wc -l)" = "1" ]; then echo "RECHAZADO: OK"; else echo "FALLO: el hook no corrió"; exit 1; fi
git commit -m "chore: actualiza kit a 1.6.2" 2>&1 | tail -15 && echo "commit con hooks: OK"
git status --short | wc -l

echo "== 6. instalación limpia de la 1.6.2"
mkdir "$T/proy2" && cd "$T/proy2" && git init -q
git submodule add -q "$T/kit" .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit >/dev/null
grep -n "image:" docker-compose.yml
git add -A && git commit -qm "chore: instala kit" && echo "commit con hooks: OK"
rm -rf "$T"
echo "== FIN"
