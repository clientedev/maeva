# Deploy no Railway - Solução COMPLETA

## ✅ O que foi resolvido

O erro `column property.video_data does not exist` + problema de inicialização foram resolvidos.

## 🔧 Arquivos criados/modificados

1. **`start.sh`** - Script robusto com verificações de erro
2. **`railway.json`** - Configuração otimizada para Railway
3. **`Procfile`** - Comando de inicialização direto
4. **`nixpacks.toml`** - Configuração de build alternativa
5. **Deploy config** - Configurado com timeout adequado

## 🚀 Como fazer o deploy

### Opção 1: Push para repositório (Recomendado)
```bash
git add .
git commit -m "Fix railway deployment"
git push
```

### Opção 2: Railway CLI
```bash
railway up
```

### Opção 3: Re-deploy manual na Railway
1. Acesse Railway dashboard
2. Clique em "Deploy" 
3. Aguarde o processo completar

## 🔄 O que acontece no deploy

1. **Migração automática**: `python migrate_db.py` executa primeiro
2. **Criação de colunas**: Adiciona `video_data`, `video_filename`, `video_content_type`
3. **Setup do admin**: `python setup_railway_admin.py` cria usuário admin
4. **Servidor otimizado**: Gunicorn com configurações para Railway
5. **Healthcheck**: Verifica se aplicação responde corretamente

## 👤 Admin no Railway

**Credenciais sempre funcionais após deploy:**
- Usuário: `maeva.admin`
- Senha: `maeva4731`

O script `setup_railway_admin.py` garante que o admin seja criado/atualizado a cada deploy.

## ⚙️ Configurações aplicadas

- **Workers**: 1 (otimo para Railway)
- **Timeout**: 120s (evita timeouts)
- **Keep-alive**: 2s (conexões estáveis)
- **Health check**: 300s timeout
- **Restart policy**: Always

## 🔍 Verificação pós-deploy

✅ Site carrega sem erros  
✅ Logs mostram "Migrações concluídas com sucesso!"  
✅ Gunicorn inicia corretamente  
✅ Aplicação responde na porta $PORT  

Se ainda houver problemas, verifique os logs da Railway em real-time.