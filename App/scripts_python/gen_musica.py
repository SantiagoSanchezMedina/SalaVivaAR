"""Música original para Sala Viva AR (generada por código, sin derechos de terceros).
- Coleccion_musica.wav: ~19 s en bucle. Flauta de carrizo en escala pentatónica, tambor grave tipo huéhuetl y sonaja.
- Coleccion_completa.wav: remate corto para cuando se completan las 4 postales."""
import numpy as np, wave
SR = 44100
rng = np.random.default_rng(7)

def env(n, a=0.04, r=0.25):
    t = np.arange(n) / SR; e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e

def flauta(f, dur, vol=0.32):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.3, 0, 1)
    fase = 2 * np.pi * f * np.cumsum(vib) / SR
    s = np.sin(fase) + 0.18 * np.sin(2 * fase) + 0.06 * np.sin(3 * fase)
    soplo = rng.normal(0, 1, n); soplo = np.convolve(soplo, np.ones(30) / 30, "same") * 0.12
    return (s + soplo) * env(n, 0.06, min(0.3, dur * 0.5)) * vol

def tambor(dur=0.6, f=72, vol=0.55):
    n = int(dur * SR); t = np.arange(n) / SR
    fr = f * (1 + 0.6 * np.exp(-t * 18))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 6.5)
    golpe = rng.normal(0, 1, n) * np.exp(-t * 60) * 0.25
    return (s + golpe) * vol

def sonaja(dur=0.18, vol=0.10):
    n = int(dur * SR); t = np.arange(n) / SR
    s = rng.normal(0, 1, n); s = s - np.convolve(s, np.ones(4) / 4, "same")   # brillo (pasa altas)
    return s * np.exp(-t * 28) * vol

def poner(pista, x, seg):
    i = int(seg * SR); pista[i:i + len(x)] += x[:max(0, len(pista) - i)]

# escala pentatónica menor en La: La Do Re Mi Sol
NOTA = {"A3": 220.0, "C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.0, "A4": 440.0, "C5": 523.25, "D5": 587.33, "E5": 659.25}
BPM = 84; b = 60 / BPM

def musica_coleccion():
    compases = 7; L = compases * 4 * b
    pista = np.zeros(int((L + 1.5) * SR))
    melodia = [("E4", 1), ("G4", .5), ("A4", 1.5), ("G4", .5), ("E4", .5), ("D4", 2),
               ("C4", 1), ("D4", .5), ("E4", 1.5), ("G4", .5), ("A4", .5), ("E4", 2),
               ("A4", 1), ("C5", .5), ("D5", 1.5), ("C5", .5), ("A4", .5), ("G4", 2),
               ("E4", 1), ("D4", .5), ("C4", 1), ("D4", .5), ("A3", 3)]
    t = 0.5 * b * 2
    for n, d in melodia:
        poner(pista, flauta(NOTA[n], d * b * 1.05), t); t += d * b
    for k in range(compases * 4):                       # tambor: 1 y 3 fuertes, contratiempo suave
        poner(pista, tambor(vol=0.5 if k % 2 == 0 else 0.28, f=70 if k % 4 == 0 else 84), k * b)
        for s in (0, .5): poner(pista, sonaja(vol=0.09 if s == 0 else 0.06), (k + s + .25) * b)
    pista = pista[:int(L * SR)]
    # empalme suave para el bucle
    f = int(0.05 * SR); pista[:f] *= np.linspace(0, 1, f); pista[-f:] *= np.linspace(1, 0, f)
    return pista

def remate():
    pista = np.zeros(int(3.6 * SR))
    for i, n in enumerate(["A3", "C4", "E4", "A4"]): poner(pista, flauta(NOTA[n], 0.32, 0.30), i * 0.16)
    poner(pista, flauta(NOTA["E5"], 1.6, 0.30), 0.7); poner(pista, flauta(NOTA["A4"], 1.8, 0.22), 0.7)
    for i in range(3): poner(pista, tambor(vol=0.45), 0.7 + i * 0.12)
    for i in range(10): poner(pista, sonaja(vol=0.07), 0.7 + i * 0.09)
    return pista

def guardar(x, ruta):
    x = x / max(1e-6, np.abs(x).max()) * 0.8
    st = np.stack([x, np.roll(x, 220) * 0.92], 1)           # leve amplitud estéreo
    with wave.open(ruta, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())

guardar(musica_coleccion(), "Coleccion_musica.wav")
guardar(remate(), "Coleccion_completa.wav")
