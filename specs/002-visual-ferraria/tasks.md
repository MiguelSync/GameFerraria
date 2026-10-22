---

description: "Tarefas da identidade visual da Ferraria, agrupadas em 8 etapas (uma etapa = um commit)"
---

# Tasks: Identidade Visual da Vila Ferraria

**Input**: Design documents from `specs/002-visual-ferraria/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/README.md), [quickstart.md](./quickstart.md)

**Tests**: a 002 não tem comportamento de servidor novo. Em **toda** etapa: regressão automática
`python tests/cenarios.py` (suíte da 001, intocada), fronteira
`git diff --exit-code 5bbf4f8 -- server.py tests/ docs/especificacao.md specs/001-vila-ferraria`
e, a partir da Etapa 1, determinismo da arte (`python tools/gerar_arte.py --mapa` +
`git diff --exit-code client/assets/`). A parte visual é verificada pelo roteiro V1–V17 do
[quickstart.md](./quickstart.md) em portais do Maestri a 1280 × 720, com screenshots.

**Organization**: fases = etapas de commit (constituição, princípio VII). Rótulo `[USn]` liga a
tarefa à história da spec 002.

**Regras que valem para todas as tarefas** (cobrem FR-001–FR-004, FR-011, SC-002 e SC-003):

- **Não tocar** em `server.py`, `tests/`, `docs/especificacao.md`, `specs/001-vila-ferraria/` nem
  em `specs/002-visual-ferraria/spec.md`. Nenhum nome de evento, dado enviado, causa ou número muda.
- No bloco Vue de `client/index.html`, só mudam: frases de reação dos `ouvir`, argumentos de
  `jogo.*` (passar `d.estado`) e HTML/CSS da interface. `pedir`, `ouvir`, `registrar`, `resumir`,
  `atualizar`, contadores, botões por papel e rodapé continuam como estão; a ordem em cada `ouvir`
  continua `atualizar(d)` → `avisar(...)` → `jogo.*`; o comentário do porquê de cada `ouvir`
  continua presente.
- A cena **só reage**: nunca muda estado, nunca emite, nunca usa relógio (`Date`, `setInterval`)
  para decidir fase ou disparar reação; tweens/timers só animam.
- Todo elemento da vila é criado pela fábrica `elemento(tipo, ...)` (reserva do modo simples já
  embutida) — índices e reservas exatamente como em [contracts/assets.md](./contracts/assets.md).
- Commits pelo Maestro ("Claude Code #3"), um por etapa, com a mensagem indicada; nunca `git push`
  sem autorização. Antes do commit: `revisor-eventos` + regressão + roteiro visual da etapa.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem depender de tarefa incompleta)
- **[Story]**: história da spec 002 (US1…US8)

---

## Etapa 1 — Script de arte e assets gerados (Setup)

**Arquivos**: `tools/gerar_arte.py`, `tools/requirements.txt`, `.gitignore`,
`client/assets/tileset-ferraria.png`, `client/assets/sprites16-ferraria.png`,
`client/assets/sprites32-ferraria.png` · **Fatos cobertos**: nenhum (a cena ainda usa a arte do kit)

**Pronto quando**: `python tools/gerar_arte.py --previa` roda sem erro; os PNGs têm exatamente
256 × 64, 128 × 48 e 128 × 96; rodar de novo não muda nenhum byte; a prévia (📸 `tools/previa.png`)
mostra cada peça/quadro do contrato reconhecível e nenhuma peça lembra a arte do kit; regressão e
fronteira passam.

**Commit**: `feat: script de arte original da Ferraria e assets gerados`

- [ ] T001 [P] Criar `tools/requirements.txt` com `Pillow>=10` (dependência só de desenvolvimento; não mexer no `requirements.txt` da aplicação)
- [ ] T002 [P] Acrescentar `tools/previa.png` ao `.gitignore`
- [ ] T003 Criar o esqueleto de `tools/gerar_arte.py` (research R1): docstring com uso (`--mapa`, `--previa`), determinismo, autoria/licença da arte e a nota de que o script foi escrito com ajuda de IA; `PALETA` com as 31 cores de `data-model.md` §1 (letra → RGBA, `.` transparente); `desenhar(matriz)` que converte uma lista de strings em `Image` RGBA validando largura/altura exatas (16 ou 32) e letras existentes na paleta; `espelhar`, `sobrepor` e `folha(quadros, colunas, tamanho)`; `salvar(img, caminho)` com `optimize=False`; `random.Random(2026)` como única fonte de variação; `main` com `argparse` que grava os PNGs em `client/assets/` e confere os tamanhos finais
- [ ] T004 Em `tools/gerar_arte.py`, desenhar as 64 peças de `tileset-ferraria.png` conforme `contracts/assets.md`: chão 0–7; caminho de terra 8–23 e água 24–39 gerados por função a partir de uma peça base + bordas por lado (regra 8/24 + Norte 1, Leste 2, Sul 4, Oeste 8); trilho 40–45; decoração 46–55; pedreira/paredão 56–63
- [ ] T005 Em `tools/gerar_arte.py`, desenhar os quadros 0–20 de `sprites16-ferraria.png` (ferreiro parado, 4 de andar, 2 de martelar a partir de um corpo base com variações de pernas/braço; faísca; fumaça ×3; lingote; carrinho vazio/cheio; lanterna apagada/acesa; carimbo; pedaços ×3; minério) e deixar 21–23 transparentes
- [ ] T006 Em `tools/gerar_arte.py`, desenhar os quadros 0–11 de `sprites32-ferraria.png` (canteiro com andaime e bigorna; forja acesa ×3 variando a brasa; forja apagada; mina fechada/aberta; quadro de avisos; pergaminho pregado/amarelado/carimbado; estrado da pilha)
- [ ] T007 Em `tools/gerar_arte.py`, `--previa`: folha de contato ampliada 4× com grade e o número de cada peça/quadro, gravada em `tools/previa.png`
- [ ] T008 Validar: rodar `python tools/gerar_arte.py --previa`, guardar `shasum client/assets/*-ferraria.png`, rodar de novo e conferir que os hashes não mudaram (os PNGs ainda não estão no git, então `git diff` não serve antes do commit); conferir a prévia contra `contracts/assets.md` (📸); quickstart §2 (regressão e fronteira)

**Checkpoint**: arte original existe e é reproduzível; nada visível mudou ainda.

---

## Etapa 2 — Mapa novo, arte nova na cena e arte do kit removida (US1)

**Arquivos**: `tools/gerar_arte.py`, `client/assets/vila.json`, `client/assets/LEIA-ME.txt`,
`client/index.html` (cena), remoção de `client/assets/tileset-vila.png` e
`client/assets/sprites-vila.png` · **Fatos cobertos**: `estado.sincronizado` (cenário estático) e
as reações da 001 continuando a funcionar com os sprites novos

**Pronto quando**: roteiro V1 (sem ferreiros e sem luz ainda) e V2; o mapa abre no Tiled sem erro
(ou, sem Tiled, o JSON passa nas checagens do script); `--mapa` é determinístico; nenhuma
referência a `tileset-vila`, `sprites-vila`, `acampamento` ou ao spritesheet `"sprites"` do kit em
`client/`; regressão e fronteira passam. Cobre **US1 #1–#3**, FR-006, FR-007, FR-021.

**Commit**: `feat: mapa da Ferraria gerado por script e arte do kit removida`

- [ ] T009 [US1] Em `tools/gerar_arte.py`, `--mapa`: layout 24 × 12 como matriz de letras (esboço e regras de `contracts/mapa.md`), conversão para gids de `chao` (todas as células) e `decoracao` (0 = vazio) com caminho e água autoajustados pelos vizinhos; os 17 pontos com coordenadas em pixels; gravar `client/assets/vila.json` com exatamente os campos do contrato (tileset embutido `tileset-ferraria`, camadas `chao`/`decoracao`/`pontos`, objetos `"point": true`), `json.dump(..., indent=1)` estável; `assert`s das regras de layout (rua horizontal em `saida.y`, 32 × 32 livres em volta de cada lote, rota espera→lote ≤ 270 px, trilho sem cruzar a rua); aviso no terminal de que `--mapa` sobrescreve edições do Tiled
- [ ] T010 [US1] Rodar `python tools/gerar_arte.py --mapa`, conferir que `vila.json` é JSON válido com 17 pontos e abrir no Tiled (se disponível) para confirmar que é editável
- [ ] T011 [US1] Remover `client/assets/tileset-vila.png` e `client/assets/sprites-vila.png` (`git rm`) e reescrever `client/assets/LEIA-ME.txt`: arquivos, resumo de peças/quadros (remetendo a `tools/gerar_arte.py` e ao contrato), camadas e pontos do mapa, como gerar de novo, autoria e licença (research R5)
- [ ] T012 [US1] Em `client/index.html` (cena): `preload` com as chaves `tiles` (`assets/tileset-ferraria.png`), `sprites16` (16 × 16), `sprites32` (32 × 32) e `mapa`, mais `this.load.on("loaderror", f => this.falhas.add(f.key))`; jogo com 768 × 384; `create` monta o tilemap com `addTilesetImage("tileset-ferraria", "tiles")` e lê os pontos por nome num objeto `this.p`, completando os que faltarem com `PONTOS_PADRAO` (constante com os 17 pontos gerados)
- [ ] T013 [US1] Em `client/index.html` (cena): fábrica `elemento(tipo, x, y)` com a tabela de tipos → `{chave, quadro, reserva}` de `contracts/assets.md`, usando a textura se `textures.exists(chave) && !falhas.has(chave)` e a reserva (emoji/forma) senão, com `definirQuadro(q)` que funciona nos dois casos; cenário fixo: entrada da mina (fechada), carrinho parado, quadro vazio, estrado da pilha e lanternas nos seus pontos
- [ ] T014 [US1] Em `client/index.html` (cena): portar as reações atuais para a arte nova via `elemento()` — canteiro (`sprites32` 0) com barra, forja acesa (`sprites32` 1) no lugar da casa do kit, textos flutuantes saindo do ponto `mina`, pergaminho atual mantido — e apagar `criarCasa`/qualquer uso do spritesheet `"sprites"` do kit
- [ ] T015 [US1] Validar: V1 e V2 do `quickstart.md` (📸), `grep -rn "tileset-vila\|sprites-vila\|acampamento\|\"sprites\"" client/` vazio, determinismo por `shasum` de `client/assets/vila.json` e dos PNGs antes/depois de um novo `--mapa`, regressão e fronteira

**Checkpoint**: a vila já é de ferreiros, com arte 100 % original.

---

## Etapa 3 — Personagens e reações a obra, produção e recusa (US2, US3, US4)

**Arquivos**: `client/index.html` · **Fatos cobertos**: `forja.construcao_iniciada`,
`forja.construcao_concluida`, `recurso.produzido`, `operacao.recusada`

**Pronto quando**: roteiro V3–V8 e V17 (📸) — ferreiro caminha ≤ 3 s e martela, barra de 12 s
sem passar do fim, canteiro mais antigo vira forja acesa com brasa e fumaça, ferreiro volta, "×2"
no 7º canteiro, carrinho termina antes do ciclo seguinte, faísca e pilha, recusa só na aba que
pediu sem mexer em nada desenhado, rajada converge em ≤ 3 s; frases de reação novas no Painel;
regressão e fronteira passam. Cobre **US2 #1–#5, US3 #1–#3, US4 #1–#2**, FR-009–FR-012, FR-014,
FR-016, SC-008.

**Commit**: `feat: ferreiros, forjas e carrinho reagem aos fatos de obra, produção e recusa`

- [ ] T016 [US2] Em `client/index.html` (cena): infraestrutura de research R6 — `this.ultimo`, `this.cenas` + `iniciarCena(chave, criar)` que completa a cena anterior da mesma chave antes de criar a nova, `conferir(estado)` (forjas desenhadas = `concluidas`, canteiros = `em_obra`, ferreiros livres = `limite − ferreiros`, lingotes na pilha = `min(lingotes, 10)`) e `reconstruir(estado)` que limpa e desenha sem animação forjas por lote, canteiros com ferreiro e barra em modo "em andamento", ferreiros livres nas esperas e a pilha; `mostrarEstado` passa a chamar `reconstruir` (FR-010, FR-016)
- [ ] T017 [US2] Em `client/index.html` (cena): criar as animações `andar`, `martelar`, `fumaca` (de `sprites16`) e `brasa` (de `sprites32`) só quando a textura carregou (`contracts/assets.md`)
- [ ] T018 [US2] Em `client/index.html` (cena): `limite` ferreiros nas esperas `espera1`/`espera2`; `rota(espera, lote)` = `[espera, saida, (lote.x, saida.y), lote]`; `caminhar(ferreiro, pontos, aoChegar)` com `andar`, `flipX` pela direção e duração total `min(3000, distância / 90 px/s)` (research R7)
- [ ] T019 [US2] Em `client/index.html` (cena), `obraIniciada(estado)`: lote `usados++ % 6`, canteiro (na frente da forja se o lote já tiver uma), barra "exata" enchendo em `estado.tempo_obra` s a partir de agora (limitada a 1), primeiro ferreiro livre caminha até o lote e `martelar` ao chegar, "−40 🪨" sobe da `mina`, obra entra no fim da fila `obras`; `conferir`
- [ ] T020 [US2] Em `client/index.html` (cena), `obraConcluida(estado)`: `obras.shift()`; canteiro some com poeira e a forja acesa aparece (escala 0,3 → 1, 400 ms) com `brasa` e fumaça em laço (chave por forja); barra some; "🔥 Forja pronta!"; o ferreiro completa a caminhada em curso (se houver) e volta pela rota inversa até a espera; marca "×N" quando o lote reúne ≥ 2 forjas; `conferir`
- [ ] T021 [US3] Em `client/index.html` (cena), `recursoProduzido(estado, d)`: cena `carrinho` (cheio até `trilho_fim` em 1,2 s, volta vazio em 1,2 s), "+10 🪨" da mina; se `d.ganho_lingotes > 0`, faísca em cada forja acesa e "+N lingotes" na pilha; pilha redesenhada com `min(lingotes, 10)` lingotes e o número ao lado se > 10; `conferir`
- [ ] T022 [US4] Em `client/index.html` (cena), `recusado(motivo)`: `cameras.main.shake(300, 0.006)`, cena `balao` com retângulo arredondado creme, borda queimada e "✋ " + motivo exato por 3,5 s, acima da luz; não mexe em nenhum outro elemento e não chama `conferir` (FR-014)
- [ ] T023 [US2] Em `client/index.html` (Vue, SC-003: números antes da cena): trocar as frases de reação de `forja.construcao_iniciada`, `forja.construcao_concluida`, `recurso.produzido` e `operacao.recusada` pelas de `contracts/cenas.md` §3–§6 (FR-005), mantendo comentários, avisos e a ordem `atualizar` → `avisar` → `jogo.*`
- [ ] T024 [US2] Validar V3–V8 e V17 (📸, 3 portais), regressão e fronteira

**Checkpoint**: o par obra → forja e a passagem do tempo contam a história sozinhos.

---

## Etapa 4 — Dia e noite pelos fatos e sincronização completa (US5)

**Arquivos**: `client/index.html` · **Fatos cobertos**: `estado.sincronizado`, `vila.iniciada`,
`vila.encerrada`

**Pronto quando**: roteiro V9, V10 (sem o pergaminho detalhado), V11 (sem o pergaminho) e V16
(📸); a fase só muda com fato (nenhum `Date`/`setInterval` na cena decide fase); reconexão não
duplica nada; regressão e fronteira passam. Cobre **US5 #1–#4**, FR-008, FR-012, FR-015.

**Commit**: `feat: dia e noite pelos fatos e vila sincronizada para quem entra no meio`

- [ ] T025 [US5] Em `client/index.html` (cena): camada `luz` (retângulo do tamanho do mapa) com madrugada/dia/noite de research R9, brilhos das lanternas em `BlendModes.ADD` acima da luz, ordem de profundidade (cenário < personagens < luz < brilhos < faixa < balão/aviso) e `aplicarFase(fase, duracaoMs)` (0 = sem transição)
- [ ] T026 [US5] Em `client/index.html` (cena), completar `reconstruir(estado)` (FR-015, SC-004: pronto em ≤ 2 s para quem entra no meio): luz da fase sem transição, lanternas e porta da mina coerentes, forjas acesas (brasa + fumaça) se aberta ou apagadas (quadro 4) se encerrada, ferreiros das obras martelando se aberta ou parados se encerrada, barra "em andamento" animada ou parada, faixa da temporada; idempotente (chamar duas vezes não duplica — reconexão)
- [ ] T027 [US5] Em `client/index.html` (cena), `vilaIniciada(estado)`: cena `luz` madrugada → dia em 1,5 s, faixa "☀️ Temporada aberta", lanternas apagam, mina abre (quadro 6); `conferir`
- [ ] T028 [US5] Em `client/index.html` (cena), `vilaEncerrada(estado)`: cena `luz` dia → noite em 2,5 s, faixa "🌙 Temporada encerrada", `brasa` para e forjas trocam para o quadro 4, fumaça e faíscas param, lanternas acendem, cena `carrinho` pausada onde está, `martelar` para (quadro 0), barras pausam, ferreiros caminhando completam e param; `conferir`
- [ ] T029 [US5] Em `client/index.html` (cena): `this.game.events.on("visible", ...)` completa todas as cenas e chama `reconstruir(this.ultimo)` (research R13)
- [ ] T030 [US5] Em `client/index.html` (Vue): frases de `estado.sincronizado`, `vila.iniciada` e `vila.encerrada` de `contracts/cenas.md` §1, §2 e §10; passar `d.estado` em `jogo.vilaIniciada` e `jogo.vilaEncerrada`
- [ ] T031 [US5] Validar V9, V10, V11 e V16 (📸), `grep -n "Date\|setInterval" client/index.html` só no bloco Vue já existente (horário do Painel), regressão e fronteira

**Checkpoint**: da abertura ao encerramento, e para quem entra no meio, a vila bate com o estado.

---

## Etapa 5 — Quadro de encomendas (US6)

**Arquivos**: `client/index.html` · **Fatos cobertos**: `encomenda.publicada`,
`encomenda.cumprida`, `encomenda.expirada` (e a retirada do pergaminho em `vila.encerrada` e no
`estado.sincronizado`)

**Pronto quando**: roteiro V10 e V11 completos (com pergaminho) e V12 (📸); barra do prazo nunca
negativa nem recomeça; regressão e fronteira passam. Cobre **US6 #1–#4, US5 #2/#3**, FR-013.

**Commit**: `feat: quadro de encomendas com pergaminho, carimbo e prazo`

- [ ] T032 [US6] Em `client/index.html` (cena): elemento pergaminho no ponto `quadro` (`sprites32` 8) com texto "N lingotes · +R 🪨" (de `estado.encomenda`) e barra de prazo em `restante/prazo` esvaziando em `restante` s (FR-013); substitui o pergaminho simples da 001
- [ ] T033 [US6] Em `client/index.html` (cena), `encomendaPublicada(estado)`: cena `pergaminho` — desce e "prega" (escala 1,3 → 1, 600 ms); `conferir`
- [ ] T034 [US6] Em `client/index.html` (cena), `encomendaCumprida(estado)`: 3 lingotes em arco da pilha ao quadro (800 ms), pilha passa a `estado.lingotes`, carimbo cai e o pergaminho troca para o quadro 10, sobe e some (600 ms), "+40 🪨" no quadro; `conferir`
- [ ] T035 [US6] Em `client/index.html` (cena), `encomendaExpirada(estado)`: quadro 9 por 500 ms, some soltando os pedaços 17–19 que caem girando, "⌛ prazo vencido", pilha intacta; `conferir`
- [ ] T036 [US6] Em `client/index.html` (cena): `reconstruir` desenha o pergaminho com a barra no `restante` se `encomenda` e fase aberta; `vilaEncerrada` retira o pergaminho sem cena de expiração; `conferir` inclui "pergaminho existe ⇔ encomenda ativa e fase aberta"
- [ ] T037 [US6] Em `client/index.html` (Vue): frases de `encomenda.publicada`, `encomenda.cumprida` e `encomenda.expirada` de `contracts/cenas.md` §7–§9; passar `d.estado` em `jogo.encomendaExpirada`
- [ ] T038 [US6] Validar V10, V11 e V12 (📸), regressão e fronteira

**Checkpoint**: os 10 fatos têm a sua cena (SC-001 conferível).

---

## Etapa 6 — Interface de vila e fonte pixel (US7)

**Arquivos**: `client/index.html` (HTML/CSS; textos da cena) · **Fatos cobertos**: todos (só
aparência)

**Pronto quando**: roteiro V15 a 1280 × 720 (📸) — vila, estoque, botões, avisos, Painel (com
contadores, ⬆ emit/⬇ on e cores de pedido/fato/recusa) e rodapé visíveis, legíveis e sem
sobreposição durante as cenas; sem internet para as fontes, tudo continua legível com a fonte de
sistema; regressão e fronteira passam. Cobre **US7 #1–#3**, FR-004, FR-017, FR-018, SC-007.

**Commit**: `feat: interface de vila com fonte pixel e painéis de madeira`

- [ ] T039 [US7] Em `client/index.html`: `<link rel="preconnect">` e `<link>` do Google Fonts para Pixelify Sans (400/600) e VT323 com `display=swap`; variáveis CSS de fonte com reserva `system-ui, sans-serif` e `ui-monospace, monospace` (research R11)
- [ ] T040 [US7] Em `client/index.html` (CSS): estoque e botões em "tábuas de madeira", avisos e Painel de eventos em "pergaminho"; manter as cores e etiquetas que distinguem pedido/fato/recusa e ⬆ emit/⬇ on, os contadores no topo do Painel e o rodapé; VT323 ≥ 16 px no Painel; contraste legível
- [ ] T041 [US7] Em `client/index.html` (CSS/HTML): layout em duas colunas a partir de 1100 px (vila, estoque, botões e avisos à esquerda; Painel de eventos à direita com rolagem própria), uma coluna abaixo disso; canvas da vila responsivo dentro da coluna; meta a 1280 × 720: título, vila, estoque e botões sem rolar a página, avisos limitados aos 3 mais novos visíveis, Painel rolando por dentro e rodapé ao fim da página; nada posicionado por cima de outros blocos (FR-018, SC-007)
- [ ] T042 [US7] Em `client/index.html`: criar o jogo Phaser só depois de `document.fonts.load('8px "Pixelify Sans"')` ou 1 s (o que vier primeiro; preserva os 2 s do SC-004); textos da cena (faixa, flutuantes, balão, pergaminho, "×N") com a fonte pixel e reserva de sistema
- [ ] T043 [US7] Validar V15 (📸) e repetir V3/V6/V12 olhando sobreposição; testar com o Google Fonts bloqueado (fonte de sistema); regressão e fronteira

---

## Etapa 7 — Modo simples quando a arte não carrega (US8)

**Arquivos**: `client/index.html` (cena) · **Fatos cobertos**: os 10, em modo simples

**Pronto quando**: roteiro V13 (só um PNG ausente → só os elementos dele em reserva) e V14 (toda a
arte ausente → chão de formas, emojis, os 3 cenários de `docs/especificacao.md` e uma encomenda
com reação visível em cada um dos 10 fatos e números certos) (📸); aviso "arte indisponível —
modo simples" na vila, sem evento nem registro no Painel; arquivos devolvidos e `git status`
limpo; regressão e fronteira passam. Cobre **US8 #1–#2**, FR-019, SC-005.

**Commit**: `feat: modo simples quando a arte não carrega`

- [ ] T044 [US8] Em `client/index.html` (cena): se `this.falhas` não estiver vazio, mostrar o texto discreto "arte indisponível — modo simples" no canto inferior da vila (acima da luz), sem `pedir`, sem `registrar` e sem aviso no Vue
- [ ] T045 [US8] Em `client/index.html` (cena): se `mapa` ou `tiles` falhou, desenhar o chão com `Graphics` (fundo verde, rua de terra na altura de `saida.y`, lagoa azul, cascalho da pedreira) e usar `PONTOS_PADRAO` inteiro
- [ ] T046 [US8] Em `client/index.html` (cena): revisar cada tipo de `elemento()` e cada cena das Etapas 3–5 para a reserva de `contracts/assets.md` — trocas de quadro viram troca de emoji/alfa, `martelar` vira "🔨" piscando, `brasa` vira "🔥" pulsando, fumaça vira círculo cinza; nenhuma chamada `anims.play`/`setFrame` em elemento de reserva
- [ ] T047 [US8] Validar V13 e V14 (📸, 3 portais), devolver os arquivos movidos, `git status` limpo, regressão e fronteira

**Checkpoint**: o visual nunca derruba o fluxo de eventos.

---

## Etapa 8 — README e auditoria final (polish)

**Arquivos**: `README.md` (e correções pontuais que a auditoria apontar) · **Fatos cobertos**:
nenhum

**Pronto quando**: README com extras, créditos de cada item de arte e fonte, como gerar a arte e
uso de IA atualizado; auditoria sem pendência; quickstart completo (V1–V17, SC-001 10/10, SC-009
≥ 8/10); regressão e fronteira passam. Cobre FR-020, FR-022, SC-001, SC-006, SC-009.

**Commit**: `docs: README com a identidade visual, créditos e geração da arte`

- [ ] T048 Em `README.md`, **Extras**: acrescentar a identidade visual em pixel art original (002) como extra feito depois de tudo o que é obrigatório (FR-022) e trocar o item "Mapa personalizado a partir do mapa do kit" por "mapa da Ferraria gerado por script e editável no Tiled"
- [ ] T049 Em `README.md`, **Créditos**: arte original (tileset, sprites, mapa) de Miguel Antonio Selhorst, gerada por `tools/gerar_arte.py`, com a licença livre escolhida pelo autor (sugestão: CC BY 4.0 — confirmar com o usuário); fontes Pixelify Sans e VT323 (autor conforme a página do Google Fonts, SIL Open Font License 1.1); emojis do sistema nos textos e no modo simples; a arte do kit deixou de ser usada (removida na Etapa 2); nenhuma arte, nome ou asset de jogo comercial (FR-020, FR-021, SC-006)
- [ ] T050 Em `README.md`, nova seção **Como gerar a arte**: `pip install -r tools/requirements.txt`, `python tools/gerar_arte.py` / `--mapa` (sobrescreve edições do Tiled) / `--previa`, determinismo, e que o mapa pode ser editado no Tiled
- [ ] T051 Em `README.md`, **Uso de IA**: a feature 002 (spec, plano, tarefas e análise no Spec Kit em `specs/002-visual-ferraria/`), o script de arte e a nova cena escritos com ajuda do Claude Code, e o que o autor revisou/mudou (matrizes, paleta, cenas)
- [ ] T052 Em `README.md`, **Como testar com duas abas**: atualizar só as descrições visuais (ferreiro caminha e martela, forja acesa, carrinho, pilha, pergaminho no quadro, amanhecer/anoitecer, modo simples), sem mudar nenhuma regra, número ou evento
- [ ] T053 Auditoria de `client/index.html`: `git diff 5bbf4f8 -- client/index.html` só muda cena, CSS/HTML, frases de reação e argumentos de `jogo.*`; os 10 `ouvir` e os 5 `pedir` com os mesmos nomes (comparar com `docs/especificacao.md`); comentário do porquê em cada um; frases = `contracts/cenas.md`; nenhum relógio decide fase; rodar o agente `revisor-eventos`
- [ ] T054 Fechamento: quickstart §1 e §2, roteiro V1–V17 completo (📸), SC-001 (10/10 na tabela de `contracts/cenas.md`) e SC-009 (observador sem contexto, ≥ 8/10)

---

## Dependencies & Execution Order

- Ordem **sequencial** 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8, um commit por etapa.
- Etapa 2 depende da 1 (assets). Etapas 3–5 dependem da 2 (mapa, pontos, fábrica `elemento`).
  Etapa 4 completa o `reconstruir` criado na 3. Etapa 5 depende da 4 (pergaminho some no
  anoitecer e no sync). Etapa 6 pode ir antes da 3 se for mais cômodo (só CSS/HTML), mas a ordem
  sugerida mantém a vila pronta antes da moldura. Etapa 7 depende de 3–5 (revisa a reserva de
  todas as cenas). Etapa 8 depende de todas.

### Histórias × etapas

| História | Etapas |
|---|---|
| US1 (cenário) | 2 (e 3/4 completam ferreiros e luz no V1) |
| US2 (obra viva) | 3 |
| US3 (mina e lingotes) | 3 |
| US4 (recusa só para quem pediu) | 3 |
| US5 (dia, noite e entrada no meio) | 4, 5 (pergaminho) |
| US6 (quadro de encomendas) | 5 |
| US7 (interface) | 6 |
| US8 (modo simples) | 2 (fábrica com reserva), 7 |

### Parallel Opportunities

Quase tudo é `client/index.html` (sequencial). Paralelos reais: T001 ∥ T002 (arquivos
diferentes) e, na Etapa 1, T003–T007 (`tools/gerar_arte.py`) ∥ nada que dependa deles. A Etapa 6
(CSS/HTML) pode ser feita por outra pessoa em paralelo às Etapas 3–5 se o arquivo for combinado
com cuidado — não recomendado num trabalho individual.

## Implementation Strategy

1. **MVP visual**: Etapas 1–3 — arte original, mapa novo e os fatos centrais (obra, produção,
   recusa). Parar e validar com V1–V8.
2. Etapas 4–5 completam os 10 fatos (SC-001).
3. Etapa 6 dá a moldura de vila; Etapa 7 garante que o visual nunca derruba o fluxo.
4. Etapa 8 documenta. Push só com autorização do usuário.

## Notes

- Qualquer vontade de mudar regra, número, evento ou dado enviado durante a 002 está **fora da
  fronteira**: volta para a spec (spec-writer) como feature nova.
- Rodar `--mapa` descarta edições feitas à mão no Tiled; se o mapa for editado no Tiled depois da
  Etapa 2, passar a rodar o script só sem `--mapa` (e a checagem de determinismo vira só dos PNGs).
