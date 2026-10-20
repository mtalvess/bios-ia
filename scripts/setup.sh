#!/usr/bin/env bash
# Instala o que os modelos de vídeo/imagem precisam. Rode uma vez: ./scripts/setup.sh
set -e
cd "$(dirname "$0")/.."
command -v ffmpeg >/dev/null || { echo "Instale o ffmpeg (sudo apt install ffmpeg / brew install ffmpeg)"; exit 1; }
npm i --no-save playwright@1 && npx playwright install chromium
pip install numpy scipy soundfile sherpa-onnx
mkdir -p vozes && cd vozes
for v in faber cadu jeff; do
  m=vits-piper-pt_BR-$v-medium
  [ -d $m ] || { curl -L -o $m.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/$m.tar.bz2 && tar xjf $m.tar.bz2 && rm $m.tar.bz2; }
done
echo "Pronto."
