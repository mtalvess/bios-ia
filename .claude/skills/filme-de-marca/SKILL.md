---
name: filme-de-marca
description: Gera o filme de marca cinematográfico de 15s da BIOS (barras de cinema, glitch, voo 3D entre aparelhos, revelação do logo) com design de som original. Use para vídeos institucionais/de impacto.
---
Modelo: `modelos/filme-marca/`.

1. Textos e cenas: `cinema.html` (abertura, dores, palavras de serviço, final com "Comenta PROJETO").
2. Trilha: `python3 -I cinema_audio.py trilha.wav` (sincronizada com os tempos fixos do HTML; se mudar tempos, ajuste os dois).
3. Vídeo com desfoque de movimento: `FPS=60 node render.js cinema.html bruto60.mp4 15`, depois
   `ffmpeg -i bruto60.mp4 -i trilha.wav -filter_complex "[0:v]tmix=frames=2:weights='1 1',fps=30[v]" -map "[v]" -map 1:a -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1 -c:a aac -b:a 192k -t 15 filme.mp4`
4. Quando houver telas reais de projetos de clientes, substitua os mockups dos aparelhos no mundo 3D.
