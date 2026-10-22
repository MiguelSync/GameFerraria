# Feature Specification: Vila Ferraria em Tempo Real

**Feature Branch**: `001-vila-ferraria` (sem branch git; diretório da feature apenas)

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "A vila Ferraria completa em tempo real, como exigem as seções 2 a 5 do
enunciado do Trabalho 01 e a Etapa 8 do Guia de Implementação: dois papéis (Mestre e Jogador),
estado mantido pelo servidor, minério de ferro produzido pela mina em intervalos, forjas construídas
por ferreiros, lingotes como recurso refinado, recusas só para quem pediu, disputa pelo último
ferreiro, encerramento da temporada, Painel de eventos com causa de cada fato e um fluxo de eventos
próprio (encomenda de lingotes com prazo)."

## Visão geral

Uma vila de ferreiros aconchegante. A mina da vila extrai **minério de ferro** sozinha, de tempos em
tempos. Os Jogadores gastam minério para erguer **forjas**; cada obra ocupa um **ferreiro** até
terminar. Cada forja pronta passa a fundir **lingotes** a cada ciclo de produção. O Mestre abre e
encerra a temporada e pode publicar uma **encomenda** de lingotes com prazo, que os Jogadores
tentam cumprir antes que expire. Todos veem tudo acontecer ao mesmo tempo, sem recarregar a tela,
e um Painel de eventos mostra cada pedido, cada fato e a causa de cada fato.

### Regras e números (fonte única; `docs/especificacao.md` usa os mesmos)

| Regra | Valor |
|---|---|
| Recurso primário | Minério de ferro (minérios) |
| Recurso refinado | Lingotes de ferro (lingotes) |
| Estoque inicial | 120 minérios e 0 lingotes |
| Custo de uma forja | 40 minérios |
| Tempo da obra | 12 segundos |
| Limite de ferreiros | 2 (cada obra ocupa 1 ferreiro do início ao fim) |
| Intervalo de produção | 5 segundos (o primeiro ciclo ocorre 5 s depois da abertura) |
| Produção por ciclo | +10 minérios (mina) e +1 lingote por forja concluída |
| Quando a obra termina | O ferreiro fica livre e a forja passa a produzir 1 lingote por ciclo |
| Encomenda | 3 lingotes, prazo de 30 segundos, recompensa de 40 minérios, uma ativa por vez |

Consequências usadas nos testes: o estoque inicial (120) paga 3 forjas, mas só há 2 ferreiros;
logo, logo após a abertura, a 3ª forja pedida é recusada por falta de ferreiro com 40 minérios
ainda no estoque. A recompensa da encomenda (40) paga exatamente uma forja.

### Catálogo de eventos

| Evento | Emite | Recebe | O que muda no estado | Causa que o fato carrega |
|---|---|---|---|---|
| `estado.sincronizado` | Servidor | Só quem conectou | Nada muda; entrega o estado atual a quem acabou de entrar | `conexao` |
| `vila.abertura_solicitada` | Mestre | Servidor | É um pedido; nada muda | — |
| `vila.iniciada` | Servidor | Todos | Fase: aguardando → aberta; a produção começa | `vila.abertura_solicitada` + nome do Mestre que pediu |
| `forja.construcao_solicitada` | Jogador | Servidor | É um pedido; nada muda | — |
| `forja.construcao_iniciada` | Servidor | Todos | Minérios −40; ferreiros ocupados +1; forjas em obra +1 | `forja.construcao_solicitada` + nome de quem pediu |
| `operacao.recusada` | Servidor | Só quem pediu | Nada muda; informa o motivo | o pedido recusado + o motivo |
| `recurso.produzido` | Servidor | Todos | Minérios +10; lingotes + (número de forjas concluídas) | `temporizador` |
| `forja.construcao_concluida` | Servidor | Todos | Ferreiros ocupados −1; forjas em obra −1; forjas concluídas +1 | `forja.construcao_iniciada (temporizador)` + nome de quem pediu a obra |
| `vila.encerramento_solicitado` | Mestre | Servidor | É um pedido; nada muda | — |
| `vila.encerrada` | Servidor | Todos | Fase: aberta → encerrada; temporizadores param; encomenda ativa é descartada | `vila.encerramento_solicitado` + nome do Mestre que pediu |
| `encomenda.publicacao_solicitada` | Mestre | Servidor | É um pedido; nada muda | — |
| `encomenda.publicada` | Servidor | Todos | Encomenda ativa: nenhuma → 3 lingotes, prazo 30 s, recompensa 40 minérios | `encomenda.publicacao_solicitada` + nome do Mestre que publicou |
| `encomenda.entrega_solicitada` | Jogador | Servidor | É um pedido; nada muda | — |
| `encomenda.cumprida` | Servidor | Todos | Lingotes −3; minérios +40; encomenda ativa → nenhuma | `encomenda.entrega_solicitada` + nome de quem entregou |
| `encomenda.expirada` | Servidor | Todos | Encomenda ativa → nenhuma (nada é debitado nem pago) | `encomenda.publicada (temporizador)` |

