# Comandos para mantener el kit. Este archivo solo existe en el repositorio del kit: no se copia a los
# proyectos, así que ahí estos comandos no existen. El Makefile lo incluye si lo encuentra.

.PHONY: test-kit

# Los nombres anteriores de las opciones (en español) se siguen aceptando.
ONLY ?= $(SOLO)
STRICT ?= $(ESTRICTO)
KEEP ?= $(CONSERVAR)

test-kit: ## Pruebas automáticas del kit (ONLY=texto filtra, SINCE=v1.7.0 elige la versión anterior, STRICT=1 para CI, KEEP=1 conserva la carpeta temporal)
	@python3 pruebas/ejecutar.py $(if $(ONLY),--solo "$(ONLY)",) $(if $(SINCE),--desde $(SINCE),) $(if $(STRICT),--estricto,) $(if $(KEEP),--conservar,)
