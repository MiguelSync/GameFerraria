# Feature Specification: Identidade Visual da Vila Ferraria

**Feature Branch**: `002-visual-ferraria` (sem branch git; diretório da feature apenas)

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Dar à Vila Ferraria uma identidade visual própria em pixel art
ORIGINAL, criada para o projeto, com clima de vila aconchegante de jogo de fazenda mas sem arte de
jogo comercial, e fazer a vila desenhada reagir a cada fato de forma viva: cenário redesenhado como
vila de ferreiros (mina com trilho e carrinho, pedreira, caminho de terra batida, rio/lagoa, quadro
de avisos), mantendo os 6 lotes e o ponto de onde sai a produção; personagens e objetos novos
(ferreiro, canteiro com andaime e bigorna, forja de pedra com chaminé e brasa, carrinho de minério,
pilha de lingotes, quadro de encomendas com pergaminho); uma reação visual para cada um dos 10
fatos que a aba escuta; interface com cara de jogo de vila (tipografia pixel, painéis de
madeira/pergaminho), legível e sem esconder o Painel de eventos. Esta feature é só de apresentação:
nenhuma regra, número, evento, dado enviado ou causa da 001 muda."

## Visão geral

Hoje a vila desenhada usa a arte genérica do kit (casa, canteiro, pedras). Esta feature troca a
apresentação por uma **vila de ferreiros com arte própria**: a mina com o carrinho de minério, os
ferreiros andando e martelando, as forjas de pedra acesas, a pilha de lingotes e o quadro de
encomendas. Cada fato que a aba recebe passa a ter uma cena curta e reconhecível, de modo que quem
olha só para a vila entende o que aconteceu, enquanto o Painel de eventos continua mostrando os
eventos em si.

**Fronteira desta feature (não negociável):** ela é só de apresentação. Tudo o que está em
`specs/001-vila-ferraria/spec.md` e em `docs/especificacao.md` continua valendo sem mudança: os 15
nomes de eventos, quem emite e quem recebe, os números (120 / 40 / 12 s / 2 ferreiros / 5 s /
+10 minérios / +1 lingote por forja / encomenda 3 lingotes, 30 s, +40 minérios), a ordem das
verificações, os motivos de recusa, os dados enviados e a causa de cada fato. A vila desenhada só
**reage** aos fatos recebidos; ela nunca decide nada, nunca muda o estado e nunca emite eventos.

### Reação visual por fato (os 10 fatos que a aba escuta)

| Fato | Reação na vila desenhada | Duração da cena |
|---|---|---|
| `estado.sincronizado` | A vila aparece exatamente como está: luz da fase (madrugada, dia ou noite), uma forja acesa por forja concluída, um canteiro com ferreiro por obra em andamento, ferreiros livres na entrada da mina, pilha com os lingotes atuais e, se houver encomenda ativa, o pergaminho no quadro com o prazo restante | sem animação de entrada (≤ 1 s para aparecer); a barra das obras já em andamento fica em modo "em andamento", sem fração exata |
| `vila.iniciada` | Amanhecer: a luz passa de madrugada para dia, a faixa da temporada vira "aberta", a lanterna da mina apaga e a mina "acorda" (porta aberta, trilho livre) | ≤ 2 s |
| `forja.construcao_iniciada` | Um ferreiro livre sai da entrada da mina, caminha pelo caminho de terra até o próximo lote livre, o lote vira canteiro com andaime e bigorna e o ferreiro começa a martelar; acima do canteiro, uma barra de progresso do tempo da obra começa a encher; "−40 🪨" sobe do estoque | caminhada ≤ 3 s; barra enche ao longo dos 12 s da obra |
| `forja.construcao_concluida` | O canteiro mais antigo vira forja de pedra acesa, com brasa e fumaça saindo da chaminé; a barra some; o ferreiro daquele canteiro volta caminhando até a entrada da mina | ≤ 3 s; fumaça e brasa continuam enquanto a temporada estiver aberta |
| `recurso.produzido` | O carrinho sai da entrada da mina pelo trilho carregado de minério, com "+10 🪨" subindo; se o ciclo rendeu lingotes, cada forja acesa solta uma faísca e "+N lingotes" aparece, e a pilha de lingotes cresce até a quantidade atual | ≤ 3 s (termina antes do ciclo seguinte) |
| `operacao.recusada` | Só na aba de quem pediu: a vila treme e um balão em pergaminho mostra o motivo exato recebido | ≤ 1,5 s de tremida; balão visível por ≥ 3 s |
| `encomenda.publicada` | Um pergaminho é pregado no quadro de avisos da vila, mostrando "3 lingotes · +40 🪨" e uma barra de prazo que esvazia ao longo dos 30 s | pregar ≤ 1,5 s; barra esvazia em 30 s |
| `encomenda.cumprida` | Três lingotes saem da pilha até o quadro, o pergaminho recebe um carimbo de "entregue" e é recolhido; "+40 🪨" aparece no quadro | ≤ 3 s |
| `encomenda.expirada` | O pergaminho amarela, rasga e se desfaz em pedaços que caem do quadro; nada sai da pilha | ≤ 2 s |
| `vila.encerrada` | Anoitecer: a luz passa para noite, as brasas das forjas apagam e a fumaça para, as lanternas da vila e da mina acendem, o carrinho para no trilho, ferreiros em obra param de martelar e ficam parados no canteiro, barras de progresso param onde estavam, o pergaminho da encomenda (se houver) é retirado do quadro | ≤ 3 s |

