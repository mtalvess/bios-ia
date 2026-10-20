"""Trilha original + efeitos + mixagem com narração, guiados pela linha do tempo do reels."""
import json, sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
import soundfile as sf

SR = 44100
BPM = 100
BEAT = 60 / BPM
rng = np.random.default_rng(7)

def midi(n): return 440 * 2 ** ((n - 69) / 12)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x, axis=0)
def env(n, a, d, sustain=0.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * (sustain + (1 - sustain) * np.exp(-t / d))
    return e
def add(buf, x, t):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0: return
    if i < 0: x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]

def reverb_ir(sec=2.2, decay=0.55):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)], 1) * np.exp(-t / decay)[:, None]
    ir = lp(ir, 5000); ir[: int(.012 * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(0))
IR = reverb_ir()
def verb(x, wet):
    w = np.stack([fftconvolve(x[:, c], IR[:, c])[: len(x)] for c in range(2)], 1)
    return x + wet * w

CHORDS = [  # Fmaj9, Em9, Dm9, Cmaj9: (baixo, voicing)
    (41, [57, 60, 64, 67]), (40, [55, 59, 62, 66]), (38, [53, 57, 60, 64]), (36, [52, 55, 59, 62])]

def keys_note(f, dur, vel):
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(1, 7):
        x += (1 / k ** 1.7) * np.sin(2 * np.pi * f * k * t + k) * np.exp(-t * (1.0 + 0.9 * k))
    x *= np.minimum(1, t / .004) * (1 + .25 * np.sin(2 * np.pi * 4.2 * t))  # tremolo suave
    rel = np.clip((dur + 0.25 - t) / 0.25, 0, 1)
    return x * rel * vel

def saw(f, n):
    t = np.arange(n) / SR
    return 2 * ((f * t) % 1) - 1

def build_music(dur, s2, s3, s4):
    n = int((dur + 2.5) * SR)
    keys = np.zeros((n, 2)); pad = np.zeros((n, 2)); bass = np.zeros(n)
    kick = np.zeros(n); snare = np.zeros((n, 2)); hats = np.zeros((n, 2)); fx = np.zeros((n, 2))
    bars = int(np.ceil(dur / (4 * BEAT))) + 1
    stab = [(0, 1.3, 1.0), (1.5, 0.9, .7), (2.75, 1.1, .8)]
    for b in range(bars):
        t0 = b * 4 * BEAT
        root, voic = CHORDS[b % 4]
        for (o, d, v) in stab:
            for j, m in enumerate(voic):
                x = keys_note(midi(m), d * BEAT, v * .16 * (1 - .08 * j))
                dl = int((.002 + .009 * (j % 2)) * SR)
                add(keys[:, 0], x, t0 + o * BEAT + j * .012)
                add(keys[:, 1], np.concatenate([np.zeros(dl), x]), t0 + o * BEAT + j * .012)
        # pad
        m = int(4 * BEAT * SR); e = env(m, .5, 9, .8) * np.clip((4 * BEAT - np.arange(m) / SR) / .4, 0, 1)
        for c, det in enumerate((-0.07, 0.07)):
            x = sum(saw(midi(mm + 12) * (1 + det / 100 * 12), m) for mm in voic) * e * .035
            add(pad[:, c], x, t0)
        # baixo
        for (o, d) in [(0, 2.2), (2.5, 1.2)]:
            m2 = int(d * BEAT * SR); t = np.arange(m2) / SR
            x = np.tanh(1.6 * np.sin(2 * np.pi * midi(root + 12) * t)) * env(m2, .006, 1.5, .6) * np.clip((d * BEAT - t) / .06, 0, 1) * .32
            add(bass, x, t0 + o * BEAT)
        # bateria
        for o in (0, 2.5, 3.25 if b % 2 else 99):
            m3 = int(.5 * SR); t = np.arange(m3) / SR
            ph = 2 * np.pi * np.cumsum(48 + 110 * np.exp(-t / .035)) / SR
            add(kick, np.sin(ph) * np.exp(-t / .22) * .9 + rng.standard_normal(m3) * np.exp(-t / .003) * .08, t0 + o * BEAT)
        for o in (1, 3):
            m4 = int(.45 * SR); t = np.arange(m4) / SR
            nz = bp(rng.standard_normal(m4), 900, 7000) * np.exp(-t / .12) * .35 + np.sin(2 * np.pi * 190 * t) * np.exp(-t / .05) * .25
            add(snare[:, 0], nz, t0 + o * BEAT); add(snare[:, 1], nz, t0 + o * BEAT + .004)
        for h in range(8):
            o = h * .5 + (.08 if h % 2 else 0)  # swing
            m5 = int(.12 * SR); t = np.arange(m5) / SR
            x = hp(rng.standard_normal(m5), 7500) * np.exp(-t / (.035 if h % 2 else .02)) * (.13 if h % 2 else .2)
            c = h % 2
            add(hats[:, c], x * .8, t0 + o * BEAT); add(hats[:, 1 - c], x * .45, t0 + o * BEAT)
    # seções: gancho = teclas filtradas + pad; problema = + baixo e bumbo abafado; demo/cta = tudo aberto
    T = np.arange(n) / SR
    def ramp(a, b): return np.clip((T - a) / max(b - a, 1e-3), 0, 1)
    secA = 1 - ramp(s3 - .05, s3)
    open_ = ramp(s3 - .05, s3)
    end_cut = 1 - ramp(dur - .45, dur - .35)
    keys_dark = lp(keys, 900); keys_bright = lp(keys, 6000)
    k = keys_dark * secA[:, None] + keys_bright * open_[:, None]
    kick_m = lp(kick, 160) * ramp(s2 - .02, s2) * secA + kick * open_
    drums = np.stack([kick_m, kick_m], 1) * .9 + (snare + hats) * open_[:, None]
    bassm = (bass * ramp(s2 - .02, s2))[:, None].repeat(2, 1)
    mix = verb(k * 1.0 + pad * 1.0, .35) + bassm + verb(drums, .12)
    mix *= end_cut[:, None]
    # riser antes da demo e da chamada + impacto
    for s in (s3, s4):
        L = 1.6; m = int(L * SR); t = np.arange(m) / SR
        nz = rng.standard_normal((m, 2))
        sw = np.zeros_like(nz)
        for i in range(0, m, 2048):
            f = 400 + 7000 * (i / m) ** 2
            sw[i:i + 2048] = bp(nz[i:i + 2048], f, min(f * 1.6, 18000))
        add2(fx, sw * (t / L)[:, None] ** 2 * .22, s - L)
        m2 = int(1.8 * SR); t2 = np.arange(m2) / SR
        boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t2 / .08)) / SR) * np.exp(-t2 / .5) * .5
        add2(fx, verb(np.stack([boom, boom], 1), .3), s)
    # acorde final com cauda
    root, voic = CHORDS[0]
    for j, m in enumerate(voic + [root + 24]):
        x = keys_note(midi(m), 1.8, .2)
        add2(fx, np.stack([x, x], 1), dur - .4 + j * .02)
    fx = verb(fx, .2)
    return (mix + fx)[: int(dur * SR) + int(1.5 * SR)]

