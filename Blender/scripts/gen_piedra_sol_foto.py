"""Piedra del Sol a partir de una foto frontal real.

Toma la foto (fondo blanco, disco centrado), la recorta al disco y la escala a 2048 px.
- Color: la foto misma (piedra real, con su desgaste y pigmento).
- Altura: relieve estimado con las luces y sombras de la foto (filtro paso-altas multi-escala).
- Normal: derivada de la altura (formato OpenGL, el que usa Unity).
Mantiene la misma convención que gen_piedra_sol.py (disco = 0.985 de la imagen) para reutilizar
piedra_sol_blender.py sin cambios.
Uso: python gen_piedra_sol_foto.py <foto> <carpeta_salida>
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

foto, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
N = 2048

im = Image.open(foto).convert("RGB")
a = np.asarray(im).astype(float)
mask = a.min(-1) < 235                                   # todo lo que no es fondo blanco
ys, xs = np.nonzero(mask)
cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
r = ((xs.max() - xs.min()) + (ys.max() - ys.min())) / 4
half = r / 0.985
crop = im.crop((cx - half, cy - half, cx + half, cy + half)).resize((N, N), Image.LANCZOS)
crop = crop.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
col = np.asarray(crop).astype(float) / 255

lin = (np.arange(N) + 0.5) / N * 2 - 1
X, Y = np.meshgrid(lin / 0.985, -lin / 0.985)
R = np.hypot(X, Y)
DISC = R <= 0.995
# restos del fondo blanco dentro del disco (bordes de la foto): se tratan como piedra lisa
BLANCO = ndimage.binary_dilation((col.min(-1) > 0.80) & DISC, iterations=6) & DISC
tono0 = col[DISC & ~BLANCO & (R > 0.9)].mean(0)
col[BLANCO] = tono0

# ---------- altura a partir de luces y sombras ----------
L = col @ np.array([0.299, 0.587, 0.114])
L_rellena = L.copy(); L_rellena[~DISC] = L[DISC].mean()
fino = ndimage.gaussian_filter(L_rellena, 1.5) - ndimage.gaussian_filter(L_rellena, 18)
medio = ndimage.gaussian_filter(L_rellena, 4) - ndimage.gaussian_filter(L_rellena, 60)
d = 0.65 * fino / fino[DISC].std() + 0.35 * medio / medio[DISC].std()
d = np.clip(d, -3, 3) / 3
H = 0.62 + 0.30 * d
# borde de la piedra un poco redondeado
H = H - 0.25 * np.clip((R - 0.975) / 0.02, 0, 1)
H[BLANCO] = ndimage.gaussian_filter(H, 6)[BLANCO] * 0 + 0.6
H = np.where(BLANCO, ndimage.gaussian_filter(H, 3), H)
H[~DISC] = 0
H = np.clip(H, 0, 1)
Image.fromarray((H * 65535).astype(np.uint16)).save(os.path.join(out, "PiedraSol_altura.png"))
# Para la malla: relieve suavizado (forma de los glifos), el detalle fino va en el normal map
H_geo = ndimage.gaussian_filter(H, 5.0)
H_geo = np.where(DISC, 0.62 + (H_geo - 0.62) * 0.75, 0)
np.save(os.path.join(out, "PiedraSol_altura.npy"), H_geo.astype(np.float16))

# ---------- color: la foto, con el exterior rellenado del tono medio ----------
tono = col[DISC & (R < 0.95)].mean(0)
col_out = col.copy(); col_out[~DISC] = tono
Image.fromarray((np.clip(col_out, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, "PiedraSol_color.png"))

# ---------- normal ----------
strength = 14.0
gy, gx = np.gradient(ndimage.gaussian_filter(H, 0.8))
nx, ny, nz = -gx * strength * (N / 512), gy * strength * (N / 512), np.ones_like(H)
ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
nrm = np.stack([nx / ln, ny / ln, nz / ln], -1) * 0.5 + 0.5
Image.fromarray((nrm * 255).astype(np.uint8)).save(os.path.join(out, "PiedraSol_normal.png"))

# ---------- vista previa: relieve solo (gris) y relieve + color con luz rasante ----------
light = np.array([-0.55, 0.55, 0.62]); light /= np.linalg.norm(light)
lam = np.clip((nrm * 2 - 1) @ light, 0, 1)
gris = np.clip(0.25 + 0.85 * lam, 0, 1)[..., None] * np.array([0.8, 0.8, 0.8])
gris[~DISC] = 0.2
Image.fromarray((gris * 255).astype(np.uint8)).resize((1024, 1024)).save(os.path.join(out, "PiedraSol_preview_relieve.png"))
prev = np.clip(col_out * (0.55 + 0.6 * lam[..., None]), 0, 1); prev[~DISC] = 0.2
Image.fromarray((prev * 255).astype(np.uint8)).resize((1024, 1024)).save(os.path.join(out, "PiedraSol_preview.png"))
print("ok", N, "disco r(px foto) =", r)