### Motivos de recusa (texto exato de `operacao.recusada`)

| Pedido | Ordem de verificação → motivo |
|---|---|
| `vila.abertura_solicitada` | 1. não é Mestre → "Só o Mestre pode abrir a temporada"; 2. fase diferente de aguardando → "A temporada já foi aberta" |
| `vila.encerramento_solicitado` | 1. não é Mestre → "Só o Mestre pode encerrar a temporada"; 2. fase diferente de aberta → "A temporada não está aberta" |
| `forja.construcao_solicitada` | 1. não é Jogador → "Só Jogadores constroem forjas"; 2. fase diferente de aberta → "A temporada não está aberta"; 3. minérios < 40 → "Minério insuficiente"; 4. ferreiros ocupados = 2 → "Sem ferreiro livre" |
| `encomenda.publicacao_solicitada` | 1. não é Mestre → "Só o Mestre pode publicar encomendas"; 2. fase diferente de aberta → "A temporada não está aberta"; 3. já há encomenda ativa → "Já existe uma encomenda ativa" |
| `encomenda.entrega_solicitada` | 1. não é Jogador → "Só Jogadores entregam encomendas"; 2. fase diferente de aberta → "A temporada não está aberta"; 3. sem encomenda ativa → "Nenhuma encomenda ativa"; 4. lingotes < 3 → "Lingotes insuficientes" |

