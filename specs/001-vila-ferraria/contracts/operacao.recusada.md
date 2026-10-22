# Contrato: `operacao.recusada`

| Campo | Valor |
|---|---|
| Tipo | Recusa (fato só para quem pediu) |
| Emite | Servidor |
| Recebe | Só quem pediu |
| Causa que carrega | o nome do pedido recusado (um dos 5 `*_solicitada`/`*_solicitado`) |
| Etapa do guia | servidor: 2 · tela: 4 |
| Spec | FR-010, FR-012, US1 #3–#4, US2 #2–#5, US4, US5 #4–#6, US6 #3/#5/#6/#8, SC-003 |
| Teste em `tests/cenarios.py` | `recusas_basicas`, `recusa`, `disputa`, `encerramento`, `encomenda` (sempre conferindo que nenhum outro cliente recebeu) |

## Como é emitido / escutado

servidor: `async def recusar(sid, motivo, causa): await sio.emit("operacao.recusada", {"motivo": motivo, "causa": causa}, to=sid)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "motivo": "Sem ferreiro livre", "causa": "forja.construcao_solicitada" }
```

## Quando acontece

Primeira validação que falha em qualquer um dos 5 pedidos. Motivos exatos (texto da spec): "Só o Mestre pode abrir a temporada", "A temporada já foi aberta", "Só o Mestre pode encerrar a temporada", "A temporada não está aberta", "Só Jogadores constroem forjas", "Minério insuficiente", "Sem ferreiro livre", "Só o Mestre pode publicar encomendas", "Já existe uma encomenda ativa", "Só Jogadores entregam encomendas", "Nenhuma encomenda ativa", "Lingotes insuficientes".

## O que muda no estado

Nada muda (não leva `estado`).

## Reação no cliente

`ouvir("operacao.recusada", "avisa o motivo e a vila treme", d => { avisar(d.motivo, "erro"); jogo.recusado(d.motivo); })`. Aparece em vermelho no painel (classe `recusa` do kit).
