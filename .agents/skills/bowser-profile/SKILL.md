---
name: bowser-profile
description: "Crea o actualiza el perfil del proyecto (partes, tecnologías y comandos) mirando el código, y lo propone para aprobación."
---
<!-- GENERADO por scripts/sincronizar.py desde equipo/comandos/profile.md. No editar: cambia la fuente y ejecuta `make sincronizar`. -->

El perfil (`equipo/perfil.json`) le dice al kit qué partes tiene el proyecto, en qué carpeta está cada una y qué comando ejecuta cada verbo (formato, revisar, probar, cobertura, auditar, generar). Aplica la skill `perfil-proyecto`.

Si la persona escribió "ver", ejecuta `make profile`, explica el resultado en lenguaje simple y termina.

En cualquier otro caso:

1. Ejecuta `make profile DETECTAR=1` (solo lee: muestra en JSON lo que encontró en el proyecto) y, si ya hay perfil, `make profile`.
2. Delega en el `arquitecto` la redacción del perfil, pasándole esa salida. Si tu herramienta no puede lanzar subagentes, asume tú ese rol.
3. Lo que no se pueda deducir del código (cómo se prueba, qué versión se usa, si una carpeta es de terceros) **se pregunta a la persona**. Si el proyecto no tiene algo todavía (por ejemplo, pruebas), el verbo queda en `null`: no inventes un comando.
4. Muestra la propuesta en lenguaje simple: qué partes encontraste, con qué tecnología, qué agente trabaja cada una, qué comando corre cada verbo y cuáles quedan sin definir. Espera la aprobación explícita de la persona.
5. Con su "sí", escribe `equipo/perfil.json` y ejecuta `make profile`. Si marca errores, corrígelos y vuelve a mostrar el resultado.
6. Dile a la persona que el commit del perfil lo confirma ella, con `APROBADO_PERFIL=1 git commit ...`. Nunca uses esa variable por tu cuenta: los comandos del perfil se ejecutan en su máquina y en la integración continua.

Si la persona escribió algo junto a `$bowser-profile`, esos son los argumentos: [vacío para crear o actualizar; "ver" solo lo muestra].