A primeira verificação que falhar define o motivo; as demais não são avaliadas. Como o papel é
sempre verificado antes da fase, fora da temporada quem tem o papel certo recebe "A temporada não
está aberta" (ou "A temporada já foi aberta", no caso da abertura), e quem tem o papel errado recebe
o motivo de papel (ex.: o Mestre que pede uma forja depois do encerramento recebe "Só Jogadores
constroem forjas").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entrar na vila e o Mestre abrir a temporada (Priority: P1)

Uma pessoa entra na vila escolhendo um nome e um papel (Mestre ou Jogador) e vê a vila exatamente
como ela está naquele momento. O Mestre abre a temporada e todos percebem, na hora, que a vila
começou a funcionar.

**Why this priority**: sem estado sincronizado e sem temporada aberta nenhuma outra ação é possível;
é o primeiro elo da cadeia de eventos.

**Independent Test**: abrir duas abas (Mestre e Jogador), entrar nas duas e clicar em "Abrir
temporada" no Mestre; as duas abas mudam para "aberta" sem recarregar.

**Acceptance Scenarios**:

1. **Given** a vila recém-iniciada, **When** uma pessoa entra, **Then** só ela recebe
   `estado.sincronizado` com causa `conexao`, mostrando 120 minérios, 0 lingotes, ferreiros 0/2,
   0 forjas e fase aguardando.
2. **Given** a fase aguardando, **When** o Mestre emite `vila.abertura_solicitada`, **Then** todos
   recebem `vila.iniciada` com causa `vila.abertura_solicitada` e o nome do Mestre, e a fase passa
   a aberta.
3. **Given** a fase aguardando, **When** um Jogador emite `vila.abertura_solicitada`, **Then** só ele
   recebe `operacao.recusada` com motivo "Só o Mestre pode abrir a temporada" e a fase continua
   aguardando.
4. **Given** a fase aberta, **When** o Mestre emite `vila.abertura_solicitada` de novo, **Then** só ele
   recebe `operacao.recusada` com motivo "A temporada já foi aberta".
5. **Given** a temporada aberta com uma forja em obra e uma encomenda ativa, **When** uma nova pessoa
   entra, **Then** ela recebe `estado.sincronizado` com a obra em andamento e a encomenda ativa.

---

### User Story 2 - Jogador constrói uma forja e recebe recusas só para si (Priority: P1)

Um Jogador pede para construir uma forja. Se houver minério e ferreiro livre, a obra começa e todos
veem o canteiro surgir e o estoque cair. Se faltar algo, só ele é avisado, com o motivo.

**Why this priority**: é o par pedido/fato central do trabalho e a recusa como evento.

**Independent Test**: com a temporada aberta, clicar em "Construir forja" três vezes seguidas em uma
aba de Jogador; duas obras começam e a terceira é recusada só naquela aba.

**Acceptance Scenarios**:

1. **Given** a temporada aberta, 120 minérios e ferreiros 0/2, **When** o Jogador A emite
   `forja.construcao_solicitada`, **Then** todos recebem `forja.construcao_iniciada` com causa
   `forja.construcao_solicitada` e o nome de A, e o estado fica em 80 minérios, ferreiros 1/2,
   1 forja em obra.
2. **Given** a temporada aberta, 40 minérios e ferreiros 2/2, **When** A emite
   `forja.construcao_solicitada`, **Then** só A recebe `operacao.recusada` com motivo
   "Sem ferreiro livre" e o estado não muda.
3. **Given** a temporada aberta, 20 minérios e ferreiros 1/2, **When** A emite
   `forja.construcao_solicitada`, **Then** só A recebe `operacao.recusada` com motivo
   "Minério insuficiente"; o estoque continua 20 e os ferreiros 1/2.
4. **Given** a fase aguardando, **When** A emite `forja.construcao_solicitada`, **Then** só A recebe
   `operacao.recusada` com motivo "A temporada não está aberta".
5. **Given** a temporada aberta, **When** o Mestre emite `forja.construcao_solicitada`, **Then** só o
   Mestre recebe `operacao.recusada` com motivo "Só Jogadores constroem forjas".

---

### User Story 3 - A passagem do tempo: produção e fim de obra (Priority: P1)

Sem ninguém clicar, a mina produz minério a cada 5 segundos e cada obra termina sozinha 12 segundos
depois de começar. Cada forja concluída passa a render lingotes nos ciclos seguintes.

**Why this priority**: temporizadores como fonte de eventos são requisito explícito.

**Independent Test**: abrir a temporada, iniciar uma forja e só observar por 15 segundos.

**Acceptance Scenarios**:

1. **Given** a temporada aberta há pouco, 120 minérios e nenhuma forja concluída, **When** passam
   5 segundos, **Then** todos recebem `recurso.produzido` com causa `temporizador`, +10 minérios e
   +0 lingotes.
2. **Given** que A recebeu `forja.construcao_iniciada` logo após a abertura (80 minérios, 1/2),
   **When** passam 12 segundos desde o início da obra, **Then** todos recebem
   `forja.construcao_concluida` com causa `forja.construcao_iniciada (temporizador)` e o nome de A;
   ferreiros 0/2, 1 forja concluída.
3. **Given** a cena do item 2, **When** chega o ciclo dos 15 segundos, **Then** `recurso.produzido`
   leva o estoque a 110 minérios e 1 lingote.
4. **Given** 2 forjas concluídas, **When** ocorre um ciclo de produção, **Then** os lingotes sobem 2.

---

### User Story 4 - Disputa pelo último ferreiro (Priority: P1)

Dois Jogadores pedem uma forja no mesmo instante, mas só resta um ferreiro livre. O servidor decide
um pedido de cada vez: um vence e o outro recebe a recusa.

**Why this priority**: o enunciado exige explicitamente que, na disputa, só um consiga.

**Independent Test**: três abas (Mestre, A e B); abrir; A constrói uma vez; A e B clicam em
"Construir forja" quase ao mesmo tempo.

**Acceptance Scenarios**:

1. **Given** a temporada aberta, 80 minérios e ferreiros 1/2, **When** A e B emitem
   `forja.construcao_solicitada` ao mesmo tempo, **Then** todos recebem um único
   `forja.construcao_iniciada` (40 minérios, ferreiros 2/2) com o nome de quem foi tratado primeiro,
   e só o outro recebe `operacao.recusada` com motivo "Sem ferreiro livre".
2. **Given** qualquer sequência de pedidos simultâneos, **When** eles são tratados, **Then** os
   ferreiros ocupados nunca passam de 2 e minérios e lingotes nunca ficam negativos.

---

### User Story 5 - O Mestre encerra a temporada (Priority: P2)

O Mestre encerra a temporada; a vila "anoitece" para todos, a produção para e qualquer nova ação é
recusada.

**Why this priority**: fecha a cadeia de eventos da abertura ao encerramento.

**Independent Test**: com a temporada aberta e uma obra em andamento, clicar em "Encerrar
temporada"; o estoque para de subir e "Construir forja" passa a ser recusado.

**Acceptance Scenarios**:

1. **Given** a fase aberta, **When** o Mestre emite `vila.encerramento_solicitado`, **Then** todos
   recebem `vila.encerrada` com causa `vila.encerramento_solicitado` e o nome do Mestre, e a fase
   passa a encerrada.
2. **Given** a fase encerrada, **When** passam 5 segundos ou mais, **Then** nenhum
   `recurso.produzido` é emitido.
3. **Given** uma forja em obra no momento do encerramento, **When** completam-se os 12 segundos da
   obra, **Then** nenhum `forja.construcao_concluida` é emitido; a obra fica inacabada (continua
   contada como em obra e o ferreiro continua ocupado no estado final).
4. **Given** a fase encerrada, **When** um Jogador emite `forja.construcao_solicitada`, **Then** só
   ele recebe `operacao.recusada` com motivo "A temporada não está aberta".
5. **Given** a fase aberta, **When** um Jogador emite `vila.encerramento_solicitado`, **Then** só ele
   recebe `operacao.recusada` com motivo "Só o Mestre pode encerrar a temporada".
6. **Given** a fase encerrada, **When** o Mestre emite `vila.abertura_solicitada`, **Then** só ele
   recebe `operacao.recusada` com motivo "A temporada já foi aberta" (a temporada não reabre).

---

### User Story 6 - Encomenda de lingotes com prazo (evento próprio) (Priority: P3)

O Mestre publica uma encomenda: 3 lingotes em até 30 segundos. Qualquer Jogador pode entregá-la de
uma vez se a vila tiver lingotes suficientes; a vila recebe 40 minérios de pagamento. Se o prazo
acabar antes, a encomenda expira sozinha.

**Why this priority**: é a adaptação própria da Ferraria (Etapa 8) e dá uso aos lingotes; depende
das histórias 1 a 3 funcionando.

**Independent Test**: abrir a temporada, construir duas forjas, publicar a encomenda e entregá-la
depois que os lingotes chegarem a pelo menos 3 (com 2 forjas eles sobem 0 → 2 → 4); em outra rodada, publicar e esperar 30 segundos.

**Acceptance Scenarios**:

1. **Given** a temporada aberta e nenhuma encomenda ativa, **When** o Mestre emite
   `encomenda.publicacao_solicitada`, **Then** todos recebem `encomenda.publicada` com causa
   `encomenda.publicacao_solicitada` e o nome do Mestre, quantidade 3, prazo 30 s e recompensa
   40 minérios.
2. **Given** uma encomenda ativa e 4 lingotes, **When** o Jogador A emite
   `encomenda.entrega_solicitada`, **Then** todos recebem `encomenda.cumprida` com causa
   `encomenda.entrega_solicitada` e o nome de A; lingotes 1, minérios +40, nenhuma encomenda ativa.
3. **Given** uma encomenda ativa e 2 lingotes, **When** A emite `encomenda.entrega_solicitada`,
   **Then** só A recebe `operacao.recusada` com motivo "Lingotes insuficientes" e nada muda.
4. **Given** uma encomenda publicada e não entregue, **When** passam 30 segundos desde
   `encomenda.publicada`, **Then** todos recebem `encomenda.expirada` com causa
   `encomenda.publicada (temporizador)` e a encomenda deixa de existir, sem débito nem pagamento.
5. **Given** uma encomenda ativa, **When** o Mestre emite `encomenda.publicacao_solicitada`, **Then**
   só ele recebe `operacao.recusada` com motivo "Já existe uma encomenda ativa".
6. **Given** uma encomenda ativa e 3 ou mais lingotes, **When** A e B emitem
   `encomenda.entrega_solicitada` ao mesmo tempo, **Then** só um `encomenda.cumprida` é emitido e o
   outro recebe `operacao.recusada` com motivo "Nenhuma encomenda ativa".
7. **Given** uma encomenda cumprida, **When** completam-se os 30 segundos do prazo original,
   **Then** nenhum `encomenda.expirada` é emitido.
8. **Given** nenhuma encomenda ativa, **When** A emite `encomenda.entrega_solicitada`, **Then** só A
   recebe `operacao.recusada` com motivo "Nenhuma encomenda ativa".

---

### User Story 7 - Contadores por evento (extra no trabalho individual) (Priority: P4)

No alto do Painel de eventos aparecem etiquetas com quantas vezes cada evento já ocorreu naquela aba.

**Why this priority**: obrigatório só para duplas; incluído como extra e feito por último.

**Independent Test**: realizar algumas ações e conferir que, por exemplo,
`forja.construcao_iniciada ×2` cresce a cada novo evento daquele nome.

**Acceptance Scenarios**:

1. **Given** o painel aberto, **When** a aba emite ou escuta um evento, **Then** o contador daquele
   nome de evento aumenta em 1.

---

### Edge Cases

- Pedido feito antes da abertura ou depois do encerramento → `operacao.recusada` só para quem
  pediu, com o motivo dado pela ordem do catálogo (papel antes de fase): quem tem o papel certo
  recebe "A temporada não está aberta"; quem tem o papel errado recebe o motivo de papel (ex.:
  Mestre pedindo forja depois do encerramento → "Só Jogadores constroem forjas"); e o Mestre que
  pede a abertura de uma temporada já aberta ou encerrada recebe "A temporada já foi aberta" (US5#6).
- Dois pedidos chegam no mesmo instante → tratados em sequência; a segunda validação já enxerga o
  estado deixado pelo primeiro (US4).
- Ciclo de produção e fim de obra no mesmo instante → tratados em sequência; a forja só rende
  lingotes nos ciclos que acontecem depois de `forja.construcao_concluida`.
- Encerramento com obras em andamento → as obras ficam inacabadas; nenhum
  `forja.construcao_concluida` é emitido depois de `vila.encerrada`.
- Encerramento com encomenda ativa → a encomenda é descartada junto com `vila.encerrada` (o estado
  enviado já não tem encomenda) e `encomenda.expirada` não é emitido.
- Pessoa entra no meio da temporada ou depois do encerramento → recebe só `estado.sincronizado` com
  o estado atual (inclusive obras em andamento e encomenda ativa).
- Pessoa sai (fecha a aba) → nada é emitido; obras e encomendas que ela iniciou continuam.
- Estoque nunca fica negativo e ferreiros nunca passam do limite, em nenhuma ordem de pedidos.

## Requirements *(mandatory)*

### Functional Requirements

**Papéis e temporada**

- **FR-001**: O sistema MUST permitir entrar na vila informando um nome e escolhendo o papel Mestre
  ou Jogador, sem login e senha.
- **FR-002**: O sistema MUST manter a temporada em uma de três fases: aguardando → aberta →
  encerrada, sem voltar de fase.
- **FR-003**: Apenas o Mestre MUST conseguir abrir (`vila.abertura_solicitada` → `vila.iniciada`) e
  encerrar (`vila.encerramento_solicitado` → `vila.encerrada`) a temporada; os demais pedidos desses
  tipos MUST ser recusados com os motivos do catálogo. `vila.iniciada` e `vila.encerrada` MUST
  levar a causa e o nome do Mestre que pediu.
- **FR-004**: Ao conectar, a pessoa MUST receber `estado.sincronizado` apenas para si, com o estado
  completo atual e causa `conexao`.

**Construção e recursos**

- **FR-005**: O estado inicial MUST ser 120 minérios, 0 lingotes, ferreiros 0/2, 0 forjas em obra,
  0 forjas concluídas, nenhuma encomenda e fase aguardando.
- **FR-006**: Um Jogador MUST poder pedir uma forja (`forja.construcao_solicitada`). O pedido MUST
  ser validado na ordem do catálogo de motivos e, se aceito, MUST debitar 40 minérios, ocupar 1
  ferreiro, somar 1 forja em obra e emitir `forja.construcao_iniciada` para todos, com causa e nome
  de quem pediu.
- **FR-007**: A validação de um pedido e a alteração do estado MUST ocorrer como um passo único e
  ininterrupto, de modo que pedidos simultâneos sejam decididos em sequência.
- **FR-008**: Cada obra MUST terminar sozinha 12 segundos após `forja.construcao_iniciada`,
  liberando 1 ferreiro, subtraindo 1 forja em obra, somando 1 forja concluída e emitindo
  `forja.construcao_concluida` para todos, com causa `forja.construcao_iniciada (temporizador)` e o
  nome de quem pediu a obra.
- **FR-009**: Enquanto a temporada estiver aberta, a cada 5 segundos (o primeiro ciclo 5 s após
  `vila.iniciada`) o sistema MUST somar 10 minérios e 1 lingote por forja concluída e emitir
  `recurso.produzido` para todos, com causa `temporizador`, mesmo quando 0 lingotes forem
  produzidos.
- **FR-010**: Toda recusa MUST ser emitida como `operacao.recusada` somente para quem pediu, com o
  motivo exato do catálogo e a causa (nome do pedido recusado), sem alterar o estado.

**Encerramento**

- **FR-011**: Ao `vila.encerrada`, o sistema MUST parar a produção, descartar a encomenda ativa e
  não emitir mais `recurso.produzido`, `forja.construcao_concluida` nem `encomenda.expirada`; obras
  em andamento ficam inacabadas no estado final.
- **FR-012**: Antes da abertura e depois do encerramento, todo pedido de encerramento, construção,
  publicação ou entrega MUST ser recusado, e depois do encerramento também o pedido de abertura.
  O motivo MUST seguir a ordem do catálogo de motivos, em que o papel é verificado antes da fase:
  quem tem o papel certo recebe "A temporada não está aberta" (ou "A temporada já foi aberta", na
  abertura pedida pelo Mestre depois do encerramento); quem tem o papel errado recebe o motivo de
  papel daquele pedido (ex.: Mestre pedindo forja depois do encerramento recebe "Só Jogadores
  constroem forjas").

**Encomenda (fluxo próprio)**

- **FR-013**: O Mestre MUST poder publicar uma encomenda (`encomenda.publicacao_solicitada`) com
  valores fixos: 3 lingotes, prazo de 30 segundos e recompensa de 40 minérios; só pode haver uma
  encomenda ativa por vez. Se aceita, todos recebem `encomenda.publicada`, com causa e nome de
  quem publicou.
- **FR-014**: Um Jogador MUST poder entregar a encomenda ativa de uma só vez
  (`encomenda.entrega_solicitada`). Se aceita, MUST debitar 3 lingotes, creditar 40 minérios,
  encerrar a encomenda e emitir `encomenda.cumprida` para todos, com causa e nome de quem entregou.
- **FR-015**: Se a encomenda não for cumprida em 30 segundos após `encomenda.publicada`, o sistema
  MUST encerrá-la sem débito nem pagamento e emitir `encomenda.expirada` para todos, com causa
  `encomenda.publicada (temporizador)`. Uma encomenda já cumprida MUST NOT expirar depois.

**Tela e Painel de eventos**

- **FR-016**: A tela MUST mostrar a fase da temporada, minérios, lingotes, ferreiros ocupados no
  formato "ocupados/limite" (ex.: 1/2), forjas em obra e concluídas, a encomenda ativa (se houver),
  os botões do papel, a vila desenhada e avisos de sucesso, recusa, fim de obra e encomenda.
- **FR-017**: Cada fato recebido MUST provocar uma reação visível na vila desenhada (canteiro ao
  iniciar a forja, forja pronta ao concluir, "+10" ao produzir, tremida e motivo ao recusar,
  faixa de temporada aberta/encerrada, aviso de encomenda publicada/cumprida/expirada).
- **FR-018**: O Painel de eventos MUST listar em tempo real cada evento que a aba emitiu (⬆ emit) e
  escutou (⬇ on), com nome, horário, dados, causa e a reação do cliente; MUST distinguir pedidos,
  fatos e recusas; e MUST NOT ser removido.
- **FR-019**: Todo fato que muda a vila MUST levar o estado atual completo, para que todas as abas
  mostrem o mesmo estado sem recarregar.
- **FR-020**: O rodapé MUST mostrar o nome do desenvolvedor (Miguel Antonio Selhorst).
- **FR-021** *(extra)*: O Painel de eventos MUST mostrar contadores de quantas vezes cada evento
  ocorreu naquela aba.

**Nomes e visual**

- **FR-022**: Os 15 nomes de eventos do catálogo MUST ser usados letra por letra em toda a
  aplicação e na documentação.
- **FR-023**: O visual MUST usar apenas emojis, CSS ou arte de uso livre creditada; arte, nomes ou
  assets de jogos comerciais MUST NOT ser usados.

### Key Entities

- **Vila (estado)**: fase da temporada; minérios; lingotes; ferreiros ocupados e limite (2); forjas
  em obra; forjas concluídas; produção por ciclo (10 minérios + 1 lingote por forja concluída);
  intervalo (5 s); tempo de obra (12 s); custo da forja (40 minérios); encomenda ativa (ou nenhuma).
- **Participante**: nome e papel (Mestre ou Jogador), escolhidos ao entrar; existe só enquanto a
  aba está conectada.
- **Obra de forja**: quem pediu e o instante de início; ocupa 1 ferreiro por 12 s e vira forja
  concluída.
- **Encomenda**: quantidade (3 lingotes), prazo (30 s a partir da publicação), recompensa
  (40 minérios); termina como cumprida, expirada ou descartada no encerramento.
- **Evento**: nome, quem emite, quem recebe, dados (estado atual, causa, quem pediu ou motivo).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em teste com duas ou mais abas, todo fato aparece em todas as abas em até 1 segundo,
  sem recarregar a página.
- **SC-002**: Em 10 repetições do cenário de disputa, 100% terminam com exatamente um
  `forja.construcao_iniciada` e uma `operacao.recusada`; ferreiros nunca passam de 2/2 e o estoque
  nunca fica negativo.
- **SC-003**: 100% das recusas aparecem apenas na aba de quem pediu e em nenhuma outra.
- **SC-004**: Os 15 eventos do catálogo aparecem no Painel de eventos com nome, horário, dados,
  causa (nos fatos) e reação.
- **SC-005**: Sem nenhum clique, `recurso.produzido` aparece a cada 5 s (±1 s) com a temporada
  aberta e `forja.construcao_concluida` aparece 12 s (±1 s) após o início de cada obra.
- **SC-006**: Os três cenários de `docs/especificacao.md` (recusa, passagem do tempo e disputa)
  produzem exatamente os eventos e números descritos na primeira tentativa.
- **SC-007**: Após `vila.encerrada`, 0 fatos de produção, de fim de obra ou de expiração são
  emitidos, e 100% dos pedidos de ação são recusados.
- **SC-008**: Quem testa consegue explicar, para qualquer evento do painel, quem emitiu, quem
  recebeu e o que mudou, consultando apenas esta especificação.

## Assumptions

- Trabalho individual (Miguel Antonio Selhorst, @MiguelSync); os contadores por evento entram como
  extra. Se virar dupla, o extra passa a obrigatório e nada mais muda.
- O papel é escolhido livremente ao entrar; pode haver mais de um Mestre conectado e qualquer um
  deles pode abrir, encerrar e publicar encomendas.
- Uma única vila e uma única temporada por execução do servidor; o estado vive só na memória e
  volta ao início quando o servidor reinicia. A temporada encerrada não reabre.
- Os valores da encomenda são fixos (o Mestre não escolhe quantidade nem prazo) para manter o
  escopo pequeno e os testes reproduzíveis.
- A forja não consome minério para fundir lingotes: cada forja concluída rende 1 lingote por ciclo.
  A produção de minério da mina é constante (10 por ciclo) e não muda com as forjas.
- Não há limite para o número de forjas concluídas; a vila desenhada reaproveita os lotes do mapa.
- Obras em andamento no encerramento ficam inacabadas (não são reembolsadas nem concluídas).
- Sair da vila (fechar a aba) não gera evento nem cancela obras ou encomendas.
- O visual tem "clima" de vila aconchegante de fazenda, apenas como inspiração; nenhuma arte, nome
  ou asset de jogo comercial é usado.
- Nomes de eventos: `vila.*`, `estado.sincronizado`, `operacao.recusada` e `recurso.produzido` são
  mantidos (são da vila como um todo; `recurso.produzido` cobre os dois recursos no mesmo ciclo);
  os eventos de construção passam a `forja.*` porque a única construção da Ferraria é a forja; o
  fluxo próprio usa `encomenda.*`.
