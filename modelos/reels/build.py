"""Gera narração, linha do tempo, vídeo e áudio de cada reels, e junta tudo em mp4."""
import hashlib, json, math, os, subprocess, sys
import soundfile as sf

BASE = os.path.dirname(os.path.abspath(__file__))
VOZ = os.environ.get('VOZ_DIR', os.path.join(BASE, '..', '..', 'vozes'))
WORK = os.path.join(BASE, 'work'); os.makedirs(WORK, exist_ok=True)
OUT = os.path.join(BASE, 'saida'); os.makedirs(OUT, exist_ok=True)
VOICE = os.environ.get('VOICE', 'faber')
SPEED = float(os.environ.get('SPEED', '1.08'))
NAMES = {1: 'cardapio', 2: 'site', 3: 'agenda', 4: 'sistema', 5: 'automacao'}
KW = {1: 'CARDÁPIO', 2: 'SITE', 3: 'AGENDA', 4: 'SISTEMA', 5: 'AUTO'}
TOAST_AT = {1: 3.3, 2: 3.5, 3: 3.4, 4: 3.4, 5: 3.9}
TAPS = {1: [1.0, 1.8, 2.8], 2: [1.7, 3.0], 3: [1.2, 2.4], 4: [2.9], 5: [2.7]}
AUTO = 'E essa mensagem chega no automático.'
N = {
 1: dict(hooks=['Sua lanchonete ainda recebe pedido por áudio?', 'Para de anotar pedido no caderno.', 'Cardápio em foto borrada? Tem jeito melhor.'],
         prob=['Áudio de dois minutos pra um pedido.', 'Foto borrada do cardápio.', 'Pedido anotado errado.', 'E pedido errado... é cliente que não volta.'],
         demo=['Agora imagina: o cliente abre seu cardápio digital, escolhe, toca em pedir...', 'e o pedido chega prontinho no seu uótsap.'],
         cta=['Comenta cardápio, que eu te mando como funciona.', AUTO]),
 2: dict(hooks=['Seu cliente te procura no gúgou. Ele te acha?', 'Só Instagram não é site.', 'Não tá no gúgou? Tá perdendo pro concorrente.'],
         prob=['Você não aparece no gúgou.', 'O cliente não acha seu endereço, nem seu horário.', 'E o perfil fica com cara de amador.', 'Quem não é visto... não é lembrado.'],
         demo=['Com um site profissional, ele te encontra na pesquisa, vê que você é sério...', 'e te chama no uótsap com um toque.'],
         cta=['Comenta site, que eu te mando uns exemplos.', AUTO]),
 3: dict(hooks=['Você passa o dia respondendo: tem horário?', 'Seu cliente marca horário sozinho. Até de madrugada.', 'Sua agenda ainda é no papel?'],
         prob=['Tem horário hoje? O dia inteiro.', 'Agenda no papel, horário duplicado.', 'Cliente que esquece e não aparece.', 'Horário vazio... é dinheiro perdido.'],
         demo=['Com o ép de agendamento, o cliente escolhe o serviço, o horário, e confirma sozinho...', 'vinte e quatro horas por dia.'],
         cta=['Comenta agenda, que eu te mostro como funciona.', AUTO]),
 4: dict(hooks=['Você sabe quanto o seu negócio lucrou esse mês?', 'Planilha que ninguém atualiza não é gestão.', 'Três sinais de que você precisa de um sistema.'],
         prob=['Estoque no acho que tem.', 'Caixa que não fecha no fim do dia.', 'Planilha sempre desatualizada.', 'Sem controle... o lucro some.'],
         demo=['Com o sistema de gestão, você acompanha tudo pelo celular, e ele te avisa antes de faltar produto...', 'vendas, estoque e caixa, num painel só.'],
         cta=['Comenta sistema, que eu te mando uma demonstração.', AUTO]),
 5: dict(hooks=['Seu negócio pode atender sozinho. Olha só.', 'Ainda responde a mesma pergunta o dia todo?', 'Cliente mandou mensagem às onze da noite. Quem respondeu?'],
         prob=['A mesma pergunta, o dia todo.', 'Cliente esperando resposta.', 'Venda perdida fora do horário.', 'Demorou pra responder... perdeu a venda.'],
         demo=['Com a automação, seu uótsap responde na hora, mostra o cardápio e leva o cliente até o pedido...', 'mesmo enquanto você dorme.'],
         cta=['Comenta auto, e vê na prática.', 'Porque essa mensagem que você vai receber... é automática.']),
}

