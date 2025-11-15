import http.server
from http.cookies import SimpleCookie
import os
import html
import json
import re
from urllib.parse import parse_qs
from email import message_from_bytes
from email.policy import HTTP

from models.user import user_manager
from models.session import session_manager

# --- Configuración y Rutas ---
CONTROLLERS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CONTROLLERS_DIR, '..'))
VIEWS_PATH = os.path.join(PROJECT_ROOT, 'views')
STATIC_PATH = os.path.join(PROJECT_ROOT, 'static')
PUBLIC_FILES_PATH = os.path.join(PROJECT_ROOT, 'public_files')

# Cargar configuración
try:
    with open(os.path.join(PROJECT_ROOT, 'config.json'), 'r') as f:
        CONFIG = json.load(f)
    APP_TITLE = CONFIG.get('app_title', 'File Server')
    FILE_RESTRICTIONS = CONFIG.get('file_restrictions', {})
    MAX_FILE_SIZE_MB = CONFIG.get('max_file_size_mb', 3000)  # 3GB por defecto
except FileNotFoundError:
    # Valores por defecto si no hay config.json
    APP_TITLE = "File Server"
    FILE_RESTRICTIONS = {}
    MAX_FILE_SIZE_MB = 3000

def find_logo():
    """Busca un archivo de logo en static/img/ y devuelve su ruta web."""
    img_dir = os.path.join(STATIC_PATH, 'img')
    if not os.path.isdir(img_dir):
        return None
    
    for ext in ['.png', '.gif', '.jpeg', '.jpg', '.svg']:
        logo_file = 'logo' + ext
        if os.path.exists(os.path.join(img_dir, logo_file)):
            return f'/static/img/{logo_file}'
    return None

LOGO_PATH = find_logo()

