#!/bin/bash
# Script para detener el servidor de archivos

echo "🛑 Deteniendo servidor de archivos..."

# Encontrar y matar todos los procesos usando el puerto 8000
PIDS=$(lsof -ti :8000 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✅ No hay servidor corriendo en el puerto 8000"
    exit 0
fi

for PID in $PIDS; do
    echo "   Matando proceso $PID..."
    kill -9 $PID 2>/dev/null
done

sleep 1

# Verificar si se detuvo correctamente
if lsof -ti :8000 > /dev/null 2>&1; then
    echo "❌ Error: No se pudo detener el servidor"
    exit 1
else
    echo "✅ Servidor detenido correctamente"
fi
