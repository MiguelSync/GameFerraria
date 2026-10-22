# Contrato: `forja.construcao_concluida`

| Campo | Valor |
|---|---|
| Tipo | Fato (temporizador) |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `forja.construcao_iniciada (temporizador)` |
| Etapa do guia | 5 |
| Spec | FR-008, FR-011, US3 #2, US5 #3, SC-005 |
| Teste em `tests/cenarios.py` | `passagem_do_tempo`, `recusa`, `encerramento` |

## Como é emitido / escutado

servidor: dentro de `obra(nome)`: `await sio.sleep(TEMPO_OBRA)` → se fase ≠ aberta, `return` → altera → `await sio.emit("forja.construcao_concluida", fato("forja.construcao_iniciada (temporizador)", por=nome))`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aberta", "minerios": 100, "lingotes": 0, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 1, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "forja.construcao_iniciada (temporizador)", "por": "<nome de quem pediu a obra>" }
```

## Quando acontece

12 s depois de cada `forja.construcao_iniciada`, se a temporada ainda estiver aberta. Depois de `vila.encerrada`, não sai (obra inacabada).

## O que muda no estado

`ferreiros −1`; `em_obra −1`; `concluidas +1` (a forja passa a render 1 lingote nos ciclos seguintes).

## Reação no cliente

`ouvir("forja.construcao_concluida", "transforma o canteiro em forja acesa", d => { atualizar(d); avisar("Forja de " + d.por + " pronta! Agora ela funde lingotes.", "ok"); jogo.obraConcluida(d.estado); })`
