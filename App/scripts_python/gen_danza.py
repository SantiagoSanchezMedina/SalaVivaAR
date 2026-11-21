"""Texturas para la 'Danza del Sol' de la colección: anillo dorado con resplandor y chispa para partículas."""
import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter
N = 1024; K = 2; S = N * K
c = S / 2
lin = Image.new("L", (S, S), 0); d = ImageDraw.Draw(lin)
def anillo(r, w): d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=int(w))
anillo(S * .47, S * .012); anillo(S * .41, S * .006); anillo(S * .30, S * .010); anillo(S * .26, S * .004)
for k in range(20):                                     # 20 marcas entre anillos
    a = k * 2 * math.pi / 20
    for r0, r1, w in ((S * .415, S * .465, S * .010),):
        d.line([(c + r0 * math.cos(a), c + r0 * math.sin(a)), (c + r1 * math.cos(a), c + r1 * math.sin(a))], fill=255, width=int(w))
for k in range(8):                                      # 8 rayos triangulares hacia adentro
    a = k * 2 * math.pi / 8 + math.pi / 8
    p = [(c + S * .30 * math.cos(a - .09), c + S * .30 * math.sin(a - .09)), (c + S * .37 * math.cos(a), c + S * .37 * math.sin(a)),
         (c + S * .30 * math.cos(a + .09), c + S * .30 * math.sin(a + .09))]
    d.polygon(p, fill=255)
for k in range(40):                                     # puntos finos
    a = k * 2 * math.pi / 40 + .05
    r = S * .44; d.ellipse([c + r * math.cos(a) - S * .004, c + r * math.sin(a) - S * .004, c + r * math.cos(a) + S * .004, c + r * math.sin(a) + S * .004], fill=255)
lin = lin.resize((N, N), Image.LANCZOS)
glow = lin.filter(ImageFilter.GaussianBlur(14)).point(lambda v: min(255, v * 2))
a = np.maximum(np.asarray(lin, np.float32), np.asarray(glow, np.float32) * .55)
img = np.zeros((N, N, 4), np.uint8); img[..., 0] = 255; img[..., 1] = 196; img[..., 2] = 92; img[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
Image.fromarray(img).save("extras/anillo_sol.png")
n = 64; yy, xx = np.mgrid[0:n, 0:n]; r = np.hypot(xx - n / 2 + .5, yy - n / 2 + .5) / (n / 2)
ch = np.zeros((n, n, 4), np.uint8); ch[..., :3] = 255; ch[..., 3] = (np.clip(1 - r, 0, 1) ** 2 * 255).astype(np.uint8)
Image.fromarray(ch).save("extras/chispa.png")
