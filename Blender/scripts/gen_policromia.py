"""Restitución cromática HIPOTÉTICA de la Piedra del Sol con la paleta mexica documentada
(rojo, ocre, azul, blanco y negro). Se pinta por anillos sobre la textura original, conservando
el relieve (el tono sale de la luminancia de la foto)."""
import sys, numpy as np, cv2
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255
H, W = im.shape[:2]
g = cv2.cvtColor((im * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
# detecta el disco
m = (np.abs(im - im[5, 5]).sum(2) > 0.08).astype(np.uint8)
cx, cy, R = W / 2, H / 2, 0.486 * W
yy, xx = np.mgrid[0:H, 0:W]; r = np.hypot(xx - cx, yy - cy) / R; a = np.arctan2(yy - cy, xx - cx)
ROJO, OCRE, AZUL, BLANCO, NEGRO = np.array([.58, .14, .09]), np.array([.78, .57, .24]), np.array([.16, .43, .55]), np.array([.90, .87, .80]), np.array([.08, .07, .07])
# por anillo: (color de figura en relieve, color de fondo)
zonas = [(0.00, 0.16, OCRE, ROJO), (0.16, 0.36, OCRE, ROJO), (0.36, 0.47, BLANCO, AZUL), (0.47, 0.56, ROJO, OCRE),
         (0.56, 0.76, OCRE, ROJO), (0.76, 0.97, AZUL, ROJO), (0.97, 1.01, OCRE, ROJO)]
fig = np.zeros((H, W, 3), np.float32); fon = np.zeros((H, W, 3), np.float32)
for r0, r1, cf, cb in zonas:
    z = (r >= r0) & (r < r1); fig[z] = cf; fon[z] = cb
fig = cv2.GaussianBlur(fig, (0, 0), 4); fon = cv2.GaussianBlur(fon, (0, 0), 4)
gl = cv2.GaussianBlur(g, (0, 0), 1.0); base = cv2.GaussianBlur(g, (0, 0), 18)
rel = np.clip((gl - base) * 4.0 + .5, 0, 1)                  # 1 = relieve alto, 0 = fondo hundido
t = np.clip((rel - .38) / .22, 0, 1)[..., None]
pintura = fon * (1 - t) + fig * t
pintura = pintura * (0.55 + 0.6 * rel[..., None])
pintura = np.where(rel[..., None] < .16, pintura * .4 + NEGRO * .6, pintura)   # contornos negros en lo más hundido
piedra = im * 0.9
out = pintura * 0.8 + piedra * 0.2                             # se nota la textura de la piedra debajo del pigmento
dentro = (r < 1.0)[..., None]
res = np.where(dentro, out, im)
Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8)).save(dst)
