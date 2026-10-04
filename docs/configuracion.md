# Configuración

- [Introducción](#introducción)
- [equipo/config.json](#equipoconfigjson)
    - [Herramientas activas](#herramientas-activas)
    - [Modelos](#modelos)
    - [Exclusiones del kit](#exclusiones-del-kit)
    - [Costos](#costos)
    - [Aplicar los cambios](#aplicar-los-cambios)
- [Variables de entorno](#variables-de-entorno)
- [CODEOWNERS](#codeowners)
- [Configuración en GitHub](#configuración-en-github)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

Casi todo el kit funciona sin configurar nada. Lo que sí se ajusta en cada proyecto está en cuatro lugares: `equipo/config.json`, el archivo `.env`, `.github/CODEOWNERS` y la configuración del repositorio en GitHub.

Los tres primeros son **semillas**: el kit los copia una vez con valores de ejemplo y después pertenecen al proyecto. Una actualización del kit nunca los sobrescribe.

## equipo/config.json

Es el archivo que lee `make sincronizar` para generar la configuración de cada herramienta.

### Herramientas activas

```json
"herramientas": ["claude", "codex", "opencode"]
```

Deja solo las que use tu equipo. Para cada herramienta de la lista, `make sincronizar` genera sus archivos; las que quites dejan de generarse.

### Modelos

Cada herramienta tiene su bloque dentro de `"modelos"`:

```json
"opencode": {
  "orquestador": "opencode-go/deepseek-v4.1-flash",
  "ligero": "opencode-go/mimo-v2.6-flash",
  "niveles": { "alto": "opencode-go/mimo-v2.6-pro", "medio": "opencode-go/glm-5.3-flash", "bajo": "opencode-go/mimo-v2.6-flash" },
  "agentes": { "dev-backend": "opencode-go/deepseek-v4.1-flash" }
}
```

| Clave | Qué define |
|---|---|
| `orquestador` | El modelo de la sesión principal, la que coordina |
| `niveles` | El modelo para cada nivel de rol: `alto`, `medio` o `bajo` |
| `agentes` | Excepciones: un modelo concreto para un agente concreto |
| `ligero` | Solo OpenCode: el modelo para tareas auxiliares, como generar títulos |
| `agente_principal` | Solo OpenCode: el agente que se abre por defecto |
| `temperatura` | Solo OpenCode: excepciones de temperatura por agente |

El modelo de un agente se decide en este orden: su excepción en `agentes`, luego el modelo de su nivel y, si ambos están vacíos, el modelo de la sesión. Los criterios para elegir, la temperatura y el agente principal están explicados en [Modelos por agente](modelos.md).

`"esfuerzo_codex"` traduce cada nivel al esfuerzo de razonamiento de Codex (`high`, `medium`, `low`).

### Exclusiones del kit

```json
"kit": { "excluir": ["Makefile", ".agents/skills/go-backend/"] }
```

Las rutas de esta lista dejan de ser gestionadas por el kit: el proyecto mantiene su propia versión y las actualizaciones no las tocan. Una carpeta termina en `/`. Cuándo conviene y qué se pierde está en [Personalizar un proyecto](personalizar.md).

### Costos

Opcional. Sirve para fijar a mano el precio de un modelo o cambiar la tarifa de hora pico:

```json
"costos": {
  "precios_manuales": {
    "opencode-go/mi-modelo": { "input": 0.2, "output": 0.8, "cache_read": 0.02, "cache_write": 0 }
  }
}
```

Los precios van en dólares por millón de tokens. El detalle está en [Costos de IA](costos.md).

### Aplicar los cambios

Después de editar `equipo/config.json`:

```bash
make sincronizar   # regenera la configuración de cada herramienta
make modelos       # muestra qué modelo usa cada agente y de dónde sale
```

Reinicia el agente de código para que tome la configuración nueva, e incluye en el commit tanto `config.json` como los archivos generados.

> [!NOTE]
> Cuando el kit cambia su recomendación de modelos, `make actualizar-kit` lo avisa pero no modifica tu `config.json`. Para adoptarla: `make actualizar-modelos`, que muestra las diferencias y pide confirmación.

## Variables de entorno

`.env.example` lista las variables que necesita el proyecto, sin valores reales, y sí se sube a git. Cada persona crea su `.env` a partir de él:

```bash
cp .env.example .env
```

Las variables que usa el kit:

| Variable | Para qué |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Credenciales y nombre de la base de datos local |
| `POSTGRES_PORT` | Puerto de PostgreSQL en tu máquina. Cámbialo si el 5432 está ocupado |
| `DATABASE_URL` | La dirección completa de la base de datos; la usa `make db-migrate` |
| `DATABASE_URL_TEST` | La base de datos de las pruebas de integración |
| `VITE_API_URL` | La dirección del backend, para el frontend |

Cuando una funcionalidad necesita una variable nueva, se agrega a `.env.example` sin su valor real. Eso lo hace el rol `devops`.

> [!WARNING]
> `.env` nunca se sube a git y nunca se pega en el chat del agente. Los [hooks de git](hooks-de-git.md) bloquean el commit, y en Claude Code el agente ni siquiera puede leerlo.

## CODEOWNERS

`.github/CODEOWNERS` le dice a GitHub quién debe aprobar un Pull Request según los archivos que toca. El kit lo trae apuntando a las reglas y a los agentes:

```
/.specify/memory/constitution.md   @tu-org/direccion-tecnica
/AGENTS.md                         @tu-org/direccion-tecnica
/equipo/                           @tu-org/direccion-tecnica
/.agents/skills/                   @tu-org/direccion-tecnica
/.github/workflows/                @tu-org/direccion-tecnica
```

Reemplaza `@tu-org/direccion-tecnica` por el usuario o el equipo de GitHub que decide sobre las reglas en tu organización. Así nadie cambia la constitución ni las instrucciones de los agentes sin esa aprobación.

## Configuración en GitHub

Tres ajustes que se hacen en el repositorio, no en archivos:

| Ajuste | Dónde | Para qué |
|---|---|---|
| Proteger la rama `main` y exigir la aprobación de Code Owners | Settings → Branches | Para que `CODEOWNERS` tenga efecto y nada entre sin pasar por la integración continua |
| Secreto `KIT_TOKEN` | Settings → Secrets and variables → Actions → Secrets | Solo si tu copia del kit es un repositorio privado: un token con permiso de lectura, para que la integración continua pueda descargar el submódulo |
| Variables de versión | Settings → Secrets and variables → Actions → Variables | Opcional. Cambian la versión de una herramienta en la integración continua sin tocar `ci.yml`. Ver [Integración continua](integracion-continua.md#cambiar-la-versión-de-una-herramienta) |

## Siguientes pasos

- [Modelos por agente](modelos.md): cómo elegir el modelo de cada rol.
- [Personalizar un proyecto](personalizar.md): versiones propias de archivos del kit.
- [Cambiar de herramienta](cambiar-de-herramienta.md): pasar de un agente de código a otro.
