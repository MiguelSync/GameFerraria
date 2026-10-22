# Research: Vila Ferraria em Tempo Real

Fase 0 do `/speckit-plan`. O Technical Context do [plan.md](./plan.md) não tinha nenhum
"NEEDS CLARIFICATION": a stack é fixa (kit do professor). Esta pesquisa registra as decisões de
desenho que a spec deixa para o plano.

## R1 — Nomes e números nascem conforme a spec

- **Decision**: desde a Etapa 1 o estado usa `minerios`, `lingotes`, `ferreiros`, `limite=2`,
  `custo=40`, `tempo_obra=12`, `intervalo=5`, `producao=10`; desde a Etapa 3 os eventos de
  construção já se chamam `forja.construcao_solicitada` / `forja.construcao_iniciada` /
  `forja.construcao_concluida`. O guia (toras, `construcao.*`, 150/50/8 s) é só referência de
  mecânica.
- **Rationale**: pedido explícito do usuário; evita commits de "renomeação" e o risco de um nome
  antigo sobrar em algum `ouvir`/`emit` (FR-022, princípio I).
- **Alternatives considered**: seguir o guia ao pé da letra e renomear tudo na Etapa 8 —
  rejeitado: gera diffs grandes e nomes divergentes da spec já commitada em 7 commits.

## R2 — Chaves do estado compatíveis com a cena Phaser do kit

- **Decision**: manter as chaves que a cena Phaser do kit lê (`custo`, `producao`, `tempo_obra`,
  `concluidas`, `em_obra`, `fase`) e trocar só as que mudam de significado: `toras` → `minerios`,
  `trabalhadores` → `ferreiros`; acrescentar `lingotes` e `encomenda`.
- **Rationale**: a cena funciona sem alteração nas Etapas 1–7 (só os emojis 🪵 ficam errados até a
  Etapa 8). Chaves sem acento evitam problemas de digitação entre Python e JS.
- **Alternatives considered**: chaves com acento (`minérios`) — rejeitado por fragilidade;
  renomear tudo (`forjas_concluidas`) — rejeitado porque obrigaria mexer na cena já na Etapa 1.

## R3 — Disputa: validar e alterar sem `await` no meio

- **Decision**: cada handler segue o molde da Etapa 4 do guia: calcula `motivo` com uma cadeia
  `if/elif` **na ordem exata do catálogo de motivos da spec**, depois, se não houver motivo, altera
  o estado e só então faz `await sio.emit(...)`. Nenhum `await` entre a primeira leitura do estado
  e a última escrita. Vale para os 5 handlers de pedido.
