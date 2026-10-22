# Contrato: assets gerados (`tools/gerar_arte.py` → cena Phaser)

O script é a **única** fonte destes arquivos; a cena só depende dos nomes, tamanhos e índices
abaixo. Mudar um índice exige mudar este contrato, o script e a cena juntos.

## Geração

```bash
pip install -r tools/requirements.txt      # Pillow (só desenvolvimento)
python tools/gerar_arte.py                 # grava os 3 PNGs em client/assets/
python tools/gerar_arte.py --mapa          # idem + reescreve client/assets/vila.json (descarta edições do Tiled)
python tools/gerar_arte.py --previa        # idem + tools/previa.png ampliada 4× (ignorada no git)
```

Determinismo: rodar duas vezes seguidas gera bytes idênticos (`git diff --exit-code client/assets/`
vazio). Cada PNG é RGBA, fundo transparente, sem antisserrilhado (só cores da paleta de
[data-model.md](../data-model.md) §1).

## `tileset-ferraria.png` — 256 × 64, peças 16 × 16, 16 colunas

Chave no Phaser: `"tiles"`; nome do tileset no Tiled: `tileset-ferraria`. O número é o da peça
no Tiled (gid − 1).

| Peças | Conteúdo |
|---|---|
| 0 | grama lisa |
| 1 | grama com tufos |
| 2 | grama com flores |
| 3 | terra batida (pátio) |
| 4 | cascalho (chão da pedreira) |
| 5 | grama escura (sombra de árvore) |
| 6 | lastro de cascalho (sob o trilho) |
| 7 | tábuas (chão da entrada da mina) |
| 8–23 | **caminho de terra batida**: número = 8 + soma dos lados com mais caminho (Norte 1, Leste 2, Sul 4, Oeste 8) — mesma regra do kit; ex.: 18 reto horizontal, 13 reto vertical, 23 cruzamento |
| 24–39 | **água** (lagoa/rio): número = 24 + mesma soma; 39 = água por dentro |
| 40 | trilho horizontal |
| 41 | trilho vertical |
| 42 | trilho curva sul→leste |
| 43 | trilho curva oeste→sul |
| 44 | batente do fim do trilho (lado leste) |
| 45 | batente do fim do trilho (lado oeste) |
| 46 | pinheiro |
| 47 | arbusto |
| 48 | pedra pequena |
| 49 | rochedo |
| 50 | toco |
| 51 | cerca horizontal |
| 52 | cerca vertical |
| 53 | lenha empilhada |
| 54 | monte de carvão |
| 55 | placa de madeira (sem texto) |
| 56 | paredão da pedreira — topo |
| 57 | paredão da pedreira — meio |
| 58 | paredão — borda esquerda |
| 59 | paredão — borda direita |
| 60 | paredão — canto superior esquerdo |
| 61 | paredão — canto superior direito |
| 62 | rochas soltas no cascalho |
| 63 | veio de minério na rocha |

## `sprites16-ferraria.png` — 128 × 48, quadros 16 × 16, 8 colunas

Chave no Phaser: `"sprites16"` (`load.spritesheet(..., { frameWidth: 16, frameHeight: 16 })`).

| Quadro | Conteúdo | Reserva no modo simples |
|---|---|---|
| 0 | ferreiro parado (avental, martelo na mão) | texto "🧑‍🏭" |
| 1–4 | ferreiro andando (4 passos) | "🧑‍🏭" se movendo |
| 5 | ferreiro martelando — martelo no alto | "🧑‍🏭" + "🔨" piscando |
| 6 | ferreiro martelando — martelo na bigorna | (idem) |
| 7 | faísca | "✨" |
| 8–10 | fumaça (3 tamanhos) | círculo cinza semitransparente |
| 11 | lingote | "🧱" |
| 12 | carrinho de minério vazio | "🛒" |
| 13 | carrinho de minério cheio | "🛒" + "🪨" |
| 14 | lanterna apagada | "🏮" com alfa 0,4 |
| 15 | lanterna acesa | "🏮" |
| 16 | carimbo "entregue" (círculo vermelho) | "✅" |
| 17–19 | pedaços de pergaminho (3 formatos) | "📜" caindo e sumindo |
| 20 | pedra de minério | "🪨" |
| 21–23 | reservados (transparentes) | — |

Animações (criadas só se a textura carregou): `andar` 1–4 a 8 qps em laço; `martelar` 5–6 a 6 qps
em laço; `fumaca` 8–10 a 4 qps (cada nuvem também sobe e some por tween).

## `sprites32-ferraria.png` — 128 × 96, quadros 32 × 32, 4 colunas

Chave no Phaser: `"sprites32"`.

| Quadro | Conteúdo | Reserva no modo simples |
|---|---|---|
| 0 | canteiro com andaime e bigorna | "🏗️" |
| 1–3 | forja de pedra com chaminé, acesa (3 quadros de brasa) | "🔥" pulsando |
| 4 | forja apagada (brasa escura, sem fumaça) | "🪨" (forja fria) |
| 5 | entrada da mina fechada (porta de tábuas) | "⛏️" com alfa 0,5 |
| 6 | entrada da mina aberta (trilho entrando) | "⛏️" |
| 7 | quadro de avisos (vazio) | retângulo marrom 26 × 20 com borda |
| 8 | pergaminho pregado | "📜" |
| 9 | pergaminho amarelado (prazo vencendo/vencido) | "📜" com tinta amarela |
| 10 | pergaminho carimbado "entregue" | "📜✅" |
| 11 | estrado da pilha de lingotes (vazio) | retângulo de madeira 24 × 6 |

Animação: `brasa` 1–3 a 6 qps em laço (para em `vila.encerrada`, trocando para o quadro 4).

## Elementos desenhados só com formas (sem asset)

Barra de progresso da obra e do prazo (retângulos), camada de luz (retângulo), brilho das
lanternas (círculo em `BlendModes.ADD`), balão de recusa (retângulo arredondado creme com borda +
texto), faixa da temporada (texto com fundo), marca "×N" do lote, textos flutuantes ("+10 🪨",
"−40 🪨", "+N lingotes", "+40 🪨") e o aviso "arte indisponível — modo simples".
