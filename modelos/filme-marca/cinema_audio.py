"""Design de som e trilha do filme BIOS (15s), sincronizados com cinema.html."""
import importlib.util, os, sys
import numpy as np
import soundfile as sf

spec = importlib.util.spec_from_file_location('a', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio.py'))
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
SR, lp, hp, bp, verb, midi, saw = A.SR, A.lp, A.hp, A.bp, A.verb, A.midi, A.saw
rng = np.random.default_rng(21)
DUR = 15.0
N = int((DUR + .2) * SR)
mix = np.zeros((N, 2))

def put(x, t, g=1.0, pan=0.0):
    if x.ndim == 1: x = np.stack([x * (1 - max(pan, 0)), x * (1 + min(pan, 0))], 1)
    i = int(t * SR)
    if i >= N: return
    n = min(len(x), N - i); mix[i:i + n] += x[:n] * g
def tt(sec): return np.arange(int(sec * SR)) / SR

def impact(big=1.0):
    t = tt(2.5)
    sub = np.sin(2 * np.pi * np.cumsum(32 + 75 * np.exp(-t / .09)) / SR) * np.exp(-t / (.7 * big))
    body = lp(rng.standard_normal(len(t)), 900) * np.exp(-t / .12) * .8
    crack = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t / .03) * .5
    x = np.tanh((sub * 1.4 + body + crack) * 1.3)
    return verb(np.stack([x, x], 1), .45 * big)

def glitch(seed):
    r = np.random.default_rng(seed); t = tt(.45)
    x = np.tanh(bp(r.standard_normal(len(t)), 300, 6000) * 3) * np.exp(-t / .1)
    ch = x[: int(.03 * SR)]
    st = np.concatenate([ch * (1 - k * .2) for k in range(4)])
    x[: len(st)] += st * .7
    x = np.round(x * 12) / 12  # bitcrush
    ping = np.sin(2 * np.pi * (1200 + 300 * seed % 3) * t) * np.exp(-t / .08) * .3
    return np.stack([x * .5 + ping, x * .45 + ping], 1)

def braam(root=33, sec=3.2):
    t = tt(sec); e = np.minimum(1, t / .03) * np.exp(-t / 1.6)
    x = np.zeros(len(t))
    for m, a in [(root, 1), (root + 12, .7), (root + 19, .4), (root + 24, .3)]:
        for d in (-.12, .12):
            x += saw(midi(m) * (1 + d / 100), len(t)) * a
    cut = np.linspace(0, 1, len(t))
    y = np.zeros_like(x)
    for i in range(0, len(t), 2048):
        f = 2600 * np.exp(-cut[i] * 3) + 180
        y[i:i + 2048] = lp(x[i:i + 2048], f)
    y = np.tanh(y * e * .6)
    return verb(np.stack([y, np.roll(y, 300)], 1), .5)

def riser(sec, top=9000):
    t = tt(sec); nz = rng.standard_normal((len(t), 2)); y = np.zeros_like(nz)
    for i in range(0, len(t), 1024):
        f = 300 + top * (i / len(t)) ** 2; y[i:i + 1024] = bp(nz[i:i + 1024], f, min(f * 1.5, 19000))
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / sec) ** 2) / SR) * .25
    return (y * .6 + tone[:, None]) * (t / sec)[:, None] ** 2.2

def whoosh(sec=.45):
    t = tt(sec); nz = rng.standard_normal((len(t), 2)); y = np.zeros_like(nz)
    for i in range(0, len(t), 1024):
        f = 400 + 4000 * np.sin(np.pi * i / len(t)); y[i:i + 1024] = bp(nz[i:i + 1024], f, f * 2)
    return y * (np.sin(np.pi * t / sec) ** 2)[:, None] * .5

# ---- 0–5.0: drone de tensão
t = tt(5.0)
dr = sum(saw(midi(m) * (1 + d), len(t)) for m in (33, 40, 45) for d in (-.002, .002))
dr = lp(dr, 260) * (np.minimum(1, t / 1.5) * (1 + .3 * np.sin(2 * np.pi * .7 * t)))[:] * .09
dr *= np.clip((5.0 - t) / .03, 0, 1)
put(verb(np.stack([dr, np.roll(dr, 500)], 1), .3), 0)
# brilho da linha de luz
t = tt(1.4); sh = hp(rng.standard_normal(len(t)), 6000) * np.sin(np.pi * t / 1.4) ** 2 * .12
put(verb(np.stack([sh, np.roll(sh, 200)], 1), .6), .85)
put(np.sin(2 * np.pi * 2093 * tt(1.2)) * np.exp(-tt(1.2) / .4) * .08, .9)
# títulos
put(impact(.6), 1.0, .55); put(impact(.8), 1.7, .7)
# dores: glitch + impacto curto + tique-taque acelerando
for i, h in enumerate((2.6, 3.2, 3.8, 4.4)):
    put(glitch(i + 3), h, .8); put(impact(.5), h, .45)
