# BIOS IA

A "equipe de IA" da BIOS: agentes, receitas (skills), modelos de vídeo/design e rotinas automáticas para o Claude Code trabalhar pela empresa, sempre com aprovação do dono.

## A equipe (`.claude/agents/`)
| Agente | Faz |
|---|---|
| `diretor` | Recebe pedidos amplos, planeja e delega |
| `conteudo` | Plano semanal, ganchos A/B/C, roteiros, legendas |
| `designer` | Posts, stories, carrosséis, capas |
| `video` | Reels narrados, filme de marca, convites animados |
| `dev-sites` | Sites, cardápios digitais, landing pages |
| `comercial` | Propostas, orçamentos, respostas de direct/WhatsApp |
| `relatorios` | Desempenho e próximos passos |

## Receitas (`.claude/skills/`)
`reels-narrados` · `filme-de-marca` · `convite-animado` · `site-cardapio` · `plano-semanal`

## Como usar
1. Abra este repositório no Claude Code (app, web em claude.ai/code ou terminal).
2. Peça em linguagem normal, por exemplo:
   - "Diretor: monta a campanha de cardápio digital para lanchonetes deste mês"
   - "Faz o plano semanal"
   - "Cria um cardápio digital para a Pizzaria X" (mande os dados)
   - "Gera os reels do serviço AGENDA"
3. Para vídeos, rode antes `./scripts/setup.sh` (uma vez).

## Rotinas automáticas
Veja `automacoes/tarefas-agendadas.md`. Respostas automáticas do Instagram: `automacoes/manychat.md`.

## Regras
Contexto, marca e regras da empresa ficam em `CLAUDE.md`. Nada é publicado ou enviado sem aprovação.
