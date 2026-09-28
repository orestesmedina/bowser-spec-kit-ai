.PHONY: help doctor modelos sincronizar verificar-agentes instalar-hooks up down db-migrate test test-backend test-frontend lint security ci

help: ## Muestra los comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

doctor: ## Verifica que el entorno tenga todo lo necesario
	@bash scripts/doctor.sh

sincronizar: ## Genera la configuración de Claude Code, Codex y OpenCode desde equipo/
	python3 scripts/sincronizar.py

modelos: ## Muestra qué modelo usa cada agente en cada herramienta
	@python3 scripts/sincronizar.py --modelos

verificar-agentes: ## Comprueba que la configuración generada esté al día
	python3 scripts/sincronizar.py --verificar

instalar-hooks: ## Activa los hooks de git del proyecto (una vez por clon)
	git config core.hooksPath .githooks
	chmod +x .githooks/*
	@echo "Hooks de git activados."

up: ## Levanta el entorno local (PostgreSQL y servicios)
	docker compose up -d

down: ## Detiene el entorno local (conserva los datos)
	docker compose down

db-migrate: ## Aplica las migraciones pendientes
	migrate -path backend/migrations -database "$$DATABASE_URL" up

test: test-backend test-frontend ## Ejecuta todas las pruebas

test-backend: ## Pruebas del backend (unitarias + integración)
	cd backend && go test ./... && go test -tags=integration ./...

test-frontend: ## Pruebas del frontend
	cd frontend && npm test -- --run

lint: ## Linters de backend y frontend
	cd backend && gofmt -l . && go vet ./... && golangci-lint run
	cd frontend && npm run lint && npm run typecheck

security: ## Auditoría de dependencias
	cd backend && govulncheck ./...
	cd frontend && npm audit --audit-level=high

ci: lint test security ## Lo mismo que corre en CI
