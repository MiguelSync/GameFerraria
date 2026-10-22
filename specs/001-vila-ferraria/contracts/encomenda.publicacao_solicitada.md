# Contrato: `encomenda.publicacao_solicitada`

| Campo | Valor |
|---|---|
| Tipo | Pedido |
| Emite | Mestre (cliente) |
| Recebe | Servidor |
| Causa que carrega | — (é um pedido) |
| Etapa do guia | 8 |
| Spec | FR-013, US6 #1/#5 |
| Teste em `tests/cenarios.py` | `encomenda` |

## Como é emitido / escutado

cliente: `pedir("encomenda.publicacao_solicitada")` em `publicarEncomenda()`; servidor: `@sio.on("encomenda.publicacao_solicitada") async def publicar_encomenda(sid, dados=None)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
(sem dados; quantidade, prazo e recompensa são fixos)
```

## Quando acontece

Clique em "Publicar encomenda". Validação, na ordem:
  1. papel ≠ mestre → "Só o Mestre pode publicar encomendas"
  2. fase ≠ aberta → "A temporada não está aberta"
  3. `encomenda is not None` → "Já existe uma encomenda ativa"
  4. senão → cria a encomenda (novo `id`), emite `encomenda.publicada` e inicia `prazo_encomenda(id)`

## O que muda no estado

O pedido em si não muda nada.

## Reação no cliente

Registro ⬆ emit (azul) no Painel de eventos.
