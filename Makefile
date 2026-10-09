# Makefile del kit. En los proyectos lo gestiona `make instalar-kit`: no lo edites ahí.
# Para agregar comandos propios de un proyecto, créalos en proyecto.mk (se incluye al final).

.PHONY: help estado costos novedades doctor profile skills modelos actualizar-modelos sincronizar verificar-agentes instalar-hooks instalar-kit actualizar-kit verificar-kit up down db-migrate generar verificar-generados test test-backend test-frontend cobertura lint security ci

# Carpeta del submódulo del kit: la del `make -f <carpeta>/Makefile` usado, o la guardada al instalar,
# o el nombre por defecto. Se puede forzar con `make ... KIT=<carpeta>`.
KIT_INVOCADO := $(patsubst %/,%,$(filter-out ./,$(dir $(firstword $(MAKEFILE_LIST)))))
KIT_GUARDADO := $(shell bash scripts/ruta-kit.sh 2>/dev/null)
KIT ?= $(or $(KIT_INVOCADO),$(KIT_GUARDADO),.bowser-spec-kit-ai)
FORZAR ?=

help: ## Muestra los comandos disponibles
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

instalar-kit: ## Copia el kit (submódulo) a la raíz, regenera agentes y activa hooks
	@test -f $(KIT)/scripts/instalar_kit.py || { echo "No existe $(KIT)/. Agrega el submódulo (git submodule add <url> $(KIT)) o ejecuta: git submodule update --init"; exit 1; }
	@PREVIA=$$(python3 $(KIT)/scripts/instalar_kit.py --version-instalada) && \
	NOVEDADES_AL_FINAL=1 python3 $(KIT)/scripts/instalar_kit.py $(if $(FORZAR),--forzar,) && \
	python3 scripts/sincronizar.py && \
	git config core.hooksPath .githooks && \
	{ python3 scripts/actualizar_modelos.py --comprobar || true; } && \
	python3 $(KIT)/scripts/instalar_kit.py --resumen-novedades "$$PREVIA" && \
	echo "" && echo "Listo. Revisa los cambios con 'git status' y haz commit (incluye .kit-manifest.json)."

actualizar-kit: ## Trae la última versión del kit y la instala
	git submodule update --init --remote $(KIT)
	@$(MAKE) --no-print-directory instalar-kit

novedades: ## Historial de cambios del kit (DESDE=1.4.0 para ver desde una versión)
	@python3 $(KIT)/scripts/instalar_kit.py --novedades $(if $(DESDE),--desde $(DESDE),)

verificar-kit: ## Comprueba que la raíz coincida con la versión del submódulo del kit
	python3 $(KIT)/scripts/instalar_kit.py --verificar

estado: ## Por dónde vamos: roadmap, fase, aprobaciones, tareas y próximo paso
	@python3 scripts/estado.py $(if $(TODO),--todo,)

costos: ## Costo de IA de la tarea actual (TODO=1 proyecto, CERRAR=1 cierra, PRECIOS=hoy cotiza)
	@python3 scripts/costos.py $(if $(TODO),--todo,) $(if $(CERRAR),--cerrar,) $(if $(filter hoy,$(PRECIOS)),--hoy,)

doctor: ## Verifica que el entorno tenga todo lo necesario
	@bash scripts/doctor.sh

sincronizar: ## Genera la configuración de Claude Code, Codex y OpenCode desde equipo/
	python3 scripts/sincronizar.py

modelos: ## Muestra qué modelo usa cada agente en cada herramienta
	@python3 scripts/sincronizar.py --modelos

actualizar-modelos: ## Aplica al proyecto los modelos recomendados por el kit (muestra los cambios antes)
	@python3 scripts/actualizar_modelos.py $(if $(SI),--si,)

verificar-agentes: ## Comprueba que la configuración generada esté al día
	python3 scripts/sincronizar.py --verificar

instalar-hooks: ## Activa los hooks de git del proyecto (una vez por clon)
	git config core.hooksPath .githooks
	chmod +x .githooks/* equipo/adaptadores/claude/hooks/*.sh
	@echo "Hooks de git activados."

up: ## Levanta el entorno local (PostgreSQL y servicios)
	docker compose up -d

down: ## Detiene el entorno local (conserva los datos)
	docker compose down

db-migrate: ## Aplica las migraciones pendientes
	migrate -path backend/migrations -database "$$DATABASE_URL" up

profile: ## Muestra y valida el perfil del proyecto (DETECTAR=1: qué tecnologías encuentra en el proyecto)
	@python3 scripts/perfil.py $(if $(DETECTAR),--detectar,)

skills: ## Catálogo de skills de tecnología del kit: madurez de cada una y cuáles tiene el proyecto
	@python3 scripts/catalogo.py

# Con perfil (equipo/perfil.json), cada comando ejecuta el verbo que el proyecto declaró para cada parte
# (PARTE=nombre lo limita a una). Sin perfil, se comportan como siempre: Go en backend/ y React en frontend/.
CON_PERFIL := $(wildcard equipo/perfil.json)
VERBO = python3 scripts/verbos.py $(1) $(if $(PARTE),--parte $(PARTE),)

generar: ## Regenera el código generado
ifdef CON_PERFIL
	@$(call VERBO,generar)
else
	@bash scripts/generar.sh
endif

verificar-generados: ## Regenera y falla si el código generado no estaba al día
ifdef CON_PERFIL
	@$(call VERBO,generar --verificar)
else
	@bash scripts/generar.sh --verificar
endif

test: ## Ejecuta todas las pruebas
ifdef CON_PERFIL
	@$(call VERBO,probar)
else
	@$(MAKE) --no-print-directory test-backend test-frontend
endif

test-backend: ## Pruebas del backend (unitarias + integración). Solo sin perfil
	cd backend && go test ./... && go test -tags=integration ./...

test-frontend: ## Pruebas del frontend. Solo sin perfil
	cd frontend && npm test -- --run

cobertura: ## Cobertura de pruebas (falla bajo el mínimo del proyecto)
ifdef CON_PERFIL
	@$(call VERBO,cobertura)
else
	cd backend && go test -coverprofile=coverage.out ./...
	@python3 scripts/cobertura.py backend/coverage.out
endif

lint: ## Formato y análisis estático
ifdef CON_PERFIL
	@$(call VERBO,formato revisar)
else
	cd backend && gofmt -l . && go vet ./... && golangci-lint run
	cd frontend && npm run lint && npm run typecheck
endif

security: ## Auditoría de dependencias
ifdef CON_PERFIL
	@$(call VERBO,auditar)
else
	cd backend && govulncheck ./...
	cd frontend && npm audit --audit-level=high
endif

ci: $(if $(CON_PERFIL),,lint verificar-generados test cobertura security) ## Lo mismo que corre en CI (con perfil, termina con un resumen)
ifdef CON_PERFIL
	@$(call VERBO,formato revisar generar probar cobertura auditar --verificar --resumen)
endif

# Comandos propios del proyecto (opcional; no lo gestiona el kit).
-include proyecto.mk

# Comandos para mantener el kit (solo existe en el repositorio del kit; no se copia a los proyectos).
-include kit.mk
