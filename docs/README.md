# Documentación de bowser-spec-kit-ai

Un kit para que un equipo de agentes de IA construya software con **React + TypeScript, Go y PostgreSQL**, siguiendo un proceso en el que todo empieza por escrito y las personas aprueban en los puntos clave. Funciona con Claude Code, Codex y OpenCode.

Esta documentación está pensada para leerse de arriba hacia abajo la primera vez y para consultarse por tema después. Cada página explica **qué es** una pieza del kit, **para qué sirve**, **cuándo se usa** y **qué hacer cuando falla**.

> [!TIP]
> **¿Por dónde empiezo?** Si quieres entender la idea antes de instalar nada, lee [Desarrollo guiado por especificaciones](sdd.md) y [El equipo de agentes](equipo-de-agentes.md). Si prefieres empezar con las manos, ve a [Instalación](instalacion.md).

## Prólogo

- [Novedades de cada versión](../CHANGELOG.md)
- [Guía de actualización](actualizacion.md)
- [Cómo contribuir](contribuir.md)
- [Hoja de ruta](../HOJA-DE-RUTA.md)

## Primeros pasos

- [Instalación](instalacion.md)
- [Windows y WSL](windows-wsl.md)
- [Crear un proyecto nuevo](proyecto-nuevo.md)
- [Integrar el kit en un proyecto existente](proyecto-existente.md)
- [Unirse a un proyecto](unirse-a-un-proyecto.md)
- [Estructura de carpetas](estructura.md)
- [Configuración](configuracion.md)

## Conceptos

- [Desarrollo guiado por especificaciones](sdd.md)
- [El equipo de agentes](equipo-de-agentes.md)
- [El orquestador](el-orquestador.md)
- [La constitución](la-constitucion.md)
- [Una fuente, varias herramientas](una-fuente-varias-herramientas.md)
- [El kit como submódulo](submodulo.md)

## El flujo de trabajo

- [De la idea al roadmap](idea-al-roadmap.md)
- [Construir una funcionalidad](funcionalidad.md)
- [Aprobaciones](aprobaciones.md)
- [Corregir un bug](bugs.md)
- [Cambios pequeños](cambios-pequenos.md)
- [Retomar el trabajo](retomar.md)

## Profundizando

- [Roles](roles.md)
- [Skills](skills.md)
- [Modelos por agente](modelos.md)
- [Costos de IA](costos.md)
- [Cambiar de herramienta](cambiar-de-herramienta.md)
- [El perfil del proyecto](perfil-del-proyecto.md)
- [Personalizar un proyecto](personalizar.md)

## Controles

- [Capas de control](capas-de-control.md)
- [Hooks de git](hooks-de-git.md)
- [Hooks del agente](hooks-del-agente.md)
- [Integración continua](integracion-continua.md)
- [Cobertura y código generado](cobertura-y-codigo-generado.md)

## Referencia

- [Comandos](comandos.md)
- [Problemas comunes](problemas-comunes.md)
- [Reglas de oro](reglas-de-oro.md)
- [Glosario](glosario.md)

---

**Dónde leer esta documentación.** En GitHub, en la carpeta `docs/` del repositorio del kit. Dentro de un proyecto que usa el kit, en `.bowser-spec-kit-ai/docs/`: ahí está siempre la versión que corresponde al kit que ese proyecto tiene instalado.