# --- Controlador Principal ---
class AuthMVC_Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        # Establecer el directorio por defecto a public_files
        super().__init__(*args, directory=PUBLIC_FILES_PATH, **kwargs)

    def get_session_user(self):
        """Obtiene el nombre de usuario de la cookie de sesión actual."""
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
        
        cookie = SimpleCookie()
        cookie.load(cookie_header)
        session_id = cookie.get('session_id').value if 'session_id' in cookie else None
        return session_manager.get_session_user(session_id)

    def render_view(self, view_name, status_code=200, context=None, headers=None):
        """Renderiza una vista, manejando contexto y permisos."""
        file_path = os.path.join(VIEWS_PATH, view_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            username = self.get_session_user()
            
            full_context = {
                'app_title': APP_TITLE,
                'logo_path': LOGO_PATH if LOGO_PATH else ''
            }
            if context:
                full_context.update(context)

            for key, value in full_context.items():
                # Reemplazar tanto {{key}} como <!-- key -->
                content = content.replace(f"{{{{{key}}}}}", str(value))
                content = content.replace(f"<!-- {key} -->", str(value))

            if LOGO_PATH:
                content = content.replace('<!-- IF_LOGO -->', '').replace('<!-- END_IF_LOGO -->', '')
            else:
                content = re.sub(r'<!-- IF_LOGO -->.*?<!-- END_IF_LOGO -->', '', content, flags=re.DOTALL)

            if username and user_manager.has_permission(username, 'write'):
                content = content.replace('<!-- IF_WRITE_PERMISSION -->', '').replace('<!-- END_IF_WRITE_PERMISSION -->', '')
            else:
                content = re.sub(r'<!-- IF_WRITE_PERMISSION -->.*?<!-- END_IF_WRITE_PERMISSION -->', '', content, flags=re.DOTALL)

            self.send_response(status_code)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            if headers:
                for key, value in headers.items():
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "View Not Found")

    def handle_login_get(self):
        self.render_view('login.html')

    def handle_login_post(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        post_data = parse_qs(post_body.decode('utf-8'))
        username = post_data.get('username', [''])[0]
        password = post_data.get('password', [''])[0]

        if user_manager.verify(username, password):
            session_id = session_manager.create_session(username)
            self.send_response(303)
            self.send_header('Location', '/')
            self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')
            self.end_headers()
        else:
            error_msg = '<div class="alert alert-danger" role="alert">Usuario o contraseña incorrectos.</div>'
            self.render_view('login.html', context={"ERROR_MESSAGE_PLACEHOLDER": error_msg})

    def handle_logout(self):
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            if 'session_id' in cookie:
                session_manager.delete_session(cookie['session_id'].value)
        
        self.send_response(303)
        self.send_header('Location', '/login')
        self.send_header('Set-Cookie', 'session_id=; Path=/; Max-Age=0')
        self.end_headers()

    def render_directory_listing(self, dir_path, username):
        try:
            from datetime import datetime

            file_list_html = ""
            url_path = self.path
            fs_rel_path = os.path.relpath(dir_path, PUBLIC_FILES_PATH)
            current_path_display = '/' if fs_rel_path == '.' else '/' + fs_rel_path.replace(os.sep, '/')

            if current_path_display != '/':
                parent_path = '/'.join(url_path.strip('/').split('/')[:-1])
                file_list_html += f'''
                <tr>
                    <td colspan="4"><a href="/{parent_path}"><i class="bi bi-arrow-left-circle"></i> Volver</a></td>
                </tr>'''

            for item_name in sorted(os.listdir(dir_path)):
                full_fs_path = os.path.join(dir_path, item_name)
                item_url = os.path.join(url_path, item_name).replace(os.sep, '/')

                # Obtener información del archivo
                stat_info = os.stat(full_fs_path)

                if os.path.isdir(full_fs_path):
                    icon = "bi-folder-fill text-warning"
                    size_display = "-"
                else:
                    icon = "bi-file-earmark"
                    # Formatear tamaño
                    size_bytes = stat_info.st_size
                    if size_bytes < 1024:
                        size_display = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        size_display = f"{size_bytes / 1024:.1f} KB"
                    elif size_bytes < 1024 * 1024 * 1024:
                        size_display = f"{size_bytes / (1024 * 1024):.1f} MB"
                    else:
                        size_display = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

                # Formatear fecha
                mtime = datetime.fromtimestamp(stat_info.st_mtime)
                date_display = mtime.strftime("%Y-%m-%d %H:%M")

                delete_button = ""
                if user_manager.has_permission(username, 'delete') and os.path.isfile(full_fs_path):
                    delete_button = f'<button class="btn btn-sm btn-outline-danger" onclick="deleteFile(\'{item_url}\', this)"><i class="bi bi-trash-fill"></i></button>'

                file_list_html += f'''
                <tr>
                    <td><a href="{item_url}"><i class="bi {icon}"></i> {html.escape(item_name)}</a></td>
                    <td>{size_display}</td>
                    <td>{date_display}</td>
                    <td class="text-end">{delete_button}</td>
                </tr>'''

            context = {
                "FILE_LIST_PLACEHOLDER": file_list_html,
                "current_path": html.escape(current_path_display),
                "username": html.escape(username)
            }
            self.render_view('file_browser.html', context=context)
        except Exception as e:
            self.send_error(500, f"Error al listar directorio: {e}")

    def translate_path(self, path):
        """Traduce la URL a una ruta del sistema de archivos."""
        # Manejar archivos estáticos
        if path.startswith('/static/'):
            # Quitar el prefijo /static/ y construir la ruta desde PROJECT_ROOT
            rel_path = path[len('/static/'):]
            return os.path.join(STATIC_PATH, rel_path)

        # Para otros paths, usar la implementación por defecto que usa self.directory (public_files)
        return super().translate_path(path)

    def do_GET(self):
        if self.path == '/login':
            self.handle_login_get()
            return
        if self.path == '/logout':
            self.handle_logout()
            return
        if self.path.startswith('/static/'):
            # Servir archivo estático directamente
            path_translated = self.translate_path(self.path)
            if os.path.exists(path_translated) and os.path.isfile(path_translated):
                super().do_GET()
            else:
                self.send_error(404, "Archivo estático no encontrado")
            return

        username = self.get_session_user()
        if not username:
            self.send_response(303)
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # Ahora todos los paths se traducen a public_files por defecto
        path_translated = self.translate_path(self.path)
        if os.path.isdir(path_translated):
            self.render_directory_listing(path_translated, username)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/login':
            self.handle_login_post()
            return

        username = self.get_session_user()
        if not username or not user_manager.has_permission(username, 'write'):
            self.send_error(403, "Permiso denegado.")
            return

        # Parsear multipart/form-data usando el módulo email
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            self.send_error(400, "Se esperaba multipart/form-data")
            return

        # Leer el contenido completo del body
        content_length = int(self.headers.get('Content-Length', 0))

        # Validar tamaño del archivo
        max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if content_length > max_size_bytes:
            self.send_error(413, f"Archivo demasiado grande. Tamaño máximo: {MAX_FILE_SIZE_MB} MB")
            return

        body = self.rfile.read(content_length)

        # Crear un mensaje HTTP con los headers y body
        message_bytes = b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + body

        try:
            message = message_from_bytes(message_bytes, policy=HTTP)
        except Exception as e:
            self.send_error(400, f"Error al parsear formulario: {e}")
            return

        # Buscar el archivo en las partes del mensaje
        filename = None
        file_data = None

        for part in message.walk():
            content_disposition = part.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                # Extraer el nombre del archivo
                import re
                match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if match:
                    filename = match.group(1)
                    file_data = part.get_payload(decode=True)
                    break

        if not filename or not file_data:
            self.send_error(400, "No se seleccionó archivo.")
            return

        # Validar extensión del archivo
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        mode = FILE_RESTRICTIONS.get('mode')
        extensions = FILE_RESTRICTIONS.get('extensions', [])

        if mode and ((mode == 'allow' and ext not in extensions) or (mode == 'deny' and ext in extensions)):
            self.send_error(403, f"Tipo de archivo no permitido: {ext}")
            return

        # Guardar el archivo
        current_dir_path = self.translate_path(self.path)
        file_path = os.path.join(current_dir_path, os.path.basename(filename))

        with open(file_path, 'wb') as f:
            f.write(file_data)

        self.send_response(303)
        self.send_header('Location', self.path)
        self.end_headers()

    def do_DELETE(self):
        username = self.get_session_user()
        if not username or not user_manager.has_permission(username, 'delete'):
            self.send_error(403, "Permiso de eliminación denegado.")
            return
        
        file_path = self.translate_path(self.path)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Archivo eliminado')
            except Exception as e:
                self.send_error(500, f"Error al eliminar: {e}")
        else:
            self.send_error(404, "Archivo no encontrado.")