Os pedidos que a aba emite (`*_solicitada`/`*_solicitado`) não têm cena própria na vila: quem
mostra o pedido é o Painel de eventos; a vila só se mexe quando o fato chega.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - O cenário de uma vila de ferreiros (Priority: P1)

Quem abre a vila vê, em vez da arte genérica do kit, uma vila de ferreiros desenhada para o
projeto: a entrada da mina com trilho e carrinho de minério, a pedreira, um caminho de terra batida
ligando os 6 lotes, um rio ou lagoa, o quadro de avisos da vila, os ferreiros esperando na entrada
da mina e a pilha de lingotes perto das forjas.

**Why this priority**: é a base de todas as outras histórias; sem o cenário e os personagens não
há onde as reações acontecerem.

**Independent Test**: abrir uma aba antes de o Mestre abrir a temporada e conferir, só olhando a
vila, que todos os elementos do cenário estão presentes e que nenhuma peça da arte antiga do kit
aparece.

**Acceptance Scenarios**:

1. **Given** a vila recém-iniciada (fase aguardando), **When** uma pessoa entra, **Then** a vila
   desenhada mostra a entrada da mina com trilho e carrinho, a pedreira, o caminho de terra batida
   ligando os 6 lotes vazios, o rio ou lagoa, o quadro de avisos vazio, 2 ferreiros livres na
   entrada da mina, a pilha de lingotes vazia e a luz de madrugada.
2. **Given** a vila desenhada, **When** se compara com a arte do kit original, **Then** nenhuma peça
   do cenário, personagem ou objeto é a arte do kit nem de jogo comercial.
3. **Given** a vila desenhada, **When** se conta os lotes, **Then** há exatamente 6 lotes nos
   mesmos papéis da 001 (onde nascem as obras) e a produção sai da entrada da mina.

---

### User Story 2 - A obra viva: ferreiro caminha, martela e a forja acende (Priority: P1)

Quando a obra de uma forja começa, todos veem um ferreiro sair da mina, ir até o lote e martelar,
com uma barra mostrando quanto falta. Quando a obra termina, o canteiro vira uma forja de pedra
acesa soltando fumaça e o ferreiro volta para a mina.

**Why this priority**: é o par de fatos central da vila (`forja.construcao_iniciada` →
`forja.construcao_concluida`) e o que mais "conta a história" do tempo passando.

**Independent Test**: duas abas; o Mestre abre; o Jogador constrói uma forja; nas duas abas,
acompanhar o ferreiro até o lote, a barra enchendo por 12 s e a forja acendendo.

**Acceptance Scenarios**:

1. **Given** a temporada aberta e 2 ferreiros livres na entrada da mina, **When** a aba recebe
   `forja.construcao_iniciada`, **Then** um ferreiro caminha até o próximo lote livre, o lote vira
   canteiro com andaime e bigorna, o ferreiro martela, uma barra de progresso começa a encher e
   resta 1 ferreiro livre na entrada da mina; os números da tela mudam no mesmo instante que na 001.
