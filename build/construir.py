"""
Genera las paginas HTML del sitio a partir de contenido.json, en español y en inglés.

Uso:  doble click en construir.bat   (o:  python build/construir.py)

Para cambiar textos, videos u orden se edita contenido.json, no este archivo.
Los textos en inglés van en los campos que terminan en _en (texto_en, rol_en, titulo_en...).
Si un campo _en falta, se usa el español. Los créditos de Publicidad y los roles se traducen solos.
"""
import hashlib
import json
import html
import os
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(RAIZ, "contenido.json"), encoding="utf-8"))
SITIO = C["sitio"]
# huella de CSS y JS: cambia sola cuando se editan, asi el navegador nunca usa una copia vieja
VERSION = hashlib.md5(b"".join(open(os.path.join(RAIZ, "assets", r), "rb").read()
                               for r in ("css/site.css", "js/site.js"))).hexdigest()[:8]
DOMINIO = SITIO["dominio"].rstrip("/")

e = lambda s: html.escape(s or "", quote=True)

# cada pagina en español tiene su par en inglés
EN = {
    "index.html": "en.html",
    "ficcion.html": "fiction.html",
    "publicidad.html": "commercials.html",
    "reel-ai.html": "ai-reel.html",
    "sobre-mi.html": "about.html",
}

# textos fijos de la interfaz
UI = {
    "es": {"play": "Reproducir", "imagen": "Imagen", "idioma": "Idioma"},
    "en": {"play": "Play", "imagen": "Image", "idioma": "Language"},
}

# roles que se traducen solos (si una obra trae "rol_en", manda ese)
ROL_EN = {
    "Editor": "Editor",
    "Director / Editor": "Director / Editor",
    "Director /Editor": "Director / Editor",
    "Supervisor de Edición": "Supervising Editor",
    "Supervisor de Edición y Tráiler": "Supervising Editor & Trailer Editor",
    "Editor de Trailer": "Trailer Editor",
    "Compositor de VFX": "VFX Compositor",
    "Editor - Teaser": "Teaser Editor",
    "Artista AI": "AI Artist",
    "AI Director": "AI Director",
}


def t(obj, clave, lang):
    """Devuelve el campo en el idioma pedido, con el español como respaldo."""
    if lang == "en" and obj.get(clave + "_en"):
        return obj[clave + "_en"]
    return obj.get(clave, "")


def archivo_de(archivo_es, lang):
    return EN.get(archivo_es, archivo_es) if lang == "en" else archivo_es


def credito_en(texto):
    """Traduce las lineas de créditos de Publicidad (Agencia, Productora, Dirección...)."""
    salida = []
    for linea in (texto or "").split("\n"):
        l = linea.strip()
        if l.startswith("Agencia - "):
            l = "Agency - " + l[len("Agencia - "):]
        elif l.startswith("Productora - "):
            l = "Production - " + l[len("Productora - "):]
        elif l.startswith("Dirección - "):
            nombres = l[len("Dirección - "):]
            varios = " / " in nombres or " - " in nombres
            l = ("Directors - " if varios else "Director - ") + nombres
        elif l.startswith("Cliente - "):
            cliente = l[len("Cliente - "):]
            if cliente == "Ministerio de Turismo Argentina":
                cliente = "Argentina's Ministry of Tourism"
            l = "Client - " + cliente
        elif l.startswith("Premios:"):
            l = "Awards:" + l[len("Premios:"):]
        salida.append(l)
    return "\n".join(salida)


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


def video(obra, lang, cargar="lazy"):
    # dos tipos: video de YouTube ("youtube": id) o video propio ("mp4" + "poster")
    titulo = t(obra, "titulo", lang)
    if obra.get("mp4"):
        fuente, caratula = f'data-mp4="{e(obra["mp4"])}"', obra["poster"]
    else:
        # "poster" opcional: carátula elegida a mano en vez de la miniatura de YouTube
        fuente, caratula = f'data-youtube="{e(obra["youtube"])}"', obra.get("poster") or thumb(obra["youtube"])
    return (
        f'<div class="video" role="button" tabindex="0" {fuente} '
        f'data-titulo="{e(titulo)}" aria-label="{UI[lang]["play"]} {e(titulo or "video")}">'
        f'<img src="{caratula}" alt="{e(titulo)} · Luca Castello" loading="{cargar}" decoding="async" width="1280" height="720">'
        f'<span class="video__play">{PLAY_SVG}</span></div>'
    )