def add2(buf, x, t):
    for c in range(2): add(buf[:, c], x[:, c], t)

def sfx(n, tl):
    out = np.zeros((n, 2))
    for t in tl.get('whoosh', []):
        m = int(.5 * SR); tt = np.arange(m) / SR
        nz = rng.standard_normal((m, 2)); e = np.sin(np.pi * tt / .5) ** 2
        x = np.zeros_like(nz)
        for i in range(0, m, 1024):
            f = 300 + 3500 * (i / m); x[i:i + 1024] = bp(nz[i:i + 1024], f, f * 2.2)
        add2(out, x * e[:, None] * .18, t - .3)
    for t in tl.get('taps', []):
        m = int(.06 * SR); tt = np.arange(m) / SR
        x = np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt / .008) * .22 + hp(rng.standard_normal(m), 3000) * np.exp(-tt / .004) * .12
        add2(out, np.stack([x, x], 1), t)
    for t in tl.get('pops', []):
        m = int(.5 * SR); tt = np.arange(m) / SR
        x = (np.sin(2 * np.pi * 1047 * tt) * np.exp(-tt / .12) + .6 * np.sin(2 * np.pi * 1568 * tt) * np.exp(-tt / .1) * (tt > .09)) * .12
        add2(out, np.stack([x, x * .9], 1), t)
    for t in tl.get('typing', []):
        m = int(.03 * SR); tt = np.arange(m) / SR
        x = bp(rng.standard_normal(m), 2000, 6000) * np.exp(-tt / .006) * .16
        add2(out, np.stack([x, x], 1), t)
    return verb(out, .15)

def main(spec_path):
    sp = json.load(open(spec_path))
    dur = sp['end']
    music = build_music(dur, sp['s2'], sp['s3'], sp['s4'])
    n = len(music)
    voice = np.zeros(n)
    for (t, f) in sp['voice']:
        v, sr = sf.read(f)
        if v.ndim > 1: v = v.mean(1)
        if sr != SR: v = resample_poly(v, SR, sr)
        add(voice, v, t)
    # ducking da trilha sob a voz
    a = np.abs(voice); k = int(.02 * SR)
    sm = np.convolve(a, np.ones(k) / k, 'same')
    rel = np.exp(-1 / (.35 * SR)); g = np.empty_like(sm); cur = 0.0
    for i in range(0, n, 256):
        m = sm[i:i + 256].max(); cur = max(m, cur * rel ** 256); g[i:i + 256] = cur
    duck = 1 - .5 * np.clip(g / (np.percentile(a[a > 0], 90) + 1e-9 if (a > 0).any() else 1), 0, 1)
    fx = sfx(n, sp)
    vpk = np.abs(voice).max() or 1
    mix = music * .42 * duck[:, None] + fx + (voice / vpk * .85)[:, None]
    mix = np.tanh(mix * 1.1) / 1.1
    sf.write(sp['out'], mix.astype(np.float32), SR)

if __name__ == '__main__':
    main(sys.argv[1])
