#!/usr/bin/env bash
# Prueba de la 1.8.0: actualización desde 1.7.1, retiro de la guía y MODELOS.md, mensajes y constitución.
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
arbol_actual() {
  cp "$ORIGEN/.git/index" "$T/indice"
  (cd "$ORIGEN" && GIT_INDEX_FILE="$T/indice" git add -A 2>/dev/null && GIT_INDEX_FILE="$T/indice" git write-tree)
}

echo "== 1. proyecto con el kit 1.7.1 (HEAD) y actualización a 1.8.0"
mkdir "$T/kit"; git -C "$ORIGEN" archive HEAD | tar -x -C "$T/kit"
(cd "$T/kit" && git init -q && git add -A && git commit -qm "kit 1.7.1" --no-verify)
mkdir "$T/proy" && cd "$T/proy" && git init -q
git submodule add -q "$T/kit" .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit >/dev/null
git add -A && git commit -qm "chore: instala kit"
echo "  antes: $(ls docs | tr '\n' ' ') | equipo: $(ls equipo | tr '\n' ' ')"
(cd "$T/kit" && git rm -rqf . && git -C "$ORIGEN" archive "$(arbol_actual)" | tar -x -C "$T/kit" && git add -A && git commit -qm "kit 1.8.0" --no-verify)
make actualizar-kit 2>&1 | grep -E "Kit 1\.|actualizados|nuevos|eliminados|GUIA|MODELOS|PASOS|desaparecen" | cut -c1-150
echo "  después: $(ls docs | tr '\n' ' ') | equipo: $(ls equipo | tr '\n' ' ')"
espera 0 "la guía y MODELOS.md ya no están en el proyecto" bash -c '! test -e docs/GUIA-INICIO.md && ! test -e equipo/MODELOS.md'
espera 0 "la wiki está en el submódulo" test -f .bowser-spec-kit-ai/docs/aprobaciones.md
espera 0 "docs/plantillas sigue en el proyecto" test -f docs/plantillas/estado.md
espera 0 "kit verificado" python3 .bowser-spec-kit-ai/scripts/instalar_kit.py --verificar
git add -A; espera 0 "commit de la actualización pasa los hooks" git commit -m "chore: actualiza kit a 1.8.0"
echo "  orquestador: $(grep -c 'bowser-spec-kit-ai/docs' equipo/orquestador.md) referencias a la wiki; en .opencode: $(grep -c 'bowser-spec-kit-ai/docs' .opencode/agents/orquestador.md)"
bash scripts/doctor.sh 2>&1 | grep -E "docs/|sqlc|Go |Node" | sed 's/\x1b\[[0-9;]*m//g; s/^/  doctor:/' | cut -c1-150

echo "== 2. constitución"
echo "- nueva regla a mano" >> .specify/memory/constitution.md; git add -A
espera 1 "editada a mano en un proyecto normal: BLOQUEADA" git commit -m "docs: cambia constitución"
grep -E "✗" "$T/salida.txt" | sed 's/^/      /' | cut -c1-140
git checkout -q HEAD -- .specify/memory/constitution.md
python3 - <<'EOF'
import json
c = json.load(open("equipo/config.json")); c["kit"]["excluir"] = [".specify/memory/constitution.md"]
json.dump(c, open("equipo/config.json", "w"), indent=2, ensure_ascii=False)
EOF
make instalar-kit >/dev/null 2>&1; git add -A; espera 0 "excluirla del kit (commit de la exclusión) pasa" git commit -m "chore: constitución propia del proyecto"
echo "- regla propia del proyecto" >> .specify/memory/constitution.md; git add -A
espera 1 "excluida y modificada SIN aprobación: BLOQUEADA (antes pasaba)" git commit -m "docs: ajusta la constitución"
grep -E "✗" "$T/salida.txt" | sed 's/^/      /' | cut -c1-140
espera 0 "excluida y modificada CON APROBADO_CONSTITUCION=1: pasa" env APROBADO_CONSTITUCION=1 git commit -m "docs: ajusta la constitución"

echo "== 3. constitución que llega por actualización del kit (otro proyecto, sin exclusión)"
mkdir "$T/proy2" && cd "$T/proy2" && git init -q
git submodule add -q "$T/kit" .bowser-spec-kit-ai
make -f .bowser-spec-kit-ai/Makefile instalar-kit >/dev/null
git add -A; espera 0 "instalación limpia de la 1.8.0: commit pasa los hooks" git commit -m "chore: instala kit"
echo "  docs del proyecto nuevo: $(ls docs | tr '\n' ' ')"
(cd "$T/kit" && echo "- regla nueva aprobada en el kit" >> .specify/memory/constitution.md && git add -A && git commit -qm "constitución" --no-verify)
make actualizar-kit >/dev/null 2>&1; git add -A
espera 0 "constitución cambiada por el kit: pasa sin aprobación" git commit -m "chore: actualiza kit"

echo "== 4. mensaje del pre-commit sin python3"
mkdir "$T/sinpy"; for c in git bash sh grep sed awk cat head dirname basename env sort xargs tr cut; do ln -s "$(command -v $c)" "$T/sinpy/$c" 2>/dev/null; done
echo "x" > nota.txt; git add nota.txt
PATH="$T/sinpy" git commit -m "docs: nota" 2>&1 | grep -E "Detalle|python3" | sed 's/^/      /' | cut -c1-150

cd /; rm -rf "$T"
echo "== FIN · fallos: $FALLOS"
exit $FALLOS