def parrafos(texto):
    return "".join(f"<p>{e(p.strip())}</p>" for p in (texto or "").split("\n") if p.strip())


def selector(archivo_es, lang):
    """Selector ES / EN: lleva a la misma pagina en el otro idioma."""
    destinos = {"es": archivo_es, "en": EN.get(archivo_es, archivo_es)}
    partes = []
    for codigo in ("es", "en"):
        activo = ' class="activo" aria-current="true"' if codigo == lang else ""
        partes.append(f'<a href="{destinos[codigo]}" lang="{codigo}" hreflang="{codigo}"{activo}>{codigo.upper()}</a>')
    return f'<div class="idioma" aria-label="{UI[lang]["idioma"]}">' + '<span aria-hidden="true">/</span>'.join(partes) + "</div>"


def nav(archivo_es, lang):
    items = [f'<li><a href="{archivo_de(m["archivo"], lang)}">{e(t(m, "nombre", lang))}</a></li>' for m in C["menu"]]
    items.insert(3, '<li class="salto" aria-hidden="true"></li>')  # en celular corta el menu en 3 + 2
    links = "".join(items)
    return (
        '<header class="nav"><div class="contenedor">'
        f"{selector(archivo_es, lang)}<ul>{links}</ul></div></header>"
    )


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


def pie(lang):
    tel = "".join(ch for ch in SITIO["telefono"] if ch.isdigit())
    item = lambda icono, texto, href=None: (
        (f'<a class="pie__item" href="{href}"' + (' target="_blank" rel="noopener"' if href.startswith("http") else "") + ">")
        if href else '<div class="pie__item">'
    ) + f'<img src="assets/img/iconos/{icono}" alt="" width="70" height="70" loading="lazy"><span>{e(texto)}</span>' + (
        "</a>" if href else "</div>"
    )
    return (
        '<footer class="pie"><div class="pie__grilla">'
        + item("ubicacion.png", t(SITIO, "ubicacion", lang))
        + item("mail.png", SITIO["email"], f'mailto:{SITIO["email"]}')
        + item("telefono.png", SITIO["telefono"], f"https://wa.me/{tel}")
        + "</div></footer>"
    )


def obra(o, tipo, i, lang):
    if lang == "en":
        rol = o.get("rol_en") or ROL_EN.get(o["rol"], o["rol"])
        texto = o.get("texto_en") or (credito_en(o.get("texto")) if tipo == "publicidad" else o.get("texto"))
    else:
        rol, texto = o["rol"], o.get("texto")
    panel = (
        '<div class="obra__panel"><div class="obra__texto">'
        f'<h2 class="obra__titulo">{e(t(o, "titulo", lang))}</h2>'
        f'<h3 class="obra__rol">{e(rol)}</h3>'
        '<div class="obra__linea"></div>'
        f'<div class="obra__cuerpo">{parrafos(texto)}</div>'
        "</div></div>"
    )
    media = f'<div class="obra__media">{video(o, lang, "eager" if i < 2 else "lazy")}</div>'
    partes = panel + media if tipo == "ficcion" else media + panel
    revela = " revela" if tipo == "publicidad" else " revela-movil"  # Publicidad siempre; Ficción solo en celular
    return f'<article class="obra obra--{tipo}{revela}">{partes}</article>'


def url_de(archivo):
    return DOMINIO + "/" + ("" if archivo == "index.html" else archivo)


