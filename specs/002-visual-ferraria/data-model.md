# Data Model: Identidade Visual da Vila Ferraria

A 002 **não muda o estado do servidor** (ver `specs/001-vila-ferraria/data-model.md`). Este
documento descreve os dados de apresentação: a paleta e os assets que o script gera, os pontos do
mapa e o estado interno da cena (o que está desenhado), que só existe no navegador e é sempre
derivado do último `estado` recebido.

## 1. Paleta (`PALETA` em `tools/gerar_arte.py`)

Uma letra por cor nas matrizes; `.` = transparente. Valores em hex RGB (alfa 255).

| Letra | Nome | Hex | Uso |
|---|---|---|---|
| `k` | contorno | `#2b1d14` | contorno de tudo (marrom quase preto) |
| `m` | madeira escura | `#5a3d24` | vigas, quadro, cabo do martelo |
| `w` | madeira | `#8a5a32` | tábuas, andaime, carrinho |
| `W` | madeira clara | `#b9824a` | brilho da madeira, estrado |
| `p` | pedra escura | `#4a4a52` | sombras de pedra, paredão da mina |
| `P` | pedra | `#7b7b86` | forja, pedreira, bigorna |
| `q` | pedra clara | `#a9a9b3` | brilho da pedra |
| `t` | terra | `#9c7448` | rua de terra batida |
| `T` | terra clara | `#c49a64` | borda da rua, poeira |
| `c` | cascalho | `#8f8576` | chão da pedreira, trilho (lastro) |
| `g` | grama escura | `#4f7a3a` | sombra da grama |
| `G` | grama | `#6f9e4b` | grama |
| `h` | grama clara | `#93bf62` | tufos |
| `f` | flor | `#e8c547` | flores amarelas |
| `b` | brasa escura | `#9c3d14` | brasa apagando, telhado |
| `B` | brasa | `#c4511f` | brasa |
| `o` | fogo | `#f08a24` | chama |
| `y` | chama clara | `#ffd54a` | miolo da chama, faísca, lanterna acesa |
| `s` | fumaça | `#8c8a86` | fumaça |
| `S` | fumaça clara | `#c2bfb8` | fumaça clara |
| `i` | ferro | `#6b7079` | trilho, ferragens, martelo |
| `l` | lingote | `#b8bcc4` | lingote (aço) |
| `L` | brilho do aço | `#e6e9ee` | reflexo do lingote |
| `a` | água | `#3d7fb3` | lagoa (destaque frio) |
| `A` | água clara | `#6fb0d9` | reflexo |
| `e` | pergaminho | `#f1e1b8` | pergaminho, balão |
| `E` | pergaminho sombra | `#d7bf8a` | dobra, pergaminho amarelado |
| `r` | tinta/carimbo | `#a8322a` | carimbo "entregue", cordão |
| `x` | pele | `#e0a878` | ferreiro |
| `v` | avental | `#6b3f22` | avental de couro |
| `u` | camisa | `#3f6a8a` | camisa do ferreiro |

(31 cores; a noite e a madrugada são feitas pela camada de luz da cena, não por cores da paleta.)

## 2. Assets gerados

Detalhe de cada peça/quadro e da reserva do modo simples em [contracts/assets.md](./contracts/assets.md).

| Arquivo | Tamanho | Grade | Conteúdo |
|---|---|---|---|
| `client/assets/tileset-ferraria.png` | 256 × 64 | 16 × 16, 16 col. | 64 peças: chão (0–7), caminho de terra (8–23), água (24–39), trilho (40–45), decoração (46–55), pedreira/paredão (56–63) |
| `client/assets/sprites16-ferraria.png` | 128 × 48 | 16 × 16, 8 col. | 24 quadros: ferreiro, fumaça, faísca, lingote, carrinho, lanterna, carimbo, pedaços, minério |
| `client/assets/sprites32-ferraria.png` | 128 × 96 | 32 × 32, 4 col. | 12 quadros: canteiro, forja (acesa ×3, apagada), mina (fechada/aberta), quadro, pergaminho (×3), estrado |
| `client/assets/vila.json` | 24 × 12 peças | 16 px | mapa Tiled (contrato em [contracts/mapa.md](./contracts/mapa.md)) |

