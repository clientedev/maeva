#!/usr/bin/env python3
"""
Script de migração para garantir que todas as colunas necessárias existam no PostgreSQL
Execute este script sempre que adicionar novas colunas aos modelos
"""

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_columns():
    """Adiciona colunas que podem estar faltando no banco de dados"""
    
    migrations = [
        # Property table
        "ALTER TABLE property ADD COLUMN IF NOT EXISTS video_data BYTEA",
        "ALTER TABLE property ADD COLUMN IF NOT EXISTS video_filename VARCHAR(255)",
        "ALTER TABLE property ADD COLUMN IF NOT EXISTS video_content_type VARCHAR(100)",
        
        # PropertyImage table
        "ALTER TABLE property_image ADD COLUMN IF NOT EXISTS image_data BYTEA",
        "ALTER TABLE property_image ADD COLUMN IF NOT EXISTS image_filename VARCHAR(255)",
        "ALTER TABLE property_image ADD COLUMN IF NOT EXISTS image_content_type VARCHAR(100)",
        
        # Post table
        "ALTER TABLE post ADD COLUMN IF NOT EXISTS image_data BYTEA",
        "ALTER TABLE post ADD COLUMN IF NOT EXISTS image_filename VARCHAR(255)",
        "ALTER TABLE post ADD COLUMN IF NOT EXISTS image_content_type VARCHAR(100)",
        "ALTER TABLE post ADD COLUMN IF NOT EXISTS video_data BYTEA",
        "ALTER TABLE post ADD COLUMN IF NOT EXISTS video_filename VARCHAR(255)",
        "ALTER TABLE post ADD COLUMN IF NOT EXISTS video_content_type VARCHAR(100)",
    ]
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                for migration in migrations:
                    logger.info(f"Executando: {migration}")
                    conn.execute(text(migration))
                
                conn.commit()
                logger.info("✅ Todas as migrações foram aplicadas com sucesso!")
                
        except Exception as e:
            logger.error(f"❌ Erro durante migração: {e}")
            raise

def check_database_schema():
    """Verifica se todas as colunas necessárias existem"""
    
    expected_columns = {
        'property': ['video_data', 'video_filename', 'video_content_type'],
        'property_image': ['image_data', 'image_filename', 'image_content_type'],
        'post': ['image_data', 'image_filename', 'image_content_type', 
                'video_data', 'video_filename', 'video_content_type']
    }
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                for table_name, columns in expected_columns.items():
                    result = conn.execute(text(
                        f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'"
                    ))
                    existing_columns = [row[0] for row in result]
                    
                    missing = set(columns) - set(existing_columns)
                    if missing:
                        logger.warning(f"❌ Tabela {table_name} está faltando colunas: {missing}")
                        return False
                    else:
                        logger.info(f"✅ Tabela {table_name} possui todas as colunas necessárias")
                
                logger.info("✅ Schema do banco está completo!")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar schema: {e}")
            return False

if __name__ == "__main__":
    try:
        logger.info("🔍 Verificando schema do banco de dados...")
        
        # Test basic connection first
        with app.app_context():
            db.engine.connect()
            logger.info("✅ Conexão com banco de dados estabelecida")
        
        if not check_database_schema():
            logger.info("🔧 Aplicando migrações necessárias...")
            add_missing_columns()
            
            # Verificar novamente
            if check_database_schema():
                logger.info("🎉 Banco de dados atualizado com sucesso!")
            else:
                logger.error("❌ Falha ao atualizar banco de dados")
                exit(1)
        else:
            logger.info("✅ Banco de dados já está atualizado!")
            
    except Exception as e:
        logger.error(f"❌ Erro crítico na migração: {e}")
        logger.error("Tentando continuar sem migrações...")
        # Don't exit - let Railway try to start the app anyway
        exit(0)