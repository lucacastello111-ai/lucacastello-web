"""Servidor local para ver el sitio: python build/servidor.py  ->  http://localhost:8765
(el http.server comun de Python corta conexiones cuando el navegador pide muchas imagenes a la vez)"""
import http.server, os, socketserver, sys
PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class Servidor(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128
class Handler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a): pass
print(f"Sitio en http://localhost:{PUERTO}  (Ctrl+C para cortar)")
Servidor(("", PUERTO), Handler).serve_forever()
