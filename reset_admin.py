#!/usr/bin/env python3
"""
Script para resetar/criar admin quando necessário
Pode ser executado manualmente se houver problemas com autenticação
"""

import os
import sys

def reset_admin():
    """Reseta o admin com as credenciais padrão"""
    try:
        from main import app
        from database import db
        from models import Admin, AdminSession
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        print("🔄 Resetando usuário admin...")
        
        with app.app_context():
            # Limpar todas as sessões antigas
            AdminSession.query.delete()
            
            # Remover admin existente se houver
            Admin.query.delete()
            db.session.commit()
            
            print("🗑️  Dados antigos removidos")
            
            # Criar novo admin
            admin = Admin()
            admin.username = 'maeva.admin'
            admin.password_hash = generate_password_hash('maeva4731')
            admin.created_at = datetime.utcnow()
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin resetado com sucesso!")
            print("🎯 Credenciais: maeva.admin / maeva4731")
            return True
            
    except Exception as e:
        print(f"❌ ERRO ao resetar admin: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔄 RESET DO ADMIN - Maeva Investimentos")
    print("=" * 50)
    
    if reset_admin():
        print("✅ Reset concluído - admin pronto para uso!")
    else:
        print("❌ Falha no reset - verifique os logs")
        sys.exit(1)