"""Gera as imagens (JPEG, exigido pela API do Instagram) de cada carrossel."""
import csv, os, sys, datetime
from PIL import Image, ImageDraw, ImageFont
from config import *

FONTES = [
    "fonts/Bold.ttf",  # coloque aqui uma fonte sua, se quiser
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]

def fonte(tamanho):
    for caminho in FONTES:
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default()

def carregar_posts(arquivo="posts.csv"):
    posts = []
    with open(arquivo, encoding="utf-8-sig", newline="") as f:
        for linha in csv.DictReader(f):
            slides = [s.strip() for s in linha["slides"].split("|") if s.strip()]
            posts.append({"data": linha["data"].strip(), "slides": slides, "legenda": linha["legenda"].strip()})
    return posts

def quebrar(draw, texto, fnt, largura_max):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if draw.textlength(teste, font=fnt) <= largura_max:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas

def fundo():
    img = Image.new("RGB", (LARGURA, ALTURA))
    d = ImageDraw.Draw(img)
    for y in range(ALTURA):
        t = y / ALTURA
        cor = tuple(int(COR_TOPO[i] + (COR_BASE[i] - COR_TOPO[i]) * t) for i in range(3))
        d.line([(0, y), (LARGURA, y)], fill=cor)
    return img

def desenhar_slide(texto, n, total):
    img = fundo()
    d = ImageDraw.Draw(img)
    margem = 110
    area_w, area_h = LARGURA - 2 * margem, ALTURA - 2 * 260
    capa = n == 1
    cor = COR_DESTAQUE if capa else COR_TEXTO

    # escolhe o maior tamanho de fonte que cabe na área
    for tam in range(120 if capa else 92, 40, -4):
        f = fonte(tam)
        linhas = quebrar(d, texto, f, area_w)
        altura_linha = int(tam * 1.3)
        if len(linhas) * altura_linha <= area_h:
            break
    y = (ALTURA - len(linhas) * altura_linha) // 2
    for linha in linhas:
        w = d.textlength(linha, font=f)
        d.text(((LARGURA - w) / 2, y), linha, font=f, fill=cor)
        y += altura_linha

    # detalhes: barra dourada, perfil e numeração
    d.rectangle([LARGURA / 2 - 60, 150, LARGURA / 2 + 60, 158], fill=COR_DESTAQUE)
    fp = fonte(34)
    w = d.textlength(PERFIL, font=fp)
    d.text(((LARGURA - w) / 2, ALTURA - 140), PERFIL, font=fp, fill=COR_DESTAQUE)
    if total > 1:
        num = f"{n}/{total}"
        d.text((LARGURA - margem - d.textlength(num, font=fp), 90), num, font=fp, fill=(180, 200, 205))
    if n < total:
        d.text((LARGURA - margem - 40, ALTURA - 140), "›", font=fonte(60), fill=COR_DESTAQUE)
    return img

def gerar_post(post, pasta_base="images"):
    pasta = os.path.join(pasta_base, post["data"])
    os.makedirs(pasta, exist_ok=True)
    caminhos = []
    total = len(post["slides"])
    for i, texto in enumerate(post["slides"], 1):
        caminho = os.path.join(pasta, f"slide_{i}.jpg")
        desenhar_slide(texto, i, total).save(caminho, "JPEG", quality=92)
        caminhos.append(caminho)
    return caminhos

def hoje():
    from zoneinfo import ZoneInfo
    return datetime.datetime.now(ZoneInfo(FUSO)).date().isoformat()

if __name__ == "__main__":
    posts = carregar_posts()
    if "--hoje" in sys.argv:
        posts = [p for p in posts if p["data"] == hoje()]
        pasta = "images"
    else:
        pasta = "preview"  # pré-visualização local de todos os posts
    for p in posts:
        if not 2 <= len(p["slides"]) <= 10:
            sys.exit(f"Post {p['data']}: carrossel precisa ter de 2 a 10 slides.")
        print(p["data"], "->", len(gerar_post(p, pasta)), "imagens")
    if not posts:
        print("Nenhum post para hoje.")
