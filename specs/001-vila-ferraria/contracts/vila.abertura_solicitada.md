# Contrato: `vila.abertura_solicitada`

| Campo | Valor |
|---|---|
| Tipo | Pedido |
| Emite | Mestre (cliente) |
| Recebe | Servidor |
| Causa que carrega | — (é um pedido) |
| Etapa do guia | 2 (recusas visíveis na tela a partir da 4) |
| Spec | FR-003, US1 #2–#4, US5 #6 |
| Teste em `tests/cenarios.py` | `abertura`, `recusas_basicas`, `encerramento` |

## Como é emitido / escutado

cliente: `pedir("vila.abertura_solicitada")` em `abrirVila()`; servidor: `@sio.on("vila.abertura_solicitada") async def abrir_vila(sid, dados=None)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
(sem dados)
```

## Quando acontece

Clique em "Abrir temporada". Validação, na ordem, sem `await` entre validar e alterar:
  1. papel ≠ mestre → `operacao.recusada` "Só o Mestre pode abrir a temporada"
  2. fase ≠ aguardando → `operacao.recusada` "A temporada já foi aberta"
  3. senão → `fase = "aberta"`, inicia `producao()` e emite `vila.iniciada`

## O que muda no estado

O pedido em si não muda nada; se aceito, gera `vila.iniciada`.

## Reação no cliente

Registro ⬆ emit (azul) no Painel de eventos, feito por `pedir`.
