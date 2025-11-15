import socketserver
import json
import os
from controllers.handler import AuthMVC_Handler

def run_server(port):
    """Inicia el servidor en el puerto especificado."""
    
    with socketserver.TCPServer(("", port), AuthMVC_Handler) as httpd:
        print(f"Servidor MVC iniciado en http://localhost:{port}")
        print("Presiona Ctrl+C para detener el servidor.")
        httpd.serve_forever()

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')
    
    PUERTO = 8000 # Valor por defecto
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                PUERTO = config.get('port', 8000)
        except (json.JSONDecodeError, KeyError):
            # Si hay un error en el JSON o la clave no existe, usa el puerto por defecto
            print(f"Advertencia: No se pudo leer el puerto desde config.json. Usando puerto por defecto {PUERTO}.")
    
    run_server(PUERTO)
