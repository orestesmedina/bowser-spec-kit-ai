# Comandos para mantener el kit. Este archivo solo existe en el repositorio del kit: no se copia a los
# proyectos, así que ahí estos comandos no existen. El Makefile lo incluye si lo encuentra.

.PHONY: test-kit

test-kit: ## Pruebas automáticas del kit (SOLO=texto filtra, DESDE=v1.7.0 elige la versión anterior, ESTRICTO=1 para CI)
	@python3 pruebas/ejecutar.py $(if $(SOLO),--solo "$(SOLO)",) $(if $(DESDE),--desde $(DESDE),) $(if $(ESTRICTO),--estricto,) $(if $(CONSERVAR),--conservar,)