2. **Given** um canteiro com a barra enchendo, **When** passam 12 s desde que a aba recebeu
   `forja.construcao_iniciada`, **Then** a barra está cheia ou quase cheia (nunca passa do fim nem
   recomeça).
3. **Given** um canteiro em obra, **When** a aba recebe `forja.construcao_concluida`, **Then** o
   canteiro mais antigo vira forja de pedra acesa com brasa e fumaça, a barra some e o ferreiro
   volta à entrada da mina.
4. **Given** dois canteiros em obra (ferreiros 2/2), **When** a aba recebe dois
   `forja.construcao_concluida`, **Then** os dois canteiros viram forjas na ordem em que começaram
   e os 2 ferreiros voltam à entrada da mina.
5. **Given** 6 lotes já ocupados por forjas, **When** a aba recebe mais um
   `forja.construcao_iniciada`, **Then** o canteiro aparece em um lote já usado (como na 001) e o
   lote mostra quantas forjas reúne (ex.: "×2"), sem esconder o número de forjas da tela.

---

### User Story 3 - A mina produz e os lingotes empilham (Priority: P1)

A cada ciclo de produção, o carrinho sai da mina cheio de minério. Se a vila tem forjas prontas,
elas soltam faíscas e a pilha de lingotes cresce.

**Why this priority**: a passagem do tempo é requisito explícito do trabalho; ela precisa ser
visível sem ninguém clicar.

**Independent Test**: abrir a temporada, construir uma forja e só observar por 20 s.

**Acceptance Scenarios**:

1. **Given** a temporada aberta e nenhuma forja concluída, **When** a aba recebe
   `recurso.produzido`, **Then** o carrinho sai da entrada da mina pelo trilho com "+10 🪨" e
   nenhuma faísca ou lingote novo aparece.
2. **Given** 1 forja concluída, **When** a aba recebe `recurso.produzido`, **Then** além do carrinho
   a forja solta uma faísca, aparece "+1 lingote" e a pilha passa a mostrar os lingotes atuais.
3. **Given** ciclos seguidos de 5 em 5 s, **When** cada `recurso.produzido` chega, **Then** a cena do
   carrinho termina antes do ciclo seguinte (nenhuma cena se acumula na fila).

---

### User Story 4 - Recusa visível só para quem pediu (Priority: P1)

Quando um pedido é recusado, a vila de quem pediu treme e mostra o motivo num balão de pergaminho.
As outras abas não mostram nada.

**Why this priority**: a recusa só para quem pediu é critério de avaliação; o visual não pode
"vazar" a recusa para as outras abas.

**Independent Test**: duas abas de Jogador; uma pede três forjas seguidas; só ela treme e mostra
"Sem ferreiro livre".

**Acceptance Scenarios**:

1. **Given** duas abas de Jogador abertas, **When** a aba A recebe `operacao.recusada` com motivo
   "Sem ferreiro livre", **Then** só a vila da aba A treme e mostra um balão com "Sem ferreiro
   livre"; a vila da aba B não se mexe por causa dessa recusa.
2. **Given** qualquer recusa, **When** a vila treme, **Then** nenhum ferreiro sai, nenhum canteiro
   aparece e nenhuma quantidade desenhada muda.

---

### User Story 5 - Dia, noite e a vila que entra no meio (Priority: P2)

O Mestre abre a temporada e a vila amanhece; o Mestre encerra e a vila anoitece, as forjas apagam e
as lanternas acendem. Quem entra no meio, ou depois do fim, vê a vila do jeito que ela está.

**Why this priority**: fecha a cadeia de eventos da abertura ao encerramento e garante que o
estado sincronizado também apareça desenhado.

**Independent Test**: com a temporada aberta, uma forja pronta, uma obra em andamento e uma
encomenda ativa, abrir uma terceira aba; depois encerrar e abrir uma quarta aba.

**Acceptance Scenarios**:

1. **Given** a fase aguardando (madrugada), **When** a aba recebe `vila.iniciada`, **Then** a vila
   amanhece em até 2 s e a faixa da temporada mostra "aberta".
2. **Given** a temporada aberta com forjas acesas, uma obra em andamento e uma encomenda ativa,
   **When** a aba recebe `vila.encerrada`, **Then** a vila anoitece, as brasas e a fumaça apagam,
   as lanternas acendem, o ferreiro em obra para de martelar e fica no canteiro, a barra da obra
   para onde estava e o pergaminho sai do quadro.
