# Data Model: Vila Ferraria em Tempo Real

Tudo vive na memória do servidor (`server.py`). O cliente só guarda uma **cópia** do estado,
recebida em cada fato (`atualizar(d)`). Nomes de chave sem acento (ver [research.md](./research.md) R2).

## 1. Vila (estado) — `estado` em `server.py`

| Campo | Tipo | Inicial | Regra / validação | Muda em |
|---|---|---|---|---|
| `fase` | `"aguardando" \| "aberta" \| "encerrada"` | `"aguardando"` | só avança: aguardando → aberta → encerrada (FR-002) | `vila.iniciada`, `vila.encerrada` |
| `minerios` | int ≥ 0 | 120 | nunca negativo; débito só se `minerios >= custo` | `forja.construcao_iniciada` (−40), `recurso.produzido` (+10), `encomenda.cumprida` (+40) |
| `lingotes` | int ≥ 0 | 0 | nunca negativo; entrega só se `lingotes >= 3` | `recurso.produzido` (+`concluidas`), `encomenda.cumprida` (−3) |
| `ferreiros` | int, 0 ≤ x ≤ `limite` | 0 | ocupados agora; nunca passa de `limite` | `forja.construcao_iniciada` (+1), `forja.construcao_concluida` (−1) |
| `limite` | int (constante) | 2 | — | — |
| `em_obra` | int ≥ 0 | 0 | sempre igual a `ferreiros` | `forja.construcao_iniciada` (+1), `forja.construcao_concluida` (−1) |
| `concluidas` | int ≥ 0 | 0 | sem limite | `forja.construcao_concluida` (+1) |
| `custo` | int (constante `CUSTO`) | 40 | minérios por forja | — |
| `tempo_obra` | int (constante `TEMPO_OBRA`) | 12 | segundos | — |
| `intervalo` | int (constante `INTERVALO`) | 5 | segundos entre produções | — |
| `producao` | int (constante) | 10 | minérios por ciclo (a mina não melhora) | — |
| `encomenda` | `Encomenda \| None` | `None` | no máximo uma ativa | `encomenda.publicada` (→ objeto), `encomenda.cumprida` / `encomenda.expirada` / `vila.encerrada` (→ `None`) |

Constantes de módulo: `CUSTO = 40`, `TEMPO_OBRA = 12`, `INTERVALO = 5`,
`ENCOMENDA_QUANTIDADE = 3`, `ENCOMENDA_PRAZO = 30`, `ENCOMENDA_RECOMPENSA = 40`.

**Invariantes** (verificados em `tests/cenarios.py`): `minerios >= 0`, `lingotes >= 0`,
`0 <= ferreiros <= limite`, `ferreiros == em_obra`.

### Transições da fase

```text
aguardando --(vila.abertura_solicitada do Mestre)--> aberta --(vila.encerramento_solicitado do Mestre)--> encerrada
```

Na fase `encerrada`: nenhum temporizador emite fato; todo pedido é recusado (abertura com
"A temporada já foi aberta"; os demais com "A temporada não está aberta", exceto quando o papel já
falha antes).

## 2. Participante — `jogadores[sid]`

| Campo | Tipo | Origem | Regra |
|---|---|---|---|
| `nome` | str | `auth.nome` ao conectar | vazio → `"Anônimo"` |
| `papel` | `"mestre" \| "jogador"` | `auth.papel` ao conectar | qualquer outro valor → `"jogador"` |

Existe só enquanto a aba está conectada (`connect` cria, `disconnect` remove, sem evento).
Pode haver vários Mestres e vários Jogadores.

## 3. Obra de forja — temporizador `obra(nome)`

Não é guardada como objeto: é uma tarefa em segundo plano criada a cada
`forja.construcao_iniciada`, que conhece `nome` (quem pediu). Ocupa 1 ferreiro por `TEMPO_OBRA`
segundos.

```text
iniciada (ferreiros+1, em_obra+1) --12 s, fase aberta--> concluída (ferreiros−1, em_obra−1, concluidas+1)
iniciada --12 s, fase encerrada--> inacabada (nada muda, nada é emitido)
```

## 4. Encomenda — `estado["encomenda"]`

| Campo | Tipo | Valor | Enviado ao cliente? |
|---|---|---|---|
| `id` | int | contador crescente por publicação | sim |
| `quantidade` | int | 3 | sim |
| `prazo` | int (s) | 30 | sim |
| `recompensa` | int (minérios) | 40 | sim |
| `por` | str | nome do Mestre que publicou | sim |
| `expira_em` | float (`time.monotonic()`) | instante da publicação + 30 | **não** (interno) |
| `restante` | int (s) ≥ 0 | calculado no envio: `ceil(expira_em − agora)` | sim (só no envio) |

```text
nenhuma --encomenda.publicada--> ativa --encomenda.cumprida (lingotes−3, minerios+40)--> nenhuma
                                 ativa --30 s, mesmo id, fase aberta--> encomenda.expirada --> nenhuma
                                 ativa --vila.encerrada--> nenhuma (descartada, sem evento próprio)
```

## 5. Evento (payload)

Todo **fato** é montado por `fato(causa, **extras)`:

```json
{ "estado": { ...cópia do estado, com encomenda.restante... }, "causa": "<causa da spec>", "por": "<nome>", "...": "extras" }
```

`operacao.recusada` não leva estado: `{ "motivo": "<texto exato da spec>", "causa": "<nome do pedido>" }`.
Pedidos não levam dados (o servidor sabe quem é pelo `sid`). Detalhe por evento em
[contracts/](./contracts/README.md).

## 6. Cópia do estado no cliente — `estado` (Vue `reactive`)

Mesmas chaves do servidor, com valores neutros até o primeiro `estado.sincronizado`
(`fase: "aguardando"`, números 0, `encomenda: null`). Só é alterada por `atualizar(d)`, chamada
dentro dos `ouvir(...)`.
