# Contrato: `vila.iniciada`

| Campo | Valor |
|---|---|
| Tipo | Fato |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `vila.abertura_solicitada` |
| Etapa do guia | 2 |
| Spec | FR-002, FR-003, FR-009, US1 #2 |
| Teste em `tests/cenarios.py` | `abertura` |

## Como é emitido / escutado

servidor: `await sio.emit("vila.iniciada", fato(pedido, por=nome))` (sem `to`, vai para todos)

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aberta", "minerios": 120, "lingotes": 0, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "vila.abertura_solicitada", "por": "<nome do Mestre>" }
```

## Quando acontece

Logo depois de aceitar `vila.abertura_solicitada`. O temporizador `producao()` é iniciado no mesmo handler; o primeiro `recurso.produzido` sai 5 s depois.

## O que muda no estado

`fase`: aguardando → aberta; a produção automática começa.

## Reação no cliente

`ouvir("vila.iniciada", "muda a faixa para temporada aberta", d => { atualizar(d); avisar("A temporada começou!", "ok"); jogo.vilaIniciada(); })`
