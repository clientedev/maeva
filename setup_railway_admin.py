#!/usr/bin/env python3
"""
Script para criar o usuário admin no Railway
Executa automaticamente durante o deploy para garantir autenticação
"""

import os
import sys
from datetime import datetime

def setup_admin():
    """Cria o usuário admin para Railway com credenciais fixas"""
    try:
        # Import Flask app and database
        from main import app
        from database import db
        from models import Admin
        from werkzeug.security import generate_password_hash
        
        print("🔧 [RAILWAY SETUP] Configurando usuário admin...")
        
        with app.app_context():
            # Verificar se já existe admin
            existing_admin = Admin.query.filter_by(username='maeva.admin').first()
            
            if existing_admin:
                print("✅ [RAILWAY SETUP] Admin 'maeva.admin' já existe - atualizando senha...")
                # Atualizar senha para garantir que funcione
                existing_admin.password_hash = generate_password_hash('maeva4731')
                existing_admin.last_login = None  # Reset last login
                db.session.commit()
                print("✅ [RAILWAY SETUP] Senha do admin atualizada com sucesso!")
            else:
                print("🔧 [RAILWAY SETUP] Criando novo usuário admin...")
                # Criar novo admin com credenciais fixas
                admin = Admin()
                admin.username = 'maeva.admin'
                admin.password_hash = generate_password_hash('maeva4731')
                admin.created_at = datetime.utcnow()
                
                db.session.add(admin)
                db.session.commit()
                print("✅ [RAILWAY SETUP] Admin 'maeva.admin' criado com sucesso!")
            
            # Verificar se admin foi criado/atualizado corretamente
            admin_check = Admin.query.filter_by(username='maeva.admin').first()
            if admin_check:
                print(f"✅ [RAILWAY SETUP] Verificação: Admin '{admin_check.username}' está no banco de dados")
                print("🎯 [RAILWAY SETUP] Credenciais: maeva.admin / maeva4731")
                return True
            else:
                print("❌ [RAILWAY SETUP] ERRO: Admin não encontrado após criação!")
                return False
                
    except Exception as e:
        print(f"❌ [RAILWAY SETUP] ERRO ao configurar admin: {e}")
        print(f"❌ [RAILWAY SETUP] Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        from main import app
        from database import db
        from sqlalchemy import text
        
        with app.app_context():
            # Teste simples de conexão
            db.session.execute(text('SELECT 1'))
            print("✅ [RAILWAY SETUP] Conexão com banco de dados OK")
            return True
    except Exception as e:
        print(f"❌ [RAILWAY SETUP] ERRO na conexão com banco: {e}")
        return False

def main():
    """Função principal do script"""
    print("=" * 60)
    print("🚀 [RAILWAY SETUP] Iniciando configuração do admin...")
    print("=" * 60)
    
    # Verificar se estamos no Railway (opcional)
    if os.environ.get('RAILWAY_ENVIRONMENT_NAME'):
        print(f"🚂 [RAILWAY SETUP] Ambiente Railway: {os.environ.get('RAILWAY_ENVIRONMENT_NAME')}")
    
    # Testar conexão com banco
    if not test_database_connection():
        print("❌ [RAILWAY SETUP] Falha na conexão - interrompendo setup")
        sys.exit(1)
    
    # Configurar admin
    if setup_admin():
        print("✅ [RAILWAY SETUP] Configuração concluída com sucesso!")
        print("🎯 [RAILWAY SETUP] Use: maeva.admin / maeva4731 para login")
        sys.exit(0)
    else:
        print("❌ [RAILWAY SETUP] Falha na configuração do admin")
        sys.exit(1)

if __name__ == "__main__":
    main()