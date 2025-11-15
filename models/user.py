import json
import os

class UserManager:
    """
    Gestiona los usuarios y sus permisos desde un archivo JSON.
    """
    def __init__(self, config_path='users.json'):
        self.users = self._load_users(config_path)

    def _load_users(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"El archivo de configuración de usuarios no se encuentra: {config_path}")
        with open(config_path, 'r') as f:
            return json.load(f)

    def get_user(self, username):
        """Obtiene los datos de un usuario."""
        return self.users.get(username)

    def verify(self, username, password):
        """Verifica si el usuario y contraseña son correctos."""
        user_data = self.get_user(username)
        if user_data and user_data.get('password') == password:
            return True
        return False

    def has_permission(self, username, permission):
        """Verifica si un usuario tiene un permiso específico."""
        user_data = self.get_user(username)
        if user_data and permission in user_data.get('permissions', []):
            return True
        return False

# Instancia única para ser usada en la aplicación
user_manager = UserManager()