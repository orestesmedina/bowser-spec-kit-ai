---
name: web-sin-framework
description: Convenciones para interfaces web con HTML, CSS y JavaScript estándar, sin framework ni paso de compilación, según el estándar HTML, las pautas de accesibilidad WCAG y las guías de MDN y OWASP. Usar al crear o modificar páginas, plantillas, hojas de estilo o archivos JavaScript de una interfaz así.
metadata:
  madurez: redactada
---
# Web sin framework — convenciones

Fuentes: el estándar HTML (html.spec.whatwg.org), la documentación de MDN (developer.mozilla.org), las pautas de accesibilidad WCAG 2.2 del W3C en su nivel AA, y las guías de OWASP contra XSS y CSRF. Revisado el 2026-10-09. Ante una duda que esta página no resuelva, se consulta ahí.

Para interfaces donde el navegador recibe HTML ya armado (por el servidor o escrito a mano), con CSS y JavaScript servidos tal cual. Lo propio del lenguaje del servidor está en su skill.

## Estructura
- Cada cosa en su archivo: el contenido en el HTML, la apariencia en `css/`, el comportamiento en `js/`. Sin `style="…"`, sin lógica en `<script>` dentro de la página y sin `onclick="…"`.
- Lo que se repite en todas las páginas (cabecera, menú, pie) vive en un solo archivo que las demás incluyen.
- Un archivo JavaScript por pantalla o por componente, como módulo: `<script type="module" src="…">`. Lo compartido se importa con `import`, no se cuelga de `window`.
- El código de terceros no se edita. Para cambiar cómo se ve algo suyo, se sobrescribe desde la hoja de estilos propia, cargada después.
- Una biblioteca nueva o un archivo servido desde otro sitio (CDN) solo si el plan lo dice; lo que venga de un CDN lleva `integrity` y `crossorigin`, para que el navegador rechace un archivo alterado.

## HTML
- `<!DOCTYPE html>`, `<html lang="…">` con el idioma real, `<meta charset="utf-8">` y `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- El documento debe ser válido (validator.w3.org): etiquetas cerradas, `id` únicos, atributos entre comillas.
- Elementos por lo que significan: `button` para acciones, `a` para ir a otra página, `header`, `nav`, `main` (uno por página), `footer`; `table` solo para datos, con `th` y `scope`; un `h1` por página y los títulos sin saltarse niveles. Un `div` con un `click` no es un botón.
- Formularios: cada campo con su `label` (`for` + `id`), el `type` que corresponde (`email`, `number`, `date`), `autocomplete` donde aplica, y `required`, `min`, `max`, `maxlength` como ayuda. **La validación del navegador no reemplaza a la del servidor.**
- `method="post"` para lo que cambia datos; `GET` solo para consultar.

## Accesibilidad (WCAG 2.2, nivel AA)
- Todo se puede hacer solo con el teclado, en un orden lógico, y el foco siempre se ve.
- Toda imagen lleva `alt`: lo que la imagen dice, o vacío (`alt=""`) si es un adorno.
- Contraste de al menos 4.5:1 entre el texto y su fondo (3:1 en texto grande).
- La información no depende solo del color: un error lleva también texto o un ícono con nombre.
- Los mensajes que aparecen sin recargar la página (errores, confirmaciones) se anuncian con `role="alert"` o `aria-live`. Los errores de un formulario se muestran junto a su campo y se enlazan con `aria-describedby`.
- Primero el elemento HTML correcto; `aria-*` solo cuando no existe uno que lo exprese.

## CSS
- Se seleccionan clases; no `id` ni estilos en línea. Sin `!important`, salvo para ganarle a una regla de terceros, y con un comentario que lo explique.
- Los colores, tamaños y espacios que se repiten se definen una vez como propiedades personalizadas (`--color-primario`) en `:root`.
- Diseño que se adapta: se escribe primero para la pantalla angosta y se amplía con `@media (min-width: …)`. Distribución con flexbox y grid. Tamaños de texto en `rem`, no en píxeles, para respetar el tamaño que la persona configuró.
- Las animaciones se reducen o se quitan con `@media (prefers-reduced-motion: reduce)`.

## JavaScript
- JavaScript estándar, con lo que esté disponible en todos los navegadores vigentes ("Baseline" en MDN). No hay compilador que traduzca: lo que escribes es lo que se ejecuta.
- `const` por defecto y `let` cuando cambia; nunca `var`. `===` y `!==`. Los módulos ya están en modo estricto; en un archivo que no es módulo, `'use strict';` al inicio.
- Los eventos se enganchan con `addEventListener`. Los elementos se buscan con `querySelector` por una clase o un atributo `data-*` pensado para eso, no por clases de apariencia.
- Las llamadas al servidor usan `fetch` con `async`/`await`, y pasan por un solo módulo, que es donde está la dirección de la API. **`fetch` no falla con un 404 ni con un 500**: hay que comprobar `response.ok`.
- Toda llamada contempla y muestra cuatro estados: cargando, sin resultados, error y éxito. Un error nunca se queda solo en la consola. Mientras una acción está en curso, su botón se desactiva, y se reactiva también cuando falla.
- La lógica que no depende de la página (cálculos, formato, validaciones) va en funciones que reciben datos y devuelven datos, sin tocar el documento.

## Seguridad (OWASP)
- **Todo dato se escapa en el momento de ponerlo en la página**, venga de la persona o de la base de datos. En una plantilla del servidor, con la función de escape de su lenguaje (ver su skill). En JavaScript, con `textContent` o `setAttribute`; **nunca** `innerHTML`, `outerHTML`, `insertAdjacentHTML` ni `document.write` con datos.
- Una dirección que viene de datos se comprueba antes de ponerla en `href` o `src`: solo `http:`, `https:` o rutas del propio sitio. Nunca `eval`, `new Function` ni `setTimeout` con un texto.
- Ninguna contraseña, clave de API ni token en el HTML, en el JavaScript ni en `localStorage`: todo lo que llega al navegador es público. La sesión va en una cookie `HttpOnly`, `Secure` y `SameSite` que maneja el servidor.
- Los formularios y las llamadas que cambian datos llevan el token contra CSRF que entrega el servidor.
- Lo que el navegador oculta o desactiva no protege nada: el permiso se comprueba en el servidor.
- El servidor envía una política de contenido (`Content-Security-Policy`) que no permite scripts en línea; por eso no se escriben.
- Un enlace que abre otra pestaña hacia un sitio externo lleva `rel="noopener noreferrer"`.

## Pruebas
- Las pruebas van en `tests/`, en la raíz de la parte, con la herramienta que defina el plan. Lo que más rinde probar: los flujos completos en un navegador real y las funciones de lógica pura.
- Si el proyecto no tiene herramienta de pruebas, no instales una por tu cuenta. Lo mínimo antes de entregar es abrir la pantalla en el navegador y dejar escrito en la entrega qué se comprobó, paso por paso, para que QA lo repita: el camino normal, cada error, el estado sin resultados, el uso solo con teclado, una pantalla angosta, el HTML validado y la consola sin errores.

## Si el proyecto tiene sus propias convenciones
- Esta página es el estándar. Si el proyecto tiene una skill de convenciones propias, **en nombres, estructura, patrones y bibliotecas manda esa**, para que una pantalla nueva se parezca a las que ya hay. Lo que ella no diga se hace como dice esta página.
- Las reglas de **Seguridad** no admiten excepción. Si cumplirlas exige cambiar algo que tu tarea no cubre, detente y avisa.
- No reescribas lo que tu tarea no toca. Lo que encuentres fuera del estándar va en la entrega, como deuda.
