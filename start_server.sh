#!/bin/bash
# Script para iniciar el servidor de archivos

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar virtualenv
source ~/odoo-partner-tools/bin/activate

# Verificar si el puerto 8000 está en uso
if lsof -ti :8000 > /dev/null 2>&1; then
    echo "⚠️  El puerto 8000 ya está en uso"
    echo "Usa stop_server.sh para detener el servidor existente"
    exit 1
fi

# Iniciar el servidor
echo "🚀 Iniciando servidor de archivos..."
python3 app.py

