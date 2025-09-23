#!/usr/bin/env python3
"""
Script para resetar senha do admin no Railway
Execute: railway run python reset_railway_admin.py
"""
import os
import sys
from datetime import datetime

def reset_admin_password():
    """Reset da senha do admin no Railway"""
    try:
        print("=== RESET SENHA ADMIN NO RAILWAY ===")
        
        from main import app, db
        from models import Admin
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Verificar se admin existe
            admin = Admin.query.first()
            
            if not admin:
                print("❌ Nenhum usuário admin encontrado no banco do Railway!")
                print("Criando novo admin...")
                
                admin = Admin()
                admin.username = 'admin'
                admin.password_hash = generate_password_hash('admin123')
                admin.created_at = datetime.utcnow()
                db.session.add(admin)
                db.session.commit()
                
                print("✅ Novo admin criado!")
            else:
                print(f"✅ Admin encontrado: {admin.username}")
                print("Resetando senha...")
                
                # Reset senha para admin123
                admin.password_hash = generate_password_hash('admin123')
                db.session.commit()
                
                print("✅ Senha resetada!")
            
            print()
            print("🔑 CREDENCIAIS DE ACESSO:")
            print("   Usuário: admin")
            print("   Senha: admin123")
            print()
            print("⚠️  IMPORTANTE: Mude a senha após fazer login!")
            print("   Acesse: https://sua-app.railway.app/admin")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if reset_admin_password():
        print("\n✅ Reset concluído com sucesso!")
    else:
        print("\n❌ Reset falhou!")
        sys.exit(1)

if __name__ == '__main__':
    main()