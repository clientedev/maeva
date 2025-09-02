#!/bin/bash

# Script de inicialização para Railway
# Executa migração do banco e inicia o servidor

set -e  # Exit on any error

echo "🔧 Executando migrações do banco de dados..."

# Verificar se as variáveis de ambiente necessárias existem
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL não configurada!"
    exit 1
fi

# Executar migração com timeout
timeout 60 python migrate_db.py

if [ $? -eq 0 ]; then
    echo "✅ Migrações concluídas com sucesso!"
    echo "🚀 Iniciando servidor na porta ${PORT:-5000}..."
    
    # Usar configuração otimizada para Railway
    exec gunicorn \
        --bind 0.0.0.0:${PORT:-5000} \
        --workers 1 \
        --timeout 120 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --log-level info \
        main:app
else
    echo "❌ Erro nas migrações. Código de saída: $?"
    exit 1
fi