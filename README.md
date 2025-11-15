# Python Secure File Server

Un mini servidor de archivos web, simple pero seguro, construido en Python. Permite a múltiples usuarios gestionar archivos con permisos específicos a través de una interfaz web moderna y responsiva.

## ✨ Características

- **Autenticación por Sesiones:** Sistema de login/logout seguro basado en sesiones y cookies.
- **Gestión de Múltiples Usuarios:** Define diferentes usuarios con contraseñas únicas.
- **Sistema de Permisos:** Asigna permisos de lectura (`read`), escritura (`write`) y borrado (`delete`) a cada usuario.
- **Operaciones de Archivos:** Sube, descarga, navega y elimina archivos a través de la interfaz.
- **Restricción de Tipos de Archivo:** Configura una lista blanca o negra de extensiones de archivo permitidas para subir.
- **Interfaz Moderna:** Interfaz de usuario limpia y amigable construida con Bootstrap 5.
- **Cero Dependencias Externas:** Funciona completamente con las bibliotecas estándar de Python 3.7+.

## 🚀 Empezando

Sigue estos pasos para poner en marcha el servidor.

### 1. Prerrequisitos

- Python 3.7 o superior.

### 2. Instalación

1.  **Clona el repositorio** (o descarga los archivos en un directorio).

2.  **Crea un entorno virtual** (recomendado):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # En Windows usa: venv\Scripts\activate
    ```


## ⚙️ Configuración

La configuración se gestiona a través de dos archivos JSON en la raíz del proyecto. Debes crearlos a partir de sus archivos `.example` correspondientes.

### 1. Usuarios y Permisos (`users.json`)

Este archivo define quién puede acceder al servidor y qué acciones puede realizar.

-   Copia `users.json.example` a `users.json`.
-   Edita el archivo para añadir o modificar usuarios. Cada usuario tiene:
    -   `password`: Su contraseña para iniciar sesión.
    -   `permissions`: Una lista de permisos.

**Permisos disponibles:**
-   `read`: Permite ver y descargar archivos y carpetas.
-   `write`: Permite subir nuevos archivos.
-   `delete`: Permite eliminar archivos existentes.

*Ejemplo de `users.json`:*
```json
{
    "admin": {
        "password": "tu_pass_secreta",
        "permissions": ["read", "write", "delete"]
    },
    "invitado": {
        "password": "pass_invitado",
        "permissions": ["read"]
    }
}
```

### 2. Configuración General (`config.json`)

Este archivo controla la apariencia, el directorio de archivos y las reglas de la aplicación.

-   Copia `config.json.example` a `config.json` y ajústalo según tus necesidades.

#### Título de la Aplicación

-   **`app_title`**: Cambia el valor de esta clave para personalizar el título que se muestra en la barra de navegación y en el título de la página.
    ```json
    "app_title": "Mi Servidor de Documentos"
    ```

#### Directorio de Archivos Públicos

-   El servidor utiliza el directorio `public_files/` (hardcoded) para almacenar y servir archivos. Este directorio se crea automáticamente si no existe.

#### Restricciones de Archivos
-   **`file_restrictions`**: Controla qué tipos de archivo se pueden subir.
    -   **`mode`**: Define el comportamiento.
        -   `"allow"`: Solo se permitirán las extensiones de la lista (lista blanca).
        -   `"deny"`: Se permitirán todas las extensiones **excepto** las de la lista (lista negra).
    -   **`extensions`**: La lista de extensiones de archivo (en minúsculas) a las que se aplica la regla.

*Ejemplo 1: Permitir solo imágenes y PDFs*
```json
"file_restrictions": {
    "mode": "allow",
    "extensions": [".jpg", ".jpeg", ".png", ".pdf"]
}
```

*Ejemplo 2: Bloquear ejecutables y scripts*
```json
"file_restrictions": {
    "mode": "deny",
    "extensions": [".exe", ".sh", ".bat", ".js"]
}
```

### 3. Logo de la Aplicación

Puedes personalizar el logo que aparece en la parte superior de la interfaz.

1.  Crea el directorio `static/img/`.
2.  Coloca tu archivo de logo dentro. El nombre del archivo debe ser `logo`.
3.  Las extensiones soportadas son (en orden de prioridad): `.png`, `.gif`, `.jpeg`, `.jpg`, `.svg`.

Por ejemplo, si colocas un archivo en `static/img/logo.png`, el servidor lo detectará y lo mostrará automáticamente. Si no se encuentra ningún logo, no se mostrará nada.

### 3. Ejecutar el Servidor

Una vez configurado, inicia el servidor usando uno de los scripts de ayuda:

```bash
# Iniciar el servidor
./start_server.sh

# Detener el servidor
./stop_server.sh

# Reiniciar el servidor
./restart_server.sh
```

O manualmente:
```bash
source ~/odoo-partner-tools/bin/activate  # o tu virtualenv
python3 app.py
```

El servidor estará disponible en `http://localhost:8000`.

**Nota sobre Ctrl+C**: Si el servidor no se detiene con Ctrl+C, usa el script `./stop_server.sh` o ejecuta:
```bash
lsof -ti :8000 | xargs kill -9
```

##  usage Cómo Usar

1.  Abre tu navegador y ve a `http://localhost:8000`.
2.  Serás redirigido a la página de login.
3.  Inicia sesión con uno de los usuarios que definiste en `users.json`.
4.  Navega por los directorios, sube o elimina archivos según los permisos de tu usuario.
5.  Usa el botón "Cerrar Sesión" en el menú de usuario para salir de forma segura.
