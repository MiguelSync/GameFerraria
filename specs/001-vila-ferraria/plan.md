# Implementation Plan: Vila Ferraria em Tempo Real

**Branch**: `001-vila-ferraria` (sem branch git; só o diretório da feature) | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-vila-ferraria/spec.md` (e o entregável `docs/especificacao.md`, coerente com ela)

## Summary

Construir a vila Ferraria em tempo real sobre o Kit Inicial do professor, seguindo o Guia de
Implementação etapa por etapa (Etapas 0 a 8, mais uma Etapa 9 só para o README), com **um commit
por etapa**. O servidor (um único arquivo `server.py`) guarda o estado da vila em memória, valida
cada pedido sem `await` entre validar e alterar, e emite os 15 eventos do catálogo da spec com a
causa de cada fato. Três temporizadores do servidor geram fatos sozinhos: a produção a cada 5 s
(`recurso.produzido`, minérios + lingotes), o fim de cada obra 12 s depois de iniciada
(`forja.construcao_concluida`) e o prazo de 30 s da encomenda (`encomenda.expirada`). A tela
(`client/index.html`) só pede (`pedir`) e reage (`ouvir`), atualizando o painel Vue, a vila
desenhada em Phaser e o Painel de eventos. Os nomes de eventos e os números já nascem conforme a
spec (`forja.*`, 120/40/12 s/2/5 s) em vez de nascerem com os nomes do exemplo do guia
(`construcao.*`, toras) e serem renomeados depois.

## Technical Context

**Language/Version**: Python 3.10+ (servidor) · JavaScript ES2020 no navegador (cliente, sem build)

**Primary Dependencies**: `python-socketio` (AsyncServer, modo ASGI) + `uvicorn` (servidor); Vue 3.5.13,
Socket.IO client 4.7.5 e Phaser 3.90.0 carregados por CDN em `client/index.html` (exatamente as
URLs do kit); mapa Tiled em `client/assets/vila.json`

**Storage**: N/A — estado em memória do processo do servidor; volta ao início a cada reinício

**Testing**: teste manual com 2+ abas (exigido pelo guia em toda etapa) + `tests/cenarios.py`,
script assíncrono com clientes `socketio.AsyncClient` simulados que sobe um servidor novo por
cenário (dependência só de teste: `python-socketio[asyncio_client]`, em `tests/requirements.txt`)

**Target Platform**: navegador desktop moderno abrindo `http://localhost:8000`; servidor local
(macOS/Linux/Windows) com `uvicorn server:app --reload`

**Project Type**: aplicação web em tempo real (servidor de eventos + página única), estrutura plana do kit

**Performance Goals**: todo fato visível em todas as abas em ≤ 1 s (SC-001); produção a cada
5 s ± 1 s e fim de obra 12 s ± 1 s (SC-005); poucas abas simultâneas (2 a 5)

**Constraints**: sem build, sem banco, sem login; nenhum `socket.emit`/`socket.on` direto no
cliente (só `pedir`/`ouvir`); validar e alterar o estado sem `await` no meio; temporizadores com
`await sio.sleep(...)`, nunca `time.sleep(...)`; comentário em todo ponto de emit/on; Painel de
eventos não pode ser removido; nenhuma arte de jogo comercial (só arte do kit editada no Tiled,
emojis/CSS ou pacotes CC0 creditados); português do Brasil em código, comentários e commits

**Scale/Scope**: 1 vila, 1 temporada por execução, 15 eventos, 2 papéis, 1 recurso primário,
1 recurso refinado, 1 construção (forja), 1 fluxo próprio (encomenda); ~250 linhas no servidor

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como o plano cumpre | Situação |
|---|---|---|
| I. Especificação antes do código | `docs/especificacao.md` e `spec.md` já estão commitados (`cbe8676`) antes de qualquer código; plano e tarefas usam os 15 nomes de eventos letra por letra; nenhuma tarefa muda regra sem passar pela spec | ✅ |
| II. Servidor é a única fonte da verdade | Estado só em `server.py`; `atualizar(d)` no cliente só copia `d.estado`; todo handler valida e altera sem `await` no meio (ver [research.md](./research.md) R3); botões escondidos por papel são só conforto visual | ✅ (ver Complexity Tracking: Etapa 3 sem validação, como no guia) |
| III. Pedido separado de fato; recusa é evento | 5 pedidos `*_solicitada/_solicitado` não mudam estado; 9 fatos no passado; `operacao.recusada` sempre com `to=sid`; `estado.sincronizado` com `to=sid`; demais fatos para todos ([contracts/](./contracts/)) | ✅ |
| IV. Temporizadores são fontes de eventos | `producao()`, `obra()` e `prazo_encomenda()` com `await sio.sleep`, iniciados com `sio.start_background_task`; todos checam a fase depois de acordar; cliente nunca pergunta ao servidor | ✅ |
| V. Todo fato carrega a causa | Função `fato(causa, **extras)` monta `{estado, causa, ...}`; causas exatamente as da spec; `por` em todo fato ligado a uma pessoa; painel do kit mostra emit/on, nome, hora, dados, causa e reação; comentário em todo emit/on | ✅ |
| VI. Disciplina de escopo | Só o que a spec pede: 1 fluxo próprio (encomenda), contadores como extra feitos por último (Etapa 7, depois de 0–6), nada de botões/fluxos extras; arte só do kit/emojis/CSS/CC0 creditado | ✅ |
| VII. Um commit por etapa | [tasks.md](./tasks.md) agrupa as tarefas por Etapa 0–9, cada uma com critério de pronto (2+ abas) e mensagem `feat:`/`docs:`; nenhum `git push` sem autorização | ✅ |

