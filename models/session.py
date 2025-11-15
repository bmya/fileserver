import secrets
import time

class SessionManager:
    """
    Gestor de sesiones en memoria. Asocia IDs de sesión con nombres de usuario.
    """
    def __init__(self):
        # SESSIONS = { 'session_id': {'username': 'user', 'expires': timestamp} }
        self.sessions = {}

    def create_session(self, username):
        """Crea una nueva sesión para un usuario y devuelve el ID de sesión."""
        session_id = secrets.token_hex(16)
        # La sesión expira en 1 hora
        expires = time.time() + 3600
        self.sessions[session_id] = {'username': username, 'expires': expires}
        return session_id

    def get_session_user(self, session_id):
        """Devuelve el nombre de usuario si la sesión es válida, si no, None."""
        if session_id in self.sessions:
            session_data = self.sessions[session_id]
            if time.time() < session_data['expires']:
                return session_data['username']
            else:
                # La sesión ha expirado, la eliminamos
                del self.sessions[session_id]
        return None

    def delete_session(self, session_id):
        """Elimina una sesión."""
        if session_id in self.sessions:
            del self.sessions[session_id]

# Instancia única para la aplicación
session_manager = SessionManager()