## 3. Pontos do mapa (camada `pontos`)

| Ponto | Papel na cena |
|---|---|
| `lote1` … `lote6` | onde nascem canteiros e forjas (ordem numérica; regra `usados % 6` da 001) |
| `mina` | entrada da mina (sprite 32 × 32); origem da produção ("+10 🪨", "−40 🪨") |
| `espera1`, `espera2` | onde os ferreiros livres ficam, ao lado da entrada da mina |
| `saida` | ponto da rua de terra em frente à mina; a rua é horizontal na altura `saida.y` |
| `trilho_fim` | fim do trilho; o carrinho vai de `mina` até aqui e volta |
| `pilha` | estrado da pilha de lingotes (até 10 desenhados + número) |
| `quadro` | quadro de avisos (o pergaminho é pregado nele) |
| `lanterna_mina` | lanterna da mina |
| `lanterna1` … `lanterna3` | lanternas da vila (ao longo da rua) |

`PONTOS_PADRAO` no `client/index.html` é a cópia fixa destes pontos, usada só se o mapa não carregar.

## 4. Estado interno da cena (`VilaScene`)

| Campo | Tipo | Derivado de | Regra |
|---|---|---|---|
| `ultimo` | estado da vila | último `estado` recebido em qualquer fato | fonte para `conferir`/`reconstruir` |
| `fase` | `"madrugada" \| "dia" \| "noite"` | `estado.fase` (aguardando/aberta/encerrada) | só muda por fato; nunca por relógio |
| `lotes[6]` | `{forjas: [sprite], marca: texto ×N, canteiro?}` | `concluidas`, `em_obra` | soma das forjas desenhadas = `concluidas` |
| `usados` | int | contagem de forjas + obras desenhadas | próximo lote = `usados % 6` |
| `obras` | fila FIFO `{lote, canteiro, barra, fundo, ferreiro, modo: "exata" \| "andamento"}` | `em_obra` | tamanho = `em_obra`; a mais antiga sai primeiro |
| `ferreiros[limite]` | `{sprite, espera, obra?, situacao: "livre" \| "indo" \| "martelando" \| "voltando" \| "parado"}` | `limite`, `ferreiros` | livres = `limite − ferreiros` (FR-009) |
| `carrinho` | sprite | — | parado na `mina`; anda só em `recurso.produzido` |
| `pilha` | lista de sprites de lingote + texto do número | `lingotes` | desenha `min(lingotes, 10)`; número ao lado se > 10 |
| `pergaminho` | `{sprite, texto, barra, fundo}` ou `null` | `encomenda` | existe ⇔ `encomenda != null` e fase aberta |
| `lanternas` | sprites + brilhos | `fase` | acesas na madrugada e na noite |
| `cenas` | mapa `chave → tween/timer` | — | no máximo uma cena por chave (sem fila, FR-016) |
| `falhas` | conjunto de chaves de arquivo | evento `loaderror` | não vazio ⇒ aviso "arte indisponível — modo simples" |

### Transições da luz

```text
madrugada --vila.iniciada (1,5 s)--> dia --vila.encerrada (2,5 s)--> noite
estado.sincronizado: aplica a luz da fase recebida na hora, sem transição
```

### Convergência

Depois de cada fato: `conferir(estado)` compara `lotes`/`obras`/`ferreiros`/`pilha`/`pergaminho`
com o estado; qualquer diferença ⇒ `reconstruir(estado)` (limpa e desenha tudo sem animação, como
no `estado.sincronizado`). A vila desenhada nunca muda o estado nem emite eventos (FR-003).
