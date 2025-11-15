#!/bin/bash
# Script para reiniciar el servidor de archivos

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Reiniciando servidor de archivos..."
echo ""

# Detener el servidor
bash stop_server.sh

echo ""
sleep 1

# Iniciar el servidor
bash start_server.sh
