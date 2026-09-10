"""
Genera las paginas HTML del sitio a partir de contenido.json.

Uso:  doble click en construir.bat   (o:  python build/construir.py)

Para cambiar textos, videos u orden se edita contenido.json, no este archivo.
"""
import json
import html
import os
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(RAIZ, "contenido.json"), encoding="utf-8"))
SITIO = C["sitio"]
VERSION = date.today().strftime("%Y%m%d")  # evita que el navegador use CSS/JS viejo

e = lambda s: html.escape(s or "", quote=True)

# boton de play al estilo YouTube (gris; se pone rojo al pasar el mouse)
PLAY_SVG = (
    '<svg viewBox="0 0 68 48" aria-hidden="true">'
    '<path class="fondo" d="M66.5 7.7c-.8-2.9-2.5-5.4-5.4-6.2C55.8.1 34 0 34 0S12.2.1 6.9 1.6C4 2.4 2.3 4.8 1.5 7.7.1 13 0 24 0 24s.1 11 1.5 16.3c.8 2.9 2.5 5.4 5.4 6.2C12.2 47.9 34 48 34 48s21.8-.1 27.1-1.6c2.9-.8 4.6-3.2 5.4-6.2C67.9 35 68 24 68 24s-.1-11-1.5-16.3z"/>'
    '<path d="M45 24 27 14v20" fill="#fff"/></svg>'
)


def thumb(id_):
    ruta = f"assets/img/thumbs/{id_}.jpg"
    if os.path.exists(os.path.join(RAIZ, ruta)):
        return ruta
    # video nuevo sin miniatura local: se usa la de YouTube directamente
    return f"https://i.ytimg.com/vi/{id_}/hqdefault.jpg"


def video(obra, cargar="lazy"):
    # dos tipos: video de YouTube ("youtube": id) o video propio ("mp4" + "poster")
    if obra.get("mp4"):
        fuente, caratula = f'data-mp4="{e(obra["mp4"])}"', obra["poster"]
    else:
        fuente, caratula = f'data-youtube="{e(obra["youtube"])}"', thumb(obra["youtube"])
    return (
        f'<div class="video" role="button" tabindex="0" {fuente} '
        f'data-titulo="{e(obra["titulo"])}" aria-label="Reproducir {e(obra["titulo"] or "video")}">'
        f'<img src="{caratula}" alt="{e(obra["titulo"])}" loading="{cargar}" decoding="async" width="1280" height="720">'
        f'<span class="video__play">{PLAY_SVG}</span></div>'
    )


def parrafos(texto):
    return "".join(f"<p>{e(p.strip())}</p>" for p in (texto or "").split("\n") if p.strip())


def nav():
    links = "".join(f'<li><a href="{m["archivo"]}">{e(m["nombre"])}</a></li>' for m in C["menu"])
    return f'<header class="nav"><div class="contenedor"><ul>{links}</ul></div></header>'


def titulo_seccion(titulo):
    lineas = titulo.split("\n")
    extra = " titulo-seccion--doble" if len(lineas) > 1 else ""
    return (
        f'<section class="titulo-seccion{extra}"><div class="contenedor">'
        f'<h1>{"<br>".join(e(l) for l in lineas)}</h1></div></section>'
    )


def franja(contenido, fondo, clase=""):
    return (
        f'<section class="franja {clase}">'
        f'<div class="franja__fondo" style="background-image:url(assets/img/fondos/{fondo})" aria-hidden="true"></div>'
        f'<div class="contenedor">{contenido}</div></section>'
    )


def pie():
    tel = "".join(ch for ch in SITIO["telefono"] if ch.isdigit())
    item = lambda icono, texto, href=None: (
        (f'<a class="pie__item" href="{href}"' + (' target="_blank" rel="noopener"' if href.startswith("http") else "") + ">")
        if href else '<div class="pie__item">'
    ) + f'<img src="assets/img/iconos/{icono}" alt="" width="70" height="70" loading="lazy"><span>{e(texto)}</span>' + (
        "</a>" if href else "</div>"
    )
    return (
        '<footer class="pie"><div class="pie__grilla">'
        + item("ubicacion.png", SITIO["ubicacion"])
        + item("mail.png", SITIO["email"], f'mailto:{SITIO["email"]}')
        + item("telefono.png", SITIO["telefono"], f"https://wa.me/{tel}")
        + "</div></footer>"
    )


def obra(o, tipo, i):
    panel = (
        '<div class="obra__panel"><div class="obra__texto">'
        f'<h2 class="obra__titulo">{e(o["titulo"])}</h2>'
        f'<h3 class="obra__rol">{e(o["rol"])}</h3>'
        '<div class="obra__linea"></div>'
        f'<div class="obra__cuerpo">{parrafos(o.get("texto"))}</div>'
        "</div></div>"
    )
    media = f'<div class="obra__media">{video(o, "eager" if i < 2 else "lazy")}</div>'
    partes = panel + media if tipo == "ficcion" else media + panel
    revela = " revela" if tipo == "publicidad" else ""  # solo Publicidad aparece al scrollear
    return f'<article class="obra obra--{tipo}{revela}">{partes}</article>'


