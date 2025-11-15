import socketserver
import json
import os
import socket
from controllers.handler import AuthMVC_Handler

def get_local_ip():
    """Obtiene la IP local de la máquina."""
    try:
        # Crear un socket para obtener la IP sin realmente conectarse
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "N/A"

def run_server(port):
    """Inicia el servidor en el puerto especificado."""

    local_ip = get_local_ip()

    with socketserver.TCPServer(("", port), AuthMVC_Handler) as httpd:
        print(f"╔══════════════════════════════════════════════════════╗")
        print(f"║  Servidor MVC Iniciado                               ║")
        print(f"╠══════════════════════════════════════════════════════╣")
        print(f"║  Puerto: {port:<44}║")
        print(f"║                                                      ║")
        print(f"║  Acceder desde esta máquina:                         ║")
        print(f"║    http://localhost:{port:<35}║")
        print(f"║                                                      ║")
        print(f"║  Acceder desde otra máquina en la red:               ║")
        print(f"║    http://{local_ip}:{port:<33}║")
        print(f"╠══════════════════════════════════════════════════════╣")
        print(f"║  Presiona Ctrl+C para detener el servidor           ║")
        print(f"╚══════════════════════════════════════════════════════╝")
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
