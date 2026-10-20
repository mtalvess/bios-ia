# Rotinas automáticas da BIOS IA

Criadas como tarefas agendadas do Claude Code (claude.ai/code), rodando neste repositório. Cada rotina **prepara** e o Mathias **aprova**.

| Rotina | Quando | O que faz |
|---|---|---|
| Plano semanal de conteúdo | Segunda, 7h45 (Recife) | Skill `plano-semanal` → `saida/plano-*.md` |
| Ideias de gancho | Quarta, 7h45 | 10 ganchos novos baseados no que mais funcionou (agente `conteudo`) |
| Relatório semanal | Sexta, 17h45 | Agente `relatorios` com os dados que o Mathias colar ou dos plugins conectados |

Prompt da rotina de segunda:
> Use o agente diretor e a skill plano-semanal para montar o plano de conteúdo desta semana da BIOS. Salve o arquivo, faça commit numa branch `plano/AAAA-MM-DD` e me resuma os 5 posts para aprovação. Não publique nada.
