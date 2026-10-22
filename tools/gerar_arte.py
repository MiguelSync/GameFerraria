"""Gera a arte ORIGINAL da Vila Ferraria (pixel art) e, opcionalmente, o mapa.

Uso (na raiz do repositório, com o Pillow instalado: pip install -r tools/requirements.txt):

    python tools/gerar_arte.py            # grava os 3 PNGs em client/assets/
    python tools/gerar_arte.py --mapa     # idem + reescreve client/assets/vila.json
    python tools/gerar_arte.py --previa   # idem + tools/previa.png (folha de contato 4x)

Toda a arte é desenhada aqui, pixel a pixel, a partir de matrizes de letras e de primitivas
(retângulo, linha, círculo) usando só as 31 cores de PALETA. Não há imagem de terceiros nem
arte de jogo comercial. O resultado é determinístico: a única fonte de variação é
random.Random(2026), então rodar de novo grava exatamente os mesmos bytes.

Autoria e licença: arte criada para este trabalho por Miguel Antonio Selhorst (@MiguelSync),
licença CC BY 4.0. O script foi escrito com ajuda de IA (Claude Code), conforme o README.
Contratos: specs/002-visual-ferraria/contracts/assets.md e contracts/mapa.md.
"""
import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "client" / "assets"

# Uma letra por cor (data-model.md §1). "." é transparente.
PALETA = {
    "k": "#2b1d14", "m": "#5a3d24", "w": "#8a5a32", "W": "#b9824a",
    "p": "#4a4a52", "P": "#7b7b86", "q": "#a9a9b3",
    "t": "#9c7448", "T": "#c49a64", "c": "#8f8576",
    "g": "#4f7a3a", "G": "#6f9e4b", "h": "#93bf62", "f": "#e8c547",
    "b": "#9c3d14", "B": "#c4511f", "o": "#f08a24", "y": "#ffd54a",
    "s": "#8c8a86", "S": "#c2bfb8", "i": "#6b7079", "l": "#b8bcc4", "L": "#e6e9ee",
    "a": "#3d7fb3", "A": "#6fb0d9", "e": "#f1e1b8", "E": "#d7bf8a", "r": "#a8322a",
    "x": "#e0a878", "v": "#6b3f22", "u": "#3f6a8a",
}
RGBA = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) + (255,) for k, v in PALETA.items()}
rng = random.Random(2026)