3. **Given** a temporada aberta com 1 forja concluída, 1 obra em andamento, 4 lingotes e uma
   encomenda ativa, **When** uma nova pessoa entra e recebe `estado.sincronizado`, **Then** a vila
   dela mostra dia, 1 forja acesa, 1 canteiro com ferreiro martelando, 1 ferreiro livre na mina,
   a pilha com 4 lingotes e o pergaminho com a barra no prazo restante da encomenda; a barra da
   obra aparece em modo "em andamento" (animada, sem a fração exata), porque o estado enviado não
   diz há quanto tempo a obra começou e esta feature não muda os dados enviados.
4. **Given** a temporada encerrada, **When** uma nova pessoa entra, **Then** a vila dela já aparece
   de noite, com forjas apagadas, lanternas acesas e as obras inacabadas paradas nos canteiros,
   sem passar pela cena do anoitecer.

---

### User Story 6 - O quadro de encomendas (Priority: P3)

O Mestre publica uma encomenda e um pergaminho é pregado no quadro de avisos, com o prazo
esvaziando. Se um Jogador entrega, os lingotes vão até o quadro, o pergaminho é carimbado e
recolhido e a recompensa aparece. Se o prazo acaba, o pergaminho se desfaz.

**Why this priority**: é o fluxo próprio da Ferraria e depende das histórias anteriores.

**Independent Test**: abrir, construir 2 forjas, publicar a encomenda e entregá-la quando houver
pelo menos 3 lingotes; em outra rodada, publicar e esperar 30 s.

**Acceptance Scenarios**:

1. **Given** o quadro vazio, **When** a aba recebe `encomenda.publicada`, **Then** um pergaminho com
   "3 lingotes · +40 🪨" é pregado no quadro e a barra de prazo começa a esvaziar.
2. **Given** um pergaminho no quadro e 4 lingotes na pilha, **When** a aba recebe
   `encomenda.cumprida`, **Then** 3 lingotes saem da pilha até o quadro, o pergaminho é carimbado
   e recolhido, "+40 🪨" aparece e a pilha passa a mostrar 1 lingote.
3. **Given** um pergaminho no quadro, **When** a aba recebe `encomenda.expirada`, **Then** o
   pergaminho se desfaz, o quadro fica vazio e a pilha de lingotes não muda.
4. **Given** um pergaminho com a barra de prazo, **When** passam 30 s desde `encomenda.publicada`,
   **Then** a barra está vazia ou quase vazia (nunca fica negativa nem recomeça).

---

### User Story 7 - Interface com cara de jogo de vila (Priority: P3)

Os painéis de estoque, botões, avisos e o Painel de eventos ganham aparência de vila (madeira,
pergaminho, tipografia pixel), sem perder legibilidade e sem que o Painel de eventos seja coberto
ou escondido.

**Why this priority**: melhora a experiência, mas a vila funciona sem ela.

**Independent Test**: abrir a página numa janela de 1280 × 720 e conferir que estoque, botões, vila,
avisos, Painel de eventos (com contadores) e rodapé aparecem, são legíveis e nada se sobrepõe.

**Acceptance Scenarios**:

1. **Given** a página aberta, **When** se olha o Painel de eventos, **Then** cada registro continua
   mostrando ⬆ emit / ⬇ on, nome, horário, dados, causa e reação, com pedidos, fatos e recusas
   ainda distinguíveis por cor e etiqueta, e os contadores por evento continuam no topo.
2. **Given** qualquer cena acontecendo na vila, **When** ela se anima, **Then** nenhum elemento da
   vila cobre o Painel de eventos, os botões, os avisos ou o rodapé.
3. **Given** a tipografia pixel, **When** se lê o nome de um evento ou um motivo de recusa, **Then**
   ele é lido sem esforço e os nomes de eventos aparecem letra por letra como na 001.

---

### User Story 8 - A vila continua funcionando se a arte falhar (Priority: P2)

Se alguma imagem da arte nova não carregar, a vila não trava: ela passa a desenhar formas simples
e emojis no lugar, cada fato continua com uma reação visível e todo o resto da tela funciona.

**Why this priority**: o visual é secundário no trabalho; uma falha de arte nunca pode derrubar a
avaliação do fluxo de eventos.

