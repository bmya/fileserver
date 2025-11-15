# Project Overview

This project is a secure, session-based file server built with Python's standard libraries. It features a Model-View-Controller (MVC) like architecture, providing a clean separation of concerns between data handling, business logic, and presentation. The application uses a modern Bootstrap 5 frontend and supports multiple users with granular permissions.

## Key Components

### 1. Configuration
- **`users.json`**: Defines all users, their passwords, and a list of their permissions (`read`, `write`, `delete`). This file is critical for the application to run. An example file `users.json.example` is provided.
- **`config.json`**: Contains application-level settings:
  - `app_title`: Application title displayed in the interface
  - `port`: Server port (defaults to 8000)
  - `max_file_size_mb`: Maximum file upload size in megabytes (defaults to 3000 MB / 3 GB)
  - `file_restrictions`: File type restrictions with `mode` (`allow` or `deny`) and a list of file `extensions`
  - An example file `config.json.example` is provided.
- **`.gitignore`**: Excludes configuration files, user-uploaded files (`public_files/`), and Python artifacts from version control.

### 2. Architecture (MVC)

- **`app.py` (Entry Point)**: A minimal script responsible for initializing and running the `TCPServer` with the main request handler. It now loads the server port from `config.json` (defaulting to 8000).

- **Models (`models/`)**:
    - **`user.py`**: Contains the `UserManager` class, which loads `users.json`, verifies user credentials, and checks permissions.
    - **`session.py`**: Contains the `SessionManager` class, which handles the entire session lifecycle. It creates session IDs, stores them in memory mapped to a username, validates incoming session cookies, and handles session deletion (logout).

- **Views (`views/`)**:
    - **`login.html`**: The user login page with a username/password form.
    - **`file_browser.html`**: The main interface for authenticated users. It uses placeholder comments (`<!-- ... -->`) and template strings (`{{...}}`) to be dynamically rendered by the controller. It includes conditional blocks for features based on user permissions (e.g., `<!-- IF_WRITE_PERMISSION -->`).
    - **`unauthorized.html`**: A simple, styled page for 401 errors.

- **Controller (`controllers/handler.py`)**:
    - This is the core of the application, containing the `AuthMVC_Handler` class.
    - **Configuration Loading**: It loads `app_title`, `file_restrictions`, and `max_file_size_mb` directly from `config.json`. The public files directory is hardcoded to `public_files/`.
    - **Routing**: It inspects `self.path` to route `GET` and `POST` requests to the appropriate logic (e.g., `/login`, `/logout`, static files, or file operations).
    - **Session Handling**: It reads session cookies on incoming requests to identify the user and sets cookies on login/logout. It redirects unauthenticated users to `/login`.
    - **Permission Checks**: Before performing any action (`render_directory_listing`, `do_POST`, `do_DELETE`), it calls the `user_manager` to verify if the logged-in user has the required permissions.
    - **Dynamic Rendering**: The `render_view` method reads HTML templates, injects dynamic data (like the file list or username), and conditionally renders UI blocks based on permissions before sending the final HTML to the client.
    - **File Operations**:
        - Implements `do_POST` for file uploads with validation against `config.json` (file type restrictions and maximum file size)
        - File size is validated before reading the upload body, returning HTTP 413 if the file exceeds `max_file_size_mb`
        - Implements `do_DELETE` for file deletion
    - **Directory Listing**: The `render_directory_listing` method displays files in a table format showing:
        - File/folder name with appropriate icons
        - File size (formatted as B, KB, MB, or GB; directories show "-")
        - Modification date and time (YYYY-MM-DD HH:MM format)
        - Delete button (if user has delete permission)

### 3. Static & Public Files
- **`static/`**: Contains static assets for the web application itself, like custom CSS and the application logo.
- **`public_files/`**: The root directory where user-uploaded files are stored and served from. This directory is hardcoded and excluded from version control.

## Recent Changes and Current Status

Due to issues encountered with dynamic configuration of the public files directory and server port, the project has reverted to a simpler, more stable configuration approach.

*   **Public Files Directory**: The directory for serving and uploading user files is now **hardcoded** to `public_files/`. Attempts to make this configurable via `config.json` led to unexpected behavior and have been rolled back.
*   **Server Port**: The server port is now loaded from `config.json` (key: `port`), defaulting to `8000` if not specified. This allows users to change the port if `8000` is already in use.
*   **Logo Display**: Issues with the logo not displaying correctly have been addressed by reverting the static file handling logic in `controllers/handler.py` to a proven method.
*   **Configuration Centralization**: The attempt to centralize all configuration into a `config.py` module has been reverted. Configuration is now loaded directly in `app.py` (for port) and `controllers/handler.py` (for app title and file restrictions).

This approach prioritizes stability and functionality, ensuring the core features work as expected.

## Development & Running

1.  **Setup**: Before running, ensure `users.json` and `config.json` exist (copied from their `.example` counterparts).
2.  **Execution**: Run `python3 app.py`.
3.  **Authentication Flow**:
    - An unauthenticated user visiting any page is redirected to `/login`.
    - A `POST` to `/login` with correct credentials creates a session, sets a `session_id` cookie, and redirects to `/`.
    - Subsequent requests are authenticated via the session cookie.
    - A `GET` to `/logout` clears the session and the cookie, redirecting to `/login`.