"""Postales Sala Viva AR (25 x 15 cm, 300 ppp): frente con fotografía + emblema (Image Target) y reverso.
Incluye la tarjeta de colección. Genera PNG por cara y un PDF listo para imprimir.
Uso: python gen_postales.py <carpeta_fotos> <carpeta_targets> <carpeta_salida>
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

FOTOS, TARGETS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
DPI = 300
W, H = round(25 / 2.54 * DPI), round(15 / 2.54 * DPI)          # 2953 x 1772
cm = lambda x: round(x / 2.54 * DPI)
OBS, OCRE, HUESO, PAPEL, TINTA = (20, 17, 15), (224, 169, 59), (243, 233, 215), (241, 234, 220), (45, 38, 33)
TG = "/usr/share/texmf/fonts/opentype/public/tex-gyre/"
def F(n, t): return ImageFont.truetype(TG + n, t)
SERIF, SERIF_B, SERIF_I = "texgyrepagella-regular.otf", "texgyrepagella-bold.otf", "texgyrepagella-italic.otf"

PIEZAS = [
    dict(n=1, id="PiedraDelSol", foto="museo-nacional-antropologia-mexico-piedra-delsol-blog-viajares.webp", foco=(0.55, 0.5),
         nombre="Piedra del Sol", cultura="Mexica · Posclásico tardío (1250–1521 d.C.)", sala="Sala Mexica",
         ficha=[("Material", "basalto de olivino"), ("Medidas", "3.58 m de diámetro · cerca de 24 t"), ("Hallazgo", "17 de diciembre de 1790, Plaza Mayor")],
         dato="Aunque se le conoce como «Calendario azteca», nunca funcionó como calendario: probablemente fue un altar ceremonial dedicado al Sol."),
    dict(n=2, id="CabezaOlmeca", foto="dsc_0117.webp", foco=(0.5, 0.45),
         nombre="Cabeza Colosal 6", cultura="Olmeca · Preclásico (c. 1200–900 a.C.)", sala="Sala Costa del Golfo",
         ficha=[("Material", "basalto"), ("Medidas", "1.67 m de alto · 1.41 m de ancho"), ("Procedencia", "San Lorenzo Tenochtitlan, Veracruz")],
         dato="Solo se conocen 17 cabezas colosales olmecas. El basalto se trajo desde la sierra de Los Tuxtlas, sin rueda ni animales de carga."),
    dict(n=3, id="MascaraPakal", foto="Pakal-4-1.webp", foco=(0.5, 0.4),
         nombre="Máscara de Pakal", cultura="Maya · Clásico tardío (683 d.C.)", sala="Sala Maya",
         ficha=[("Material", "unos 200 fragmentos de jade"), ("Ojos", "concha e iris de obsidiana"), ("Hallazgo", "1952, Alberto Ruz Lhuillier")],
         dato="K'inich Janaab' Pakal gobernó Palenque durante 68 años. Su máscara fue robada del museo en 1985 y recuperada en 1989."),
    dict(n=4, id="ChacMool", foto="Maya_Chac_Mool_by_Luis_Alberto_Melograna.webp", foco=(0.5, 0.5),
         nombre="Chac Mool", cultura="Maya · Chichén Itzá (900–1250 d.C.)", sala="Sala Maya",
         ficha=[("Material", "piedra caliza"), ("Medidas", "1.10 m de alto · 1.48 m de largo"), ("Hallazgo", "1875, Augustus y Alice Le Plongeon")],
         dato="Nadie sabe cómo se llamaban originalmente: el nombre «Chac Mool» lo inventó Augustus Le Plongeon en 1875."),
]

# ---------------- utilidades ----------------
def cubrir(img, w, h, foco):
    """Recorta y escala la foto para llenar w x h (amplía con Lanczos y enfoca un poco)."""
    s = max(w / img.width, h / img.height)
    im = img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
    x = int((im.width - w) * foco[0]); y = int((im.height - h) * foco[1])
    im = im.crop((x, y, x + w, y + h))
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=70, threshold=2))
    im = ImageEnhance.Contrast(im).enhance(1.06); im = ImageEnhance.Color(im).enhance(1.05)
    return im

def greca(w, h, col, seed=1):
    """Franja de greca escalonada (RGBA) que no se repite exactamente."""
    rng = np.random.default_rng(seed)
    K = 3; m = Image.new("L", (w * K, h * K), 0); d = ImageDraw.Draw(m)
    g = h * K * 0.14; d.rectangle([0, 0, w * K, g], fill=255); d.rectangle([0, h * K - g, w * K, h * K], fill=255)
    x = 0; hh = h * K - 2 * g
    while x < w * K - h * K * 0.6:
        mm = h * K * rng.uniform(1.0, 1.3); t = rng.integers(0, 3); y0 = g
        if t == 0: d.line([(x, h * K - g), (x, y0 + hh * .45), (x + mm * .45, y0 + hh * .45), (x + mm * .45, y0 + hh * .1), (x + mm * .8, y0 + hh * .1)], fill=255, width=int(g))
        elif t == 1: d.line([(x + mm * .1, h * K - g), (x + mm * .1, y0 + hh * .15), (x + mm * .75, y0 + hh * .15), (x + mm * .75, y0 + hh * .7), (x + mm * .38, y0 + hh * .7), (x + mm * .38, y0 + hh * .42)], fill=255, width=int(g))
        else:
            d.polygon([(x + mm * .1, h * K - g), (x + mm * .5, y0 + hh * .2), (x + mm * .9, h * K - g)], fill=255)
        x += mm
    m = m.resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), col + (0,)); out.putalpha(m); return out

def texto(d, xy, s, fuente, tam, fill, anchor="la", esp=0):
    f = F(fuente, tam)
    if not esp: d.text(xy, s, font=f, fill=fill, anchor=anchor); return
    total = sum(f.getlength(c) for c in s) + esp * (len(s) - 1)
    x = xy[0] - (total / 2 if anchor[0] == "m" else total if anchor[0] == "r" else 0)
    for c in s: d.text((x, xy[1]), c, font=f, fill=fill, anchor="l" + anchor[1]); x += f.getlength(c) + esp

def parrafo(d, xy, s, fuente, tam, fill, ancho, interlinea=1.35):
    f = F(fuente, tam); x, y = xy; linea = ""
    for p in s.split():
        prueba = (linea + " " + p).strip()
        if f.getlength(prueba) > ancho and linea:
            d.text((x, y), linea, font=f, fill=fill); y += tam * interlinea; linea = p
        else: linea = prueba
    if linea: d.text((x, y), linea, font=f, fill=fill); y += tam * interlinea
    return y

def sombra_texto(im, xy, s, fuente, tam, fill, anchor="la", esp=0, r=6):
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0)); texto(ImageDraw.Draw(capa), xy, s, fuente, tam, (0, 0, 0, 200), anchor, esp)
    im.alpha_composite(capa.filter(ImageFilter.GaussianBlur(r)))
    texto(ImageDraw.Draw(im), xy, s, fuente, tam, fill, anchor, esp)

def poner_target(im, ruta, x, y, ancho):
    """Pega el Image Target tal cual (sin alterarlo) con un marco dorado fino alrededor."""
    t = Image.open(ruta).convert("RGB"); alto = round(ancho * t.height / t.width)
    t = t.resize((ancho, alto), Image.LANCZOS)
    d = ImageDraw.Draw(im); pad = cm(0.25)
    d.rectangle([x - pad, y - pad, x + ancho + pad, y + alto + pad], fill=(250, 248, 243, 255))
    d.rectangle([x - pad, y - pad, x + ancho + pad, y + alto + pad], outline=OCRE + (255,), width=6)
    im.paste(t, (x, y)); return alto

def marca(im, x, y, claro=True):
    d = ImageDraw.Draw(im)
    sombra_texto(im, (x, y), "SALA VIVA AR", SERIF_B, 64, OCRE, esp=8, r=5)
    sombra_texto(im, (x, y + 82), "El museo al alcance de tu mano", SERIF_I, 42, HUESO, r=5)

# ---------------- frente de una pieza ----------------
def frente(p):
    im = Image.new("RGBA", (W, H), OBS + (255,))
    foto = Image.open(os.path.join(FOTOS, p["foto"])).convert("RGB")
    zona = cm(16.4)
    fo = cubrir(foto, zona + cm(2.5), H, p["foco"]).convert("RGBA")
    a = np.ones((H, fo.width), np.float32)                                   # la foto se funde hacia el panel oscuro
    rampa = np.clip((np.arange(fo.width) - (fo.width - cm(3.2))) / cm(3.2), 0, 1)
    a *= (1 - rampa ** 1.4)[None, :]
    fo.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    viñeta = Image.new("L", fo.size, 0); ImageDraw.Draw(viñeta).rectangle([0, 0, fo.width, cm(3.4)], fill=150)
    viñeta = viñeta.filter(ImageFilter.GaussianBlur(cm(1.2)))
    fo.alpha_composite(Image.merge("RGBA", (Image.new("L", fo.size, 0),) * 3 + (viñeta,)))
    im.alpha_composite(fo, (0, 0))
    abajo = Image.new("L", (W, H), 0); da = ImageDraw.Draw(abajo)
    for yy in range(H - cm(5.5), H): da.line([(0, yy), (W, yy)], fill=int(215 * ((yy - (H - cm(5.5))) / cm(5.5)) ** 1.3))
    im.alpha_composite(Image.merge("RGBA", (Image.new("L", (W, H), OBS[0]), Image.new("L", (W, H), OBS[1]), Image.new("L", (W, H), OBS[2]), abajo)))
    # panel derecho: emblema (target), nombre y llamada a escanear
    ancho_t = cm(6.6); xt = W - cm(1.2) - ancho_t; yt = cm(1.15)
    alto_t = poner_target(im, os.path.join(TARGETS, f"Target_{p['id']}_Vuforia.jpg"), xt, yt, ancho_t)
    cx = xt + ancho_t // 2; d = ImageDraw.Draw(im)
    texto(d, (cx, yt + alto_t + cm(0.95)), "ESCANEA EL EMBLEMA", SERIF_B, 46, OCRE, "mm", esp=6)
    texto(d, (cx, yt + alto_t + cm(1.55)), "con la app Sala Viva AR", SERIF_I, 40, HUESO, "mm")
    # marca arriba a la izquierda y nombre abajo sobre la foto
    marca(im, cm(1.0), cm(0.9))
    sombra_texto(im, (cm(1.0), H - cm(2.3)), p["nombre"], SERIF_B, 150, HUESO, "ls", r=10)
    sombra_texto(im, (cm(1.05), H - cm(1.35)), p["cultura"].upper(), SERIF, 44, OCRE, "ls", esp=4, r=6)
    im.alpha_composite(greca(W, cm(0.42), OCRE, p["n"] * 7), (0, H - cm(0.42)))
    texto(d, (W - cm(1.2), H - cm(0.75)), f"{p['n']} / 4", SERIF, 36, HUESO, "rs")
    return im.convert("RGB")

# ---------------- reverso (tipo postal) ----------------
def reverso(titulo, subtitulo, bloques, dato, n, credito):
    im = Image.new("RGBA", (W, H), PAPEL + (255,)); d = ImageDraw.Draw(im)
    im.alpha_composite(greca(W, cm(0.42), (150, 104, 36), n * 11 + 3), (0, 0))
    m = cm(1.3); mitad = W // 2
    tam_t = 124
    while F(SERIF_B, tam_t).getlength(titulo) > mitad - m - cm(0.9): tam_t -= 4
    texto(d, (m, cm(1.95)), titulo, SERIF_B, tam_t, TINTA)
    tam_s = 40
    while F(SERIF, tam_s).getlength(subtitulo.upper()) + 4 * len(subtitulo) > mitad - m - cm(0.9): tam_s -= 2
    texto(d, (m, cm(2.85)), subtitulo.upper(), SERIF, tam_s, (150, 104, 36), esp=4)
    y = cm(3.8)
    for k, v in bloques:
        texto(d, (m, y), k.upper(), SERIF_B, 38, (150, 104, 36), esp=3); y += 54
        y = parrafo(d, (m, y), v, SERIF, 52, TINTA, mitad - m - cm(1.0)) + 26
    if dato:
        y += cm(0.25); ancho = mitad - m - cm(1.6)
        capa = Image.new("RGBA", im.size); alto = parrafo(ImageDraw.Draw(capa), (0, 0), dato, SERIF_I, 50, TINTA, ancho, 1.3)
        d.rounded_rectangle([m - 24, y, mitad - cm(0.9), y + 100 + alto + 30], radius=26, fill=(233, 222, 200), outline=(150, 104, 36), width=4)
        texto(d, (m + 10, y + 30), "¿SABÍAS QUE?", SERIF_B, 38, (150, 104, 36), esp=3)
        parrafo(d, (m + 10, y + 96), dato, SERIF_I, 50, TINTA, ancho, 1.3)
    texto(d, (m, H - cm(0.9)), credito, SERIF_I, 32, (120, 108, 96))
    d.line([(mitad, cm(1.3)), (mitad, H - cm(1.3))], fill=(190, 178, 160), width=4)
    # espacio para el timbre y la dirección
    tx1, ty0 = W - m, cm(1.3); tx0, ty1 = tx1 - cm(2.6), ty0 + cm(3.1)
    for i in range(0, cm(2.6), 30): d.line([(tx0 + i, ty0), (tx0 + i + 15, ty0)], fill=(170, 158, 140), width=3); d.line([(tx0 + i, ty1), (tx0 + i + 15, ty1)], fill=(170, 158, 140), width=3)
    for i in range(0, cm(3.1), 30): d.line([(tx0, ty0 + i), (tx0, ty0 + i + 15)], fill=(170, 158, 140), width=3); d.line([(tx1, ty0 + i), (tx1, ty0 + i + 15)], fill=(170, 158, 140), width=3)
    texto(d, ((tx0 + tx1) // 2, (ty0 + ty1) // 2), "TIMBRE", SERIF, 30, (170, 158, 140), "mm", esp=4)
    for k in range(4):
        yy = cm(6.3) + k * cm(1.55); d.line([(mitad + cm(1.2), yy), (W - m, yy)], fill=(170, 158, 140), width=3)
    texto(d, (mitad + cm(1.2), cm(1.9)), "Para:", SERIF_I, 48, (120, 108, 96))
    texto(d, (W - m, H - cm(0.9)), "SALA VIVA AR · El museo al alcance de tu mano", SERIF, 34, (150, 104, 36), "rs", esp=2)
    return im.convert("RGB")

# ---------------- tarjeta de colección ----------------
def frente_coleccion():
    im = Image.new("RGBA", (W, H), OBS + (255,)); d = ImageDraw.Draw(im)
    g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse([cm(-4), cm(-4), cm(14), cm(14)], fill=70); g = g.filter(ImageFilter.GaussianBlur(cm(3)))
    im.alpha_composite(Image.merge("RGBA", (Image.new("L", (W, H), 120), Image.new("L", (W, H), 75), Image.new("L", (W, H), 25), g)))
    im.alpha_composite(greca(W, cm(0.42), OCRE, 91), (0, 0)); im.alpha_composite(greca(W, cm(0.42), OCRE, 92), (0, H - cm(0.42)))
    ancho_t = cm(12.6); xt = W - cm(1.0) - ancho_t; yt = (H - round(ancho_t * 0.75)) // 2
    poner_target(im, os.path.join(TARGETS, "Target_Coleccion_Vuforia.jpg"), xt, yt, ancho_t)
    m = cm(1.1)
    marca(im, m, cm(1.2))
    texto(d, (m, cm(4.6)), "Tu colección", SERIF_B, 130, HUESO)
    texto(d, (m, cm(5.6)), "COMPLETA", SERIF_B, 70, OCRE, esp=10)
    y = parrafo(d, (m, cm(6.7)), "Escanea tus cuatro postales una por una. Después apunta a esta tarjeta: las piezas cobrarán vida juntas en la Danza del Sol.",
                SERIF_I, 46, HUESO, xt - m - cm(1.0), 1.35)
    for i, p in enumerate(PIEZAS):
        texto(d, (m, y + cm(0.5) + i * cm(0.8)), f"{p['n']}.  {p['nombre']}", SERIF, 46, OCRE)
    return im.convert("RGB")

if __name__ == "__main__":
    caras = []
    for p in PIEZAS:
        f = frente(p); r = reverso(p["nombre"], p["sala"] + " · Museo Nacional de Antropología",
                                    p["ficha"], p["dato"], p["n"], "Fotografía de referencia de uso educativo. Datos: INAH / MNA.")
        f.save(os.path.join(OUT, f"Postal_{p['n']}_{p['id']}_frente.png"), dpi=(DPI, DPI))
        r.save(os.path.join(OUT, f"Postal_{p['n']}_{p['id']}_reverso.png"), dpi=(DPI, DPI))
        caras += [f, r]
    fc = frente_coleccion()
    rc = reverso("Museo Nacional de Antropología", "Ciudad de México · desde 1964",
                 [("El museo", "Abrió el 17 de septiembre de 1964 y su edificio, obra de Pedro Ramírez Vázquez, se construyó en 19 meses."),
                  ("El Paraguas", "La columna de bronce del patio central mide más de 10 m; es obra de José y Tomás Chávez Morado."),
                  ("Cómo usarla", "Escanea las cuatro postales con Sala Viva AR y luego esta tarjeta para completar tu colección.")],
                 None, 5, "Sala Viva AR · proyecto académico de realidad aumentada. Datos: INAH / MNA.")
    fc.save(os.path.join(OUT, "Postal_5_Coleccion_frente.png"), dpi=(DPI, DPI)); rc.save(os.path.join(OUT, "Postal_5_Coleccion_reverso.png"), dpi=(DPI, DPI))
    caras += [fc, rc]
    caras[0].save(os.path.join(OUT, "Postales_Sala_Viva_AR_imprimir.pdf"), save_all=True, append_images=caras[1:], resolution=DPI)
    print("ok", len(caras), "caras", W, "x", H)
