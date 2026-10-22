# Contrato: `vila.encerramento_solicitado`

| Campo | Valor |
|---|---|
| Tipo | Pedido |
| Emite | Mestre (cliente) |
| Recebe | Servidor |
| Causa que carrega | — (é um pedido) |
| Etapa do guia | 6 |
| Spec | FR-003, US5 #1/#5 |
| Teste em `tests/cenarios.py` | `encerramento` |

## Como é emitido / escutado

cliente: `pedir("vila.encerramento_solicitado")` em `encerrarVila()`; servidor: `@sio.on("vila.encerramento_solicitado") async def encerrar_vila(sid, dados=None)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
(sem dados)
```

## Quando acontece

Clique em "Encerrar temporada". Validação, na ordem:
  1. papel ≠ mestre → "Só o Mestre pode encerrar a temporada"
  2. fase ≠ aberta → "A temporada não está aberta"
  3. senão → `fase = "encerrada"`, `encomenda = None` (Etapa 8) e emite `vila.encerrada`

## O que muda no estado

O pedido em si não muda nada.

## Reação no cliente

Registro ⬆ emit (azul) no Painel de eventos.
