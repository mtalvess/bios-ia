---
name: reels-narrados
description: Gera reels verticais narrados (1080x1920) dos serviços da BIOS, com 3 ganchos por serviço, trilha original, efeitos e narração sincronizada com as cenas. Use quando pedirem reels/vídeos curtos de serviço.
---
Modelo: `modelos/reels/`.

1. Rode `scripts/setup.sh` uma vez (instala dependências e baixa as vozes).
2. Textos: edite o dicionário `N` em `modelos/reels/build.py` (gancho A/B/C, 3 dores, demonstração, CTA) e os dados visuais em `REELS` dentro de `pack.html` (mesma ordem de serviços).
3. Gere as falas: `cd modelos/reels && python3 -I build.py tts`.
4. Gere cada vídeo: `python3 -I build.py <serviço>:<gancho>` (ex.: `1:0`), ou em paralelo:
   `for r in 1 2 3 4 5; do for h in 0 1 2; do echo $r:$h; done; done | xargs -P 3 -I{} python3 -I build.py {}`
5. Saída em `modelos/reels/saida/` (MP4 + capa PNG). Confira 4 quadros antes de entregar.

A narração é sintética (Piper pt-BR "faber"). Se o Mathias mandar a própria voz gravada, substitua os WAV de cada fala e mantenha o resto.
