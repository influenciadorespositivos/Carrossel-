# Carrossel automático para Instagram (grátis)

## Como funciona
1. Você escreve os posts em `posts.csv` (data, slides separados por `|`, legenda).
2. Todo dia às 09:00 (Brasília) o GitHub Actions gera as imagens, publica no Instagram e registra em `posted.txt`.

## Testar no computador (sem postar)
    pip install -r requirements.txt
    python generate.py        # cria a pasta preview/ com todos os carrosséis

## Configuração (uma vez só)
### A) Repositório no GitHub
1. Crie uma conta em github.com e um repositório **público** (ex.: `carrossel`). Público é necessário para o Instagram baixar as imagens.
2. Envie todos os arquivos deste projeto (inclusive a pasta `.github`).
3. Em Settings > Actions > General > Workflow permissions, marque "Read and write permissions".

### B) Token do Instagram
1. Acesse developers.facebook.com, crie um app do tipo "Business" (ou "Outro").
2. Adicione o produto/caso de uso de **API do Instagram** (Instagram Graph API).
3. Abra a ferramenta **Graph API Explorer**, selecione seu app e gere um token de usuário com as permissões:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`.
4. Troque por token de longa duração (abra no navegador, trocando os valores):
   `https://graph.facebook.com/v23.0/oauth/access_token?grant_type=fb_exchange_token&client_id=ID_DO_APP&client_secret=SEGREDO_DO_APP&fb_exchange_token=TOKEN_CURTO`
5. Com o token longo, abra `https://graph.facebook.com/v23.0/me/accounts?access_token=TOKEN_LONGO`.
   O `access_token` que aparece na sua Página é o **token da Página, que não expira**. Guarde-o, e anote o `id` da Página.
6. Pegue o ID do Instagram: `https://graph.facebook.com/v23.0/ID_DA_PAGINA?fields=instagram_business_account&access_token=TOKEN_DA_PAGINA`
   O número em `instagram_business_account.id` é o seu **IG_USER_ID**.

### C) Segredos no GitHub
Em Settings > Secrets and variables > Actions > New repository secret, crie:
- `IG_USER_ID` = o ID do passo B6
- `IG_ACCESS_TOKEN` = o token da Página do passo B5

### D) Testar
Aba **Actions** > "Postar carrossel diário" > **Run workflow**. Se houver post com a data de hoje em `posts.csv`, ele será publicado.

## Regras do posts.csv
- Data no formato AAAA-MM-DD.
- De 2 a 10 slides por carrossel, separados por `|`.
- Slide 1 é a capa (texto maior, em dourado): escreva um gancho forte.
- Para mudar cores, perfil ou horário: `config.py` e `.github/workflows/postar.yml`.
