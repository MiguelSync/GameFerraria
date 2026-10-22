# Contrato: `forja.construcao_iniciada`

| Campo | Valor |
|---|---|
| Tipo | Fato |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `forja.construcao_solicitada` |
| Etapa do guia | 3 |
| Spec | FR-006, US2 #1, US4 #1 |
| Teste em `tests/cenarios.py` | `passagem_do_tempo`, `recusa`, `disputa` |

## Como é emitido / escutado

servidor: `await sio.emit("forja.construcao_iniciada", fato(pedido, por=nome))`, seguido de `sio.start_background_task(obra, nome)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aberta", "minerios": 80, "lingotes": 0, "ferreiros": 1, "limite": 2, "em_obra": 1, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "forja.construcao_solicitada", "por": "<nome do Jogador>" }
```

## Quando acontece

Pedido de forja aceito. Na disputa (US4), só um de dois pedidos simultâneos gera este fato.

## O que muda no estado

`minerios −40`; `ferreiros +1`; `em_obra +1`.

## Reação no cliente

`ouvir("forja.construcao_iniciada", "mostra o canteiro da forja e o -40 minérios", d => { atualizar(d); avisar(d.por + " começou uma forja"); jogo.obraIniciada(d.estado); })`
