# Deploy no Railway - Solução para o erro PostgreSQL

## O que foi resolvido

O erro `column property.video_data does not exist` acontecia porque o banco PostgreSQL da Railway não tinha as colunas mais recentes do modelo.

## Arquivos criados/modificados

1. **`start.sh`** - Script que executa a migração antes de iniciar o servidor
2. **`railway.json`** - Configuração específica da Railway
3. **`Procfile`** - Comando de inicialização alternativo
4. **Deploy config** - Configurado para usar o `start.sh`

## Como fazer o deploy

### Opção 1: Re-deploy automático
1. Faça push das mudanças para seu repositório
2. A Railway vai automaticamente:
   - Executar `migrate_db.py` 
   - Criar as colunas que estão faltando
   - Iniciar o servidor
   
### Opção 2: Railway CLI
```bash
railway up
```

### Opção 3: Deploy manual
Na Railway dashboard:
1. Vá para seu projeto
2. Clique em "Deploy"
3. O script `start.sh` será executado automaticamente

## O que acontece agora

✅ Toda vez que você fizer deploy, a migração será executada automaticamente
✅ As colunas `video_data`, `video_filename` e `video_content_type` serão criadas
✅ O erro será resolvido permanentemente
✅ Seu site voltará a funcionar normalmente

## Verificação

Depois do deploy, seu site deve carregar sem erros. Você pode verificar os logs da Railway para confirmar que a migração foi executada com sucesso.