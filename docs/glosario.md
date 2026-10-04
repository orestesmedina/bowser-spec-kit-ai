# Glosario

Los términos que aparecen en esta documentación, en orden alfabético. Cada uno enlaza a la página que lo explica a fondo.

**Agente de código.** El programa de IA que lee y escribe el código del proyecto: Claude Code, Codex u OpenCode. Ver [Instalación](instalacion.md#el-agente-de-código).

**Aprobación.** El momento en que una persona se hace responsable de lo que sigue. Hay cuatro: especificación, plan, Pull Request y despliegue. Ver [Aprobaciones](aprobaciones.md).

**Archivo generado.** Un archivo que produce un comando a partir de otro, y que nunca se edita a mano. Hay de dos tipos: la configuración de los agentes (`make sincronizar`) y el código generado (`make generar`). Ver [Una fuente, varias herramientas](una-fuente-varias-herramientas.md) y [Cobertura y código generado](cobertura-y-codigo-generado.md).

**Archivo gestionado.** Un archivo que viene del kit y se reemplaza en cada actualización. No se edita en el proyecto. Ver [El kit como submódulo](submodulo.md).

**CI (integración continua).** Las pruebas y los controles automáticos que GitHub ejecuta en cada Pull Request. Ver [Integración continua](integracion-continua.md).

**Ciclo de corrección.** Una vuelta de "los revisores rechazan, el desarrollador corrige". Tras tres sin éxito, el orquestador se detiene y pide ayuda. Ver [Construir una funcionalidad](funcionalidad.md#paso-7-validación).

**Cobertura.** El porcentaje del código que se ejecuta cuando corren las pruebas. El kit exige 80 % en la capa de servicio. Ver [Cobertura y código generado](cobertura-y-codigo-generado.md).

**CODEOWNERS.** El archivo que le dice a GitHub quién debe aprobar un cambio según los archivos que toca. Ver [Configuración](configuracion.md#codeowners).

**Constitución.** Las reglas no negociables que todo el código debe cumplir. Ver [La constitución](la-constitucion.md).

**Contrato de la API.** El archivo `openapi.yaml`, que describe qué le ofrece el backend al frontend. Se escribe antes que el código.

**Conventional Commits.** El formato de los mensajes de commit: `feat:`, `fix:`, `docs:`, etc. Ver [Hooks de git](hooks-de-git.md#el-mensaje-commit-msg).

**costos.json.** El archivo de cada funcionalidad con los tokens y el costo equivalente de IA por agente y modelo. Ver [Costos de IA](costos.md).

**Criterio de aceptación.** Una condición verificable que debe cumplirse para dar algo por terminado, en formato Dado / Cuando / Entonces.

**Dirección técnica.** La persona o el grupo que decide sobre las reglas del equipo: la constitución, los roles y las skills. En un equipo pequeño puede ser una sola persona.

**Especificación (spec).** El documento que describe qué se construye y por qué, sin hablar de tecnología. Ver [Desarrollo guiado por especificaciones](sdd.md).

**estado.md.** El archivo de cada funcionalidad donde el orquestador anota la fase, las aprobaciones, los hallazgos, las decisiones y el próximo paso. Ver [Retomar el trabajo](retomar.md).

**Fase.** Cada uno de los nueve pasos del proceso, de "especificar" a "entregar". Ver [Desarrollo guiado por especificaciones](sdd.md#las-nueve-fases).

**Hook de git.** Un control automático que se ejecuta en cada commit. Ver [Hooks de git](hooks-de-git.md).

**Hook del agente.** Un control que Claude Code ejecuta cuando el agente intenta editar un archivo. Ver [Hooks del agente](hooks-del-agente.md).

**Kit.** Este conjunto de instrucciones, roles, skills, scripts y controles, que se instala en cada proyecto.

**Manifiesto.** El archivo `.kit-manifest.json`: la lista de los archivos del proyecto que vienen del kit, con su versión. Ver [El kit como submódulo](submodulo.md#el-manifiesto).

**Migración.** Un archivo versionado que cambia el esquema de la base de datos. Una vez aplicada, no se modifica.

**MVP.** La versión más pequeña del producto que resuelve el problema. Ver [De la idea al roadmap](idea-al-roadmap.md).

**Nivel.** La capacidad que necesita un rol: `alto`, `medio` o `bajo`. Decide qué modelo usa. Ver [Modelos por agente](modelos.md).

**Orquestador.** El agente principal, con el que hablas. Coordina a los especialistas y lleva el estado. Ver [El orquestador](el-orquestador.md).

**Plan.** El documento que describe cómo se construye una funcionalidad: arquitectura, datos y API.

**PR (Pull Request).** La solicitud para integrar cambios a la rama principal.

**Puerta de aprobación.** Un punto del proceso donde los agentes se detienen hasta que una persona aprueba. Ver [Aprobaciones](aprobaciones.md).

**Roadmap.** La lista ordenada de funcionalidades del producto, con el estado de cada una. Ver [De la idea al roadmap](idea-al-roadmap.md).

**Rol.** La definición de un especialista: qué hace, qué puede tocar y qué entrega. Ver [Roles](roles.md).

**Semilla.** Un archivo que el kit copia una sola vez y que después pertenece al proyecto. Ver [El kit como submódulo](submodulo.md#archivos-gestionados-y-semillas).

**Skill.** Un conjunto de instrucciones reutilizables: las convenciones de una tecnología o el paso a paso de un flujo. Ver [Skills](skills.md).

**Spec Kit.** La herramienta de GitHub que estructura el proceso en fases y aporta las plantillas de los documentos. Ver [Desarrollo guiado por especificaciones](sdd.md#spec-kit).

**Stack.** El conjunto de tecnologías del proyecto: React y TypeScript, Go y PostgreSQL.

**Subagente.** Un agente especializado en un rol, que el orquestador lanza para una tarea concreta. Ver [El equipo de agentes](equipo-de-agentes.md).

**Submódulo.** Un repositorio de git dentro de otro, fijado en una versión. Así vive el kit dentro de cada proyecto. Ver [El kit como submódulo](submodulo.md).

**Temperatura.** Cuánto azar usa un modelo al responder. Baja da respuestas consistentes; alta, más variadas. Ver [Modelos por agente](modelos.md#temperatura).

**Token.** La unidad en que se mide lo que un modelo lee y escribe. Es la base del costo. Ver [Costos de IA](costos.md).

**WSL.** El Linux que corre dentro de Windows, y donde se trabaja con el kit en ese sistema. Ver [Windows y WSL](windows-wsl.md).
