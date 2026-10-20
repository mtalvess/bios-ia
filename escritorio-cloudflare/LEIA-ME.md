# Escritório BIOS IA na Cloudflare

Tudo funcional fora do claude.ai: site + API (Pages Functions) + banco D1 + Diretor com Claude.

```
escritorio-cloudflare/
├── public/index.html          ← o escritório (pixel art, quadro, equipe, atividade)
├── functions/api/[[path]].js  ← API: estado, tarefas, atividade e o Diretor (Claude)
├── seed.json                  ← tarefas e atividade atuais (entram no 1º acesso)
├── package.json               ← dependências (SDK da Anthropic + wrangler)
└── wrangler.toml              ← configuração do projeto e do banco D1
```

Você vai precisar de 3 coisas:
- **Banco D1** (grátis): https://dash.cloudflare.com/?to=/:account/workers/d1
- **Chave da API do Claude** (para o Diretor): https://console.anthropic.com/settings/keys
- **Uma senha** que só você sabe (protege o escritório e a sua chave)

---

## Opção A: pelo GitHub (recomendado, sem instalar nada)

O código já está no repositório `mtalvess/bios-ia`, na pasta `escritorio-cloudflare`.

1. **Criar o banco D1:** https://dash.cloudflare.com/?to=/:account/workers/d1 › **Create** › nome `escritorio-bios-ia`.
2. **Criar o projeto Pages:** https://dash.cloudflare.com/?to=/:account/workers-and-pages/create/pages › **Connect to Git** › escolha `mtalvess/bios-ia`.
   - **Root directory:** `escritorio-cloudflare`
   - **Build command:** `npm install`
   - **Build output directory:** `public`
   - **Save and Deploy**
3. **Ligar o banco:** no projeto › **Settings › Bindings › Add › D1 database**: Variable name `DB`, banco `escritorio-bios-ia`.
4. **Variáveis:** **Settings › Variables and Secrets › Add**:
   - `SENHA`: a sua senha (tipo Secret)
   - `ANTHROPIC_API_KEY`: sua chave do Claude (tipo Secret)
5. **Publicar de novo** para aplicar: **Deployments › … › Retry deployment**.
6. Abra o endereço `https://escritorio-bios-ia.pages.dev` (ou o que a Cloudflare mostrar) e entre com a senha.

Domínio próprio (ex.: `escritorio.seudominio.com.br`): projeto › **Custom domains** › **Set up a custom domain**.

## Opção B: pelo terminal (wrangler)

```bash
cd escritorio-cloudflare
npm install
npx wrangler login
npx wrangler d1 create escritorio-bios-ia      # copie o database_id para o wrangler.toml
npx wrangler pages project create escritorio-bios-ia
npx wrangler pages secret put SENHA --project-name escritorio-bios-ia
npx wrangler pages secret put ANTHROPIC_API_KEY --project-name escritorio-bios-ia
npm run deploy
```

Testar no computador antes: `npx wrangler pages dev public --binding SENHA=teste` (a chave do Claude vai no arquivo `.dev.vars`: `ANTHROPIC_API_KEY=...`).

> O upload por "arrastar e soltar" no painel da Cloudflare **não** serve aqui: ele só publica a página, sem a API e sem o banco. Use a opção A ou B.

---

## Como funciona
- As tabelas do banco são criadas sozinhas no primeiro acesso, já com as 11 tarefas e a atividade de hoje (`seed.json`).
- A página atualiza a cada 5 segundos. Abra em vários dispositivos que tudo fica sincronizado.
- **Novo pedido:** o servidor chama o Claude (modelo `claude-opus-5-5`, com fallback automático do servidor caso o modelo recuse), cria as tarefas no quadro e registra a atividade. Cada pedido gasta um pouco de crédito da sua conta da Anthropic.
- A senha fica salva no navegador. Para sair, limpe os dados do site.

## Os agentes do Claude Code atualizando o escritório
Qualquer agente (ou você) pode mexer no quadro pela API, sempre com a senha:

```bash
URL=https://escritorio-bios-ia.pages.dev
# criar tarefa
curl -X POST $URL/api/tarefas -H "x-senha: SUA_SENHA" -H "content-type: application/json" \
  -d '{"titulo":"Carrossel de agendamento","agente":"designer","status":"fazendo"}'
# mudar status
curl -X PATCH $URL/api/tarefas/ID_DA_TAREFA -H "x-senha: SUA_SENHA" -H "content-type: application/json" -d '{"status":"aprovar"}'
# registrar atividade
curl -X POST $URL/api/atividade -H "x-senha: SUA_SENHA" -H "content-type: application/json" \
  -d '{"agente":"designer","texto":"entregou o carrossel para aprovação"}'
# ver tudo
curl $URL/api/estado -H "x-senha: SUA_SENHA"
```

Agentes válidos: `diretor`, `conteudo`, `designer`, `video`, `dev-sites`, `comercial`, `relatorios`.
Status: `afazer`, `fazendo`, `aprovar`, `feito`.
