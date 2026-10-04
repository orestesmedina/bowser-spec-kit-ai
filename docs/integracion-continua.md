# Integración continua

- [Introducción](#introducción)
- [Para qué sirve en este kit](#para-qué-sirve-en-este-kit)
- [Cuándo se ejecuta](#cuándo-se-ejecuta)
- [Qué comprueba](#qué-comprueba)
    - [Kit y configuración de agentes](#kit-y-configuración-de-agentes)
    - [Migraciones y constitución](#migraciones-y-constitución)
    - [Backend](#backend)
    - [Frontend](#frontend)
    - [Búsqueda de secretos](#búsqueda-de-secretos)
- [Ejecutar lo mismo en tu máquina](#ejecutar-lo-mismo-en-tu-máquina)
- [Cuando falla](#cuando-falla)
- [Cambiar la versión de una herramienta](#cambiar-la-versión-de-una-herramienta)
- [Lo que no hace](#lo-que-no-hace)
- [Siguientes pasos](#siguientes-pasos)

## Introducción

La integración continua (CI) es un conjunto de comprobaciones que **GitHub ejecuta por su cuenta** cada vez que alguien propone un cambio. Si alguna falla, el Pull Request queda marcado en rojo y no se puede integrar.

En el kit vive en un solo archivo: `.github/workflows/ci.yml`.

## Para qué sirve en este kit

Es la única capa de control que **no se puede saltar**. Los [hooks de git](hooks-de-git.md) corren en la máquina de quien hace el cambio, y esa persona (o ese agente) puede no tenerlos activos, o evitarlos con `--no-verify`. La integración continua corre en GitHub, fuera de su alcance.

Por eso repite lo que ya revisaron los hooks, y agrega lo que los hooks no hacen por ser lento: ejecutar todas las pruebas contra una base de datos real, medir la cobertura y buscar vulnerabilidades.

Para que tenga efecto, la rama principal debe estar protegida en GitHub, de modo que nada entre sin pasar por ella. Ver [Configuración](configuracion.md#configuración-en-github).

## Cuándo se ejecuta

- En cada **Pull Request**, y cada vez que se le agregan commits.
- En cada cambio que llega a la **rama principal**.

Si llega un commit nuevo mientras una ejecución anterior de la misma rama sigue en curso, la anterior se cancela.

## Qué comprueba

El trabajo se divide en cinco grupos, que corren en paralelo.

### Kit y configuración de agentes

| Comprobación | Qué detecta |
|---|---|
| Los archivos del kit coinciden con su submódulo | Que alguien editó en el proyecto un archivo que viene del kit |
| La configuración de agentes está al día | Que cambió un rol o una skill y no se ejecutó `make sincronizar` |

### Migraciones y constitución

Solo en Pull Requests, porque compara contra la rama de destino.

| Comprobación | Qué detecta |
|---|---|
| Las migraciones existentes no se modifican | Que se editó, renombró o borró una migración ya versionada. **Falla** |
| Aviso si cambia la constitución | Que el Pull Request toca las reglas. **Avisa**, y la aprobación la exige `CODEOWNERS` |

### Backend

Solo si existe `backend/go.mod`. Levanta un PostgreSQL real para las pruebas.

| Paso | Qué detecta |
|---|---|
| Formato | Código Go sin formatear |
| `go vet` | Errores que el compilador no marca |
| `golangci-lint` | Problemas de calidad |
| Código generado al día | Que cambió una consulta y no se regeneró el código de sqlc |
| Migraciones | Que las migraciones no se aplican en una base de datos vacía |
| Pruebas unitarias y de integración | Pruebas que fallan. Incluye la detección de condiciones de carrera |
| Cobertura de la capa de servicio | Menos del 80 % que exige la constitución |
| Vulnerabilidades | Dependencias de Go con fallos de seguridad conocidos |

La versión de Go sale de `backend/go.mod`, así que la integración continua usa la misma que el proyecto.

### Frontend

Solo si existe `frontend/package.json`.

| Paso | Qué detecta |
|---|---|
| Tipos de la API al día | Que cambió el contrato y no se regeneraron los tipos |
| Lint | Problemas de calidad |
| Comprobación de tipos | Errores de TypeScript |
| Pruebas | Pruebas que fallan |
| Compilación | Que el frontend no compila |
| Vulnerabilidades | Dependencias con fallos de seguridad de nivel alto o crítico |

Los dos controles de código generado y el de cobertura están explicados en [Cobertura y código generado](cobertura-y-codigo-generado.md).

### Búsqueda de secretos

Revisa todo el historial del cambio con `gitleaks`, en busca de claves, tokens o contraseñas. Corre siempre, aunque el proyecto no tenga backend ni frontend.

## Ejecutar lo mismo en tu máquina

```bash
make ci
```

Ejecuta los linters, la verificación del código generado, las pruebas, la cobertura y la auditoría de dependencias. Conviene correrlo antes de abrir un Pull Request: es más rápido enterarse en tu máquina que esperar a GitHub.

Cada parte también se puede ejecutar por separado. Ver [Comandos](comandos.md#calidad-y-pruebas).

> [!NOTE]
> `make ci` necesita las mismas herramientas que la integración continua, en las mismas versiones. Están en la página de [Instalación](instalacion.md#herramientas-de-go). Con otras versiones, algo puede pasar en tu máquina y fallar en GitHub.

## Cuando falla

1. **Abre la ejecución en GitHub** (pestaña "Checks" del Pull Request) y mira qué paso falló. El nombre del paso ya dice mucho.
2. **Reprodúcelo en tu máquina** con el comando correspondiente.
3. **Corrige la causa.** Si el cambio lo hizo un agente, pásale el error completo.

| El paso que falló | Comando para reproducirlo | Solución habitual |
|---|---|---|
| Archivos del kit | `make verificar-kit` | Revertir el cambio al archivo del kit, o `make instalar-kit` |
| Configuración de agentes | `make verificar-agentes` | `make sincronizar` |
| Formato, `go vet`, `golangci-lint`, lint del frontend | `make lint` | Corregir lo que indique |
| Código generado, tipos de la API | `make verificar-generados` | `make generar` |
| Pruebas | `make test` | Corregir el código. Nunca la prueba, salvo que la prueba esté mal |
| Cobertura | `make cobertura` | Agregar pruebas a la capa de servicio |
| Vulnerabilidades | `make security` | Actualizar la dependencia afectada |
| Secretos | `gitleaks detect -v` | Quitar el secreto **y cambiarlo**: ya quedó expuesto |
| No puede descargar el submódulo | — | La copia del kit es privada: configura `KIT_TOKEN` |

> [!WARNING]
> Un secreto que llegó a GitHub está comprometido aunque después se borre del código, porque sigue en el historial. Borrarlo no alcanza: hay que cambiar la contraseña o la clave.

## Cambiar la versión de una herramienta

Las versiones de las herramientas están fijadas en `ci.yml`, para que el resultado sea el mismo hoy y dentro de seis meses. Como ese archivo viene del kit, no se edita en el proyecto.

Si tu proyecto necesita otra versión antes de que el kit se actualice (el caso típico: adoptas una versión nueva de Go y el linter fijado no la soporta), se cambia con una **variable del repositorio**:

1. En GitHub: **Settings → Secrets and variables → Actions → Variables**.
2. Crea una variable con uno de estos nombres:

| Variable | Qué fija | Valor por defecto |
|---|---|---|
| `GOLANGCI_LINT_VERSION` | El linter de Go | `v2.14.0` |
| `MIGRATE_VERSION` | La herramienta de migraciones | `v4.20.1` |
| `GOVULNCHECK_VERSION` | El analizador de vulnerabilidades de Go | `v1.8.0` |
| `SQLC_VERSION` | El generador de consultas | `v1.31.1` |
| `NODE_VERSION` | Node.js | `24` |

Cuando el kit alcance esa versión, borra la variable para volver a usar la del kit.

## Lo que no hace

- **No ejecuta pruebas de punta a punta.** Las pruebas con Playwright que el proyecto tenga se ejecutan en local.
- **No despliega.** `ci.yml` solo comprueba. El despliegue es un workflow propio de cada proyecto, y siempre lo aprueba una persona.
- **No revisa que el cambio sea lo que el cliente pidió.** Eso lo hacen los agentes revisores y, al final, quien aprueba el Pull Request.

## Siguientes pasos

- [Capas de control](capas-de-control.md): cómo encaja la integración continua con las demás protecciones.
- [Cobertura y código generado](cobertura-y-codigo-generado.md).
- [Personalizar un proyecto](personalizar.md#workflows-propios): agregar workflows propios.
