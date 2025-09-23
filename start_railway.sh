#!/bin/bash
set -e

echo "=== RAILWAY STARTUP ==="
echo "Verificando ambiente..."

# Verificar variáveis críticas
if [ -z "$SESSION_SECRET" ]; then
    echo "❌ SESSION_SECRET não configurada!"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não configurada!"
    exit 1
fi

echo "✅ Variáveis de ambiente OK"

# Executar migração
echo "Executando migração..."
python migrate_railway.py

# Iniciar aplicação
echo "Iniciando aplicação..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload main:app