**Independent Test**: abrir a vila com as imagens da arte nova indisponíveis e rodar os três
cenários de `docs/especificacao.md`.

**Acceptance Scenarios**:

1. **Given** que a arte nova não carregou, **When** a página abre, **Then** a vila desenhada aparece
   em modo simples (formas e emojis), com um aviso discreto "arte indisponível — modo simples" na
   própria vila, e estoque, botões, avisos, Painel de eventos e rodapé funcionam normalmente.
2. **Given** o modo simples, **When** chega qualquer um dos 10 fatos, **Then** existe uma reação
   visível equivalente (ex.: canteiro 🏗️, forja 🔥, carrinho "+10 🪨", tremida e motivo,
   pergaminho 📜) e os números da tela batem com o estado recebido.

---

### Edge Cases

- Fatos chegando em rajada (ex.: um ciclo de produção e um fim de obra no mesmo instante, ou a
  disputa da US4 da 001) → cada cena começa quando o fato chega; se uma cena anterior ainda estiver
  em curso, ela é encurtada ou pulada até o fim, e a vila desenhada sempre termina mostrando o
  estado do último fato recebido. Cenas nunca formam fila crescente.
- Números da tela × cena → os números (estoque, ferreiros, forjas, encomenda) mudam no instante em
  que o fato chega, como na 001; a cena é decorativa e nunca atrasa nem adianta os números.
- Obra concluída antes de o ferreiro terminar de caminhar → não acontece com 12 s de obra e
  caminhada de até 3 s; se acontecer (aba lenta), o ferreiro vai direto para a mina e a forja
  acende.
- Aba em segundo plano por um tempo → ao voltar, a vila mostra o estado atual de imediato, sem
  reproduzir as cenas perdidas.
- Encerramento com obra em andamento → ferreiro e barra ficam parados no canteiro (obra inacabada,
  como na 001); nenhuma forja acende depois de `vila.encerrada`.
- Encerramento com encomenda ativa → o pergaminho é retirado junto com o anoitecer; não há cena de
  expiração depois.