def pagina(archivo_es, lang, titulo, cuerpo, descripcion=None, imagen_og="assets/img/fondos/home-2.jpg", precargar=None, datos_extra=""):
    archivo = archivo_de(archivo_es, lang)
    rol = t(SITIO, "rol", lang)
    titulo_full = TITULOS.get(archivo_es, {}).get(lang) or (f"{titulo} - {SITIO['nombre']}" if titulo else f"{SITIO['nombre']} - {rol}")
    desc = descripcion or t(SITIO, "descripcion", lang)
    url = url_de(archivo)
    pre = f'<link rel="preload" as="image" href="{precargar}">\n' if precargar else ""
    alternos = ""
    if archivo_es in EN:
        alternos = (
            f'<link rel="alternate" hreflang="es" href="{e(url_de(archivo_es))}">\n'
            f'<link rel="alternate" hreflang="en" href="{e(url_de(EN[archivo_es]))}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{e(url_de(archivo_es))}">\n'
        )
    locale = "es_AR" if lang == "es" else "en_US"
    datos = ""
    if archivo_es in ("index.html", "sobre-mi.html"):
        persona = {
            "@context": "https://schema.org", "@type": "Person", "name": SITIO["nombre"],
            "jobTitle": SITIO["rol"], "url": DOMINIO + "/",
            "image": DOMINIO + "/assets/img/fondos/" + C["sobre-mi"]["foto"],
            "email": "mailto:" + SITIO["email"],
            "description": desc,
            "address": {"@type": "PostalAddress", "addressLocality": "Ciudad de México", "addressCountry": "MX"},
            "worksFor": {"@type": "Organization", "name": "Gélido AI", "url": "https://gelidoai.com"},
            "knowsAbout": ["Montaje", "Dirección de cine", "Cine de terror argentino", "Cine publicitario",
                           "Dirección con inteligencia artificial", "Postproducción", "Animatics"],
            "birthPlace": {"@type": "Place", "name": "Chubut, Patagonia, Argentina"},
            "nationality": {"@type": "Country", "name": "Argentina"},
            "hasOccupation": [{"@type": "Occupation", "name": "Director de cine"},
                              {"@type": "Occupation", "name": "Editor de cine"}],
            "sameAs": [
                "https://www.imdb.com/name/nm9730734/",
                "https://www.linkedin.com/in/luca-castello-/",
                "https://www.instagram.com/luca_castello_/",
                "https://letterboxd.com/director/luca-castello/",
                "https://www.themoviedb.org/person/2265214-luca-castello",
            ],
        }
        datos = '<script type="application/ld+json">' + json.dumps(persona, ensure_ascii=False) + "</script>" + chr(10)
    auto = ""
    if archivo_es in EN:
        auto = AUTO_JS.replace("__ES__", archivo_es).replace("__EN__", EN[archivo_es]).replace("__YO__", lang) + chr(10)
    doc = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add("js")</script>
{auto}<title>{e(titulo_full)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(KEYWORDS[lang])}">
<link rel="canonical" href="{e(url)}">
{alternos}<meta property="og:type" content="website">
<meta property="og:locale" content="{locale}">
<meta property="og:title" content="{e(titulo_full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(DOMINIO + '/' + imagen_og)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#000000">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Arimo&family=Cairo&family=Raleway:wght@100;400&display=swap" rel="stylesheet">
{pre}{datos}{datos_extra}<link rel="stylesheet" href="assets/css/site.css?v={VERSION}">
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