def pagina(archivo, titulo, cuerpo, descripcion=None, imagen_og="assets/img/fondos/home-2.jpg", precargar=None):
    titulo_full = f"{titulo} - {SITIO['nombre']}" if titulo else f"{SITIO['nombre']} - {SITIO['rol']}"
    desc = descripcion or SITIO["descripcion"]
    url = SITIO["dominio"].rstrip("/") + "/" + ("" if archivo == "index.html" else archivo)
    pre = f'<link rel="preload" as="image" href="{precargar}">' if precargar else ""
    doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo_full)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="Luca Castello, editor, montajista, director, Argentina, México, publicidad, películas, cine">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(titulo_full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(SITIO['dominio'].rstrip('/') + '/' + imagen_og)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#000000">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Arimo&family=Cairo&family=Raleway:wght@100;400&display=swap" rel="stylesheet">
{pre}
<link rel="stylesheet" href="assets/css/site.css?v={VERSION}">
</head>
<body>
{cuerpo}
<script src="assets/js/site.js?v={VERSION}" defer></script>
</body>
</html>
"""
    with open(os.path.join(RAIZ, archivo), "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    return url


# ------------------------------------------------------------------ paginas
urls = []

# PORTADA
H = C["home"]
imgs = "".join(
    f'<img src="assets/img/fondos/{s}" alt=""' + (' fetchpriority="high"' if i == 0 else "") + ">"
    for i, s in enumerate(H["slides"])
)
puntos = "".join(
    f'<button{" class=\"activo\"" if i == 0 else ""} aria-label="Imagen {i + 1}"></button>'
    for i in range(len(H["slides"]))
)
links = "".join(f'<a href="{m["archivo"]}">{e(m["nombre"])}</a>' for m in H["menu"])
portada = (
    '<main class="portada">'
    f'<div class="portada__pista" aria-hidden="true">{imgs}</div>'
    '<div class="portada__centro">'
    f'<h1 class="portada__nombre">{e(SITIO["nombre"]).upper()}</h1>'
    f'<h2 class="portada__rol">{e(SITIO["rol"]).upper()}</h2>'
    f'<nav class="portada__links">{links}</nav>'
    "</div>"
    f'<div class="portada__puntos">{puntos}</div>'
    "</main>"
)
urls.append(pagina("index.html", "", portada + pie(), precargar=f"assets/img/fondos/{H['slides'][0]}"))

# FICCION
F = C["ficcion"]
cuerpo = "".join(obra(o, "ficcion", i) for i, o in enumerate(F["obras"]))
urls.append(pagina(
    "ficcion.html", "Ficción",
    nav() + titulo_seccion(F["titulo"]) + franja(cuerpo, F["fondo"]) + pie(),
    descripcion="Largometrajes de ficción editados y dirigidos por Luca Castello: Retratos del Apocalipsis, Corporea, Román, El Amigo Visible y más.",
))

# PUBLICIDAD
P = C["publicidad"]
cuerpo = "".join(obra(o, "publicidad", i) for i, o in enumerate(P["obras"]))
urls.append(pagina(
    "publicidad.html", "Publicidad",
    nav() + titulo_seccion(P["titulo"]) + franja(cuerpo, P["fondo"], "franja--publicidad") + pie(),
    descripcion="Cine publicitario editado por Luca Castello para Netflix, HBO, Toyota, Mercadopago, Nescafé, Arcor, Philco y más.",
))

# REEL AI
R = C["reel-ai"]
cuerpo = '<div class="reel">' + "".join(video(o, "eager") for o in R["obras"]) + "</div>"
I = R.get("info")
if I:
    link = f'<p class="reel__link"><a href="{e(I["link"]["url"])}" target="_blank" rel="noopener">{e(I["link"]["texto"])} &#8599;</a></p>' if I.get("link") else ""
    cuerpo += (
        '<div class="reel__info">'
        '<div class="reel__cabeza">'
        f'<h2 class="obra__titulo">{e(I["titulo"])}</h2>'
        f'<h3 class="obra__rol">{e(I["rol"])}</h3>'
        '<div class="obra__linea"></div></div>'
        f'<div class="reel__texto">{parrafos(I["texto"])}{link}</div>'
        "</div>"
    )
urls.append(pagina(
    "reel-ai.html", "Reel AI",
    nav() + titulo_seccion(R["titulo"]) + franja(cuerpo, R["fondo"]) + pie(),
    descripcion="Reel de creación audiovisual con inteligencia artificial de Luca Castello.",
))

# SOBRE MI
S = C["sobre-mi"]
cuerpo = (
    '<div class="sobre">'
    f'<img class="sobre__foto" src="assets/img/fondos/{S["foto"]}" alt="{e(SITIO["nombre"])}" loading="lazy" decoding="async">'
    f'<div class="sobre__texto">{parrafos(S["texto"])}</div>'
    "</div>"
)
urls.append(pagina(
    "sobre-mi.html", "Sobre mí",
    nav() + titulo_seccion(S["titulo"]) + franja(cuerpo, S["fondo"], "franja--sobre") + pie(),
    imagen_og=f"assets/img/fondos/{S['foto']}",
))

# 404
pagina("404.html", "Página no encontrada",
       nav() + titulo_seccion("No encontrado") +
       franja('<div class="reel" style="text-align:center;padding:60px 0"><a href="index.html">VOLVER AL INICIO</a></div>', F["fondo"]) + pie())

# sitemap + robots
hoy = date.today().isoformat()
with open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls:
        f.write(f"  <url><loc>{u}</loc><lastmod>{hoy}</lastmod></url>\n")
    f.write("</urlset>\n")
with open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: {SITIO['dominio'].rstrip('/')}/sitemap.xml\n")

print("Listo. Paginas generadas:")
for u in urls:
    print("  ", u)
