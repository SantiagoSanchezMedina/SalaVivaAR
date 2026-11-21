"""Máscara funeraria de Pakal a partir de la foto frontal.

- Silueta: se separa la máscara del fondo (relleno desde los bordes de la foto).
- Profundidad (m): domo que sigue la silueta (curvatura de la máscara) + volúmenes de la cara
  ubicados sobre los rasgos de la foto (nariz, labios, pómulos, cuencas, cejas, mentón),
  calibrados con la vista de 3/4 de la misma foto.
- Detalle: las juntas entre teselas de jade salen de la foto (zonas oscuras = ranuras).
Uso: python gen_pakal.py <foto> <carpeta_salida>
"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

foto, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)

# Recorte de la máscara frontal (lado izquierdo de la imagen de Arqueología Mexicana)
im = Image.open(foto).convert("RGB").crop((30, 10, 340, 425))
W, H = 768, 1024
im = im.resize((W, H), Image.LANCZOS)
col = np.asarray(im).astype(float) / 255
FX, FY = W / 620, H / 830          # rasgos medidos sobre la cuadrícula 620x830

# ---------- silueta ----------
fondo_ref = np.array([0.80, 0.84, 0.77])
dist = np.linalg.norm(col - fondo_ref, axis=-1)
parecido = dist < 0.13
lab, n = ndimage.label(parecido)
borde = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
fondo = np.isin(lab, list(borde))
mascara = ~fondo
mascara = ndimage.binary_opening(mascara, iterations=2)
lab2, n2 = ndimage.label(mascara)
tam = ndimage.sum(mascara, lab2, range(1, n2 + 1))
mascara = lab2 == (np.argmax(tam) + 1)
mascara = ndimage.binary_fill_holes(mascara)
mascara = ndimage.binary_erosion(mascara, iterations=2)

ys, xs = np.nonzero(mascara)
alto_px = ys.max() - ys.min()
M_PX = 0.24 / alto_px              # la máscara real mide ~24 cm de alto
print("silueta px:", xs.min(), xs.max(), ys.min(), ys.max(), "m/px", M_PX)

# ---------- domo que sigue la silueta ----------
d = ndimage.distance_transform_edt(mascara)
t = np.clip(d / (d.max() * 0.85), 0, 1)
Z = 0.055 * np.sqrt(np.clip(t * (2 - t), 0, 1))          # 5.5 cm de curvatura

yy, xx = np.mgrid[0:H, 0:W].astype(float)

def g(cx, cy, sx, sy, amp):
    cx, cy, sx, sy = cx * FX, cy * FY, sx * FX, sy * FY
    return amp * np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2) / 2)

def cresta(x0, y0, x1, y1, s, a0, a1):
    # cresta a lo largo de un segmento, altura de a0 a a1
    x0, y0, x1, y1, s = x0 * FX, y0 * FY, x1 * FX, y1 * FY, s * FX
    vx, vy = x1 - x0, y1 - y0
    L2 = vx * vx + vy * vy
    tt = np.clip(((xx - x0) * vx + (yy - y0) * vy) / L2, 0, 1)
    px, py = x0 + tt * vx, y0 + tt * vy
    dd = np.hypot(xx - px, yy - py)
    return (a0 + (a1 - a0) * tt) * np.exp(-(dd / s) ** 2 / 2)

Z += cresta(350, 70, 355, 300, 26, 0.006, 0.020)          # puente de la nariz
Z += g(355, 330, 55, 45, 0.030)                            # punta de la nariz
Z += g(298, 352, 26, 24, 0.012) + g(412, 352, 26, 24, 0.012)   # aletas
Z -= g(215, 238, 60, 38, 0.014) + g(488, 245, 60, 38, 0.014)   # cuencas
Z += g(215, 240, 32, 16, 0.006) + g(488, 247, 32, 16, 0.006)   # globo ocular
Z += g(215, 160, 75, 24, 0.008) + g(488, 165, 75, 24, 0.008)   # cejas
Z += g(190, 400, 80, 80, 0.011) + g(522, 410, 80, 80, 0.011)   # pómulos
Z += g(355, 503, 115, 34, 0.022)                           # labio superior
Z += g(355, 585, 92, 30, 0.018)                            # labio inferior
Z -= g(355, 548, 112, 7, 0.012)                            # comisura / boca entreabierta
Z += g(360, 712, 92, 58, 0.012)                            # mentón
Z -= g(355, 440, 55, 22, 0.006)                            # surco bajo la nariz

# ---------- detalle de teselas (juntas oscuras) ----------
L = col @ np.array([0.299, 0.587, 0.114])
Lm = np.where(mascara, L, L[mascara].mean())
hp = ndimage.gaussian_filter(Lm, 1.0) - ndimage.gaussian_filter(Lm, 10)
hp = np.clip(hp / hp[mascara].std(), -3, 3)
Z_detalle = 0.0012 * hp                                     # ~1-3 mm
Z_suave = ndimage.gaussian_filter(Z, 2.0)
Z_total = np.where(mascara, Z_suave + Z_detalle, 0)

np.save(os.path.join(out, "Pakal_prof.npy"), np.where(mascara, Z_suave, np.nan).astype(np.float32))
Image.fromarray((mascara * 255).astype(np.uint8)).save(os.path.join(out, "Pakal_alpha.png"))

# ---------- color: la foto, con el fondo reemplazado por el color del borde ----------
c2 = col.copy()
idx = ndimage.distance_transform_edt(~mascara, return_distances=False, return_indices=True)
c2 = c2[idx[0], idx[1]]
Image.fromarray((np.clip(c2, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, "Pakal_color.png"))

# ---------- normal (OpenGL) con forma + teselas ----------
gy, gx = np.gradient(Z_total / M_PX)        # pendiente real (adimensional)
nx, ny, nz = -gx, gy, np.ones_like(gx)
ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
nrm = np.stack([nx / ln, ny / ln, nz / ln], -1)
# para el normal map del modelo solo va el detalle (la forma ya está en la malla)
gy2, gx2 = np.gradient(ndimage.gaussian_filter(Z_detalle, 1.3) / M_PX)
n2 = np.stack([-gx2 * 1.1, gy2 * 1.1, np.ones_like(gx2)], -1)
n2 /= np.linalg.norm(n2, axis=-1, keepdims=True)
n2[~mascara] = [0, 0, 1]
Image.fromarray(((n2 * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(out, "Pakal_normal.png"))

# ---------- vistas previas ----------
light = np.array([-0.5, 0.45, 0.75]); light /= np.linalg.norm(light)
lam = np.clip(nrm @ light, 0, 1)
gris = np.where(mascara[..., None], (0.15 + 0.9 * lam)[..., None] * 0.85, 0.2)
Image.fromarray((np.clip(gris, 0, 1).repeat(3, -1) if gris.shape[-1] == 1 else np.clip(gris, 0, 1) * 255).astype(np.uint8) if False else (np.clip(np.repeat(gris, 3, -1), 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, "Pakal_preview_forma.png"))
print("ok; profundidad máx (cm):", round(Z_suave[mascara].max() * 100, 1))