tk = 2.6; gap = .3
while tk < 5.0:
    x = hp(rng.standard_normal(int(.02 * SR)), 3000) * np.exp(-tt(.02) / .004) * .25
    put(x, tk, 1, .3 if int(tk * 10) % 2 else -.3); tk += gap; gap = max(.09, gap * .9)
put(riser(1.6), 3.4, .55)
# apagão: silêncio + inspiração reversa
rev = A.keys_note(midi(57), 1.0, .4)[::-1][-int(.55 * SR):]
put(verb(np.stack([rev, rev], 1), .6) * .8, 5.05)
# DROP 5.6
put(braam(33, 3.0), 5.6, .9); put(impact(1.4), 5.6, .9)
t = tt(1.6); shim = sum(np.sin(2 * np.pi * midi(m) * t) * np.exp(-t / .9) for m in (81, 88, 93)) * .05
put(verb(np.stack([shim, np.roll(shim, 400)], 1), .7), 5.65)
# groove 6.1–11.6 (120 BPM, grade a partir de 5.6)
B = .5; g0 = 5.6
for k in range(int((11.6 - g0) / B)):
    tb = g0 + k * B
    if tb < 6.1: continue
    kt = tt(.4); kick = np.sin(2 * np.pi * np.cumsum(46 + 120 * np.exp(-kt / .03)) / SR) * np.exp(-kt / .2)
    put(np.tanh(kick * 1.5) * .55, tb)
    for s in range(4):  # baixo em semicolcheias (Am)
        notes = [45, 45, 48, 45, 52, 45, 43, 45]
        m = notes[(k * 4 + s) % 8] - 12; bt = tt(.12)
        b = np.tanh(2 * saw(midi(m), len(bt))) * np.exp(-bt / .07); b = lp(b, 700 + 500 * ((k * 4 + s) % 2))
        put(b * .16, tb + s * B / 4)
    for s in range(4):
        h = hp(rng.standard_normal(int(.05 * SR)), 8000) * np.exp(-tt(.05) / (.012 if s % 2 == 0 else .025))
        put(h * (.07 if s % 2 == 0 else .11), tb + s * B / 4, 1, -.4 if s % 2 else .4)
    if k % 2 == 1:
        ct = tt(.35); clap = bp(rng.standard_normal(len(ct)), 1000, 6000) * np.exp(-ct / .09) * .3
        put(verb(np.stack([clap, clap], 1), .25), tb)
# arpejo que abre ao longo da montagem
arp = [57, 60, 64, 67, 71, 67, 64, 60]
for j in range(int((11.6 - 6.1) / (B / 2))):
    ta = 6.1 + j * B / 2; m = arp[j % 8] + 12
    x = A.keys_note(midi(m), .2, .09 + .05 * (ta - 6.1) / 5.5)
    put(np.stack([x, np.roll(x, 600)], 1), ta, 1)
for h in (6.6, 7.6, 8.6, 9.6):
    put(whoosh(.45), h - .3, .9); put(impact(.4), h, .35)
# subida e warp 10.4–11.6
put(riser(1.25, 12000), 10.35, .7)
for j in range(16):  # rufo acelerando
    ts = 10.6 + 1.0 * (1 - (1 - j / 16) ** 1.6)
    sn = bp(rng.standard_normal(int(.08 * SR)), 1500, 7000) * np.exp(-tt(.08) / .03) * (.08 + .015 * j)
    put(sn, ts)
# FINAL 11.6: braam + impacto + prato + acorde
put(braam(33, 3.4), 11.6, 1.0); put(impact(1.6), 11.6, 1.0)
ct = tt(3.0); crash = hp(rng.standard_normal((len(ct), 2)), 5000) * np.exp(-ct / .9)[:, None] * .12
put(crash, 11.6)
pt = tt(3.4)
pad = sum(saw(midi(m) * (1 + d), len(pt)) for m in (57, 64, 71, 76) for d in (-.003, .003))
pad = lp(pad, 1800) * np.minimum(1, pt / .3) * np.exp(-pt / 2.5) * .03
put(verb(np.stack([pad, np.roll(pad, 700)], 1), .5), 11.6)
# assinatura sonora no logo e no CTA
for (ts, m) in [(12.0, 81), (12.12, 88), (12.24, 93), (13.0, 76), (13.12, 83)]:
    x = A.keys_note(midi(m), .5, .12); put(verb(np.stack([x, np.roll(x, 300)], 1), .5), ts)
put(whoosh(.5), 12.7, .5)

out = mix[: int(DUR * SR)]
fade = np.clip((DUR - np.arange(len(out)) / SR) / .5, 0, 1)
out *= fade[:, None]
out = out / (np.percentile(np.abs(out), 99.95) + 1e-9) * .8
out = np.tanh(out * 1.1) / 1.1
sf.write(sys.argv[1], out.astype(np.float32), SR)
print('ok')