**Resultado (pré-pesquisa)**: PASSA. **Reavaliação pós-design (Fase 1)**: PASSA — data model,
contratos e quickstart não introduziram entidade, evento ou dependência fora da spec; a única
dependência nova (`aiohttp`, via `python-socketio[asyncio_client]`) é só dos testes e fica em
`tests/requirements.txt`, fora do `requirements.txt` da aplicação.

## Project Structure

### Documentation (this feature)

```text
specs/001-vila-ferraria/
├── spec.md              # especificação (já commitada; NÃO alterar aqui)
├── plan.md              # este arquivo (/speckit-plan)
├── research.md          # Fase 0: decisões técnicas (R1–R12)
├── data-model.md        # Fase 1: estado da vila, participante, obra, encomenda, evento
├── quickstart.md        # Fase 1: como subir, testar com abas e rodar tests/cenarios.py
├── contracts/           # Fase 1: um contrato por evento (15) + índice
│   ├── README.md
│   ├── estado.sincronizado.md
│   ├── vila.abertura_solicitada.md
│   ├── vila.iniciada.md
│   ├── forja.construcao_solicitada.md
│   ├── forja.construcao_iniciada.md
│   ├── operacao.recusada.md
│   ├── recurso.produzido.md
│   ├── forja.construcao_concluida.md
│   ├── vila.encerramento_solicitado.md
│   ├── vila.encerrada.md
│   ├── encomenda.publicacao_solicitada.md
│   ├── encomenda.publicada.md
│   ├── encomenda.entrega_solicitada.md
│   ├── encomenda.cumprida.md
│   └── encomenda.expirada.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
server.py                  # servidor: estado, fato(), recusar(), handlers on, temporizadores
requirements.txt           # python-socketio, uvicorn (do kit, sem mudança)
client/
├── index.html             # tela: Phaser (vila desenhada) + Vue (painel, botões, avisos, Painel de eventos)
└── assets/
    ├── vila.json          # mapa Tiled (editado na Etapa 8: cara de ferraria, ponto "mina")
    ├── tileset-vila.png   # peças do kit (arte original do kit, uso livre na disciplina)
    ├── sprites-vila.png   # casa (quadro 0) e canteiro (quadro 1) do kit
    └── LEIA-ME.txt        # do kit
docs/
└── especificacao.md       # entregável (já commitado; NÃO alterar no plano)
tests/
├── cenarios.py            # clientes simulados: recusa, passagem do tempo, disputa (+ extras)
└── requirements.txt       # python-socketio[asyncio_client] (só para os testes)
README.md                  # Etapa 9: integrantes, execução, duas abas, 3 perguntas, uso de IA, extras, créditos
.gitignore                 # do kit + entradas já existentes (instruções/, .maestri/, settings.local.json)
```

**Structure Decision**: estrutura plana do Kit Inicial, exigida pelo guia ("Conteúdo: a
estrutura do kit (client/, docs/, server.py, requirements.txt, README.md, .gitignore)"). Um único
`server.py` e um único `client/index.html` mantêm cada emit/on fácil de achar na correção. A
única pasta nova é `tests/`, para os clientes simulados.

## Etapas (resumo; detalhes em [tasks.md](./tasks.md))

| Etapa | Entrega | Eventos novos | Cenário/US coberto | Commit |
|---|---|---|---|---|
| 0 | Kit copiado, `.gitignore`, rodapé com nome | — | servidor sobe, tela abre | `feat: kit inicial e esqueleto do servidor` |
| 1 | Estado da Ferraria + sincronização | `estado.sincronizado` | US1 #1 | `feat: conexão e estado.sincronizado` |
| 2 | Mestre abre a temporada | `vila.abertura_solicitada`, `vila.iniciada` | US1 #2 (#3/#4 já recusados no servidor) | `feat: Mestre abre a temporada (vila.iniciada)` |
| 3 | Pedido e fato de construir (sem validação, como no guia) | `forja.construcao_solicitada`, `forja.construcao_iniciada` | US2 #1 | `feat: construção de forja (forja.construcao_solicitada e forja.construcao_iniciada)` |
| 4 | Validações e recusa só para quem pediu | `operacao.recusada` | US1 #3/#4, US2 #2–#5 | `feat: validações e operacao.recusada` |
| 5 | Temporizadores: produção (minérios + lingotes) e fim de obra | `recurso.produzido`, `forja.construcao_concluida` | US3, cenário "Passagem do tempo", cenário "Recusa" | `feat: produção automática e obra com tempo` |
| 6 | Encerramento + disputa | `vila.encerramento_solicitado`, `vila.encerrada` | US5, US4, cenário "Disputa" | `feat: encerramento da temporada e disputa pelo último ferreiro` |
| 7 | Contadores por evento (extra) | — | US7 | `feat: contadores por evento` |
| 8 | Encomenda com prazo + textos/emojis/visual Ferraria | `encomenda.*` (5) | US6, US1 #5, FR-016/017/023 | `feat: adapta a vila à Ferraria (encomenda com prazo e visual)` |
| 9 | README | — | README/rodapé (critério "README e GitHub") | `docs: README com execução, testes, perguntas e uso de IA` |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Desvio temporário: o commit da Etapa 3 ainda não valida o pedido de forja (o "bug proposital" do guia). Não há validação no cliente, então o princípio II não é contrariado, mas a vila pode ficar negativa nesse único commit | O guia separa "pedido e fato" (Etapa 3) de "recusa" (Etapa 4) e o usuário pediu um commit por etapa do guia; o histórico mostra a evolução que o professor espera ver | Antecipar as validações para a Etapa 3 deixaria a Etapa 4 vazia e misturaria duas etapas num commit; o desvio dura um único commit e a Etapa 4 o corrige antes de qualquer temporizador existir |
