---
name: perfil-proyecto
description: Cómo redactar o corregir el perfil del proyecto (equipo/perfil.json), que declara sus partes, tecnologías y el comando de cada verbo. Usar con el comando bowser-profile, al iniciar un proyecto, o cuando el proyecto suma una parte o una tecnología.
---
# El perfil del proyecto

`equipo/perfil.json` describe el proyecto para que el kit no suponga nada: qué partes tiene, dónde están y cómo se ejecuta cada verbo. Es del proyecto. Lo redacta un agente y lo aprueba una persona.

## Formato

```json
{
  "partes": [
    {
      "nombre": "api",
      "carpeta": "backend",
      "descripcion": "API REST del producto",
      "roles": [
        {"rol": "dev-backend", "skills": ["go-backend"]},
        {"rol": "dev-dba", "skills": ["postgres-db"]}
      ],
      "terceros": ["vendor"],
      "inmutables": ["migrations/*.sql"],
      "verbos": {
        "formato": "test -z \"$(gofmt -l .)\"",
        "revisar": "go vet ./... && golangci-lint run",
        "probar": "go test ./...",
        "cobertura": null,
        "auditar": "govulncheck ./...",
        "generar": null
      }
    }
  ]
}
```

| Campo | Qué es |
|---|---|
| `nombre` | Minúsculas, números y guiones. Único |
| `carpeta` | Relativa a la raíz. `"."` si el proyecto es una sola parte |
| `roles` | Los agentes de `equipo/agentes/` que trabajan esa parte. Cada elemento es un nombre (`"dev-backend"`) o un objeto con las skills que son solo de ese rol (`{"rol": "dev-frontend", "skills": ["react-frontend"]}`) |
| `skills` | Skills con las convenciones de su tecnología: del catálogo del kit o propias del proyecto (`.agents/skills/`). Las reciben todos los roles de la parte, además de las propias de cada uno |
| `terceros` | Carpetas con código ajeno copiado dentro de la parte (relativas a ella). No se revisan ni se formatean |
| `inmutables` | Patrones de archivos que no se modifican una vez versionados (relativos a la parte). Ej.: migraciones |
| `verbos` | El comando de cada verbo. Se ejecuta con `bash` **dentro de la carpeta de la parte** |

## Los verbos

| Verbo | Qué debe hacer el comando | Lo usa |
|---|---|---|
| `formato` | Comprobar el formato sin cambiar archivos. Rápido | Cada commit (si el commit toca la parte) y `make lint` |
| `revisar` | Análisis estático: linters, tipos, sintaxis | `make lint` |
| `probar` | Ejecutar las pruebas | `make test` |
| `cobertura` | Medir cobertura y **fallar** bajo el mínimo del proyecto | `make cobertura` |
| `auditar` | Buscar vulnerabilidades en las dependencias | `make security` |
| `generar` | Regenerar el código generado | `make generar`, `make verificar-generados` |

Todo comando termina con código 0 si está bien y distinto de 0 si no.

Cada comando recibe dos variables de entorno: `PERFIL_RAIZ` (ruta completa de la raíz del proyecto) y `PERFIL_TERCEROS` (las carpetas de `terceros` de esa parte, una por línea). Úsalas en vez de repetir la lista de terceros dentro del comando.

Si un verbo necesita un script propio del proyecto, va en `tools/`, en la raíz, y el comando lo llama con `bash "$PERFIL_RAIZ/tools/<script>.sh"`. Nunca en `scripts/`: es del kit. `tools/` no es una parte del proyecto, aunque la detección la liste como carpeta con código.

## Cómo redactarlo

1. Parte de los hechos: la salida de `make profile DETECTAR=1` y lo que leas en el código (archivos de configuración, `README`, scripts existentes). Un archivo de tecnología que trae `dentro_de_carpeta_a_confirmar` suele ser de una biblioteca copiada dentro del proyecto: no lo tomes por la tecnología del proyecto sin mirar la carpeta.
2. **Una parte es algo que se construye, se prueba o se despliega por separado.** No dividas por dividir: un proyecto pequeño puede ser una sola parte con `"carpeta": "."`. Si una parte mezcla oficios (por ejemplo, PHP que genera HTML junto a su CSS y su JavaScript), no la partas en carpetas artificiales: dale varios `roles`, cada uno con sus skills.
   **Quién trabaja cada parte.** Los roles no traen tecnología: reciben del perfil sus carpetas, skills y comandos, y una parte sin `roles` no tiene quién la trabaje. `dev-backend`, el lado del servidor; `dev-frontend`, la interfaz; `dev-dba`, la base de datos (esquema, migraciones, consultas, procedimientos). **La base de datos es de `dev-dba`, no de `dev-backend`:** si vive en su propia carpeta, es una parte con ese rol; si sus archivos están dentro de la carpeta del servidor, esa parte lleva los dos roles y la skill del motor va en `dev-dba`. Cualquier otro rol de `roles_disponibles` puede trabajar una parte si el proyecto lo necesita (por ejemplo, `devops` en una carpeta de infraestructura).
3. Usa solo comandos que el proyecto ya puede ejecutar: herramientas que ya usa o que están en sus archivos de configuración. Si propones una herramienta nueva, dilo aparte como recomendación; no la pongas en el perfil hasta que esté instalada.
4. **Si el proyecto no tiene algo, el verbo va en `null`.** Un proyecto sin pruebas tiene `"probar": null`, no un comando inventado que siempre pasa. Lista los verbos sin definir como deuda, para que la persona decida.
5. Lo que no puedas deducir, pregúntalo: cómo se levanta, qué versión del lenguaje usa, si una carpeta dudosa es de terceros.
6. Asigna solo skills que aparezcan en `skills_disponibles` de la detección: son las del catálogo del kit más las propias del proyecto. Las del catálogo que el perfil nombre las copia `make instalar-kit`, y las que deje de nombrar las retira. Si una es `redactada` (ver `madurez_de_las_skills_del_catalogo`), avisa que todavía no se usó en un proyecto real. Si falta la de una tecnología, dilo: el agente trabajará sin ella.
7. Nada de secretos en los comandos: las credenciales vienen de variables de entorno.

## Entrega

- El JSON propuesto.
- Un resumen en lenguaje simple: partes, tecnología de cada una, roles que la trabajan, verbos definidos y verbos sin definir.
- Las preguntas abiertas.

Después de escribirlo, `make profile` lo valida y `make instalar-kit` trae sus skills y regenera los roles con lo que el perfil dice de cada parte (sin ese paso, el commit se rechaza porque los archivos generados no están al día). El commit lo confirma una persona con `APROBADO_PERFIL=1`; un agente nunca usa esa variable.