- Mais forjas do que lotes → lotes são reaproveitados com a marca "×N" (US2#5); a quantidade de
  forjas da tela continua sendo a fonte do número.
- Pilha de lingotes grande → a pilha desenha até 10 lingotes; acima disso mostra a pilha cheia com
  o número atual ao lado.
- Recusa enquanto outra cena acontece → a tremida e o balão aparecem por cima, sem cancelar a cena
  em curso nem alterar quantidades desenhadas.
- Arte que falha no meio da sessão (ex.: só uma imagem não carregou) → só o elemento afetado cai
  para o modo simples; o resto continua com a arte nova.

## Requirements *(mandatory)*

### Functional Requirements

**Fronteira e não regressão**

- **FR-001**: Esta feature MUST NOT alterar nenhuma regra, número, nome de evento, quem emite, quem
  recebe, dado enviado, causa, ordem de verificação ou motivo de recusa definidos em
  `specs/001-vila-ferraria/spec.md` e `docs/especificacao.md`.
- **FR-002**: Todos os cenários de aceitação da 001 e os três cenários de `docs/especificacao.md`
  (recusa, passagem do tempo e disputa) MUST continuar passando com os mesmos eventos e números.
- **FR-003**: A vila desenhada MUST apenas reagir a fatos recebidos: ela MUST NOT mudar o estado,
  emitir eventos ou mostrar uma mudança antes de o fato correspondente chegar.
- **FR-004**: O Painel de eventos (⬆ emit / ⬇ on, nome, horário, dados, causa e reação, com
  distinção de pedidos, fatos e recusas), os contadores por evento, os avisos de sucesso, recusa,
  fim de obra e encomenda, os botões por papel e o rodapé com o nome do desenvolvedor MUST
  continuar presentes e funcionando.
- **FR-005**: O texto de "reação" registrado no Painel para cada fato MUST descrever a nova cena da
  tabela "Reação visual por fato" (ex.: `forja.construcao_iniciada` → "um ferreiro vai ao lote e
  começa a martelar a forja").

**Cenário e personagens**

- **FR-006**: O cenário MUST ser uma vila de ferreiros com: entrada da mina com trilho e carrinho de
  minério, pedreira, caminho de terra batida ligando os 6 lotes, rio ou lagoa e quadro de avisos.
- **FR-007**: O cenário MUST manter exatamente 6 lotes onde as obras nascem e um ponto de origem da
  produção, agora na entrada da mina.
- **FR-008**: A vila MUST desenhar: ferreiro (parado, andando e martelando), canteiro com andaime e
  bigorna, forja de pedra com chaminé, brasa e fumaça (acesa e apagada), carrinho de minério,
  pilha de lingotes, quadro de avisos e pergaminho de encomenda (pregado, carimbado e desfeito),
  lanternas e as luzes de madrugada, dia e noite.
- **FR-009**: A quantidade de ferreiros desenhados MUST ser igual ao limite (2): os livres ficam na
  entrada da mina e os ocupados ficam nos canteiros, batendo sempre com "ferreiros ocupados/limite"
  da tela.
- **FR-010**: Forjas acesas, canteiros, lingotes na pilha (até 10 desenhados, mais o número) e
  pergaminho MUST bater com o estado do último fato recebido.

**Reação a cada fato**

- **FR-011**: Cada um dos 10 fatos que a aba escuta MUST disparar a reação da tabela "Reação visual
  por fato", dentro da duração indicada.
- **FR-012**: A barra de progresso da obra MUST encher ao longo do tempo de obra do estado
  (12 s), contado a partir do recebimento de `forja.construcao_iniciada`, e parar onde estiver em
  `vila.encerrada`. Para obras que já estavam em andamento quando a aba recebeu
  `estado.sincronizado`, a barra MUST aparecer em modo "em andamento" (animada, sem fração exata)
  até `forja.construcao_concluida` ou `vila.encerrada`.
- **FR-013**: A barra de prazo da encomenda MUST esvaziar ao longo do prazo restante informado no
  estado (30 s na publicação; o restante enviado para quem entra no meio) e sumir em
  `encomenda.cumprida`, `encomenda.expirada` ou `vila.encerrada`.
- **FR-014**: A reação de `operacao.recusada` (tremida e balão com o motivo exato) MUST aparecer só
  na aba que recebeu a recusa e MUST NOT alterar nada desenhado.
- **FR-015**: Ao receber `estado.sincronizado`, a vila MUST aparecer já no estado atual, sem
  reproduzir cenas passadas, incluindo a luz da fase, forjas, canteiros, ferreiros, pilha e
  pergaminho com prazo restante.
- **FR-016**: Cenas MUST NOT formar fila: um fato novo encurta ou conclui a cena anterior, e a vila
  sempre converge para o estado do último fato recebido.

**Interface**

- **FR-017**: Estoque, botões, avisos e Painel de eventos MUST ter aparência de vila (madeira,
  pergaminho, tipografia pixel) e MUST continuar legíveis; nomes de eventos MUST aparecer letra por
  letra.
- **FR-018**: Nenhum elemento visual MUST cobrir o Painel de eventos, os botões, os avisos ou o
  rodapé, em nenhuma cena.

**Resiliência da arte**

- **FR-019**: Se uma imagem da arte nova falhar ao carregar, o elemento afetado MUST cair para um
  desenho simples (formas e emojis) com reação equivalente, e a vila MUST mostrar um aviso discreto
  de "modo simples"; nenhuma outra parte da tela pode deixar de funcionar.

**Arte e créditos**

- **FR-020**: Toda arte MUST ser original, criada para este projeto, ou de licença de uso livre; o
  README MUST creditar cada item (o que é, autor ou origem, licença), dizer como a arte original é
  gerada novamente a partir do repositório e incluir essa geração na declaração de uso de IA.
- **FR-021**: A feature MUST NOT usar arte, nomes, personagens, lugares ou assets de jogos
  comerciais; a referência a "vila de fazenda aconchegante" é só de clima.
- **FR-022**: O README MUST listar esta identidade visual como extra, feito depois de tudo o que é
  obrigatório funcionar.

### Key Entities

- **Cena**: a reação desenhada a um fato; tem o fato que a dispara, os elementos que se mexem e uma
  duração máxima. Não guarda estado da vila: só lê o estado do fato recebido.
- **Elemento da vila**: cada coisa desenhada (mina, trilho, carrinho, lote, canteiro, forja,
  ferreiro, pilha de lingotes, quadro, pergaminho, lanterna) com suas aparências (ex.: forja acesa
  ou apagada) e um desenho simples equivalente para o modo simples.
- **Luz da fase**: madrugada (aguardando), dia (aberta) e noite (encerrada).
- **Lote**: um dos 6 lugares do caminho onde uma obra nasce; pode reunir mais de uma forja (×N).
- **Crédito de arte**: item, autor ou origem e licença, listados no README.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Os 10 fatos que a aba escuta têm, cada um, uma reação visível e distinta na vila
  desenhada (10 de 10 na tabela conferida durante o teste).
- **SC-002**: 100% dos cenários de aceitação da 001 e dos três cenários de `docs/especificacao.md`
  passam depois da feature, com os mesmos eventos e números, e nenhum nome de evento, dado enviado
  ou causa muda.
- **SC-003**: Os números da tela aparecem em até 1 s após cada fato, como na 001; nenhuma cena
  atrasa essa atualização.
- **SC-004**: Quem entra no meio da temporada vê, em até 2 s, a vila desenhada batendo 100% com o
  estado recebido em fase, forjas acesas, canteiros (com a barra em modo "em andamento"), ferreiros
  livres e ocupados, lingotes e encomenda.
- **SC-005**: Com a arte nova indisponível, 100% dos cenários de `docs/especificacao.md` passam e
  cada um dos 10 fatos ainda tem reação visível.
- **SC-006**: 100% dos itens de arte usados aparecem nos créditos do README com origem e licença; 0
  itens de jogos comerciais ou do kit original no cenário, personagens e objetos.
- **SC-007**: Numa janela de 1280 × 720, a vila, o estoque, os botões, os avisos, o Painel de
  eventos e o rodapé aparecem sem nenhuma sobreposição durante todas as cenas.
- **SC-008**: Depois de uma rajada de fatos (ex.: 2 obras, 3 ciclos e uma encomenda em 20 s), a
  vila desenhada para de se mexer e bate com o estado em até 3 s após o último fato.
- **SC-009**: Uma pessoa que nunca viu a aplicação, olhando só a vila (sem ler o Painel), diz
  corretamente o que aconteceu em pelo menos 8 dos 10 fatos.

## Assumptions

- A feature é um extra visual (o enunciado diz que não é preciso criar gráficos do zero e aceita
  extras depois de tudo funcionando); por isso só começa depois de a 001 estar completa, e é
  listada como extra no README.
- "Arte original criada para o projeto" conta como arte de uso livre (constituição 1.0.1,
  princípio VI): o README declara a autoria e uma licença livre. Se algum item vier de pacote de
  terceiros, só de licença livre e com crédito.
- A arte será desenhada por um script versionado no repositório, que gera as imagens da vila; quem
  quiser pode refazer a arte rodando esse script. Como o script é escrito com ajuda de IA, isso
  entra na declaração de uso de IA do README.
- Quem entra no meio de uma obra vê a barra em modo "em andamento", sem a fração exata (decisão do
  Maestro, Q1 = A, 2026-10-22): o estado enviado não informa o início de cada obra e esta feature
  não muda os dados enviados.
- O estilo é pixel art numa grade de 16 pixels, como a vila do kit, com uma paleta própria de tons
  quentes (pedra, brasa, madeira, terra) e um destaque frio para água e noite.
- As durações de cena são máximas e curtas para nunca disputar atenção com os números; a cena do
  carrinho termina antes do próximo ciclo de produção (5 s).
- A barra de progresso da obra é contada a partir de quando a aba recebeu
  `forja.construcao_iniciada`, usando o tempo de obra que já vem no estado; diferenças de até 1 s
  entre abas são aceitáveis (o fato que vale é `forja.construcao_concluida`).
- Os 2 ferreiros desenhados representam o limite de ferreiros; não há ferreiros extras de enfeite.
- Fase aguardando é desenhada como madrugada, para que `vila.iniciada` seja um amanhecer visível.
- Não há som nesta feature; não há mudança para celular (o alvo é janela de computador a partir de
  1280 × 720).
- A ordem dos lotes e a regra de reaproveitamento seguem a 001 (cada aba escolhe o próximo lote
  livre em ordem; quem entra no meio desenha primeiro as forjas concluídas e depois as obras).
- O aviso de "modo simples" fica dentro da vila desenhada e não gera evento nem registro no Painel
  (o Painel só lista eventos).