# ---------------------------------------------------------------- tela de pixels
class Tela:
    """Grade de letras da paleta; vira uma Image RGBA sem antisserrilhado."""

    def __init__(self, larg, alt, fundo="."):
        self.larg, self.alt = larg, alt
        self.px = [[fundo] * larg for _ in range(alt)]

    def p(self, x, y, c):
        if 0 <= x < self.larg and 0 <= y < self.alt and c != " ":
            self.px[y][x] = c

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.larg and 0 <= y < self.alt else "."

    def ret(self, x0, y0, x1, y1, c):                 # retângulo cheio, inclusivo
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.p(x, y, c)

    def borda(self, x0, y0, x1, y1, c):
        for x in range(x0, x1 + 1):
            self.p(x, y0, c); self.p(x, y1, c)
        for y in range(y0, y1 + 1):
            self.p(x0, y, c); self.p(x1, y, c)

    def linha(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.p(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def circ(self, cx, cy, r, c):                     # círculo cheio
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.p(x, y, c)

    def matriz(self, linhas, dx=0, dy=0):             # cola uma matriz de letras
        for y, linha in enumerate(linhas):
            for x, c in enumerate(linha):
                if c != ".":
                    self.p(dx + x, dy + y, c)

    def contornar(self, c="k"):
        """Põe contorno em volta de tudo o que não é transparente."""
        alvo = [(x, y) for y in range(self.alt) for x in range(self.larg)
                if self.px[y][x] == "." and any(self.get(x + dx, y + dy) not in (".", c)
                                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in alvo:
            self.px[y][x] = c

    def salpicar(self, x0, y0, x1, y1, cores, chance, so_cheio=False):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if rng.random() < chance:
                    cor = rng.choice(cores)
                    if not (so_cheio and self.get(x, y) == "."):
                        self.p(x, y, cor)

    def imagem(self):
        img = Image.new("RGBA", (self.larg, self.alt), (0, 0, 0, 0))
        for y, linha in enumerate(self.px):
            for x, c in enumerate(linha):
                if c != ".":
                    if c not in RGBA:
                        raise ValueError(f"letra fora da paleta: {c!r}")
                    img.putpixel((x, y), RGBA[c])
        return img


def desenhar(linhas, tam):
    """Matriz de letras -> Tela, validando o tamanho exato."""
    if len(linhas) != tam or any(len(l) != tam for l in linhas):
        raise ValueError(f"matriz deveria ter {tam}x{tam}")
    t = Tela(tam, tam)
    t.matriz(linhas)
    return t


def espelhar(t):
    novo = Tela(t.larg, t.alt)
    novo.px = [list(reversed(l)) for l in t.px]
    return novo


def folha(quadros, colunas, tam, linhas):
    img = Image.new("RGBA", (colunas * tam, linhas * tam), (0, 0, 0, 0))
    for i, q in enumerate(quadros):
        if q is not None:
            img.paste(q.imagem(), ((i % colunas) * tam, (i // colunas) * tam))
    return img


def salvar(img, caminho):
    img.save(caminho, format="PNG", optimize=False)


# ---------------------------------------------------------------- tileset 16x16
def chao(base, salpicos, chance):
    t = Tela(16, 16, base)
    t.salpicar(0, 0, 15, 15, salpicos, chance)
    return t


def grama(var):
    t = chao("G", "gh", 0.10)
    if var == 1:                                     # tufos
        for _ in range(4):
            x, y = rng.randint(1, 13), rng.randint(2, 14)
            t.p(x, y, "h"); t.p(x + 1, y - 1, "h"); t.p(x + 2, y, "h"); t.p(x + 1, y, "g")
    if var == 2:                                     # flores
        for _ in range(4):
            x, y = rng.randint(1, 14), rng.randint(1, 14)
            t.p(x, y, "f"); t.p(x, y + 1, "g")
    return t


def regiao(x, y, soma, lo, hi):
    """Pixel dentro da região de caminho/água (regra N=1, L=2, S=4, O=8)."""
    h = "O" if x < lo else ("L" if x > hi else None)
    v = "N" if y < lo else ("S" if y > hi else None)
    lado = {"N": 1, "L": 2, "S": 4, "O": 8}
    if h and v:
        return bool(soma & lado[h]) and bool(soma & lado[v])
    if h:
        return bool(soma & lado[h])
    if v:
        return bool(soma & lado[v])
    return True


def autopeca(soma, lo, hi, miolo, salpico, beira, chance):
    t = grama(0)
    dentro = [[regiao(x, y, soma, lo, hi) for x in range(16)] for y in range(16)]
    for y in range(16):
        for x in range(16):
            if not dentro[y][x]:
                continue
            viz = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                viz.append(dentro[ny][nx] if 0 <= nx < 16 and 0 <= ny < 16 else True)
            if not all(viz):
                t.p(x, y, beira)
            else:
                t.p(x, y, salpico if rng.random() < chance else miolo)
    return t


def trilho(vertical):
    t = Tela(16, 16)
    for d in range(1, 16, 4):                        # dormentes de madeira
        for e in range(3, 13):
            (t.p(e, d, "w") if vertical else t.p(d, e, "w"))
            (t.p(e, d + 1, "m") if vertical else t.p(d + 1, e, "m"))
    for e in (5, 10):                                # trilhos de ferro
        for d in range(16):
            (t.p(e, d, "i") if vertical else t.p(d, e, "i"))
        for d in range(0, 16, 3):
            (t.p(e, d, "q") if vertical else t.p(d, e, "q"))
    return t


def trilho_curva(canto):
    """canto = (cx, cy) do centro do arco: (16,16) sul->leste, (-1,16) oeste->sul."""
    t = Tela(16, 16)
    cx, cy = canto
    for y in range(16):
        for x in range(16):
            r = math.hypot(x - cx + 0.5, y - cy + 0.5)
            if 3.5 <= r <= 12.5 and int(math.degrees(math.atan2(y - cy, x - cx))) % 20 < 6:
                t.p(x, y, "w")
            if abs(r - 5.5) < 0.6 or abs(r - 10.5) < 0.6:
                t.p(x, y, "i")
    return t


def batente(leste):
    t = trilho(False)
    x0 = 11 if leste else 1
    t.ret(x0, 3, x0 + 3, 12, "m"); t.ret(x0 + 1, 4, x0 + 2, 11, "w")
    t.ret(x0, 2, x0 + 3, 2, "k"); t.p(x0 + 1, 6, "i"); t.p(x0 + 1, 9, "i")
    return t


def decoracao():
    pinheiro = desenhar([
        ".......k........", "......kgk.......", ".....kgGgk......", "....kgGhGgk.....",
        "......kgk.......", ".....kgGGgk.....", "....kgGhGGgk....", "...kgGGhGGGgk...",
        ".....kgGGgk.....", "....kgGhGGGgk...", "...kgGGGhGGGgk..", "..kggggggggggk..",
        "...kkkkkkkkkk...", "......kmmk......", "......kwmk......", ".....kkkkkk.....",
    ], 16)
    arbusto = desenhar([
        "................", "................", "................", "................",
        "................", "......kkkk......", "....kkgGGgkk....", "...kgGGhGGGgk...",
        "..kgGhGGGGhGgk..", "..kgGGGfGGGGgk..", "..kgGGGGGGhGgk..", "..kggGGGGGGggk..",
        "...kgggggggg k..".replace(" ", "g"), "....kkkkkkkk....", "................", "................",
    ], 16)
    pedra = Tela(16, 16)
    pedra.circ(7.5, 10.5, 3.6, "P"); pedra.ret(5, 8, 7, 9, "q"); pedra.ret(6, 12, 10, 13, "p")
    pedra.contornar()
    rochedo = Tela(16, 16)
    rochedo.circ(7.5, 9, 5.8, "P"); rochedo.circ(5.5, 7, 2.5, "q"); rochedo.ret(4, 12, 12, 14, "p")
    rochedo.linha(8, 5, 10, 10, "p"); rochedo.contornar()
    toco = Tela(16, 16)
    toco.ret(5, 8, 10, 13, "w"); toco.ret(5, 7, 10, 8, "W"); toco.ret(7, 7, 8, 7, "T")
    toco.linha(5, 9, 5, 13, "m"); toco.p(4, 13, "w"); toco.p(11, 13, "w"); toco.contornar()
    cerca_h = Tela(16, 16)
    for x in (2, 13):
        cerca_h.ret(x, 5, x + 1, 13, "w"); cerca_h.p(x, 5, "W")
    cerca_h.ret(0, 7, 15, 8, "W"); cerca_h.ret(0, 11, 15, 11, "w")
    cerca_h.contornar()
    cerca_v = Tela(16, 16)
    cerca_v.ret(7, 0, 8, 15, "w"); cerca_v.ret(6, 3, 9, 4, "W"); cerca_v.ret(6, 11, 9, 12, "W")
    cerca_v.contornar()
    lenha = Tela(16, 16)
    for i, (x, y) in enumerate(((3, 11), (8, 11), (5, 8), (10, 8) if False else (5, 8))):
        pass
    for (x, y) in ((2, 11), (7, 11), (12, 11), (4, 8), (9, 8), (7, 5)):
        lenha.circ(x + 0.5, y + 0.5, 2.2, "w"); lenha.p(x, y, "T"); lenha.p(x + 1, y, "W")
    lenha.contornar()
    carvao = Tela(16, 16)
    carvao.circ(7.5, 11, 4.6, "p"); carvao.circ(7.5, 12, 4.6, "k")
    carvao.circ(7.5, 10.5, 3.2, "p"); carvao.p(6, 9, "i"); carvao.p(9, 10, "i"); carvao.p(8, 12, "b")
    carvao.contornar()
    placa = Tela(16, 16)
    placa.ret(7, 8, 8, 15, "m"); placa.ret(2, 2, 13, 8, "w"); placa.ret(3, 3, 12, 7, "W")
    placa.linha(4, 5, 11, 5, "w"); placa.contornar()
    return [pinheiro, arbusto, pedra, rochedo, toco, cerca_h, cerca_v, lenha, carvao, placa]


def pedreira():
    def bloco(topo):
        t = Tela(16, 16, "P")
        for y in range(0, 16, 5):                    # fiadas de pedra
            t.ret(0, y, 15, y, "p")
            off = 0 if (y // 5) % 2 else 6
            for x in range(off, 16, 11):
                t.ret(x, y, x, min(y + 4, 15), "p")
        t.salpicar(0, 0, 15, 15, "qp", 0.08)
        if topo:
            t.ret(0, 0, 15, 2, "g"); t.ret(0, 3, 15, 3, "k"); t.salpicar(0, 0, 15, 1, "Gh", 0.4)
        return t

    topo, meio = bloco(True), bloco(False)
    esq, dir_ = bloco(False), bloco(False)
    esq.ret(0, 0, 1, 15, "q"); dir_.ret(14, 0, 15, 15, "p"); dir_.ret(15, 0, 15, 15, "k")
    ce, cd = bloco(True), bloco(True)
    ce.ret(0, 0, 1, 15, "q"); cd.ret(14, 4, 15, 15, "p"); cd.ret(15, 0, 15, 15, "k")
    soltas = chao("c", "ps", 0.12)
    for (x, y, r) in ((4, 5, 2.2), (11, 10, 2.6), (6, 12, 1.6)):
        soltas.circ(x, y, r, "P"); soltas.p(int(x) - 1, int(y) - 1, "q")
    veio = bloco(False)
    for (x, y) in ((4, 6), (5, 7), (9, 9), (10, 10), (11, 9), (6, 12), (12, 3)):
        veio.p(x, y, "B"); veio.p(x + 1, y, "b")
    return [topo, meio, esq, dir_, ce, cd, soltas, veio]


def tileset():
    pecas = [grama(0), grama(1), grama(2),
             chao("t", "T", 0.12),                     # 3 terra batida
             chao("c", "pq", 0.15),                    # 4 cascalho
             chao("g", "G", 0.15),                     # 5 grama escura
             chao("c", "pst", 0.25)]                   # 6 lastro
    tabuas = Tela(16, 16, "w")                         # 7 tábuas
    for y in range(0, 16, 4):
        tabuas.ret(0, y, 15, y, "m")
        tabuas.ret(0, y + 1, 15, y + 1, "W")
    for y, x in ((1, 5), (5, 11), (9, 3), (13, 9)):
        tabuas.ret(x, y, x, y + 2, "m")
    pecas.append(tabuas)
    pecas += [autopeca(s, 4, 11, "t", "T", "T", 0.10) for s in range(16)]   # 8–23 caminho
    pecas += [autopeca(s, 3, 12, "a", "A", "A", 0.06) for s in range(16)]   # 24–39 água
    pecas += [trilho(False), trilho(True), trilho_curva((16, 16)), trilho_curva((-1, 16)),
              batente(True), batente(False)]                                 # 40–45
    pecas += decoracao()                                                     # 46–55
    pecas += pedreira()                                                      # 56–63
    assert len(pecas) == 64, len(pecas)
    return folha(pecas, 16, 16, 4)


# ---------------------------------------------------------------- sprites 16x16
FERREIRO_CORPO = [
    "................",
    "......kkkk......",
    ".....kmmmmk.....",
    ".....kmxxmk.....",
    ".....kxkxkk.....",
    ".....kxxxxk.....",
    "......kxxk......",
    "....kkuvvukk....",
    "...kxuvvvvuxk...",
    "...kxuvvvvuxk...",
    "...kkuvvvvukk...",
    ".....kvvvvk.....",
]
PERNAS = {
    "parado": ["....kmk.kmk.....", "....kmk.kmk.....", "....kkk.kkk.....", "................"],
    "passo1": ["....kmk..kmk....", "...kmk...kmk....", "...kkk....kkk...", "................"],
    "passo2": ["....kmkkmk......", ".....kmkmk......", ".....kkkkk......", "................"],
    "passo3": ["...kmk..kmk.....", "...kmk...kmk....", "..kkk....kkk....", "................"],
}


def ferreiro(pernas, martelo=None):
    t = Tela(16, 16)
    t.matriz(FERREIRO_CORPO)
    t.matriz(PERNAS[pernas], 0, 12)
    if martelo == "alto":                            # martelo erguido acima do ombro
        t.linha(12, 8, 13, 3, "m"); t.ret(12, 1, 15, 3, "i"); t.ret(12, 1, 15, 1, "q")
    elif martelo == "baixo":                         # martelo batendo na bigorna
        t.linha(12, 9, 14, 12, "m"); t.ret(13, 12, 15, 14, "i"); t.ret(13, 12, 15, 12, "q")
    elif martelo == "mao":
        t.linha(12, 9, 12, 13, "m"); t.ret(11, 13, 13, 14, "i")
    return t


def sprites16():
    q = [ferreiro("parado", "mao"),
         ferreiro("passo1"), ferreiro("passo2"), ferreiro("passo3"), ferreiro("passo2"),
         ferreiro("parado", "alto"), ferreiro("parado", "baixo")]
    faisca = Tela(16, 16)
    faisca.ret(7, 3, 8, 12, "y"); faisca.ret(3, 7, 12, 8, "y"); faisca.ret(6, 6, 9, 9, "L")
    for d in (4, 11):
        faisca.p(d, d, "o"); faisca.p(d, 15 - d, "o")
    q.append(faisca)
    for r in (2.6, 4.0, 5.6):                        # fumaça
        f = Tela(16, 16)
        f.circ(7.5, 8, r, "s"); f.circ(6.5, 7, r * 0.6, "S")
        q.append(f)
    lingote = Tela(16, 16)
    lingote.matriz(["....kkkkkkkk....", "...klLLLLLLlk...", "..klLLlllllllk..", ".kkkkkkkkkkkkkk.",
                    ".klllllllllllik.", ".kiiiiiiiiiiiik.", ".kkkkkkkkkkkkkk."], 0, 5)
    q.append(lingote)
    for cheio in (False, True):                      # carrinho de minério
        c = Tela(16, 16)
        c.ret(1, 6, 14, 11, "w"); c.ret(2, 7, 13, 10, "W"); c.ret(1, 6, 14, 6, "m")
        c.ret(4, 7, 4, 10, "w"); c.ret(11, 7, 11, 10, "w")
        c.ret(0, 11, 15, 11, "i")
        c.circ(4, 13, 1.8, "p"); c.circ(11, 13, 1.8, "p"); c.p(4, 13, "q"); c.p(11, 13, "q")
        if cheio:
            c.circ(5, 5, 2.4, "P"); c.circ(9.5, 4.5, 2.6, "p"); c.circ(12, 5.5, 1.8, "P")
            c.p(5, 4, "B"); c.p(10, 3, "b"); c.p(9, 5, "B"); c.p(12, 5, "q")
        c.contornar()
        q.append(c)
    for acesa in (False, True):                      # lanterna
        lt = Tela(16, 16)
        lt.ret(7, 0, 8, 2, "i"); lt.ret(5, 3, 10, 3, "k")
        lt.ret(5, 4, 10, 10, "y" if acesa else "p"); lt.ret(6, 5, 9, 9, "L" if acesa else "s")
        if acesa:
            lt.ret(7, 6, 8, 8, "o")
        lt.ret(5, 4, 5, 10, "k"); lt.ret(10, 4, 10, 10, "k"); lt.ret(5, 11, 10, 11, "k")
        lt.ret(7, 12, 8, 15, "m")
        q.append(lt)
    carimbo = Tela(16, 16)
    carimbo.circ(7.5, 7.5, 6.6, "r"); carimbo.circ(7.5, 7.5, 5.2, "."); carimbo.circ(7.5, 7.5, 4.4, "r")
    carimbo.circ(7.5, 7.5, 3.2, ".")
    carimbo.linha(5, 8, 7, 10, "r"); carimbo.linha(7, 10, 11, 5, "r")
    q.append(carimbo)
    for formato in range(3):                         # pedaços de pergaminho
        pd = Tela(16, 16)
        pts = [((4, 4), (11, 5), (9, 12), (3, 10)), ((6, 3), (12, 8), (5, 12)),
               ((3, 6), (12, 4), (10, 11), (6, 9))][formato]
        xs, ys = [p_[0] for p_ in pts], [p_[1] for p_ in pts]
        for y in range(min(ys), max(ys) + 1):
            for x in range(min(xs), max(xs) + 1):
                if (x + y + formato) % 5 != 0:
                    pd.p(x, y, "e" if (x * y) % 7 else "E")
        pd.contornar("E")
        q.append(pd)
    minerio = Tela(16, 16)
    minerio.circ(7.5, 9, 5, "P"); minerio.circ(6, 7.5, 2.5, "q")
    for (x, y) in ((8, 9), (5, 11), (10, 7), (9, 12)):
        minerio.p(x, y, "B"); minerio.p(x + 1, y, "b")
    minerio.contornar()
    q.append(minerio)
    q += [None, None, None]                          # 21–23 reservados
    assert len(q) == 24, len(q)
    return folha(q, 8, 16, 3)


# ---------------------------------------------------------------- sprites 32x32
def forja(brasa):
    """Forja de pedra com chaminé. brasa: 0, 1, 2 (acesa) ou None (apagada)."""
    t = Tela(32, 32)
    t.ret(3, 14, 28, 30, "P")                        # corpo de pedra
    for y in range(14, 31, 4):
        t.ret(3, y, 28, y, "p")
        off = 3 if (y // 4) % 2 else 7
        for x in range(off, 29, 8):
            t.ret(x, y, x, min(y + 3, 30), "p")
    t.salpicar(4, 15, 27, 29, "q", 0.06)
    for i in range(9):                               # telhado de telha cozida
        t.ret(2 + i, 13 - i, 29 - i if i < 3 else 22, 13 - i, "b" if i % 2 else "B")
    t.ret(1, 13, 30, 13, "b")
    t.ret(22, 1, 27, 13, "P"); t.ret(22, 1, 27, 2, "q")     # chaminé
    for y in range(4, 13, 3):
        t.ret(22, y, 27, y, "p")
    t.ret(21, 0, 28, 0, "p")
    t.ret(9, 19, 22, 30, "k")                        # boca da fornalha
    t.ret(10, 20, 21, 30, "p")
    t.ret(8, 18, 23, 18, "q")
    if brasa is None:
        t.ret(11, 26, 20, 29, "b"); t.salpicar(11, 26, 20, 29, "ps", 0.4)
    else:
        t.ret(11, 25, 20, 29, "B")
        chama = [(12, 24), (15, 22), (18, 23), (14, 26), (17, 25)]
        for j, (x, y) in enumerate(chama):
            h = 2 + (j + brasa) % 3
            t.ret(x, y - h + 2, x + 1, 28, "o")
            t.ret(x, y - h + 4, x + 1, 28, "y")
        t.salpicar(11, 27, 20, 29, "yB", 0.25)
        t.p(13 + brasa * 2, 21, "y")
    t.ret(24, 24, 28, 30, "m"); t.ret(25, 25, 27, 29, "w")   # lenha encostada
    t.contornar()
    return t


def canteiro():
    t = Tela(32, 32)
    t.ret(4, 22, 27, 30, "P"); t.ret(4, 22, 27, 22, "q")       # base de pedra começada
    for x in range(4, 28, 6):
        t.ret(x, 23, x, 30, "p")
    t.ret(4, 26, 27, 26, "p")
    for x in (3, 27):                                          # andaime
        t.ret(x, 4, x + 1, 30, "w"); t.ret(x, 4, x, 30, "W")
    for y in (6, 14):
        t.ret(3, y, 28, y + 1, "w"); t.ret(3, y, 28, y, "W")
    t.linha(5, 15, 26, 6, "m"); t.linha(5, 6, 26, 15, "m")
    t.ret(12, 2, 19, 5, "w"); t.ret(13, 3, 18, 4, "W")       # balde de argamassa
    t.ret(14, 17, 22, 18, "i"); t.ret(12, 16, 23, 16, "q")    # bigorna
    t.ret(16, 19, 20, 21, "i"); t.ret(14, 22, 22, 22, "p")
    t.ret(10, 16, 12, 17, "i")
    t.contornar()
    return t


def mina(aberta):
    t = Tela(32, 32)
    t.circ(15.5, 19, 15, "p"); t.circ(15.5, 19, 13, "P"); t.salpicar(2, 5, 29, 31, "qp", 0.12, so_cheio=True)
    for (x, y) in ((6, 12), (24, 10), (9, 25), (25, 22)):
        t.p(x, y, "B"); t.p(x + 1, y, "b")
    t.ret(0, 31, 31, 31, ".")
    t.ret(9, 12, 22, 31, "k")                                  # boca
    t.ret(7, 10, 24, 12, "m"); t.ret(7, 10, 24, 10, "W")       # viga
    t.ret(7, 12, 9, 31, "m"); t.ret(22, 12, 24, 31, "m"); t.ret(7, 12, 7, 31, "W")
    if aberta:
        t.ret(10, 13, 21, 31, "k")
        for y in range(16, 31, 3):
            t.ret(11, y, 20, y, "m")
        t.ret(12, 14, 12, 31, "i"); t.ret(19, 14, 19, 31, "i")
    else:
        t.ret(10, 13, 21, 31, "w")
        for x in range(10, 22, 3):
            t.ret(x, 13, x, 31, "m")
        t.ret(10, 18, 21, 19, "m"); t.ret(10, 26, 21, 27, "m"); t.p(20, 22, "i")
    t.contornar()
    return t


def quadro():
    t = Tela(32, 32)
    t.ret(5, 20, 6, 31, "m"); t.ret(25, 20, 26, 31, "m")      # postes
    t.ret(2, 6, 29, 22, "m"); t.ret(3, 7, 28, 21, "w")        # moldura e tábuas
    for y in range(7, 22, 4):
        t.ret(3, y, 28, y, "W")
    t.ret(1, 3, 30, 5, "b"); t.ret(3, 2, 28, 2, "B")           # telhadinho
    t.contornar()
    return t


def pergaminho(tipo):
    t = Tela(32, 32)
    papel, sombra = ("E", "w") if tipo == "amarelo" else ("e", "E")
    t.ret(9, 8, 22, 20, papel); t.ret(8, 8, 23, 9, sombra); t.ret(8, 19, 23, 20, sombra)
    for y in (12, 14, 16):
        t.ret(11, y, 20 if y != 16 else 16, y, "m" if tipo != "amarelo" else "w")
    t.ret(15, 7, 16, 8, "r")                                   # prego/cordão
    if tipo == "amarelo":
        t.salpicar(9, 10, 22, 18, "Ew", 0.15)
        t.p(22, 19, "."); t.p(21, 20, "."); t.p(9, 20, ".")
    if tipo == "carimbado":
        t.circ(19, 16, 3.6, "r"); t.circ(19, 16, 2.4, papel); t.linha(17, 16, 18, 17, "r")
        t.linha(18, 17, 21, 14, "r")
    t.contornar()
    return t


def estrado():
    t = Tela(32, 32)
    t.ret(3, 25, 28, 26, "W"); t.ret(3, 27, 28, 28, "w")
    for x in (4, 15, 26):
        t.ret(x, 29, x + 1, 30, "m")
    t.contornar()
    return t


def sprites32():
    q = [canteiro(), forja(0), forja(1), forja(2), forja(None), mina(False), mina(True),
         quadro(), pergaminho("pregado"), pergaminho("amarelo"), pergaminho("carimbado"), estrado()]
    return folha(q, 4, 32, 3)


# ---------------------------------------------------------------- mapa (Tiled)
L, A = 24, 12        # peças


def gerar_mapa():
    chao_ = [[0] * L for _ in range(A)]
    deco = [[-1] * L for _ in range(A)]
    caminho, agua = set(), set()

    for x in range(L):                               # rua horizontal (linha 6)
        caminho.add((x, 6))
    for x in (2,):                                   # da mina até a rua
        caminho.update({(x, 4), (x, 5)})
    for x in (8, 13, 18):                            # ligações dos lotes
        caminho.update({(x, 5), (x, 7)})
    for y in range(7, A):                            # lagoa no canto inferior esquerdo
        for x in range(0, 2 + (y - 7)):
            if x < 6:
                agua.add((x, y))

    def soma(conj, x, y, fora_dentro):
        s = 0
        for bit, (dx, dy) in ((1, (0, -1)), (2, (1, 0)), (4, (0, 1)), (8, (-1, 0))):
            nx, ny = x + dx, y + dy
            dentro = (nx, ny) in conj if 0 <= nx < L and 0 <= ny < A else fora_dentro
            s += bit if dentro else 0
        return s

    for y in range(A):
        for x in range(L):
            r = rng.random()
            chao_[y][x] = 1 if r < 0.18 else (2 if r < 0.28 else 0)
    for y in range(0, 4):                            # pedreira: cascalho em volta da mina
        for x in range(0, 7):
            chao_[y][x] = 4
    chao_[2][2] = 7; chao_[3][2] = 7                 # tábuas na boca da mina
    for (x, y) in caminho:
        chao_[y][x] = 8 + soma(caminho, x, y, True)
    for (x, y) in agua:
        chao_[y][x] = 24 + soma(agua, x, y, True)

    for x in range(0, 6):                            # paredão nas linhas 0 e 1
        deco[0][x] = 61 if x == 5 else 56
        deco[1][x] = 59 if x == 5 else 57
    deco[1][3] = 63                                  # veio de minério
    deco[3][5] = 62; deco[3][0] = 62
    for x in range(4, 14):                           # trilho da mina até o batente
        deco[2][x] = 40
        chao_[2][x] = 6
    deco[2][14] = 44; chao_[2][14] = 6
    deco[3][1] = 53                                  # lenha perto da mina
    for (x, y, peca) in ((7, 0, 46), (12, 0, 46), (17, 0, 46), (23, 0, 46), (23, 2, 47),
                         (0, 4, 46), (23, 4, 47), (6, 10, 46), (10, 11, 46), (11, 10, 47),
                         (16, 11, 46), (21, 11, 46), (22, 11, 46), (23, 10, 46), (15, 9, 48),
                         (9, 9, 49), (20, 9, 50), (3, 5, 55), (11, 3, 48), (16, 3, 50),
                         (21, 1, 47), (10, 1, 49), (5, 10, 47)):
        deco[y][x] = peca
    for x in range(19, 24):                          # cerca do pátio do quadro
        deco[9][x] = 51
    deco[9][19] = 51
    deco[4][11] = 54; deco[8][16] = 54               # carvão perto dos lotes

    def ponto(nome, x, y):
        return {"id": 0, "name": nome, "type": "", "point": True, "x": x, "y": y,
                "width": 0, "height": 0, "rotation": 0, "visible": True}

    pts = [ponto("lote1", 136, 64), ponto("lote2", 216, 64), ponto("lote3", 296, 64),
           ponto("lote4", 136, 144), ponto("lote5", 216, 144), ponto("lote6", 296, 144),
           ponto("mina", 40, 40), ponto("espera1", 24, 76), ponto("espera2", 60, 76),
           ponto("saida", 40, 104), ponto("trilho_fim", 216, 40), ponto("pilha", 352, 128),
           ponto("quadro", 356, 64), ponto("lanterna_mina", 66, 30), ponto("lanterna1", 104, 88),
           ponto("lanterna2", 256, 88), ponto("lanterna3", 328, 120)]
    for i, p_ in enumerate(pts, start=1):
        p_["id"] = i
    plano = lambda m: [v + 1 if v >= 0 else 0 for linha in m for v in linha]   # noqa: E731
    return {
        "type": "map", "version": "1.10", "tiledversion": "1.10.2", "orientation": "orthogonal",
        "renderorder": "right-down", "width": L, "height": A, "tilewidth": 16, "tileheight": 16,
        "infinite": False, "nextlayerid": 4, "nextobjectid": len(pts) + 1,
        "tilesets": [{"firstgid": 1, "name": "tileset-ferraria", "image": "tileset-ferraria.png",
                      "imagewidth": 256, "imageheight": 64, "columns": 16, "tilecount": 64,
                      "tilewidth": 16, "tileheight": 16, "margin": 0, "spacing": 0}],
        "layers": [
            {"id": 1, "name": "chao", "type": "tilelayer", "width": L, "height": A, "x": 0, "y": 0,
             "opacity": 1, "visible": True, "data": plano(chao_)},
            {"id": 2, "name": "decoracao", "type": "tilelayer", "width": L, "height": A, "x": 0,
             "y": 0, "opacity": 1, "visible": True, "data": plano(deco)},
            {"id": 3, "name": "pontos", "type": "objectgroup", "draworder": "topdown", "x": 0,
             "y": 0, "opacity": 1, "visible": True, "objects": pts},
        ],
    }


# ---------------------------------------------------------------- prévia e main
def previa(imagens):
    blocos = []
    for nome, img, tam in imagens:
        big = img.resize((img.width * 4, img.height * 4), Image.NEAREST)
        fundo = Image.new("RGBA", big.size, (246, 239, 226, 255))
        fundo.alpha_composite(big)
        d = ImageDraw.Draw(fundo)
        n = 0
        for y in range(0, big.height, tam * 4):
            for x in range(0, big.width, tam * 4):
                d.rectangle([x, y, x + tam * 4 - 1, y + tam * 4 - 1], outline=(200, 80, 40, 255))
                d.text((x + 2, y + 1), str(n), fill=(40, 20, 10, 255))
                n += 1
        blocos.append((nome, fundo))
    larg = max(b.width for _, b in blocos) + 20
    alt = sum(b.height + 30 for _, b in blocos) + 10
    folha_ = Image.new("RGBA", (larg, alt), (255, 255, 255, 255))
    d = ImageDraw.Draw(folha_)
    y = 10
    for nome, b in blocos:
        d.text((10, y), nome, fill=(0, 0, 0, 255))
        folha_.alpha_composite(b, (10, y + 16))
        y += b.height + 30
    return folha_


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mapa", action="store_true", help="reescreve client/assets/vila.json")
    ap.add_argument("--previa", action="store_true", help="grava tools/previa.png")
    args = ap.parse_args()

    imagens = [("tileset-ferraria.png", tileset(), 16), ("sprites16-ferraria.png", sprites16(), 16),
               ("sprites32-ferraria.png", sprites32(), 32)]
    esperado = {"tileset-ferraria.png": (256, 64), "sprites16-ferraria.png": (128, 48),
                "sprites32-ferraria.png": (128, 96)}
    for nome, img, _ in imagens:
        assert img.size == esperado[nome], (nome, img.size)
        salvar(img, ASSETS / nome)
        print("gravado", ASSETS / nome, img.size)
    if args.mapa:
        mapa = gerar_mapa()
        (ASSETS / "vila.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=1) + "\n",
                                          encoding="utf-8")
        print("gravado", ASSETS / "vila.json")
    if args.previa:
        salvar(previa(imagens), Path(__file__).resolve().parent / "previa.png")
        print("gravado tools/previa.png")


if __name__ == "__main__":
    main()
