---

description: "Tarefas da Vila Ferraria, agrupadas pelas Etapas 0–9 do guia (uma etapa = um commit)"
---

# Tasks: Vila Ferraria em Tempo Real

**Input**: Design documents from `specs/001-vila-ferraria/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/README.md), [quickstart.md](./quickstart.md)

**Tests**: pedidos explicitamente — `tests/cenarios.py` com clientes simulados para os 3 cenários
da especificação (recusa, passagem do tempo, disputa) e para as demais histórias. Em cada etapa o
teste do cenário é escrito **antes** do código e deve falhar até a etapa ficar pronta.

**Organization**: diferente do modelo padrão do Spec Kit, as fases são as **Etapas do Guia de
Implementação**, porque cada etapa vira exatamente **um commit** (constituição, princípio VII).
Dentro de cada etapa, o rótulo `[USn]` liga a tarefa à história da spec.

**Regras que valem para todas as tarefas** (não repetidas em cada uma):

- Nomes de eventos letra por letra como em [contracts/](./contracts/README.md); payloads e
  validações exatamente como nos contratos.
- Cliente: só `pedir(...)`/`ouvir(...)`, nunca `socket.emit`/`socket.on` direto para eventos da vila.
- Servidor: handlers `async def f(sid, dados=None)`; validar e alterar **sem `await` no meio**;
  temporizadores com `await sio.sleep(...)`, nunca `time.sleep(...)`.
- **Comentário explicando o porquê em todo ponto de emit e de on** (servidor e cliente).
- Painel de eventos do kit nunca é removido. Português do Brasil em tudo.
- Commits são feitos pelo Maestro ("Claude Code #3"), um por etapa, com a mensagem indicada;
  **nunca `git push` sem autorização do usuário**. Antes de cada commit: rodar o agente
  `revisor-eventos` e o `testador-cenarios` (ou `python tests/cenarios.py`) e o roteiro manual
  com 2+ abas do [quickstart.md](./quickstart.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem depender de tarefa incompleta)
- **[Story]**: história da spec (US1…US7) atendida pela tarefa

---

## Etapa 0 — Kit inicial e esqueleto do servidor (Setup)

**Arquivos tocados**: `server.py`, `requirements.txt`, `client/index.html`, `client/assets/*`,
`README.md` (modelo do kit), `.gitignore` · **Eventos**: nenhum

**Pronto quando**: `uvicorn server:app --reload` sobe, `http://localhost:8000` abre a tela de
entrada; ao entrar como Jogador aparece a vila desenhada com "⏳ Aguardando o Mestre", painel
"Nenhum evento ainda" e o rodapé com o nome (roteiro M0 do quickstart).

**Commit**: `feat: kit inicial e esqueleto do servidor`

- [ ] T001 Copiar de `instruções/kit-original/` para a raiz do repositório: `server.py`, `requirements.txt`, `client/index.html`, `client/assets/vila.json`, `client/assets/tileset-vila.png`, `client/assets/sprites-vila.png`, `client/assets/LEIA-ME.txt` e `README.md` (modelo, preenchido na Etapa 9). **NÃO** copiar `instruções/kit-original/docs/especificacao.md` (sobrescreveria o `docs/especificacao.md` já commitado)
- [ ] T002 Mesclar o `.gitignore` do kit no `.gitignore` da raiz: garantir `.venv/`, `__pycache__/`, `*.pyc`, `.DS_Store`, `.idea/`, `.vscode/` e manter as entradas já existentes (`instruções/`, `.claude/settings.local.json`, `.maestri/`); tirar do índice o `.DS_Store` que entrou no commit inicial (`git rm --cached .DS_Store`)
- [ ] T003 Trocar o rodapé de `client/index.html` para `Desenvolvido por: Miguel Antonio Selhorst (@MiguelSync)` (FR-020)
- [ ] T004 Criar `.venv`, `pip install -r requirements.txt`, subir `uvicorn server:app --reload` e executar o roteiro M0 de `specs/001-vila-ferraria/quickstart.md`

**Checkpoint**: servidor no ar e tela aberta, sem nenhum evento.

---

## Etapa 1 — Conectar e sincronizar o estado (US1, base de todas as histórias)

**Arquivos tocados**: `server.py`, `client/index.html`, `tests/cenarios.py`, `tests/requirements.txt`
· **Eventos**: `estado.sincronizado`

**Pronto quando**: duas abas entram e ambas mostram 120 minérios, 0 lingotes, ferreiros 0/2,
0 forjas (0 concluídas, 0 em obra) e fase aguardando; o painel de cada aba mostra ⬇ on
`estado.sincronizado` com `causa: conexao` só uma vez (roteiro M1); `python tests/cenarios.py
sincronizacao` passa. Cobre **US1 #1**, FR-001, FR-004, FR-005.

**Commit**: `feat: conexão e estado.sincronizado`

### Testes (escrever primeiro)

- [ ] T005 [P] [US1] Criar `tests/requirements.txt` com a linha `python-socketio[asyncio_client]` (dependência só de teste; não mexer no `requirements.txt` da aplicação)
- [ ] T006 [P] [US1] Criar a infraestrutura de `tests/cenarios.py` (research R12): `subir_servidor()` que inicia `sys.executable -m uvicorn server:app --port <porta livre>` com `cwd` na raiz, espera a porta aceitar conexão e encerra o processo no fim; classe `Cliente(nome, papel)` com `socketio.AsyncClient`, conexão com `auth={"nome": nome, "papel": papel}`, gravação de todo evento recebido via handler `"*"` como `(nome, dados, time.monotonic())`, e métodos `pedir(evento)`, `esperar(evento, timeout)`, `recebidos(evento)` e `nada_de(evento, janela)`; função `invariantes(estado)` que confere `minerios >= 0`, `lingotes >= 0`, `0 <= ferreiros <= limite` e `ferreiros == em_obra`; registro de cenários por nome e `main` que roda todos (ou só o nome passado em `sys.argv`), imprime `OK <cenário>` por cenário, `TODOS OS CENÁRIOS PASSARAM` no fim e sai com código 1 na primeira falha
- [ ] T007 [US1] Em `tests/cenarios.py`, cenário `sincronizacao`: A (jogador) conecta e recebe exatamente um `estado.sincronizado` com `causa == "conexao"` e estado inicial `{"fase": "aguardando", "minerios": 120, "lingotes": 0, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": None}`; depois B (mestre) conecta, B recebe o seu `estado.sincronizado` e A **não** recebe um segundo (janela de 0,5 s)

### Implementação

- [ ] T008 [US1] Em `server.py`, abaixo do comentário do kit: constantes `CUSTO = 40`, `TEMPO_OBRA = 12`, `INTERVALO = 5`; dicionário `estado` com os campos e valores iniciais de `data-model.md` §1 (`fase`, `minerios`, `lingotes`, `ferreiros`, `limite`, `em_obra`, `concluidas`, `custo`, `tempo_obra`, `intervalo`, `producao`, `encomenda: None`) com comentário em cada campo; `jogadores = {}  # sid -> {"nome", "papel"}`
- [ ] T009 [US1] Em `server.py`, funções `instantaneo()` (cópia do estado, copiando também o dict de `encomenda` quando não for `None` — research R6) e `fato(causa, **extras)` que devolve `{"estado": instantaneo(), "causa": causa, **extras}`, com docstring explicando que todo fato leva o estado e a causa
- [ ] T010 [US1] Em `server.py`, `@sio.event async def connect(sid, environ, auth)`: registra `jogadores[sid] = {"nome": auth.get("nome") or "Anônimo", "papel": "mestre" se auth.get("papel") == "mestre" senão "jogador"}` e emite `estado.sincronizado` com `fato("conexao")` e `to=sid` (contrato `contracts/estado.sincronizado.md`); `@sio.event async def disconnect(sid)`: `jogadores.pop(sid, None)` com comentário "sair não gera evento; obras e encomendas continuam"
- [ ] T011 [US1] Em `client/index.html` (bloco Vue): trocar o `reactive` de `estado` pelas chaves de `data-model.md` §6 (`fase`, `minerios`, `lingotes`, `ferreiros`, `limite`, `em_obra`, `concluidas`, `custo`, `tempo_obra`, `intervalo`, `producao`, `encomenda: null`); trocar a seção `.painel` para mostrar "Minérios: {{ estado.minerios }} (+{{ porMinuto }}/min)", "Lingotes: {{ estado.lingotes }}", "Ferreiros: {{ estado.ferreiros }}/{{ estado.limite }}" com `<progress>`, "Forjas: {{ estado.concluidas }} concluídas, {{ estado.em_obra }} em obra"; texto do botão do Jogador "Construir forja (custo {{ estado.custo }} minérios)"; em `resumir()` trocar a linha de toras por `"minérios " + e.minerios + ", lingotes " + e.lingotes + ", ferreiros " + e.ferreiros + "/" + e.limite`
- [ ] T012 [US1] Em `client/index.html`, região ESCUTAS de `entrar()`: `ouvir("estado.sincronizado", "guarda o estado e desenha a vila como está agora", ...)` chamando `atualizar(d)` e `jogo.mostrarEstado(d.estado)`, com comentário do porquê (só quem conectou recebe)
- [ ] T013 [US1] Validar: `python tests/cenarios.py sincronizacao` e roteiro M1 do `quickstart.md` com 2 abas

**Checkpoint**: US1 #1 funcionando; base para todas as outras histórias.

---

## Etapa 2 — O Mestre abre a temporada (US1)

**Arquivos tocados**: `server.py`, `client/index.html`, `tests/cenarios.py` · **Eventos**:
`vila.abertura_solicitada`, `vila.iniciada` (e `operacao.recusada` já emitida pelo servidor)

**Pronto quando**: Mestre clica "Abrir temporada" e as duas abas (Mestre e Jogador) passam para
aberta e "☀️ Temporada aberta" sem recarregar; o Mestre vê ⬆ emit `vila.abertura_solicitada` e
⬇ on `vila.iniciada` (`causa: vila.abertura_solicitada`); o Jogador vê só o ⬇ on (roteiro M2);
`python tests/cenarios.py abertura` passa. Cobre **US1 #2** (US1 #3/#4 já recusados no servidor,
visíveis na Etapa 4).

**Commit**: `feat: Mestre abre a temporada (vila.iniciada)`

- [ ] T014 [US1] Em `tests/cenarios.py`, cenário `abertura`: Mestre e Jogador conectam; Mestre pede `vila.abertura_solicitada`; ambos recebem exatamente um `vila.iniciada` com `causa == "vila.abertura_solicitada"`, `por` == nome do Mestre e `estado.fase == "aberta"`; os dois recebem o fato em até 1 s depois do pedido (SC-001)
- [ ] T015 [US1] Em `server.py`, `async def recusar(sid, motivo, causa)` que emite `operacao.recusada` com `{"motivo": motivo, "causa": causa}` e `to=sid` (contrato `contracts/operacao.recusada.md`), com comentário "só quem pediu recebe"
- [ ] T016 [US1] Em `server.py`, `@sio.on("vila.abertura_solicitada") async def abrir_vila(sid, dados=None)`: validação na ordem papel ≠ mestre → "Só o Mestre pode abrir a temporada"; fase ≠ aguardando → "A temporada já foi aberta" (via `recusar`); senão `estado["fase"] = "aberta"` (FR-002/FR-003: só avança, só o Mestre) e emite `vila.iniciada` com `fato("vila.abertura_solicitada", por=nome)` para todos (contrato `contracts/vila.iniciada.md`)
- [ ] T017 [US1] Em `client/index.html`: `ouvir("vila.iniciada", "muda a faixa para temporada aberta", ...)` com `atualizar(d)`, `avisar("A temporada começou!", "ok")`, `jogo.vilaIniciada()`; em `abrirVila()`: `pedir("vila.abertura_solicitada")`; comentários do porquê nos dois pontos
- [ ] T018 [US1] Validar: `python tests/cenarios.py sincronizacao abertura` (ou um de cada vez) e roteiro M2 com 2 abas

**Checkpoint**: US1 #1–#2 completas.

---

## Etapa 3 — Pedido e fato: construir forja (US2)

**Arquivos tocados**: `server.py`, `client/index.html` · **Eventos**: `forja.construcao_solicitada`,
`forja.construcao_iniciada`

**Pronto quando**: com a temporada aberta, o Jogador clica "Construir forja" e as duas abas mostram
80 minérios, ferreiros 1/2, 1 em obra e o aviso "<nome> começou uma forja"; aparece o canteiro com
barra de progresso e "-40" subindo; o painel do Jogador mostra ⬆ emit
`forja.construcao_solicitada` e ⬇ on `forja.construcao_iniciada` (`causa:
forja.construcao_solicitada`); o Mestre só o ⬇ on (roteiro M3). Cobre **US2 #1**. Como no guia,
ainda **sem validação** (4 cliques levam a −40 minérios e 4/2 — corrigido na Etapa 4; ver
Complexity Tracking do plano).

**Commit**: `feat: construção de forja (forja.construcao_solicitada e forja.construcao_iniciada)`

- [ ] T019 [US2] Em `server.py`, `@sio.on("forja.construcao_solicitada") async def construir(sid, dados=None)`: `minerios -= CUSTO`, `ferreiros += 1`, `em_obra += 1` e emite `forja.construcao_iniciada` com `fato("forja.construcao_solicitada", por=nome)` para todos (contrato `contracts/forja.construcao_iniciada.md`); comentário "validações entram na Etapa 4"
- [ ] T020 [US2] Em `client/index.html`: `ouvir("forja.construcao_iniciada", "mostra o canteiro da forja e o -40 minérios", ...)` com `atualizar(d)`, `avisar(d.por + " começou uma forja")`, `jogo.obraIniciada(d.estado)`; em `construir()`: `pedir("forja.construcao_solicitada")`; comentários do porquê
- [ ] T021 [US2] Validar o roteiro M3 do `quickstart.md` com Mestre + Jogador; rodar `python tests/cenarios.py sincronizacao abertura` (não pode regredir)

**Checkpoint**: par pedido/fato central funcionando.

---

## Etapa 4 — Recusa: só quem pediu é avisado (US2, US1)

**Arquivos tocados**: `server.py`, `client/index.html`, `tests/cenarios.py` · **Eventos**:
`operacao.recusada` (agora visível na tela)

**Pronto quando**: roteiro M4 — Jogador construindo antes da abertura vê "A temporada não está
aberta" só na sua aba (vermelho no painel, vila treme com ✋); depois da abertura, 2 forjas
(40 minérios, 2/2) e a 3ª recusada com "Sem ferreiro livre" só para ele; Mestre abrindo de novo vê
"A temporada já foi aberta" só para ele; `python tests/cenarios.py recusas_basicas` passa. Cobre
**US1 #3/#4, US2 #2/#4/#5**, FR-006, FR-007, FR-010, SC-003. (US2 #3 "Minério insuficiente" é
coberto pelo cenário `recusa` da Etapa 5, que precisa da passagem do tempo para chegar a
20 minérios com 1/2.)

**Commit**: `feat: validações e operacao.recusada`

- [ ] T022 [US2] Em `tests/cenarios.py`, cenário `recusas_basicas` (Mestre M, Jogador A): (a) A pede `forja.construcao_solicitada` em aguardando → só A recebe `operacao.recusada` `{"motivo": "A temporada não está aberta", "causa": "forja.construcao_solicitada"}` e M não recebe nada em 0,5 s; (b) A pede `vila.abertura_solicitada` → só A recebe "Só o Mestre pode abrir a temporada" e a fase continua aguardando; (c) M abre; M pede `forja.construcao_solicitada` → só M recebe "Só Jogadores constroem forjas"; (d) M pede `vila.abertura_solicitada` de novo → só M recebe "A temporada já foi aberta"; (e) A pede forja 3× seguidas → 2 `forja.construcao_iniciada` (último estado 40 minérios, ferreiros 2/2) e a 3ª vira "Sem ferreiro livre" só para A; `invariantes()` em todo estado recebido
- [ ] T023 [US2] Em `server.py`, reescrever `construir` no molde da Etapa 4 do guia (research R3/R4): `motivo` calculado por `if/elif` na ordem papel ≠ jogador → "Só Jogadores constroem forjas"; fase ≠ aberta → "A temporada não está aberta"; `minerios < CUSTO` → "Minério insuficiente"; `ferreiros >= limite` → "Sem ferreiro livre"; se houver motivo, `await recusar(sid, motivo, pedido)` e `return`; senão altera e emite — **sem nenhum `await` entre a primeira leitura e a última escrita**, com o comentário do guia explicando a disputa
- [ ] T024 [US1] Em `client/index.html`: `ouvir("operacao.recusada", "avisa o motivo e a vila treme", ...)` com `avisar(d.motivo, "erro")` e `jogo.recusado(d.motivo)`, comentário "só quem pediu recebe; nada muda no estado, por isso não chama atualizar"
- [ ] T025 [US2] Validar: `python tests/cenarios.py recusas_basicas` (+ cenários anteriores) e roteiro M4 com 2 abas

**Checkpoint**: recusa como evento, só para quem pediu.

---

## Etapa 5 — A passagem do tempo (US3) — cenários "Passagem do tempo" e "Recusa"

**Arquivos tocados**: `server.py`, `client/index.html`, `tests/cenarios.py` · **Eventos**:
`recurso.produzido` (minérios + lingotes), `forja.construcao_concluida`

**Pronto quando**: roteiro M5 — sem cliques, nas duas abas os minérios sobem +10 a cada 5 s
(`causa: temporizador`); 12 s após o início da obra chega `forja.construcao_concluida` (`causa:
forja.construcao_iniciada (temporizador)`, ferreiros 0/2, 1 concluída), o canteiro vira forja; no
ciclo seguinte +1 lingote (110 minérios e 1 lingote aos 15 s). Roteiro M6 reproduz o cenário
"Recusa" da especificação. `python tests/cenarios.py passagem_do_tempo recusa` passa. Cobre
**US3 #1–#4, US2 #3**, FR-008, FR-009, SC-005, SC-006 e os cenários **Passagem do tempo** e **Recusa** de
`docs/especificacao.md`.

**Commit**: `feat: produção automática e obra com tempo`

- [ ] T026 [P] [US3] Em `tests/cenarios.py`, cenário `passagem_do_tempo` (o da especificação): M abre (t0 = recebimento de `vila.iniciada`), A pede 1 forja logo em seguida (80, 1/2); conferir, em todos os clientes: `recurso.produzido` com `causa == "temporizador"` em t0+5 s ± 1 (90 minérios, 0 lingotes, `ganho_lingotes == 0`) e t0+10 s ± 1 (100); `forja.construcao_concluida` 12 s ± 1 após `forja.construcao_iniciada`, com `causa == "forja.construcao_iniciada (temporizador)"`, `por == "A"`, ferreiros 0, `concluidas == 1`; `recurso.produzido` em t0+15 s ± 1 com 110 minérios e 1 lingote
- [ ] T027 [US3] Em `tests/cenarios.py`, cenário `recusa` (o da especificação): M abre; A pede 2 forjas logo em seguida (40, 2/2); esperar os dois `forja.construcao_concluida` (60 minérios, 0/2); A pede 1 forja (20, 1/2) e logo de novo → só A recebe `operacao.recusada` `{"motivo": "Minério insuficiente", "causa": "forja.construcao_solicitada"}`; o estado continua 20 minérios e 1/2; M não recebe `operacao.recusada` nem um novo `forja.construcao_iniciada` em 0,5 s; em seguida, o próximo `recurso.produzido` traz `ganho_lingotes == 2` (US3 #4: 2 forjas concluídas)
- [ ] T028 [US3] Em `server.py`, `async def producao()` (contrato `contracts/recurso.produzido.md`, research R5): `while estado["fase"] == "aberta"`: `await sio.sleep(INTERVALO)`; se a fase mudou, `break`; `ganho = estado["concluidas"]`; `minerios += producao`; `lingotes += ganho`; emite `recurso.produzido` com `fato("temporizador", ganho_minerios=estado["producao"], ganho_lingotes=ganho)` para todos, mesmo com ganho 0
- [ ] T029 [US3] Em `server.py`, `async def obra(nome)` (contrato `contracts/forja.construcao_concluida.md`): `await sio.sleep(TEMPO_OBRA)`; se fase ≠ aberta, `return` sem emitir (obra inacabada); senão `ferreiros -= 1`, `em_obra -= 1`, `concluidas += 1` (sem mexer em `producao`) e emite `forja.construcao_concluida` com `fato("forja.construcao_iniciada (temporizador)", por=nome)`
- [ ] T030 [US3] Em `server.py`, iniciar os temporizadores: `sio.start_background_task(producao)` em `abrir_vila` logo depois de `fase = "aberta"`; `sio.start_background_task(obra, nome)` em `construir` logo depois do emit de `forja.construcao_iniciada`; comentário "temporizador é fonte de evento"
- [ ] T031 [US3] Em `client/index.html`: `ouvir("recurso.produzido", "atualiza o estoque e mostra +10 minérios (e +N lingotes)", ...)` com `atualizar(d)` e `jogo.recursoProduzido(d.estado, d)`; `ouvir("forja.construcao_concluida", "transforma o canteiro em forja acesa", ...)` com `atualizar(d)`, `avisar("Forja de " + d.por + " pronta! Agora ela funde lingotes.", "ok")` e `jogo.obraConcluida(d.estado)`; no `.painel`, acrescentar "(+{{ lingotesPorMinuto }}/min)" ao lado dos lingotes com `lingotesPorMinuto = concluidas * 60 / intervalo` (computed); comentários do porquê
- [ ] T032 [US3] Validar: `python tests/cenarios.py passagem_do_tempo recusa` (+ anteriores) e roteiros M5 e M6 com 2 abas

**Checkpoint**: temporizadores como fonte de eventos; dois dos três cenários da especificação passam.

---

## Etapa 6 — Encerramento e disputa (US5, US4) — cenário "Disputa"

**Arquivos tocados**: `server.py`, `client/index.html`, `tests/cenarios.py` · **Eventos**:
`vila.encerramento_solicitado`, `vila.encerrada`

**Pronto quando**: roteiro M7 (3 abas: Mestre, A, B) — um único `forja.construcao_iniciada`
(40, 2/2) com o nome de quem foi atendido primeiro e "Sem ferreiro livre" só para o outro; roteiro
M8 — "Encerrar temporada" escurece a vila em todas as abas, o estoque para, a obra em andamento
nunca termina e "Construir forja" é recusado; `python tests/cenarios.py disputa encerramento`
passa (disputa 10× sem falha). Cobre **US4 #1–#2, US5 #1–#6**, FR-011, FR-012, SC-002, SC-006, SC-007 e o
cenário **Disputa** de `docs/especificacao.md`.

**Commit**: `feat: encerramento da temporada e disputa pelo último ferreiro`

- [ ] T033 [P] [US4] Em `tests/cenarios.py`, cenário `disputa` repetido 10 vezes (um servidor novo por repetição): M, A e B conectam; M abre; A pede 1 forja (80, 1/2); A e B pedem `forja.construcao_solicitada` ao mesmo tempo (`asyncio.gather`); conferir que M, A e B recebem cada um exatamente um novo `forja.construcao_iniciada` (40 minérios, ferreiros 2/2, `por` = vencedor), que só o perdedor recebe `operacao.recusada` "Sem ferreiro livre" e que `invariantes()` vale em todos os estados; todos recebem o fato em até 1 s depois dos pedidos (SC-001); imprimir o placar de vencedores (SC-002)
- [ ] T034 [US5] Em `tests/cenarios.py`, cenário `encerramento`: M abre; A pede 1 forja; A pede `vila.encerramento_solicitado` → só A recebe "Só o Mestre pode encerrar a temporada"; M encerra → todos recebem `vila.encerrada` com `causa == "vila.encerramento_solicitado"`, fase encerrada, `em_obra == 1`, `ferreiros == 1`; durante 13 s depois disso nenhum cliente recebe `recurso.produzido` nem `forja.construcao_concluida` (SC-007); A pede forja → "A temporada não está aberta"; M pede abertura → "A temporada já foi aberta"; M pede encerramento de novo → "A temporada não está aberta"; um cliente novo conecta e recebe `estado.sincronizado` com fase encerrada e a obra ainda contada
- [ ] T035 [US5] Em `server.py`, `@sio.on("vila.encerramento_solicitado") async def encerrar_vila(sid, dados=None)` (contrato `contracts/vila.encerramento_solicitado.md`): papel ≠ mestre → "Só o Mestre pode encerrar a temporada"; fase ≠ aberta → "A temporada não está aberta"; senão `fase = "encerrada"` (FR-002/FR-003) e emite `vila.encerrada` com `fato("vila.encerramento_solicitado", por=nome)`; comentário explicando que os temporizadores param sozinhos porque conferem a fase ao acordar
- [ ] T036 [US5] Em `client/index.html`: `ouvir("vila.encerrada", "escurece a vila e passa a mostrar temporada encerrada", ...)` com `atualizar(d)`, `avisar("Temporada encerrada.")`, `jogo.vilaEncerrada()`; em `encerrarVila()`: `pedir("vila.encerramento_solicitado")`; comentários do porquê
- [ ] T037 [US4] Revisar `abrir_vila`, `construir` e `encerrar_vila` em `server.py`: nenhum `await` entre validar e alterar; comentário da disputa presente em `construir` (FR-007)
- [ ] T038 [US4] Validar: `python tests/cenarios.py` (todos até aqui) e roteiros M7 (3 abas) e M8

**Checkpoint**: todo o obrigatório do enunciado funcionando (Etapas 0–6). Os três cenários da
especificação passam.

---

## Etapa 7 — Contadores por evento (US7, extra do trabalho individual)

**Arquivos tocados**: `client/index.html` · **Eventos**: nenhum novo

**Pronto quando**: no alto do Painel de eventos aparecem etiquetas como
`forja.construcao_iniciada ×2` e `vila.iniciada ×1`, que crescem a cada evento emitido ou escutado
naquela aba (roteiro M9). Cobre **US7 #1**, FR-021.

**Commit**: `feat: contadores por evento`

- [ ] T039 [US7] Em `client/index.html`, no `<section class="eventos">`, trocar o comentário `ETAPA 7 (dupla)` por `<div class="contadores"><span v-for="(n, nome) in contadores" class="chip">{{ nome }} ×{{ n }}</span></div>` (os `contadores` já são incrementados por `registrar()` do kit)
- [ ] T040 [US7] Validar o roteiro M9 com 2 abas e rodar `python tests/cenarios.py` (sem regressão)

---

## Etapa 8 — Adaptação à Ferraria: encomenda com prazo e visual (US6, US1 #5, FR-016/017/023)

**Arquivos tocados**: `server.py`, `client/index.html`, `client/assets/vila.json`,
`tests/cenarios.py` · **Eventos**: `encomenda.publicacao_solicitada`, `encomenda.publicada`,
`encomenda.entrega_solicitada`, `encomenda.cumprida`, `encomenda.expirada` (e `vila.encerrada`
passa a descartar a encomenda)

**Pronto quando**: roteiro M10 (Mestre, A, B) — encomenda publicada aparece em todas as abas com
3 lingotes, prazo correndo e recompensa 40; A entrega com lingotes ≥ 3 → `encomenda.cumprida`
(lingotes −3, minérios +40) em todas; nova encomenda não entregue expira sozinha em 30 s com
`causa: encomenda.publicada (temporizador)`; roteiro M11 — aba que entra no meio desenha obra e
encomenda; a vila tem cara de ferraria (mapa editado, emojis 🪨 🧱 ⚒️ 🔥 📜, paleta quente) sem
nenhuma arte de jogo comercial; `python tests/cenarios.py` passa inteiro. Cobre **US6 #1–#8,
US1 #5**, FR-013–FR-017, FR-019, FR-022, FR-023.

**Commit**: `feat: adapta a vila à Ferraria (encomenda com prazo e visual)`

### Testes (escrever primeiro)

- [ ] T041 [P] [US6] Em `tests/cenarios.py`, cenário `encomenda` (M, A, B): M abre; A pede 2 forjas; M publica → todos recebem `encomenda.publicada` com `causa == "encomenda.publicacao_solicitada"` e `estado.encomenda` com `quantidade 3`, `prazo 30`, `recompensa 40`, `restante` entre 29 e 30 (US6 #1); M publica de novo → só M recebe "Já existe uma encomenda ativa" (US6 #5); A entrega com 0 lingotes → só A recebe "Lingotes insuficientes" e nada muda (US6 #3); M pede entrega → "Só Jogadores entregam encomendas"; A pede publicação → "Só o Mestre pode publicar encomendas"; um cliente C conecta e recebe `estado.sincronizado` com `em_obra == 2` e a encomenda ativa com `restante` < 30 (US1 #5); esperar lingotes ≥ 3 (~20 s) e A e B entregam ao mesmo tempo → um único `encomenda.cumprida` (`lingotes` −3, `minerios` +40, `encomenda is None`, `por` = vencedor) e o outro recebe "Nenhuma encomenda ativa" (US6 #2/#6); esperar até 31 s após a publicação → nenhum `encomenda.expirada` (US6 #7); M publica outra e ninguém entrega → `encomenda.expirada` 30 s ± 1 depois, com `causa == "encomenda.publicada (temporizador)"`, minérios/lingotes sem débito nem pagamento além da produção (US6 #4); A entrega → "Nenhuma encomenda ativa" (US6 #8); M publica a terceira e encerra → `vila.encerrada` já com `encomenda is None`, nenhum `encomenda.expirada` em 31 s, e publicar/entregar depois → "A temporada não está aberta" (FR-011/FR-012)

### Servidor

- [ ] T042 [US6] Em `server.py`: constantes `ENCOMENDA_QUANTIDADE = 3`, `ENCOMENDA_PRAZO = 30`, `ENCOMENDA_RECOMPENSA = 40` e contador de ids; ajustar `instantaneo()` para enviar a encomenda sem `expira_em` e com `restante = max(0, ceil(expira_em - time.monotonic()))` (data-model §4, research R7)
- [ ] T043 [US6] Em `server.py`, `@sio.on("encomenda.publicacao_solicitada") async def publicar_encomenda(sid, dados=None)` (contrato `contracts/encomenda.publicacao_solicitada.md`, FR-013): papel ≠ mestre → "Só o Mestre pode publicar encomendas"; fase ≠ aberta → "A temporada não está aberta"; encomenda ativa → "Já existe uma encomenda ativa"; senão cria `{"id", "quantidade", "prazo", "recompensa", "por", "expira_em"}`, emite `encomenda.publicada` com `fato("encomenda.publicacao_solicitada", por=nome)` e inicia `sio.start_background_task(prazo_encomenda, id)`
- [ ] T044 [US6] Em `server.py`, `async def prazo_encomenda(id_encomenda)` (contrato `contracts/encomenda.expirada.md`, FR-015): `await sio.sleep(ENCOMENDA_PRAZO)`; se fase ≠ aberta, ou não há encomenda, ou o `id` é outro → `return` sem emitir; senão `encomenda = None` e emite `encomenda.expirada` com `fato("encomenda.publicada (temporizador)")`
- [ ] T045 [US6] Em `server.py`, `@sio.on("encomenda.entrega_solicitada") async def entregar_encomenda(sid, dados=None)` (contrato `contracts/encomenda.entrega_solicitada.md`, FR-014): papel ≠ jogador → "Só Jogadores entregam encomendas"; fase ≠ aberta → "A temporada não está aberta"; sem encomenda → "Nenhuma encomenda ativa"; `lingotes < quantidade` → "Lingotes insuficientes"; senão, sem `await` no meio, `lingotes -= 3`, `minerios += 40`, `encomenda = None` e emite `encomenda.cumprida` com `fato("encomenda.entrega_solicitada", por=nome)`
- [ ] T046 [US6] Em `server.py`, `encerrar_vila`: `estado["encomenda"] = None` antes do emit de `vila.encerrada`, com comentário "encomenda descartada; o prazo não expira depois" (research R8)

### Cliente (Vue + Phaser)

- [ ] T047 [US6] Em `client/index.html` (Vue): `ouvir` de `encomenda.publicada`, `encomenda.cumprida` e `encomenda.expirada` exatamente como nos contratos (atualizar, avisar, método do `jogo`); funções `publicarEncomenda()` → `pedir("encomenda.publicacao_solicitada")` e `entregarEncomenda()` → `pedir("encomenda.entrega_solicitada")` devolvidas no `return` do `setup`; botões "📜 Publicar encomenda" (Mestre) e "📦 Entregar encomenda (3 🧱)" (Jogador), nunca desabilitados (o servidor recusa); linha no `.painel`: "📜 Encomenda: {{ quantidade }} lingotes · paga {{ recompensa }} minérios · prazo {{ prazo }} s" quando `estado.encomenda`, senão "📜 Encomenda: nenhuma"; em `resumir()`, acrescentar ", encomenda: N lingotes (Rs)" quando `e.encomenda` existir, para o painel mostrar a encomenda nos dados; comentários do porquê
- [ ] T048 [US6] Em `client/index.html` (cena Phaser): métodos `encomendaPublicada(estado)` (pergaminho 📜 num ponto fixo com barra que esvazia em `estado.encomenda.restante * 1000` ms), `encomendaCumprida(estado)` (remove o pergaminho e flutua "+40 🪨"), `encomendaExpirada()` (remove o pergaminho e flutua "⌛ Encomenda expirou"); `mostrarEstado` desenha o pergaminho se `estado.encomenda` (US1 #5); `vilaEncerrada` remove o pergaminho; expor os três no objeto devolvido por `criarJogo()`
- [ ] T049 [US1] Em `client/index.html` (cena Phaser), textos da Ferraria: `obraIniciada` flutua "-40 🪨"; `recursoProduzido(estado, d)` flutua "+10 🪨" e, se `d.ganho_lingotes > 0`, "+N 🧱"; `obraConcluida` flutua "🔥 Forja pronta!"; `criarCasa` desenha o sprite do kit com um "🔥" por cima (forja acesa)
- [ ] T050 [US1] Editar `client/assets/vila.json` no Tiled usando só `tileset-vila.png` do kit (Anexo A do guia): trocar hortas (45/46) por pedras (42) e tocos (43) perto da mina, manter `lote1`…`lote6`, renomear o ponto `acampamento` para `mina`; em `client/index.html`, trocar `pontos.find((p) => p.name === "acampamento")` por `"mina"` (e o nome da propriedade para `this.mina`)
- [ ] T051 [US1] Em `client/index.html`, textos e visual: `<title>` e títulos "⚒️ Vila Ferraria"; rótulos do painel com emojis (🪨 Minérios, 🧱 Lingotes, ⚒️ Ferreiros, 🔥 Forjas, 📜 Encomenda); botão "🔨 Construir forja (custo 40 🪨)"; CSS de paleta quente (fundo creme, bordas marrons, botões cor de brasa), sem remover nem esconder o Painel de eventos; revisar as frases de reação de todos os `ouvir(...)` para que batam com a coluna "O que muda" da spec (FR-018)
- [ ] T052 [US6] Validar: `python tests/cenarios.py` (todos, ~3 min) e roteiros M10 e M11 com 3 abas; conferir, somando os painéis da aba do Mestre e da aba do Jogador (cada aba só vê o que emitiu ou escutou), que os 15 eventos aparecem com nome, hora, dados, causa e reação (SC-004)

**Checkpoint**: vila adaptada à Ferraria, com o fluxo próprio e todos os cenários passando.

---

## Etapa 9 — README e revisão final (polish)

**Arquivos tocados**: `README.md` (e correções pontuais que a revisão apontar) · **Eventos**: nenhum

**Pronto quando**: README com todos os itens exigidos pelo enunciado; auditoria final sem
pendências; `python tests/cenarios.py` passa; roteiro M1–M11 conferido.

**Commit**: `docs: README com execução, testes, perguntas e uso de IA`

- [ ] T053 Preencher `README.md` a partir do modelo do kit: título "Vila em Tempo Real — Ferraria"; **Integrantes**: Miguel Antonio Selhorst — @MiguelSync; **Linguagem e bibliotecas** (Python 3, python-socketio, uvicorn, Vue 3, Socket.IO, Phaser 3, Tiled); **Como instalar e executar** (venv, `pip install -r requirements.txt`, `uvicorn server:app --reload`, `http://localhost:8000`); **Como testar com duas abas** (roteiro resumido do `quickstart.md`, incluindo os 3 cenários da especificação e a disputa com 3 abas) e **testes automáticos** (`pip install -r tests/requirements.txt`, `python tests/cenarios.py`)
- [ ] T054 Em `README.md`, responder as 3 perguntas: (1) lista dos 15 eventos, separando o que o cliente emite (5 pedidos) e escuta (10 fatos, incluindo `operacao.recusada`); (2) o servidor emite o fato para todos (`sio.emit` sem `to`) logo depois de mudar o estado, e só para quem pediu/conectou com `to=sid`; o cliente nunca pergunta, só escuta; (3) apontar `pedir`/`ouvir` e a região ESCUTAS em `client/index.html`, os handlers `@sio.on(...)`, `recusar` e os temporizadores `producao`/`obra`/`prazo_encomenda` em `server.py`; cada resposta deve permitir explicar qualquer evento só com a spec e os contratos (SC-008)
- [ ] T055 Em `README.md`, **Uso de IA**: Claude Code (agentes spec-writer, planejador, revisor-eventos, testador-cenarios) + GitHub Spec Kit (constitution → specify → plan → tasks → analyze → implement) + Codex; dizer o que foi gerado e o que o autor revisou/mudou; **Extras**: contadores por evento (Etapa 7), encomenda com prazo, lingotes como recurso refinado, mapa personalizado no Tiled, testes automatizados; **Créditos**: arte do kit (`client/assets/LEIA-ME.txt`), emojis do sistema, e qualquer pacote CC0 usado (autor, link, licença); nenhuma arte de jogo comercial
- [ ] T056 Auditoria de nomes (FR-022): para cada um dos 15 eventos, `grep` em `docs/especificacao.md`, `server.py` e `client/index.html` confirma a grafia idêntica; nenhum nome do exemplo do guia sobrou (`construcao.solicitada`, `construcao.iniciada`, `construcao.concluida`, `toras`, `trabalhadores`)
- [ ] T057 Auditoria de regras em `server.py` e `client/index.html`: nenhum `time.sleep`; nenhum `socket.emit`/`socket.on` de evento da vila fora de `pedir`/`ouvir` (o `socket.on("connect")` do kit é a única exceção); todo `sio.emit`, `@sio.on`, `@sio.event`, `pedir(` e `ouvir(` com comentário do porquê; Painel de eventos e rodapé presentes (rodar o agente `revisor-eventos`)
- [ ] T058 Rodar `python tests/cenarios.py` completo e o roteiro M1–M11 do `quickstart.md` uma última vez

---

## Dependencies & Execution Order

### Etapas (fases)

- A ordem é **fixa e sequencial**: 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9. Cada etapa depende da
  anterior estar pronta, validada e commitada (um commit por etapa).
- Etapas 0–6 = tudo o que o enunciado exige. A Etapa 7 (extra) só começa depois da 6 passar
  inteira (princípio VI). A Etapa 8 depende da 6 (encerramento descarta a encomenda) e da 5
  (lingotes vêm da produção).
- A Etapa 9 depende de todas.

### Histórias × etapas

| História | Etapas | Depende de |
|---|---|---|
| US1 (entrar e abrir) | 1, 2, 4 (recusas), 8 (#5: entrada com encomenda) | — |
| US2 (construir e recusas) | 3, 4, 5 (#3 Minério insuficiente) | US1 |
| US3 (passagem do tempo) | 5 | US1, US2 |
| US4 (disputa) | 4 (código), 6 (teste) | US2 |
| US5 (encerrar) | 6 | US1, US3 |
| US7 (contadores) | 7 | US1–US5 |
| US6 (encomenda) | 8 | US1, US3, US5 |

### Dentro de cada etapa

- Teste do cenário primeiro (deve falhar) → servidor → cliente → validação manual com 2+ abas →
  revisor → commit.

### Parallel Opportunities

Quase tudo toca `server.py` ou `client/index.html`, então o paralelismo é pequeno e só entre
arquivos diferentes:

- Etapa 1: T005 (`tests/requirements.txt`) ∥ T006 (`tests/cenarios.py`) ∥ T008–T010 (`server.py`).
- Etapa 5: T026 → T027 (mesmo arquivo `tests/cenarios.py`, em sequência) em paralelo com o servidor (T028–T030).
- Etapa 6: T033 → T034 (mesmo arquivo de teste, em sequência) em paralelo com T035 (`server.py`) e T036 (`client/index.html`).
- Etapa 8: T041 (testes) ∥ T042–T046 (`server.py`) ∥ a parte Tiled de T050 (`client/assets/vila.json`); a linha de T050 em `client/index.html` entra na fila do cliente.

## Parallel Example: Etapa 8

```bash
# Em paralelo, arquivos diferentes:
Task: "T041 cenário encomenda em tests/cenarios.py"
Task: "T042–T046 encomenda no server.py"
Task: "T050 (parte Tiled) editar client/assets/vila.json (só tileset do kit)"
# Depois, em sequência no mesmo arquivo client/index.html:
Task: "T047 → T048 → T049 → T051"
```

---

## Implementation Strategy

### MVP (obrigatório do enunciado)

1. Etapas 0–2 → vila sincroniza e abre (US1).
2. Etapas 3–4 → construir com recusa (US2) — primeiro incremento demonstrável do paradigma.
3. Etapa 5 → passagem do tempo (US3) — cenários "Passagem do tempo" e "Recusa".
4. Etapa 6 → encerramento e disputa (US5, US4) — cenário "Disputa". **PARAR e validar**: todo o
   mínimo do enunciado pronto, cada etapa com seu commit.

### Incremental

5. Etapa 7 → contadores (extra individual).
6. Etapa 8 → adaptação Ferraria (obrigatória pelo guia: "um trabalho igual ao exemplo não cumpre o
   escopo"): encomenda + visual.
7. Etapa 9 → README e auditoria final. Push só com autorização do usuário.

## Notes

- Toda mudança de regra, número ou evento descoberta durante a implementação volta primeiro para a
  spec (agente `spec-writer`, commit `docs: ...`), nunca direto no código.
- `tests/cenarios.py` usa tempos reais (5/12/30 s); o conjunto completo leva ~3 min.
- Depois de salvar arquivos com `--reload`, a vila volta ao início: recarregue as abas.
