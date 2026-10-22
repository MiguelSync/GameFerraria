# Contrato: mapa `client/assets/vila.json`

Gerado por `python tools/gerar_arte.py --mapa` e editável no Tiled 1.10+ (Anexo A do guia). A cena
depende só do que está aqui.

## Formato

| Campo | Valor |
|---|---|
| `type` / `orientation` / `renderorder` | `map` / `orthogonal` / `right-down` |
| `width` × `height` | 24 × 12 peças |
| `tilewidth` / `tileheight` | 16 / 16 (mapa de 384 × 192 px; canvas 768 × 384 com zoom 2×) |
| `version` / `tiledversion` | `1.10` / `1.10.2` |
| `tilesets` | **um**, embutido: `name: "tileset-ferraria"`, `image: "tileset-ferraria.png"`, `firstgid: 1`, `columns: 16`, `tilecount: 64`, `imagewidth: 256`, `imageheight: 64`, `tilewidth/tileheight: 16`, `margin/spacing: 0` |
| `layers[0]` | `tilelayer` `chao` — 288 inteiros (`gid = peça + 1`), **todas** as células preenchidas (grama, terra, cascalho, caminho, água, tábuas) |
| `layers[1]` | `tilelayer` `decoracao` — 288 inteiros, `0` = vazio (trilho, árvores, pedras, cercas, paredão, lenha, carvão, placa) |
| `layers[2]` | `objectgroup` `pontos` — só objetos ponto (`"point": true`, `width/height: 0`) |

Na cena: `make.tilemap({ key: "mapa" })`, `addTilesetImage("tileset-ferraria", "tiles")`,
`createLayer("chao", ...)`, `createLayer("decoracao", ...)`, `getObjectLayer("pontos").objects`.

## Pontos obrigatórios (`name` exato)

`lote1`, `lote2`, `lote3`, `lote4`, `lote5`, `lote6`, `mina`, `espera1`, `espera2`, `saida`,
`trilho_fim`, `pilha`, `quadro`, `lanterna_mina`, `lanterna1`, `lanterna2`, `lanterna3`.
Papel de cada um em [data-model.md](../data-model.md) §3. Coordenadas em pixels do mapa (centro do
elemento).

## Regras de layout que a cena assume

1. A rua de terra batida é **horizontal** na linha de `saida.y` e liga a frente da mina aos 6 lotes
   (3 acima e 3 abaixo da rua, cada um com uma ligação curta até ela); a rota de um ferreiro é
   `espera → saida → (lote.x, saida.y) → lote` (research R7).
2. O trilho sai da `mina` em linha reta até `trilho_fim`, sem cruzar a rua.
3. Cada lote tem 32 × 32 px livres (sem decoração) em volta do ponto; nenhum lote fica a mais de
   270 px de rota da espera (caminhada ≤ 3 s a 90 px/s).
4. `quadro` e `pilha` ficam na faixa da direita, longe do trilho, com 32 px livres acima (para o
   pergaminho, a pilha de 10 lingotes e os textos flutuantes).
5. Pedreira (paredão 56–63 + cascalho) em volta da mina no canto superior esquerdo; lagoa (água
   24–39) no canto inferior esquerdo; árvores e arbustos nas bordas.

Esboço (1 caractere = 1 peça; `M` mina, `=` trilho, `-` rua, `1`–`6` lotes, `Q` quadro, `P` pilha,
`*` lanterna, `~` água, `^` paredão, `:` cascalho, `T` árvore):

```text
^^^^^^:TT....T....T....T
^^^^^^:.................
^^M===========......Q..T
^^:::::.................
T.......1.....2.....3...
..*.....|.....|.....|..*
------------------------
~~......|.....|.....|...
~~~.....4.....5.....6.P.
~~~~..*.................
~~~~~T.....T.....T....T.
~~~~~~TT...T...T....TTT.
```

(O esboço é indicativo; o que vale são os pontos e as regras acima.)

## Reserva (`PONTOS_PADRAO`)

`client/index.html` guarda uma cópia fixa dos 17 pontos gerados pelo script. Se `vila.json` ou o
tileset falhar ao carregar, a cena desenha o chão com formas (fundo verde, rua de terra, lagoa
azul, área de cascalho) e usa `PONTOS_PADRAO`. Se o mapa for editado no Tiled, `PONTOS_PADRAO` não
precisa mudar (só é usado quando o mapa não carrega).
