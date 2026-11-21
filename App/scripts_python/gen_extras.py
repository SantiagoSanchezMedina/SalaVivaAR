"""Recursos extra de Sala Viva AR: sombra de contacto, silueta humana de 1.70 m, ícono y logo de la app."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
OUT = "extras"; import os; os.makedirs(OUT, exist_ok=True)
# --- sombra de contacto (degradado radial negro con alfa) ---
n = 256; yy, xx = np.mgrid[0:n, 0:n]; r = np.hypot(xx - n / 2 + .5, yy - n / 2 + .5) / (n / 2)
a = np.clip(1 - r, 0, 1) ** 1.6 * 0.75
img = np.zeros((n, n, 4), np.uint8); img[..., 3] = (a * 255).astype(np.uint8)
Image.fromarray(img).save(f"{OUT}/sombra.png")
# --- silueta humana tipo señalética (alto = 1.70 m, con marca) ---
K = 4; W, H = 220 * K, 1000 * K
s = Image.new("L", (W, H), 0); d = ImageDraw.Draw(s)
cx = W / 2; u = H / 1000
d.ellipse([cx - 62 * u, 10 * u, cx + 62 * u, 134 * u], fill=255)                     # cabeza
d.rounded_rectangle([cx - 88 * u, 150 * u, cx + 88 * u, 560 * u], radius=int(44 * u), fill=255)   # torso
for sx in (-1, 1):
    d.rounded_rectangle([cx + sx * 96 * u - 24 * u, 160 * u, cx + sx * 96 * u + 24 * u, 520 * u], radius=int(24 * u), fill=255)  # brazos
    d.rounded_rectangle([cx + sx * 44 * u - 38 * u, 500 * u, cx + sx * 44 * u + 38 * u, 995 * u], radius=int(30 * u), fill=255)  # piernas
s = s.resize((W // K, H // K), Image.LANCZOS)
sil = Image.new("RGBA", s.size, (243, 233, 215, 0)); sil.putalpha(s.point(lambda v: int(v * 0.88)))
sil.save(f"{OUT}/silueta_persona.png")
# --- ícono de la app (1024) y logo para la pantalla de carga ---
em = Image.open("/mnt/user-data/uploads/Unity/SalaVivaAR/Assets/SalaViva/UI/emblema.png").convert("RGBA")
ic = Image.new("RGBA", (1024, 1024), (20, 17, 15, 255)); di = ImageDraw.Draw(ic)
for i in range(512):                                                               # resplandor cálido al centro
    pass
g = Image.new("L", (1024, 1024), 0); ImageDraw.Draw(g).ellipse([180, 180, 844, 844], fill=90); g = g.filter(ImageFilter.GaussianBlur(120))
ic = Image.composite(Image.new("RGBA", (1024, 1024), (110, 70, 25, 255)), ic, g)
e = em.resize((760, int(760 * em.height / em.width)), Image.LANCZOS)
ic.alpha_composite(e, ((1024 - e.width) // 2, (1024 - e.height) // 2))
ic.save(f"{OUT}/icono_app.png")
logo = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0)); e2 = em.resize((640, int(640 * em.height / em.width)), Image.LANCZOS)
logo.alpha_composite(e2, ((1024 - e2.width) // 2, 40))
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf", 120)
dl = ImageDraw.Draw(logo); dl.text((512, 800), "SALA VIVA AR", font=f, fill=(224, 169, 59, 255), anchor="mm")
f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 58)
dl.text((512, 930), "El museo al alcance de tu mano", font=f2, fill=(243, 233, 215, 255), anchor="mm")
logo.save(f"{OUT}/logo_carga.png")
