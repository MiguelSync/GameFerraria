# Research: Identidade Visual da Vila Ferraria

Fase 0 do `/speckit-plan`. Nenhum "NEEDS CLARIFICATION" no Technical Context: a stack do cliente é
a da 001, o script de arte é Python + Pillow (já no `.venv`) e a única dúvida da spec (barra de
quem entra no meio) foi resolvida pelo Maestro (Q1 = A).

## R1 — Arte original desenhada por script

- **Decision**: `tools/gerar_arte.py` desenha cada peça/quadro a partir de **matrizes de
  caracteres** (uma letra por pixel) e de uma **paleta nomeada** no próprio código
  (`PALETA = {"a": (r, g, b, 255), ...}`; `"."` = transparente), com funções auxiliares para
  repetir/espelhar/sobrepor (ex.: o ferreiro andando = corpo + 4 posições de pernas). Grava PNG
  RGBA sem compressão variável (`optimize=False`) em `client/assets/`. **Sem aleatoriedade**
  (ou `random.Random(2026)` fixo para tufos de grama), para que rodar de novo gere bytes idênticos.
  Uso: `python tools/gerar_arte.py` (PNGs) e `python tools/gerar_arte.py --mapa` (PNGs + `vila.json`,
  sobrescrevendo edições feitas no Tiled — o script avisa). `--previa` grava também uma folha de
  contato ampliada 4× em `tools/previa.png` (ignorada no git) para revisar a arte.
- **Rationale**: FR-020 (refazer a arte a partir do repositório), constituição 1.0.1 (arte gerada
  por script versionado conta como uso livre); matrizes legíveis no código deixam claro que a arte
  é original e permitem revisão em diff.
- **Alternatives considered**: desenhar à mão num editor (não é reproduzível a partir do repo);
  pacote CC0 (Kenney etc.) — permitido, mas a spec pede identidade própria e o crédito ficaria
  mais complexo.

## R2 — Inventário e tamanhos

- **Decision**: três imagens, todas na grade de 16 px (detalhe em [contracts/assets.md](./contracts/assets.md)):
  - `tileset-ferraria.png` — 256 × 64, peças 16 × 16, 16 colunas × 4 linhas (64 peças), **mesma
    regra de numeração do kit** para caminho (8–23) e água (24–39), para continuar fácil de editar
    no Tiled.
  - `sprites16-ferraria.png` — 128 × 48, quadros 16 × 16 (8 × 3 = 24 quadros): ferreiro (parado,
    4 de andar, 2 de martelar), fumaça (3), faísca, lingote, carrinho (vazio/cheio), lanterna
    (apagada/acesa), carimbo, pedaços de pergaminho (3), minério, poste.
  - `sprites32-ferraria.png` — 128 × 96, quadros 32 × 32 (4 × 3 = 12 quadros): canteiro com
    andaime e bigorna, forja acesa (3 quadros de brasa), forja apagada, entrada da mina
    (fechada/aberta), quadro de avisos, pergaminho (pregado, amarelado, carimbado), estrado da pilha.
- **Rationale**: Phaser carrega uma spritesheet por tamanho de quadro; dois tamanhos (personagens
  e objetos pequenos × prédios) cobrem tudo sem desperdício; 16/32 respeitam a grade.
- **Alternatives considered**: um atlas JSON com tamanhos variados — exige gerar o JSON do atlas e
  complica o modo simples; uma spritesheet só de 32 × 32 — ferreiro e lingote ficariam com 75 %
  de quadro vazio.

## R3 — Paleta

- **Decision**: 31 cores nomeadas em [data-model.md](./data-model.md) §1: tons quentes (madeira,
  terra, pedra, brasa, couro, pergaminho), verdes de grama e um destaque frio (água, noite, aço do
  lingote). Contorno escuro quente (`#2b1d14`) em vez de preto puro.
