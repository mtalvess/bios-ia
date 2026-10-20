---
name: convite-animado
description: Gera convite digital animado de aniversário (vídeo vertical + imagem) a partir de dados do cliente, com trilha e efeitos. Use quando um cliente pedir convite animado.
---
Modelo base: `modelos/convite-brinquedos/convite.html` (tema original de brinquedos, sem personagens de terceiros, pode ser vendido).

1. Edite o objeto `D` no topo do HTML (nome, idade, data, hora, local, confirmação).
2. Prévia: `node render.js convite.html previa 18 1.6,5.6,16.5`.
3. Vídeo: `node render.js convite.html convite.mp4 18`, depois some uma trilha (componha no estilo de `modelos/reels/audio.py`) com ffmpeg e normalize a -14 LUFS.

Personagens licenciados (Sonic, Disney…): só para uso pessoal do cliente, com imagens que **o cliente** fornecer; nunca como produto de catálogo da BIOS.