- **Rationale**: o AsyncServer roda num único laço de eventos; sem ponto de suspensão entre ler e
  escrever, dois pedidos simultâneos são decididos em sequência (FR-007, US4, SC-002, US6 #6).
- **Alternatives considered**: `asyncio.Lock` — desnecessário e esconderia o conceito que o
  professor quer ver; validar no cliente — proibido (princípio II).

## R4 — Ordem das validações inclui o papel

- **Decision**: o primeiro teste de todo pedido é o papel (`jogadores[sid]["papel"]`), como manda o
  catálogo da spec ("não é Jogador → Só Jogadores constroem forjas"), embora o código da Etapa 4
  do guia não verifique papel em `construir`.
- **Rationale**: a spec é a fonte da verdade; US2 #5 e US5 #5 exigem essas recusas.
- **Alternatives considered**: confiar que o botão não aparece para o Mestre — rejeitado (botão é
  só conforto visual).
- **Nota (conflito na spec, reportado ao spec-writer)**: FR-012 e o edge case "Pedido feito …
  depois do encerramento → 'A temporada não está aberta'" parecem valer para qualquer pedido, mas o
  catálogo de motivos verifica o papel antes da fase (ex.: Mestre pedindo forja depois do
  encerramento recebe "Só Jogadores constroem forjas") e US5 #6 dá "A temporada já foi aberta"
  para a abertura. O plano segue o **catálogo** (ordem explícita, "a primeira verificação que
  falhar define o motivo").

## R5 — Temporizadores

- **Decision**: três corrotinas iniciadas com `sio.start_background_task`, todas com
  `await sio.sleep(...)`:
  - `producao()`: iniciada uma vez em `abrir_vila`; laço `while fase == "aberta"`: dorme
    `INTERVALO`, confere de novo a fase, soma `producao` (10) a `minerios` e `concluidas` a `lingotes`,
    emite `recurso.produzido` com `ganho_minerios` e `ganho_lingotes`.
  - `obra(nome)`: uma por forja iniciada; dorme `TEMPO_OBRA`; se a fase não for `aberta`, retorna
    sem emitir (obra fica inacabada); senão `ferreiros -= 1`, `em_obra -= 1`, `concluidas += 1` e
    emite `forja.construcao_concluida` com `por=nome`. **Não** soma 5 à produção como no guia: na
    Ferraria a forja rende lingotes, a mina continua em 10 (Assumptions da spec).
  - `prazo_encomenda(id_encomenda)`: ver R7.
- **Rationale**: FR-008, FR-009, FR-011, FR-015; princípio IV. Como a temporada não reabre
  (FR-002), checar a fase depois de acordar basta para parar todos os temporizadores, sem
  cancelamento explícito de tarefas.
- **Alternatives considered**: guardar e cancelar as tarefas no encerramento — mais código sem
  ganho, já que a fase "encerrada" é terminal.

## R6 — Payload dos fatos e cópia do estado

- **Decision**: `fato(causa, **extras)` devolve `{"estado": instantaneo(), "causa": causa, **extras}`,
  onde `instantaneo()` copia o estado **e** o dicionário aninhado da encomenda (cópia rasa do kit
  não basta, porque `encomenda` é um dict mutável) e calcula `encomenda.restante` (segundos que
  faltam). Fatos ligados a uma pessoa levam `por` (nome de quem pediu). `operacao.recusada` leva só
  `{motivo, causa}` (não muda o estado).
- **Rationale**: FR-019 (todo fato leva o estado completo) e princípio V (fato ligado a uma pessoa
  leva quem pediu). `vila.iniciada`, `vila.encerrada` e `encomenda.publicada` também levam `por`
  (o Mestre): o catálogo da spec não lista o nome nesses três, mas a constituição exige; é um dado
  a mais, não muda nenhum comportamento.
- **Alternatives considered**: `copy.deepcopy(estado)` — equivale, mas não calcula `restante`.

## R7 — Encomenda: um id por publicação e prazo relativo

- **Decision**: `estado["encomenda"]` é `None` ou
  `{"id", "quantidade": 3, "prazo": 30, "recompensa": 40, "por"}` mais o campo interno
  `expira_em` (`time.monotonic() + 30`, não enviado). Ao publicar, um contador global gera `id`;
  `prazo_encomenda(id)` dorme 30 s e só expira se a fase ainda for `aberta` **e** a encomenda ativa
  ainda tiver o mesmo `id`. No envio, `instantaneo()` troca `expira_em` por `restante` (inteiro,
  ≥ 0).
- **Rationale**: US6 #7 (encomenda cumprida não expira depois) e o caso "cumprida e outra
  publicada antes dos 30 s da primeira" — sem `id`, o temporizador antigo expiraria a nova.
  `restante` relativo permite a quem entra no meio (US1 #5) desenhar o prazo certo sem depender
  do relógio do navegador.
- **Alternatives considered**: cancelar a tarefa do prazo ao cumprir — exige guardar a tarefa;
  enviar horário absoluto — depende de relógios sincronizados.

## R8 — Encerramento

- **Decision**: `encerrar_vila` valida (papel → fase), então `fase = "encerrada"` e
  `encomenda = None` (a partir da Etapa 8) antes de emitir `vila.encerrada`. Obras em andamento
  não são tocadas (continuam contadas em `em_obra` e `ferreiros`).
- **Rationale**: FR-011, US5 #3, edge case "Encerramento com encomenda ativa" (o estado enviado já
  não tem encomenda e `encomenda.expirada` nunca sai).

## R9 — Conexão, papel e saída

- **Decision**: `connect(sid, environ, auth)` lê `nome` (padrão "Anônimo") e `papel`; qualquer
  papel diferente de `"mestre"` vira `"jogador"`. `disconnect` só remove o participante, sem
  emitir nada. `estado.sincronizado` vai com `to=sid` e causa `conexao`.
- **Rationale**: FR-001, FR-004, edge case "Pessoa sai → nada é emitido".

## R10 — Cliente: só `pedir`/`ouvir`, botões por papel

- **Decision**: manter as funções do kit (`pedir`, `ouvir`, `registrar`, `atualizar`, `avisar`);
  cada `ouvir` chama `atualizar(d)`, um `avisar` e o método certo de `jogo`. Os botões continuam
  separados por papel como no kit (Mestre: abrir, encerrar, publicar encomenda; Jogador: construir,
  entregar encomenda) e **nunca** são desabilitados por estado — assim, clicar sem minério, sem
  ferreiro, fora da temporada ou sem encomenda mostra a recusa do servidor. As recusas por papel
  (Jogador abrindo, Mestre construindo) são verificadas pelos clientes simulados em
  `tests/cenarios.py`, já que a tela não oferece esses botões ao papel errado.
- **Rationale**: princípio II/III; regra 6 do CLAUDE.md; o painel do kit já distingue pedido
  (`_solicitad[ao]$`), fato e recusa e já conta eventos (`contadores`).
- **Alternatives considered**: mostrar todos os botões a todos os papéis para demonstrar as
  recusas de papel na tela — rejeitado: polui a interface e foge do kit; os testes cobrem.

## R11 — Visual da Ferraria (Etapa 8)

- **Decision**: (a) editar `client/assets/vila.json` no Tiled usando só o `tileset-vila.png` do
  kit — trocar hortas (45/46) por pedras (42) e tocos (43) perto da mina, renomear o ponto
  `acampamento` para `mina` (e ajustar a única linha da cena que o procura); (b) emojis da Ferraria
  em todos os textos flutuantes e no painel: 🪨 minério, 🧱 lingote, ⚒️ ferreiro, 🔥 forja,
  📜 encomenda; a forja concluída é o sprite de casa do kit com um "🔥" por cima; (c) CSS de
  paleta quente (creme/marrom/laranja-brasa) no `index.html`; (d) novos métodos na cena para a
  encomenda (`encomendaPublicada`, `encomendaCumprida`, `encomendaExpirada`) e lingotes no
  `recursoProduzido`. Nenhum pacote de terceiros é obrigatório; se algum CC0 (ex.: Kenney) for
  usado, ele é creditado no README.
- **Rationale**: FR-017, FR-023, princípio VI; clima "vila aconchegante" só como inspiração.
- **Alternatives considered**: tileset de jogo comercial — proibido; desenhar sprites novos do
  zero — fora do escopo ("não precisa criar gráficos do zero").

## R12 — Testes automatizados com clientes simulados

- **Decision**: `tests/cenarios.py`, script `asyncio` sem pytest: para cada cenário sobe um
  `uvicorn server:app` novo numa porta livre (subprocesso), conecta clientes
  `socketio.AsyncClient` com `auth={"nome", "papel"}`, grava cada evento recebido com o horário
  (`time.monotonic()`), e verifica com `assert` os eventos, os números, quem recebeu e os tempos
  (± 1 s). Uso: `python tests/cenarios.py` (todos) ou `python tests/cenarios.py disputa`.
  Cenários: `sincronizacao`, `abertura`, `recusas_basicas`, `passagem_do_tempo`, `recusa`
  (Minério insuficiente, o cenário da especificação), `disputa` (repetida 10×, SC-002),
  `encerramento`, `encomenda`. Dependência só de teste em `tests/requirements.txt`:
  `python-socketio[asyncio_client]`.
- **Rationale**: um servidor novo por cenário porque a temporada não reabre; tempos reais (5/12/30 s)
  porque os números da spec são fixos e não devem virar configuração só para teste. Duração total
  estimada ≈ 3 minutos.
- **Alternatives considered**: pytest + pytest-asyncio — mais dependências; reduzir os tempos por
  variável de ambiente — muda o servidor só por causa do teste.
- **Risco e plano B**: a máquina de desenvolvimento usa Python 3.15; se o `aiohttp` (exigido
  pelo `AsyncClient`) não instalar nessa versão, trocar para `socketio.Client` síncrono
  (`python-socketio[client]`, puro Python) com uma thread por cliente simulado e
  `threading.Barrier` para os pedidos simultâneos da disputa; o resto do desenho não muda.
