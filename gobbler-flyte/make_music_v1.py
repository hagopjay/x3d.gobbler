#!/usr/bin/env python3
"""A 96-second loop for Mission Control, synthesised offline (numpy only), then encoded with ffmpeg.
150 BPM: one bar is 1.6 s (the heart's beat), four bars are 6.4 s (one shockwave cycle), 60 bars are one tour.
Everything is added into a circular buffer, so the loop has no seam. Nobody has listened to it yet."""
import math, pathlib, subprocess, wave
import numpy as np
SR, BEAT, BARS = 44100, 0.4, 60
N = int(round(BARS * 4 * BEAT * SR)); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(9)
D = 146.83
SCALE = [0, 2, 3, 5, 7, 8, 10]                       # D natural minor
def hz(deg, octave=0): return D * 2 ** ((SCALE[deg % 7] + 12 * (deg // 7 + octave)) / 12)
def put(sig, t, pan=0.0, gain=1.0):
    i = int(round(t * SR)) % N; idx = (i + np.arange(len(sig))) % N
    np.add.at(L, idx, sig * gain * math.sqrt(0.5 * (1 - pan))); np.add.at(R, idx, sig * gain * math.sqrt(0.5 * (1 + pan)))
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / d)
def tone(fr, dur, a=0.005, d=0.3, harm=(1, 0.5, 0.25), detune=0.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = sum(h * np.sin(2 * math.pi * fr * (k + 1) * (1 + detune * k) * t) for k, h in enumerate(harm))
    return s * env(n, a, d)
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR; ph = 2 * math.pi * (45 * t + (150 - 45) * 0.03 * (1 - np.exp(-t / 0.03)))
    return np.sin(ph) * np.exp(-t / 0.16)
def hat(d=0.03): n = int(0.12 * SR); x = rng.standard_normal(n); x = np.diff(x, prepend=0); return x * np.exp(-np.arange(n) / SR / d)
def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for fr in freqs:
        for dt in (-0.004, 0, 0.004): s += np.sin(2 * math.pi * fr * (1 + dt) * t + rng.uniform(0, 6.28)) + 0.3 * np.sin(4 * math.pi * fr * (1 + dt) * t)
    e = np.minimum(t / 1.6, 1) * np.minimum((dur - t) / 1.6, 1); return s * e / (3 * len(freqs))
def riser(dur):
    n = int(dur * SR); x = rng.standard_normal(n); t = np.arange(n) / n; y = np.zeros(n); a = 0.0
    for i in range(n): a += (0.002 + 0.25 * t[i] ** 3) * (x[i] - a); y[i] = a
    return y * t ** 2
PROG = [(0, 2, 4), (5, 7, 9), (2, 4, 6), (6, 8, 10)]   # Dm, Bb, F, C: one chord per four bars
MOTIF = [0, 2, 4, 7, 9, 7, 4, 2, 4]                    # nine notes for nine wheels
bar = 4 * BEAT
for b in range(BARS):
    t0 = b * bar; ch = PROG[(b // 4) % 4]; sec = b // 4          # fifteen 4-bar sections
    full = sec in (4, 5, 6, 7, 8, 9, 12, 13, 14); build = sec in (2, 3, 11); quiet = sec in (0, 1, 10)
    if b % 4 == 0: put(pad([hz(d, -1) for d in ch] + [hz(ch[0], -2)], 4 * bar + 3.2), t0 - 0.2, 0, 0.5)
    if b % 4 == 0: put(tone(hz(ch[0], -3), 1.4, 0.01, 0.8, (1, 0.3)), t0, 0, 0.9 if not quiet else 0.5)      # the shockwave's note
    for q in range(4):
        t = t0 + q * BEAT
        if full or (build and q % 2 == 0): put(kick(), t, 0, 0.95)
        if full: put(hat(), t + BEAT / 2, 0.3, 0.16)
        if full or build:
            put(tone(hz(ch[0], -2), BEAT * 0.9, 0.004, 0.16, (1, 0.6, 0.3, 0.15)), t + BEAT / 2, 0, 0.42)
    if not quiet or sec == 1:
        for s in range(16):
            deg = ch[0] + MOTIF[(s + b * 7) % 9]
            g = 0.16 if full else 0.1
            put(tone(hz(deg, 0), 0.5, 0.003, 0.14, (1, 0.35, 0.12)), t0 + s * BEAT / 4, 0.7 * math.sin(s * 0.9 + b), g)
            if full and s % 4 == 2: put(tone(hz(deg + 2, 1), 0.9, 0.002, 0.4, (1, 0.2)), t0 + s * BEAT / 4, -0.6 * math.sin(s + b), 0.07)
    if b % 2 == 0:
        put(tone(hz(ch[2] + (b // 2) % 3, 1), 2.6, 0.01, 1.1, (1, 0.25, 0.4, 0.1), 0.002), t0 + bar * 0.5, 0.5 * (-1) ** (b // 2), 0.09 if quiet else 0.06)
for sec in (3, 11): put(riser(4 * bar), sec * 4 * bar, 0, 0.5)
for sec in (4, 12): put(tone(hz(0, -3), 3.5, 0.005, 1.4, (1, 0.4)), sec * 4 * bar, 0, 1.0); put(hat(0.5) * 0.6, sec * 4 * bar, 0, 0.5)
# a soft echo, circular like everything else
for buf, other in ((L, R), (R, L)):
    dly = int(0.3 * SR); buf += 0.22 * np.roll(other, dly) + 0.1 * np.roll(buf, 2 * dly)
peak = max(np.abs(L).max(), np.abs(R).max()); L, R = (np.tanh(1.6 * x / peak) / math.tanh(1.6) * 0.89 for x in (L, R))
out = pathlib.Path(__file__).resolve().parent
pcm = (np.stack([L, R], 1) * 32767).astype("<i2")
with wave.open(str(out / "loop.wav"), "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
rms = lambda x: 20 * math.log10(float(np.sqrt(np.mean(x ** 2))))
seam = float(abs(L[0] - L[-1])); print(f"{N / SR:.2f} s, peak {20 * math.log10(max(np.abs(L).max(), np.abs(R).max())):.1f} dBFS, RMS L {rms(L):.1f} R {rms(R):.1f} dBFS, seam step {seam:.4f}")
for s in range(15):
    a, b = int(s * 6.4 * SR), int((s + 1) * 6.4 * SR); print(f"  section {s:2d} RMS {rms(L[a:b]):6.1f} dBFS", end="\n" if s % 3 == 2 else "")
