#!/bin/bash

# Script de inicialização para Railway
# Executa migração do banco e inicia o servidor

echo "🔧 Executando migrações do banco de dados..."
python migrate_db.py

if [ $? -eq 0 ]; then
    echo "✅ Migrações concluídas com sucesso!"
    echo "🚀 Iniciando servidor..."
    gunicorn --bind 0.0.0.0:${PORT:-5000} main:app
else
    echo "❌ Erro nas migrações. Saindo..."
    exit 1
fi