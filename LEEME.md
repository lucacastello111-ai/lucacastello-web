# lucacastello.com

Copia propia del sitio que estaba en IM Creator. HTML estático, sin dependencias: se puede subir a cualquier hosting.

## Cambiar textos, videos u orden

1. Abrí `contenido.json` (con el Bloc de notas o VS Code).
2. Editá lo que quieras:
   - **Agregar un video**: copiá un bloque `{ "titulo": ..., "rol": ..., "youtube": ... }` dentro de la sección que corresponda y cambiá el ID. El ID es lo que va después de `watch?v=` en el link de YouTube.
   - **Reordenar**: mové los bloques de lugar. El orden del archivo es el orden en la página.
   - **Borrar**: eliminá el bloque (ojo con las comas entre bloques).
3. Doble click en `construir.bat`. Regenera todas las páginas en un segundo.

Los videos nuevos que no tengan miniatura local usan la miniatura de YouTube automáticamente.

### Videos propios (no están en YouTube)

Visa y el Reel AI están alojados en el sitio, en `assets/video/`. Para sumar otro así:

1. Comprimirlo para web (queda ~15-20 MB por minuto en 1080p; tiene que pesar menos de 25 MB):
   ```
   ffmpeg -i "ORIGINAL.mp4" -c:v libx264 -preset slow -crf 21 -maxrate 4.5M -bufsize 9M -pix_fmt yuv420p -vf scale=1920:-2 -c:a aac -b:a 160k -movflags +faststart assets/video/nombre.mp4
   ffmpeg -ss 3 -i "ORIGINAL.mp4" -frames:v 1 -vf scale=1280:-2 -q:v 3 assets/video/nombre.jpg
   ```
2. En `contenido.json` usar `"mp4"` y `"poster"` en vez de `"youtube"`:
   `{ "titulo": "...", "rol": "...", "texto": "...", "mp4": "assets/video/nombre.mp4", "poster": "assets/video/nombre.jpg" }`

El texto de Gélido que va debajo del reel se edita en `contenido.json` → `reel-ai` → `info`.

## Estructura

| Archivo | Qué es |
|---|---|
| `contenido.json` | **Todo el contenido.** Lo único que hace falta tocar. |
| `construir.bat` | Regenera los `.html` desde el contenido. |
| `assets/css/site.css` | Diseño: colores, tipografía y espaciados (variables arriba de todo). |
| `assets/js/site.js` | Carátulas de video, slideshow de la portada, aparición al scrollear. |
| `assets/img/fondos/` | Slides de la portada, fondos fijos de cada sección, retrato. |
| `assets/img/iconos/` | Íconos del pie (ubicación, mail, teléfono). |
| `assets/img/thumbs/` | Miniaturas de los videos (nombre = ID de YouTube). |
| `build/construir.py` | El generador. No hace falta tocarlo. |
| `build/originales/` | Imágenes originales sin comprimir (no se suben). |
| `*.html`, `sitemap.xml`, `robots.txt` | Generados. No editar a mano, se pisan al construir. |

## Qué cambió respecto a IM Creator

El diseño es una copia del original (mismas tipografías, medidas, colores, fondos e íconos). Lo que cambió es cómo cargan los videos:

- **Antes**: cada página cargaba todos los reproductores de YouTube a la vez y en loop (35 en Publicidad). Por eso se trababa.
- **Ahora**: cada video muestra su carátula con el botón de play. Al hacer click se reproduce ahí mismo, en el mismo tamaño. Si abrís otro, el anterior vuelve a su carátula: nunca hay más de un reproductor cargado.
- En Publicidad las obras van apareciendo a medida que se scrollea (en Ficción no, a pedido). Las carátulas se cargan recién cuando están por verse.
- Imágenes propias y comprimidas (ya no dependen de los servidores de IM Creator).
- Se adapta al celular: en pantallas chicas el video queda arriba y el texto abajo.
- Email clickeable y teléfono que abre WhatsApp.

## Ver en local

Doble click no alcanza (los fondos usan rutas absolutas). Correr:

```
python build/servidor.py
```
y abrir http://localhost:8765

## Publicar

Pendiente de definir. Opción recomendada: Cloudflare Pages o Netlify (gratis) y apuntar el dominio desde IONOS.
