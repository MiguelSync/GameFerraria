# Contrato: `forja.construcao_solicitada`

| Campo | Valor |
|---|---|
| Tipo | Pedido |
| Emite | Jogador (cliente) |
| Recebe | Servidor |
| Causa que carrega | — (é um pedido) |
| Etapa do guia | 3 (sem validação, como no guia) · 4 (validações) |
| Spec | FR-006, FR-007, US2, US4 |
| Teste em `tests/cenarios.py` | `recusas_basicas`, `recusa`, `disputa`, `encerramento` |

## Como é emitido / escutado

cliente: `pedir("forja.construcao_solicitada")` em `construir()`; servidor: `@sio.on("forja.construcao_solicitada") async def construir(sid, dados=None)`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
(sem dados)
```

## Quando acontece

Clique em "Construir forja". Validação, na ordem, sem `await` entre validar e alterar (a partir da Etapa 4):
  1. papel ≠ jogador → "Só Jogadores constroem forjas"
  2. fase ≠ aberta → "A temporada não está aberta"
  3. `minerios < 40` → "Minério insuficiente"
  4. `ferreiros >= limite` (2) → "Sem ferreiro livre"
  5. senão → `minerios −= 40`, `ferreiros += 1`, `em_obra += 1`, emite `forja.construcao_iniciada` e inicia `obra(nome)`

## O que muda no estado

O pedido em si não muda nada.

## Reação no cliente

Registro ⬆ emit (azul) no Painel de eventos.
