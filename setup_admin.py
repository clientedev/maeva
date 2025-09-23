#!/usr/bin/env python3
"""
Script para configuração inicial do administrador
Execute apenas uma vez no Railway: railway run python setup_admin.py
"""
import os
import sys
from datetime import datetime

def setup_admin():
    """Configuração inicial do admin - execute apenas uma vez"""
    try:
        from main import app, db
        from models import Admin
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Verificar se admin já existe
            existing_admin = Admin.query.first()
            if existing_admin:
                print("❌ Usuário admin já existe!")
                print(f"   Username: {existing_admin.username}")
                print(f"   Criado em: {existing_admin.created_at}")
                print("\n⚠️  Para resetar a senha, use:")
                print("   railway run python setup_admin.py --reset-password")
                return False
            
            # Verificar se é reset de senha
            if len(sys.argv) > 1 and sys.argv[1] == '--reset-password':
                if existing_admin:
                    new_password = input("Digite a nova senha para o admin: ")
                    if len(new_password) < 6:
                        print("❌ Senha deve ter pelo menos 6 caracteres")
                        return False
                    
                    existing_admin.password_hash = generate_password_hash(new_password)
                    db.session.commit()
                    print("✅ Senha alterada com sucesso!")
                    return True
                else:
                    print("❌ Nenhum admin existe ainda")
                    return False
            
            # Criar novo admin
            print("=== CONFIGURAÇÃO INICIAL DO ADMIN ===")
            username = input("Username do admin (padrão: admin): ").strip() or 'admin'
            
            password = input("Senha do admin (mínimo 6 caracteres): ").strip()
            if len(password) < 6:
                print("❌ Senha deve ter pelo menos 6 caracteres")
                return False
            
            confirm_password = input("Confirme a senha: ").strip()
            if password != confirm_password:
                print("❌ Senhas não coincidem")
                return False
            
            # Criar admin
            admin = Admin()
            admin.username = username
            admin.password_hash = generate_password_hash(password)
            admin.created_at = datetime.utcnow()
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin criado com sucesso!")
            print(f"   Username: {username}")
            print("   ⚠️  Guarde essas credenciais em local seguro!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao configurar admin: {e}")
        return False

def main():
    print("CONFIGURAÇÃO SEGURA DO ADMINISTRADOR")
    print("=" * 40)
    
    if setup_admin():
        print("\n✅ Configuração concluída!")
    else:
        print("\n❌ Configuração falhou!")
        sys.exit(1)

if __name__ == '__main__':
    main()