# Idioma automatico (va en el <head>, antes de dibujar la pagina):
# español si el dispositivo esta en un pais hispanohablante (por zona horaria) o si el navegador
# esta en español; si no, inglés. Si la persona eligio ES/EN a mano, se respeta esa eleccion.
# Los buscadores y las vistas previas de links no se redirigen.
AUTO_JS = (
    '<script>(function(){var par={es:"__ES__",en:"__EN__"},yo="__YO__",k="lcIdioma";'
    'document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest(".idioma a");'
    'if(a){try{localStorage.setItem(k,a.lang)}catch(x){}}});'
    'if(/bot|crawl|spider|slurp|lighthouse|facebookexternalhit|whatsapp|telegram|preview/i.test(navigator.userAgent))return;'
    'var g=null;try{g=localStorage.getItem(k)}catch(x){}'
    'if(g!=="es"&&g!=="en"){var tz="";try{tz=Intl.DateTimeFormat().resolvedOptions().timeZone||""}catch(x){}'
    'var n=((navigator.languages&&navigator.languages[0])||navigator.language||"").toLowerCase();'
    r'var h=/^(America\/(Argentina\/.+|Buenos_Aires|Cordoba|Catamarca|Jujuy|Mendoza|Mexico_City|Cancun|Merida|Monterrey|Matamoros|Chihuahua|Ciudad_Juarez|Ojinaga|Mazatlan|Bahia_Banderas|Hermosillo|Tijuana|Bogota|Lima|Santiago|Punta_Arenas|Caracas|Guayaquil|La_Paz|Asuncion|Montevideo|Costa_Rica|Panama|Guatemala|El_Salvador|Tegucigalpa|Managua|Havana|Santo_Domingo|Puerto_Rico)|Europe\/Madrid|Africa\/(Ceuta|Malabo)|Atlantic\/Canary|Pacific\/(Easter|Galapagos))$/;'
    'g=(h.test(tz)||n.indexOf("es")===0)?"es":"en"}'
    'if(g!==yo)location.replace(par[g]+location.search+location.hash)})();</script>'
)

# ---------------------------------------------------------------- SEO
# titulo de pestaña con palabras clave (lo que mas pesa en Google)
TITULOS = {
    "index.html": {"es": "Luca Castello | Director y editor de cine, publicidad e IA",
                   "en": "Luca Castello | Film director and editor, commercials and AI"},
    "ficcion.html": {"es": "Ficción | Luca Castello, director y editor de cine",
                     "en": "Fiction | Luca Castello, film director and editor"},
    "publicidad.html": {"es": "Publicidad | Luca Castello, editor de cine publicitario",
                        "en": "Commercials | Luca Castello, commercial film editor"},
    "reel-ai.html": {"es": "Reel AI | Luca Castello, dirección audiovisual con IA",
                     "en": "AI Reel | Luca Castello, AI filmmaking"},
    "sobre-mi.html": {"es": "Sobre mí | Luca Castello, director y editor",
                      "en": "About | Luca Castello, director and editor"},
}
KEYWORDS = {
    "es": "Luca Castello, director de cine, editor de cine, montajista, montaje, cine de terror argentino, "
          "Retratos del Apocalipsis, Gélido AI, dirección con inteligencia artificial, cine publicitario, "
          "editor de publicidad, Ciudad de México, Buenos Aires, Chubut, Patagonia",
    "en": "Luca Castello, film director, film editor, Argentine horror film, Retratos del Apocalipsis, "
          "Gélido AI, AI filmmaking, AI director, commercial editor, Mexico City, Buenos Aires",
}
LUCA = {"@type": "Person", "name": "Luca Castello", "url": "https://lucacastello.com/"}
# directores de cada película (para vincular a Luca con sus colaboradores)
DIRECTORES = {
    "Retratos del Apocalipsis": ["Luca Castello", "Fabián Forte", "Nicanor Loreti"],
    "Corporea": ["Cristian Bidone"],
    "La Piel No Es Un Límite": ["Luca Castello"],
    "El Ritual del Nahual": ["Carlos Matienzo Serment"],
    "El Amigo Visible": ["Cristian Bidone"],
    "El Hombre de la Luna": ["Rodrigo Pérez Green"],
    "Román": ["Majo Staffolani"],
    "La Amante": ["Luca Castello"],
    "Golondrinas": ["Mariano Mouriño"],
}


def ld(dato):
    return '<script type="application/ld+json">' + json.dumps(dato, ensure_ascii=False) + "</script>" + chr(10)


