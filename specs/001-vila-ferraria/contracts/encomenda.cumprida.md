# Contrato: `encomenda.cumprida`

| Campo | Valor |
|---|---|
| Tipo | Fato |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `encomenda.entrega_solicitada` |
| Etapa do guia | 8 |
| Spec | FR-014, FR-015, US6 #2/#6/#7 |
| Teste em `tests/cenarios.py` | `encomenda` |

## Como é emitido / escutado

servidor: `await sio.emit("encomenda.cumprida", fato(pedido, por=nome))`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aberta", "minerios": 90, "lingotes": 1, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "encomenda.entrega_solicitada", "por": "<nome do Jogador>" }
```

## Quando acontece

Entrega aceita. Na entrega simultânea (US6 #6), só um dos pedidos gera este fato; o outro recebe "Nenhuma encomenda ativa".

## O que muda no estado

`lingotes −3`; `minerios +40`; `encomenda` → nenhuma. O temporizador do prazo, ao acordar, vê outro `id`/nenhuma e não emite nada.

## Reação no cliente

`ouvir("encomenda.cumprida", "recolhe o pergaminho e mostra +40 minérios", d => { atualizar(d); avisar(d.por + " entregou a encomenda! +40 minérios", "ok"); jogo.encomendaCumprida(d.estado); })`
