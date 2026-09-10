import json, re

S = json.load(open('build/structure.json', encoding='utf-8'))

def obras(page, start_marker=None):
    out = []
    for st in S[page]:
        if st['kind'] == 'page' and st['videos']:
            out.append({
                'titulo': st['title'].replace('\u201c','"').replace('\u201d','"')
                           .replace('\u2018','"').replace('\u2019','"'),
                'rol': st['subtitle'],
                'texto': st['body'],
                'youtube': st['videos'][0],
            })
    return out

sobre = ''
for st in S['sobre-mi']:
    if st['kind'] == 'page' and st['body']:
        sobre = st['body']

C = {
  "_leeme": "Este archivo es el contenido de la web. Edita los textos aqui y corre construir.bat.",
  "sitio": {
    "nombre": "Luca Castello",
    "rol": "Editor / Director",
    "dominio": "https://lucacastello.com",
    "descripcion": "Reel de Luca Castello, editor y director. Cine publicitario, largometrajes y contenido generado con IA. Ciudad de Mexico / Buenos Aires.",
    "email": "lucacastello93@gmail.com",
    "telefono": "(+54) 11 5959 4094",
    "ubicacion": "Ciudad de M\u00e9xico / Buenos Aires"
  },
  "menu": [
    {"nombre": "Ficci\u00f3n", "archivo": "ficcion.html"},
    {"nombre": "Publicidad", "archivo": "publicidad.html"},
    {"nombre": "Reel AI", "archivo": "reel-ai.html"},
    {"nombre": "Sobre m\u00ed", "archivo": "sobre-mi.html"}
  ],
  "home": {
    "slides": ["home-1.jpg", "home-2.jpg", "home-3.jpg", "home-4.jpg"]
  },
  "ficcion": {"titulo": "Ficci\u00f3n", "layout": "detalle", "obras": obras('largometrajes')},
  "publicidad": {"titulo": "Cine publicitario", "layout": "grilla", "obras": obras('publicidad')},
  "reel-ai": {"titulo": "Reel AI", "layout": "unico", "obras": obras('reel-ai')},
  "sobre-mi": {"titulo": "Sobre m\u00ed", "foto": "retrato.jpg", "texto": sobre}
}

json.dump(C, open('contenido.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('ficcion:', len(C['ficcion']['obras']), '| publicidad:', len(C['publicidad']['obras']), '| reel-ai:', len(C['reel-ai']['obras']))
print('sobre-mi chars:', len(sobre))