_tts = None
def tts(text):
    global _tts
    key = hashlib.md5(f'{VOICE}|{SPEED}|{text}'.encode()).hexdigest()[:12]
    raw, fin = f'{WORK}/{key}.raw.wav', f'{WORK}/{key}.wav'
    if not os.path.exists(fin):
        if _tts is None:
            import sherpa_onnx
            d = f'{VOZ}/vits-piper-pt_BR-{VOICE}-medium'
            cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=f'{d}/pt_BR-{VOICE}-medium.onnx', tokens=f'{d}/tokens.txt', data_dir=f'{d}/espeak-ng-data',
                noise_scale=0.72, noise_scale_w=0.85), num_threads=4))
            _tts = sherpa_onnx.OfflineTts(cfg)
        a = _tts.generate(text, sid=0, speed=SPEED)
        sf.write(raw, a.samples, a.sample_rate)
        af = ('silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
              'highpass=f=75,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=1.5,'
              'acompressor=threshold=-20dB:ratio=3:attack=5:release=90,aresample=44100')
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', raw, '-af', af, fin], check=True)
    return fin, sf.info(fin).duration

Q = 0.3  # meio tempo a 100 BPM: cortes caem no ritmo da trilha
def qz(x): return math.ceil(x / Q - 1e-6) * Q

def plan(r, h):
    n = N[r]; voice = []; tl = {}
    f, d = tts(n['hooks'][h]); voice.append((0.12, f))
    s2 = qz(max(2.4, 0.12 + d + 0.3))
    t = s2 + 0.2
    for i, line in enumerate(n['prob'][:3]):
        f, d = tts(line); tl[f'p{i}'] = round(t - 0.05, 3); voice.append((t, f)); t += d + 0.12
    t += 0.2; f, d = tts(n['prob'][3]); tl['pd'] = round(t - 0.05, 3); voice.append((t, f)); t += d
    s3 = qz(max(s2 + 3.0, t + 0.35))
    t = s3 + 0.55; f, d = tts(n['demo'][0]); voice.append((t, f)); t += d + 0.1
    rs = max(t, s3 + 0.6 + 0.8 * TOAST_AT[r] + 0.2)
    f, d = tts(n['demo'][1]); voice.append((rs, f)); t = rs + d
    s4 = qz(max(s3 + 5.4, t + 0.4))
    t = s4 + 0.15; line = n['cta'][0]; f, d = tts(line); voice.append((t, f))
    kw = t + d * (len('Comenta ') / len(line)) - 0.05; t += d + 0.25
    ca = t; f, d = tts(n['cta'][1]); voice.append((t, f)); t += d
    end = qz(max(s4 + 4.4, t + 1.0))
    DS = min(1.7, max(.8, (rs - s3 - .6) / TOAST_AT[r]))
    KWr, CAr = kw - s4, ca - s4
    TY = min(KWr + .75, CAr - 1.3)
    spec = dict(end=end, s2=s2, s3=s3, s4=s4, voice=voice, whoosh=[s2, s3, s4],
                taps=[s3 + .6 + td * DS for td in TAPS[r]],
                pops=[s3 + .6 + TOAST_AT[r] * DS, ca - .55],
                typing=[s4 + TY + i * .09 for i in range(len(KW[r]))])
    qs = dict(reel=r, hook=h, s2=s2, s3=s3, s4=s4, end=end, rs=round(rs, 3), kw=round(kw, 3), ca=round(ca, 3), **tl)
    return spec, qs

def build(r, h):
    name = f'0{r}-{NAMES[r]}-gancho{"ABC"[h]}'
    spec, qs = plan(r, h)
    spec['out'] = f'{WORK}/{name}.wav'
    json.dump(spec, open(f'{WORK}/{name}.json', 'w'))
    subprocess.run([sys.executable, '-I', f'{BASE}/audio.py', f'{WORK}/{name}.json'], check=True)
    url = 'pack.html?' + '&'.join(f'{k}={v}' for k, v in qs.items())
    silent = f'{WORK}/{name}.mp4'
    subprocess.run(['node', 'render.js', url, silent, str(spec['end'])], cwd=BASE, check=True, stderr=subprocess.DEVNULL)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', silent, '-i', spec['out'], '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', 'loudnorm=I=-14:TP=-1:LRA=9', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-t', str(spec['end']),
                    '-movflags', '+faststart', f'{OUT}/{name}.mp4'], check=True)
    if h == 0:
        subprocess.run(['node', 'render.js', url, f'{OUT}/0{r}-{NAMES[r]}-capa', str(spec['end']), '0.9'], cwd=BASE, check=True, stderr=subprocess.DEVNULL)
    print('ok', name, spec['end'], flush=True)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'tts':  # pré-gera todas as falas (um processo só carrega o modelo uma vez)
        for r in N:
            for h in range(3): plan(r, h)
        print('tts ok')
    else:
        r, h = map(int, mode.split(':')); build(r, h)
