# Unirse a un proyecto

- [Introducción](#introducción)
- [Accesos que necesitas](#accesos-que-necesitas)
- [Clonar y preparar el proyecto](#clonar-y-preparar-el-proyecto)
- [Conectarte a la base de datos local](#conectarte-a-la-base-de-datos-local)
- [Qué leer primero](#qué-leer-primero)
- [Tu primera semana](#tu-primera-semana)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Esta página es para quien llega a un proyecto que **ya usa el kit**. Es el caso más común: el kit ya está instalado en el repositorio, y lo que falta es preparar tu copia local.

## Accesos que necesitas

Pídelos a quien lidera el proyecto antes de empezar:

- [ ] Cuenta de **GitHub** con acceso al repositorio del proyecto.
- [ ] Acceso al **agente de código** que usa el equipo: una suscripción o clave de Claude Code, Codex u OpenCode. Cuál se usa está en `"herramientas"` dentro de `equipo/config.json`.
- [ ] Los valores del archivo `.env` del proyecto. Se entregan por un gestor de contraseñas, **nunca** por chat ni por correo.
- [ ] Acceso al gestor de tareas del equipo y a su canal de comunicación.

## Clonar y preparar el proyecto

Con tu máquina lista según la página de [Instalación](instalacion.md):

```bash
git clone --recursive git@github.com:<organizacion>/<proyecto>.git
cd <proyecto>

make instalar-hooks          # activa los controles de git (obligatorio)
cp .env.example .env         # y completa los valores que te entregaron
make up                      # levanta los servicios del proyecto (su base de datos, por ejemplo)
make doctor                  # verifica que todo esté listo
```

Qué hace cada paso:

| Comando | Por qué hace falta |
|---|---|
| `git clone --recursive` | El kit vive en un submódulo (`.bowser-spec-kit-ai/`). Sin `--recursive` esa carpeta queda vacía. Si ya clonaste sin esa opción: `git submodule update --init` |
| `make instalar-hooks` | La activación de los [hooks de git](hooks-de-git.md) no viaja con el repositorio: cada persona la hace una vez por clon. Sin ella, tus commits no pasan por ningún control local |
| `cp .env.example .env` | `.env` tiene los valores reales (contraseñas, direcciones) y nunca se sube a git |
| `make up` | Levanta con Docker los servicios que el proyecto definió en su archivo de Docker Compose. Si responde "todavía no tiene entorno local", el proyecto aún no lo creó: sáltate este paso |
| `make doctor` | Comprueba todo lo anterior. Debe terminar con "Todo listo para trabajar" |

> [!WARNING]
> Ajusta las contraseñas en `.env` **antes** del primer `make up`. Los motores de base de datos (PostgreSQL y MySQL, entre otros) solo las toman al crear la base; si las cambias después, hay que recrearla con `docker compose down -v && make up`, que borra los datos locales.

## Conectarte a la base de datos local

Qué base de datos hay, en qué puerto y con qué usuario lo define cada proyecto: los valores están en tu `.env` y el servicio, en el archivo de Docker Compose de la raíz. Con ellos te conectas desde un cliente como DBeaver, a `localhost`.

Para ver qué servicios están arriba:

```bash
docker compose ps
```

## Qué leer primero

En este orden:

1. El `README.md` del proyecto.
2. `.specify/memory/constitution.md`: las reglas que todo el código debe cumplir. Ver [La constitución](la-constitucion.md).
3. `docs/producto/roadmap.md`: qué funcionalidades tiene el producto y en qué estado está cada una.
4. La carpeta `specs/`, empezando por la funcionalidad más reciente, para ver cómo se ha trabajado.

Después ejecuta `make estado`: muestra qué está en curso y cuál es el próximo paso.

> [!NOTE]
> No edites la carpeta `.bowser-spec-kit-ai/` ni los archivos que vienen del kit (están listados en `.kit-manifest.json`). El hook de git y la integración continua lo detectan. Si algo del kit debería cambiar, propónlo a quien mantiene el kit en tu equipo.

## Tu primera semana

**Día 1**

- [ ] Recibir todos los accesos.
- [ ] Instalar el entorno y clonar el proyecto, con `make doctor` en verde.
- [ ] Leer la constitución y [Cómo funciona el proceso](sdd.md).

**Día 2**

- [ ] Leer las especificaciones y los planes de dos funcionalidades ya terminadas, con su `estado.md`.
- [ ] Ejecutar `make estado` y entender el roadmap del proyecto.
- [ ] Leer la página de [Roles](roles.md).
- [ ] Hacer un [cambio pequeño](cambios-pequenos.md) y abrir un Pull Request acompañado de alguien con experiencia.

**Días 3 a 5**

- [ ] Desarrollar una funcionalidad de práctica completa, con el flujo de [Construir una funcionalidad](funcionalidad.md), en una rama que no se integrará.
- [ ] Revisar tus aprobaciones de especificación y de plan con alguien con experiencia.
- [ ] Anotar las dudas y las fricciones que encuentres, y compartirlas: el kit y esta documentación mejoran con eso.

## Siguientes pasos

- [Desarrollo guiado por especificaciones](sdd.md): el proceso completo, explicado.
- [Construir una funcionalidad](funcionalidad.md): tu trabajo de todos los días.
- [Reglas de oro](reglas-de-oro.md): lo que nunca se hace.
