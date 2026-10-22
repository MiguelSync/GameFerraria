# Contrato: `encomenda.publicada`

| Campo | Valor |
|---|---|
| Tipo | Fato |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `encomenda.publicacao_solicitada` |
| Etapa do guia | 8 |
| Spec | FR-013, US6 #1 |
| Teste em `tests/cenarios.py` | `encomenda` |

## Como é emitido / escutado

servidor: `await sio.emit("encomenda.publicada", fato(pedido, por=nome))`, seguido de `sio.start_background_task(prazo_encomenda, id)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aberta", "minerios": 0, "lingotes": 0, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": { "id": 1, "quantidade": 3, "prazo": 30, "recompensa": 40, "por": "<Mestre>", "restante": 30 } }, "causa": "encomenda.publicacao_solicitada", "por": "<nome do Mestre>" }
```

## Quando acontece

Logo depois de aceitar `encomenda.publicacao_solicitada`.

## O que muda no estado

`encomenda`: nenhuma → `{quantidade 3, prazo 30 s, recompensa 40}`.

## Reação no cliente

`ouvir("encomenda.publicada", "mostra o pergaminho da encomenda com o prazo correndo", d => { atualizar(d); avisar("Nova encomenda: 3 lingotes em 30 s (paga 40 minérios)", "ok"); jogo.encomendaPublicada(d.estado); })`