- **Rationale**: Assumption da spec ("paleta própria de tons quentes … destaque frio para água e
  noite"); paleta fechada garante unidade visual e facilita a revisão.

## R4 — Mapa gerado e editável no Tiled

- **Decision**: com `--mapa`, o script grava `client/assets/vila.json` no formato Tiled 1.10:
  ortogonal, 24 × 12 peças de 16 px (384 × 192 px), **tileset embutido** `tileset-ferraria`
  (`image: "tileset-ferraria.png"`, firstgid 1), camadas de peças `chao` e `decoracao` (dados CSV
  como lista de inteiros) e camada de objetos `pontos` com pontos (`"point": true`) — contrato em
  [contracts/mapa.md](./contracts/mapa.md). O layout (onde ficam mina, trilho, pedreira, lagoa,
  rua, lotes, quadro, pilha, lanternas) é uma matriz de letras no script, convertida em gids.
  O canvas passa de 576 × 288 para **768 × 384** (mesmo zoom 2×).
- **Rationale**: o pedido mantém o mapa editável no Tiled (Anexo A do guia); 18 × 9 não comporta
  mina + trilho + pedreira + lagoa + quadro + pilha + 6 lotes com espaço para caminhar.
- **Alternatives considered**: manter 18 × 9 (apertado, elementos sobrepostos); desenhar o mapa
  em código Phaser (perde a edição no Tiled).

## R5 — Arte do kit: removida, não mantida como reserva

- **Decision**: na Etapa 2, `tileset-vila.png` e `sprites-vila.png` saem do repositório (ficam no
  histórico do git) e `LEIA-ME.txt` é reescrito para os assets novos. A reserva de cada elemento
  é **forma/emoji** desenhada pelo Phaser, não a arte do kit.
- **Rationale**: US1 #2 e SC-006 exigem 0 peças do kit no cenário; FR-019 define a reserva como
  "formas e emojis"; manter a arte do kit como reserva faria o kit reaparecer justamente quando
  a arte falha e duplicaria os créditos.
- **Alternatives considered**: manter os arquivos sem uso — confunde quem corrige e o README.

## R6 — Cenas sem fila e convergência para o último estado

- **Decision**: a cena guarda `this.ultimo` (o último `estado` recebido) e um registro
  `this.cenas[chave]` com o tween/timer em curso de cada elemento (`"carrinho"`, `"ferreiro0"`,
  `"pergaminho"`, `"balao"`, `"luz"`…). `iniciarCena(chave, criar)` primeiro **completa** a cena
  anterior da mesma chave (`tween.complete()` → elemento na posição final) e depois cria a nova.
  Depois de cada fato, `conferir(estado)` compara o que está desenhado (forjas acesas, canteiros,
  ferreiros livres/ocupados, lingotes na pilha, pergaminho) com o estado; se divergir (fatos
  perdidos, aba lenta), chama `reconstruir(estado)` — limpa e desenha tudo sem animação, como no
  `estado.sincronizado`.
- **Rationale**: FR-010, FR-016, SC-008 e os edge cases de rajada; uma chave por elemento deixa
  dois ferreiros caminharem ao mesmo tempo (disputa) sem fila.
- **Alternatives considered**: fila de cenas (proibida por FR-016); `tweens.killAll()` a cada fato
  (cortaria cenas de outros elementos sem necessidade).

## R7 — Ferreiros: 2 sprites, rota em "L" e obras em fila FIFO

- **Decision**: `limite` (2) ferreiros desenhados. Livres ficam em `espera1`/`espera2` (junto à
  entrada da mina). Em `forja.construcao_iniciada`, o primeiro ferreiro livre caminha pela rota
  `[espera → saida → (lote.x, saida.y) → lote]`, onde `saida` é o ponto da rua de terra em frente
  à mina e a rua é horizontal na altura de `saida.y` (o script garante isso no mapa); velocidade
  constante com duração total `min(3000 ms, distância / 90 px/s)`. Ao chegar, toca `martelar`.
  `this.obras` é FIFO (a mais antiga conclui primeiro, como no kit); `forja.construcao_concluida`
  pega `obras.shift()`, acende a forja naquele lote e devolve o ferreiro pela rota inversa até
  sua espera. Se a obra concluir com o ferreiro ainda caminhando, o tween de ida é completado e ele
  volta direto (edge case da spec). Lote da próxima obra = `usados++ % 6` (regra da 001); cada lote
  conta suas forjas e mostra "×N" quando N ≥ 2 (US2 #5); o canteiro aparece na frente da forja
  existente.
- **Rationale**: FR-009, US2 #1–#5; rota derivada de 3 pontos é simples e continua certa se os
  lotes forem movidos no Tiled ao longo da rua.
- **Alternatives considered**: pathfinding em grade (excessivo); polylines por lote no Tiled
  (6 rotas para manter a cada edição).

## R8 — Barras de progresso

- **Decision**: obra iniciada nesta aba: barra enche de 0 a 1 em `estado.tempo_obra * 1000` ms a
  partir do recebimento do fato (Assumption da spec), com `scaleX` limitado a 1. Obra vinda do
  `estado.sincronizado`: barra em modo **"em andamento"** (um segmento de 6 px indo e vindo, `yoyo`,
  `repeat: -1`), sem fração (Q1 = A). Em `vila.encerrada`, `tween.pause()` nas duas. Prazo da
  encomenda: barra cheia proporcional a `restante / prazo`, esvaziando em `restante * 1000` ms
  (FR-013).
- **Rationale**: FR-012, FR-013, US2 #2, US6 #4.

## R9 — Dia e noite dirigidos só pelos fatos

- **Decision**: um retângulo `luz` do tamanho do mapa por cima do cenário e dos personagens
  (abaixo da faixa, do balão e do aviso de modo simples) com cor/alfa por fase: madrugada
  (aguardando) `0x2a3a6a` α 0,35; dia (aberta) α 0; noite (encerrada) `0x0b1030` α 0,55. Lanternas
  com um círculo de brilho em `BlendModes.ADD` acima da luz. `estado.sincronizado` aplica a fase
  **sem** transição; `vila.iniciada` faz tween para dia em 1,5 s (lanternas apagam, porta da mina
  abre); `vila.encerrada` faz tween para noite em 2,5 s (lanternas acendem, forjas apagam, fumaça e
  faíscas param, carrinho para onde está, martelos param, barras pausam, pergaminho sai). Nenhum
  `Date`/relógio decide a fase. Na madrugada, as lanternas da vila e da mina estão acesas (a spec
  só fala em a lanterna da mina apagar no amanhecer; escolha de coerência visual).
- **Rationale**: FR-008, FR-015, US5, pedido do Maestro (só fatos).

## R10 — Modo simples por elemento

- **Decision**: `preload` registra `this.load.on("loaderror", f => this.falhas.add(f.key))`. Toda
  criação de elemento passa por `elemento(tipo, x, y)`, que usa a textura se
  `this.textures.exists(chave)` e a chave não falhou, senão desenha a **reserva** do tipo
  (tabela em [contracts/assets.md](./contracts/assets.md): ferreiro "🧑‍🏭", canteiro "🏗️", forja "🔥"/
  "🪨" apagada, carrinho "🛒", lingote "🧱", quadro retângulo marrom, pergaminho "📜", lanterna "🏮",
  mina "⛏️" etc.). Animações só são criadas para texturas presentes; a troca de quadro numa reserva
  vira troca de emoji/alfa. Se o mapa ou o tileset falhar, o chão vira formas (`Graphics`: fundo
  verde, rua de terra, lagoa azul) e os pontos vêm de `PONTOS_PADRAO`, cópia fixa dos pontos que o
  script gera. Com qualquer falha, um texto discreto "arte indisponível — modo simples" aparece no
  canto inferior da vila (sem evento e sem registro no Painel).
- **Rationale**: FR-019, US8, edge case "só uma imagem falhou".
- **Verificação**: renomear temporariamente uma ou todas as imagens em `client/assets/` e recarregar
  (roteiro V13/V14), sem código só de teste no cliente.

## R11 — Interface e fontes

- **Decision**: Google Fonts por `<link>`: **Pixelify Sans** (títulos, botões, estoque, textos da
  cena) e **VT323** (Painel de eventos e avisos, monoespaçada e legível para nomes de eventos), ambas
  SIL Open Font License 1.1, com reserva `system-ui, sans-serif` e `ui-monospace, monospace`. A cena
  Phaser só é criada depois de `document.fonts.load(...)` ou de 1 s (o que vier primeiro, para
  não ameaçar os 2 s do SC-004), para os
  textos do canvas usarem a fonte sem travar sem internet. Aparência: estoque e botões em "tábuas de
  madeira" (gradiente marrom, borda dupla), avisos e Painel em "pergaminho" (creme com borda
  queimada); as cores que distinguem pedido (azul), fato (verde) e recusa (vermelho) e as etiquetas
  ⬆ emit/⬇ on são mantidas. Layout em duas colunas a partir de 1100 px de largura (vila + estoque +
  botões + avisos à esquerda; Painel de eventos à direita, com rolagem própria); uma coluna abaixo
  disso. Nada da vila tem `position: absolute` sobre outros blocos; tudo que anima fica dentro do
  canvas.
- **Rationale**: FR-017, FR-018, US7, SC-007.
- **Alternatives considered**: "Press Start 2P" — ilegível em tamanhos pequenos (US7 #3).

## R12 — Assinaturas de `jogo.*`

- **Decision**: os métodos da cena mantêm os nomes da 001 e passam a receber o estado em todos os
  fatos: `mostrarEstado(estado)`, `vilaIniciada(estado)`, `obraIniciada(estado)`,
  `obraConcluida(estado)`, `recursoProduzido(estado, d)`, `recusado(motivo)`,
  `vilaEncerrada(estado)`, `encomendaPublicada(estado)`, `encomendaCumprida(estado)`,
  `encomendaExpirada(estado)`. No Vue, a ordem em cada `ouvir` continua `atualizar(d)` →
  `avisar(...)` → `jogo.*(...)`, para os números mudarem antes de qualquer cena (SC-003).
- **Rationale**: a cena precisa do estado para convergir (R6); é dado que já chega em `d.estado`.

## R13 — Aba em segundo plano

- **Decision**: em `this.game.events.on("visible")`, completar todas as cenas registradas e chamar
  `reconstruir(this.ultimo)`; os métodos chamados enquanto a aba estava escondida continuam
  atualizando `this.ultimo`.
- **Rationale**: edge case "ao voltar, a vila mostra o estado atual de imediato, sem reproduzir as
  cenas perdidas" (o Phaser pausa o laço quando a aba fica oculta).

## R14 — Verificação

- **Decision**: em toda etapa: (1) `python tests/cenarios.py` passa (SC-002, FR-002);
  (2) `git diff --exit-code 5bbf4f8 -- server.py tests/ docs/especificacao.md specs/001-vila-ferraria`
  vazio (FR-001); (3) a partir da Etapa 1, `python tools/gerar_arte.py --mapa` seguido de
  `git diff --exit-code client/assets/` vazio (arte reproduzível); (4) roteiro visual do
  [quickstart.md](./quickstart.md) com 2–3 abas em portais do Maestri a 1280 × 720, com screenshot
  de cada cena nomeado `V<n>-<cena>.png` anexado ao relatório da etapa (não commitado). SC-009
  ("pessoa que nunca viu") é verificado com um observador sem contexto (o usuário ou um agente novo)
  que recebe só os screenshots/GIFs das 10 cenas e diz o que aconteceu; meta ≥ 8/10.
- **Rationale**: a 002 não tem servidor novo para testar automaticamente; o que é automático é a
  não regressão e a reprodutibilidade, o resto é visual.
