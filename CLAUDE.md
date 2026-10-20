# BIOS: contexto da empresa (leia antes de qualquer tarefa)

## Quem somos
- **BIOS**: tecnologia aplicada ao crescimento de pequenos negócios.
- Instagram: **@b1os.fc** · Campina Grande-PB · atende pequenos negócios locais (lanchonetes, barbearias, salões, lojas, clínicas).
- Serviços: **sites profissionais, cardápios digitais, aplicativos (ex.: agendamento), sistemas de gestão, automação de atendimento** (WhatsApp/Instagram).
- Projetos reais já entregues (podem ser citados como case): Emilly Lanches (emillylanches.com.br), Trança Bar e Conveniência.

## Identidade visual
- Nome sempre **BIOS** (nunca "Biosserviços").
- Cores: fundo `#020A1C`, painel `#0A1A3A`, azul `#0965FA` (botões/CTA), ciano `#2EC5FF` (destaques), texto `#F5F8FF`, texto secundário `#A4B4D0`.
- Fontes: **Anton** (títulos, caixa alta) + **Inter** (texto). Arquivos em `marca/fontes/`.
- Logo: `marca/logo.svg` (recriação vetorial; trocar pelo arquivo oficial quando houver).
- Visual: escuro, tecnológico, brilho ciano, nada de emoji em peças de design.

## Tom de voz
- Português do Brasil, direto, próximo, sem jargão técnico. Fala de **resultado** (vender mais, perder menos tempo, organizar), não de tecnologia.
- Todo conteúdo termina com chamada clara: "Comenta PALAVRA que eu te mando no direct" (CARDÁPIO, SITE, AGENDA, SISTEMA, AUTO, PROJETO).

## Regras da empresa (valem para todos os agentes)
1. **Nada é publicado, enviado a cliente ou cobrado sem aprovação do Mathias.** Agentes preparam rascunhos; o dono aprova.
2. **Não inventar números, depoimentos ou clientes.** Faltou dado → deixar `[PREENCHER]`.
3. **Direitos autorais:** em peças **comerciais** da BIOS, não usar personagens, logos ou músicas de terceiros (Disney, SEGA etc.). Uso pessoal de cliente só com imagens que o próprio cliente fornecer.
4. Preços e prazos só os que o Mathias definir (ver `automacoes/precos.md` quando existir).
5. Entregáveis vão para `saida/` (fora do git) e, quando forem para outras pessoas, viram link/artefato.

## Mapa do repositório
- `.claude/agents/`: a equipe (diretor, conteudo, designer, video, dev-sites, comercial, relatorios).
- `.claude/skills/`: receitas repetíveis (reels narrados, filme de marca, convite animado, site de cardápio, plano semanal).
- `modelos/`: código-fonte dos modelos já produzidos (reels, filme, convite, criativos).
- `automacoes/`: tarefas agendadas, ManyChat, prompts de rotina.
- `scripts/setup.sh`: instala tudo que os modelos precisam (Node, Playwright, ffmpeg, vozes).

## Escritório BIOS IA (painel da equipe)
- Painel ao vivo: https://claude.ai/artifact/BCy8bwKmWfscNjWPtFYifH (código em `escritorio/index.html`).
- Ao começar uma tarefa, o agente atualiza o banco do painel com a ferramenta ArtifactData (coleção `tarefas`: `titulo`, `agente` = id do agente, `detalhe`, `status` = afazer|fazendo|aprovar|feito, `ts` = epoch ms). Ao terminar, `status: "aprovar"` (o Mathias aprova) e uma linha em `atividade` (`agente`, `texto`, `ts`).
