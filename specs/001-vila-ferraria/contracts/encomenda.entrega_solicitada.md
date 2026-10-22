# Contrato: `encomenda.entrega_solicitada`

| Campo | Valor |
|---|---|
| Tipo | Pedido |
| Emite | Jogador (cliente) |
| Recebe | Servidor |
| Causa que carrega | — (é um pedido) |
| Etapa do guia | 8 |
| Spec | FR-014, US6 #2/#3/#6/#8 |
| Teste em `tests/cenarios.py` | `encomenda` |

## Como é emitido / escutado

cliente: `pedir("encomenda.entrega_solicitada")` em `entregarEncomenda()`; servidor: `@sio.on("encomenda.entrega_solicitada") async def entregar_encomenda(sid, dados=None)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
(sem dados)
```

## Quando acontece

Clique em "Entregar encomenda". Validação, na ordem, sem `await` entre validar e alterar:
  1. papel ≠ jogador → "Só Jogadores entregam encomendas"
  2. fase ≠ aberta → "A temporada não está aberta"
  3. `encomenda is None` → "Nenhuma encomenda ativa"
  4. `lingotes < 3` → "Lingotes insuficientes"
  5. senão → `lingotes −= 3`, `minerios += 40`, `encomenda = None`, emite `encomenda.cumprida`

## O que muda no estado

O pedido em si não muda nada.

## Reação no cliente

Registro ⬆ emit (azul) no Painel de eventos.