def ld_ficcion(lang):
    items = []
    for n, o in enumerate(C["ficcion"]["obras"], 1):
        peli = {"@type": "Movie", "name": o["titulo"], "description": t(o, "texto", lang),
                "image": DOMINIO + "/" + (o.get("poster") or thumb(o["youtube"]))}
        if o.get("youtube"):
            peli["sameAs"] = "https://www.youtube.com/watch?v=" + o["youtube"]
        dirs = DIRECTORES.get(o["titulo"])
        if dirs:
            peli["director"] = [LUCA if d == "Luca Castello" else {"@type": "Person", "name": d} for d in dirs]
        rol = o["rol"].lower()
        if "editor" in rol or "edición" in rol:
            peli["editor"] = LUCA
        elif "director" not in rol:
            peli["contributor"] = LUCA
        items.append({"@type": "ListItem", "position": n, "item": peli})
    return ld({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": items})


def ld_reel(lang):
    salida = ""
    for o in C["reel-ai"]["obras"]:
        if o.get("mp4"):
            salida += ld({"@context": "https://schema.org", "@type": "VideoObject",
                          "name": t(o, "titulo", lang), "description": t(C["reel-ai"], "intro", lang),
                          "thumbnailUrl": DOMINIO + "/" + o["poster"], "contentUrl": DOMINIO + "/" + o["mp4"],
                          "uploadDate": "2026-08-24", "creator": LUCA,
                          "productionCompany": {"@type": "Organization", "name": "Gélido AI", "url": "https://gelidoai.com/"}})
    return salida


# titulos de pestaña y descripciones de cada pagina
META = {
    "ficcion.html": {
        "es": ("Ficción", "Largometrajes de ficción editados y dirigidos por Luca Castello: Retratos del Apocalipsis, Corporea, Román, El Amigo Visible y más."),
        "en": ("Fiction", "Feature films edited and directed by Luca Castello: Retratos del Apocalipsis, Corporea, Román, El Amigo Visible and more."),
    },
    "publicidad.html": {
        "es": ("Publicidad", "Cine publicitario editado por Luca Castello para Netflix, HBO, Toyota, Mercadopago, Nescafé, Arcor, Philco y más."),
        "en": ("Commercials", "Commercials edited by Luca Castello for Netflix, HBO, Toyota, Mercado Pago, Nescafé, Arcor, Philco and more."),
    },
    "reel-ai.html": {
        "es": ("Reel AI", "Reel de creación audiovisual con inteligencia artificial de Luca Castello."),
        "en": ("AI Reel", "Luca Castello's reel of AI-driven filmmaking."),
    },
    "sobre-mi.html": {
        "es": ("Sobre mí", "Luca Castello, director y editor nacido en la Patagonia argentina y radicado en Ciudad de México. Montaje de largometrajes y publicidad, dirección y creación audiovisual con IA en Gélido AI."),
        "en": ("About", "Luca Castello, a director and film editor from Argentine Patagonia based in Mexico City. Feature and commercial editing, directing and AI-driven filmmaking at Gélido AI."),
    },
}

# ------------------------------------------------------------------ paginas
urls = []
H, F, P, R, S = C["home"], C["ficcion"], C["publicidad"], C["reel-ai"], C["sobre-mi"]

for lang in ("es", "en"):
    # PORTADA
    imgs = "".join(
        f'<img src="assets/img/fondos/{s}" alt=""' + (' class="activo" fetchpriority="high"' if i == 0 else ' fetchpriority="low" decoding="async"') + ">"
        for i, s in enumerate(H["slides"])
    )
    puntos = "".join(
        ('<button class="activo"' if i == 0 else "<button") + f' aria-label="{UI[lang]["imagen"]} {i + 1}"></button>'
        for i in range(len(H["slides"]))
    )
    links = "".join(f'<a href="{archivo_de(m["archivo"], lang)}">{e(t(m, "nombre", lang))}</a>' for m in H["menu"])
    portada = (
        '<main class="portada">'
        f'<div class="portada__pista" aria-hidden="true">{imgs}</div>'
        + selector("index.html", lang)
        + '<div class="portada__centro">'
        f'<h1 class="portada__nombre">{e(SITIO["nombre"]).upper()}</h1>'
        f'<h2 class="portada__rol">{e(t(SITIO, "rol", lang)).upper()}</h2>'
        f'<nav class="portada__links">{links}</nav>'
        "</div>"
        f'<div class="portada__puntos">{puntos}</div>'
        "</main>"
    )
    urls.append(pagina("index.html", lang, "", portada + pie(lang), precargar=f"assets/img/fondos/{H['slides'][0]}"))

    # FICCION
    cuerpo = "".join(obra(o, "ficcion", i, lang) for i, o in enumerate(F["obras"]))
    titulo, desc = META["ficcion.html"][lang]
    urls.append(pagina(
        "ficcion.html", lang, titulo,
        nav("ficcion.html", lang) + titulo_seccion(t(F, "titulo", lang)) + franja(cuerpo, F["fondo"]) + pie(lang),
        descripcion=desc, datos_extra=ld_ficcion(lang),
    ))

    # PUBLICIDAD
    cuerpo = "".join(obra(o, "publicidad", i, lang) for i, o in enumerate(P["obras"]))
    titulo, desc = META["publicidad.html"][lang]
    urls.append(pagina(
        "publicidad.html", lang, titulo,
        nav("publicidad.html", lang) + titulo_seccion(t(P, "titulo", lang))
        + franja(cuerpo, P["fondo"], "franja--publicidad") + pie(lang),
        descripcion=desc,
    ))

    # REEL AI (texto corto arriba del video + ficha de Gélido abajo)
    intro = t(R, "intro", lang)
    cuerpo = '<div class="reel">'
    if intro:
        cuerpo += f'<div class="reel__intro">{parrafos(intro)}</div>'
    cuerpo += "".join(video(o, lang, "eager") for o in R["obras"]) + "</div>"
    I = R.get("info")
    if I:
        link = ""
        if I.get("link"):
            link = (f'<p class="reel__link"><a href="{e(I["link"]["url"])}" target="_blank" rel="noopener">'
                    f'{e(I["link"]["texto"])} &#8599;</a></p>')
        cuerpo += (
            '<div class="reel__info">'
            '<div class="reel__cabeza">'
            f'<h2 class="obra__titulo">{e(t(I, "titulo", lang))}</h2>'
            f'<h3 class="obra__rol">{e(t(I, "rol", lang))}</h3>'
            '<div class="obra__linea"></div></div>'
            f'<div class="reel__texto">{parrafos(t(I, "texto", lang))}{link}</div>'
            "</div>"
        )
    titulo, desc = META["reel-ai.html"][lang]
    urls.append(pagina(
        "reel-ai.html", lang, titulo,
        nav("reel-ai.html", lang) + titulo_seccion(t(R, "titulo", lang)) + franja(cuerpo, R["fondo"]) + pie(lang),
        descripcion=desc, datos_extra=ld_reel(lang),
    ))

    # SOBRE MI
    cuerpo = (
        '<div class="sobre">'
        f'<img class="sobre__foto" src="assets/img/fondos/{S["foto"]}" alt="{e(SITIO["nombre"])}" loading="lazy" decoding="async">'
        f'<div class="sobre__texto">{parrafos(t(S, "texto", lang))}</div>'
        "</div>"
    )
    titulo, desc = META["sobre-mi.html"][lang]
    urls.append(pagina(
        "sobre-mi.html", lang, titulo,
        nav("sobre-mi.html", lang) + titulo_seccion(t(S, "titulo", lang))
        + franja(cuerpo, S["fondo"], "franja--sobre") + pie(lang),
        descripcion=desc,
        imagen_og=f"assets/img/fondos/{S['foto']}",
    ))

# 404 (una sola, con las dos opciones)
pagina(
    "404.html", "es", "Página no encontrada / Page not found",
    nav("index.html", "es") + titulo_seccion("No encontrado · Not found")
    + franja('<div class="reel" style="text-align:center;padding:60px 0">'
             '<a href="index.html">VOLVER AL INICIO</a> &nbsp;·&nbsp; <a href="en.html">BACK TO HOME</a></div>',
             F["fondo"])
    + pie("es"),
)

# sitemap + robots
hoy = date.today().isoformat()
with open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls:
        f.write(f"  <url><loc>{u}</loc><lastmod>{hoy}</lastmod></url>\n")
    f.write("</urlset>\n")
with open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n")

print("Listo. Paginas generadas:")
for u in urls:
    print("  ", u)
