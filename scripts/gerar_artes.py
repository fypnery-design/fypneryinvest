"""Gera as artes do @fypneryinvest a partir de posts/AAAAMMDD/conteudo.json.

Uso: python3 scripts/gerar_artes.py posts/AAAAMMDD
Saída: slide_01.png ... slide_NN.png (Instagram) e facebook_<tema>.png na mesma pasta.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 80  # margem lateral
VERDE = (23, 61, 50)        # #173D32
VERDE_ESC = (11, 33, 27)    # #0B211B
MARFIM = (244, 240, 230)    # #F4F0E6
SALVIA = (168, 184, 165)    # #A8B8A5
DOURADO = (185, 154, 91)    # #B99A5B
ASSINATURA = "Inteligência financeira para decisões mais claras."

FONT_DIR = Path("/usr/share/fonts/opentype/inter")
ROOT = Path(__file__).resolve().parent.parent
AVATAR = Image.open(ROOT / "assets" / "avatar_fellype_nery.png").convert("RGBA")


def font(peso, tam):
    return ImageFont.truetype(str(FONT_DIR / f"Inter-{peso}.otf"), tam)


def quebrar(d, texto, f, largura):
    linhas = []
    for par in texto.split("\n"):
        atual = ""
        for palavra in par.split():
            teste = (atual + " " + palavra).strip()
            if d.textlength(teste, font=f) <= largura:
                atual = teste
            else:
                if atual:
                    linhas.append(atual)
                atual = palavra
        linhas.append(atual)
    return linhas


def bloco(d, y, texto, f, cor, largura=W - 2 * M, entre=1.3, x=M):
    for linha in quebrar(d, texto, f, largura):
        assert d.textlength(linha, font=f) <= largura, f"texto excede margem: {linha}"
        d.text((x, y), linha, font=f, fill=cor)
        y += int(f.size * entre)
    return y


def espacado(d, xy, texto, f, cor, esp=6):
    x, y = xy
    for ch in texto:
        d.text((x, y), ch, font=f, fill=cor)
        x += d.textlength(ch, font=f) + esp


def base(pagina=None, total=None):
    img = Image.new("RGB", (W, H), VERDE)
    img.paste(AVATAR, (M, 70), AVATAR)
    d = ImageDraw.Draw(img)
    d.text((208, 86), "Fellype Nery", font=font("Bold", 36), fill=MARFIM)
    d.text((208, 133), "@fypneryinvest", font=font("Regular", 30), fill=SALVIA)
    d.line((M, 214, W - M, 214), fill=DOURADO, width=2)
    d.text((M, 1264), ASSINATURA, font=font("Regular", 26), fill=SALVIA)
    if pagina:
        t = f"{pagina}/{total}"
        f = font("Regular", 28)
        d.text((W - M - d.textlength(t, font=f), 1263), t, font=f, fill=SALVIA)
    return img, d


def cartao(d, y, num, titulo, sub, alt=134):
    d.rounded_rectangle((M, y, W - M, y + alt), radius=22, fill=VERDE_ESC)
    cx, cy = M + 66, y + alt // 2
    d.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), outline=DOURADO, width=3)
    fn = font("SemiBold", 38)
    d.text((cx - d.textlength(str(num), font=fn) / 2, cy - 24), str(num), font=fn, fill=DOURADO)
    larg = W - M - 30 - (M + 130)
    ft, fs = font("SemiBold", 36), font("Regular", 28)
    assert d.textlength(titulo, font=ft) <= larg, f"título do cartão excede: {titulo}"
    assert d.textlength(sub, font=fs) <= larg, f"subtítulo do cartão excede: {sub}"
    d.text((M + 130, y + 26), titulo, font=ft, fill=MARFIM)
    d.text((M + 130, y + 78), sub, font=fs, fill=SALVIA)
    return y + alt + 20


def slide(s, pagina, total):
    img, d = base(pagina, total)
    tipo = s["tipo"]
    if tipo == "capa":
        espacado(d, (M, 334), s["rotulo"].upper(), font("SemiBold", 30), DOURADO)
        y = bloco(d, 405, s["titulo"], font("Bold", 84), MARFIM, entre=1.2)
        d.line((M, y + 30, M + 160, y + 30), fill=DOURADO, width=5)
        bloco(d, y + 70, s["subtitulo"], font("SemiBold", 52), SALVIA)
        d.text((M, 1132), "Deslize →", font=font("SemiBold", 34), fill=DOURADO)
        return img
    espacado(d, (M, 304), s["rotulo"].upper(), font("SemiBold", 30), DOURADO)
    y = bloco(d, 365, s["titulo"], font("Bold", 64), MARFIM, entre=1.2) + 40
    if tipo == "texto":
        for p in s["paragrafos"]:
            y = bloco(d, y, p, font("Regular", 38), MARFIM, entre=1.45) + 30
    elif tipo == "formula":
        d.rounded_rectangle((M, y, W - M, y + 200), radius=22, fill=VERDE_ESC)
        bloco(d, y + 38, s["formula"], font("SemiBold", 40), DOURADO, largura=W - 2 * M - 80, x=M + 40)
        y += 250
        for p in s["paragrafos"]:
            y = bloco(d, y, p, font("Regular", 38), MARFIM, entre=1.45) + 30
    elif tipo == "barras":
        maxv = max(b["valor"] for b in s["barras"])
        for b in s["barras"]:
            d.text((M, y), b["nome"], font=font("SemiBold", 36), fill=MARFIM)
            d.text((M, y + 48), b["detalhe"], font=font("Regular", 28), fill=SALVIA)
            y += 100
            larg = int((W - 2 * M - 200) * b["valor"] / maxv)
            d.rounded_rectangle((M, y, M + (W - 2 * M - 200), y + 56), radius=12, fill=VERDE_ESC)
            d.rounded_rectangle((M, y, M + larg, y + 56), radius=12, fill=DOURADO if b.get("destaque") else SALVIA)
            d.text((M + (W - 2 * M - 200) + 30, y + 2), b["rotulo"], font=font("Bold", 46), fill=MARFIM)
            y += 110
        for p in s.get("paragrafos", []):
            y = bloco(d, y, p, font("Regular", 36), MARFIM, entre=1.45) + 24
    elif tipo == "cartoes":
        for i, c in enumerate(s["cartoes"], 1):
            y = cartao(d, y, i, c[0], c[1])
    if s.get("destaque"):
        y += 10
        d.line((M, y, M + 120, y), fill=DOURADO, width=4)
        y = bloco(d, y + 30, s["destaque"], font("SemiBold", 40), DOURADO, entre=1.3)
    if s.get("nota"):
        bloco(d, 1190, s["nota"], font("Regular", 26), SALVIA)
    assert y < 1180, f"conteúdo do slide {pagina} invade o rodapé (y={y})"
    return img


def facebook(fb):
    img, d = base()
    espacado(d, (M, 266), fb["rotulo"].upper(), font("SemiBold", 30), DOURADO)
    y = bloco(d, 322, fb["titulo"], font("Bold", 64), MARFIM, entre=1.17)
    y = bloco(d, y + 6, fb["subtitulo"], font("SemiBold", 38), SALVIA) + 26
    for i, c in enumerate(fb["cartoes"], 1):
        y = cartao(d, y, i, c[0], c[1])
    d.line((M, y + 10, M + 120, y + 10), fill=DOURADO, width=4)
    y = bloco(d, y + 36, fb["frase_final"], font("SemiBold", 38), DOURADO)
    if fb.get("nota"):
        bloco(d, 1214, fb["nota"], font("Regular", 24), SALVIA)
    assert y < 1200, f"conteúdo do Facebook invade o rodapé (y={y})"
    return img


def main(pasta):
    pasta = Path(pasta)
    dados = json.loads((pasta / "conteudo.json").read_text(encoding="utf-8"))
    slides = dados["instagram"]
    assert len(slides) <= 7, "máximo de 7 slides"
    for i, s in enumerate(slides, 1):
        slide(s, i, len(slides)).save(pasta / f"slide_{i:02d}.png")
    facebook(dados["facebook"]).save(pasta / f"facebook_{dados['tema']}.png")
    (pasta / "legenda.txt").write_text(dados["legenda"], encoding="utf-8")
    print("ok:", pasta)


if __name__ == "__main__":
    main(sys.argv[1])
