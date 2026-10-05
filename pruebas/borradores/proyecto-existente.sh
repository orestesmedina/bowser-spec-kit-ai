set -uo pipefail
ORIGEN=${ORIGEN:-$(git rev-parse --show-toplevel)}
export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=protocol.file.allow GIT_CONFIG_VALUE_0=always GIT_CONFIG_KEY_1=safe.directory GIT_CONFIG_VALUE_1='*'
export GIT_AUTHOR_NAME=p GIT_AUTHOR_EMAIL=p@example.com GIT_COMMITTER_NAME=p GIT_COMMITTER_EMAIL=p@example.com
T=$(mktemp -d); mkdir "$T/kit"; git -C "$ORIGEN" archive HEAD | tar -x -C "$T/kit"
(cd "$T/kit" && git init -q && git add -A && git commit -qm kit --no-verify)
mkdir -p "$T/proy/.github/workflows" "$T/proy/src" "$T/proy/docs" && cd "$T/proy" && git init -q
printf 'build:\n\t@echo mi build\n' > Makefile
echo "# Mi proyecto" > README.md; echo "mis instrucciones" > AGENTS.md; echo "node_modules/" > .gitignore
echo "name: mi-ci" > .github/workflows/ci.yml; echo "name: deploy" > .github/workflows/deploy.yml
echo "* @yo" > .github/CODEOWNERS; echo "services: {}" > docker-compose.yml; echo "x" > src/app.txt; echo "mi doc" > docs/notas.md
git add -A && git commit -qm "feat: proyecto existente"
git submodule add -q "$T/kit" .bowser-spec-kit-ai
echo "===== make -f .bowser-spec-kit-ai/Makefile instalar-kit"
make -f .bowser-spec-kit-ai/Makefile instalar-kit 2>&1 | sed -n '1,45p'
echo "===== respaldo"; find .kit-respaldo -type f 2>/dev/null | sed 's/^/  /'
echo "===== qué quedó"
echo "Makefile: $(head -1 Makefile)"; echo "AGENTS.md: $(head -1 AGENTS.md)"; echo "ci.yml: $(head -1 .github/workflows/ci.yml)"
echo "deploy.yml: $(cat .github/workflows/deploy.yml)"; echo "CODEOWNERS: $(cat .github/CODEOWNERS)"; echo "compose: $(cat docker-compose.yml)"
echo "README: $(cat README.md)"; echo ".gitignore:"; head -4 .gitignore | sed 's/^/  /'; echo "docs: $(ls docs | tr '\n' ' ')"
echo "===== git status (resumen)"; git status --short | cut -c1-60 | head -40
python3 .bowser-spec-kit-ai/scripts/instalar_kit.py --verificar
git add -A && git commit -qm "chore: instala kit" && echo "commit con hooks: OK"
cd /; rm -rf "$T"
