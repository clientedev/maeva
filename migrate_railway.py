#!/usr/bin/env python3
"""
Migração de database para Railway
"""
import os
import sys
from datetime import datetime

try:
    print(f"[{datetime.now()}] Iniciando migração...")
    
    # Import da aplicação
    from main import app, db
    
    with app.app_context():
        print("Conectando ao database...")
        
        # Importar todos os modelos
        from models import (
            Property, PropertyImage, Post, 
            Admin, AdminSession, 
            ChatbotConversation, ContactMessage
        )
        
        print("Criando tabelas...")
        db.create_all()
        
        print("Verificando usuário admin...")
        admin = Admin.query.first()
        if not admin:
            from werkzeug.security import generate_password_hash
            
            # Criar admin padrão
            admin = Admin()
            admin.username = 'admin'
            admin.password_hash = generate_password_hash('admin123')
            admin.created_at = datetime.utcnow()
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Usuário admin criado com senha padrão: admin123")
            print("⚠️  IMPORTANTE: Mude a senha após o primeiro login!")
        else:
            print("✅ Usuário admin já existe")
        
        print("✅ Migração concluída com sucesso!")
        
except Exception as e:
    print(f"❌ Erro na migração: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
