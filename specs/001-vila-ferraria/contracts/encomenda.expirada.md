# Contrato: `encomenda.expirada`

| Campo | Valor |
|---|---|
| Tipo | Fato (temporizador) |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `encomenda.publicada (temporizador)` |
| Etapa do guia | 8 |
| Spec | FR-015, US6 #4/#7, SC-007 |
| Teste em `tests/cenarios.py` | `encomenda` |

## Como é emitido / escutado

servidor: dentro de `prazo_encomenda(id)`: `await sio.sleep(ENCOMENDA_PRAZO)` → se fase ≠ aberta ou a encomenda ativa não tem esse `id`, `return` → `encomenda = None` → `await sio.emit("encomenda.expirada", fato("encomenda.publicada (temporizador)"))`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aberta", "minerios": 0, "lingotes": 0, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "encomenda.publicada (temporizador)" }
```

## Quando acontece

30 s depois de `encomenda.publicada`, só se a mesma encomenda ainda estiver ativa e a temporada aberta.

## O que muda no estado

`encomenda` → nenhuma; nada é debitado nem pago.

## Reação no cliente

`ouvir("encomenda.expirada", "risca o pergaminho: a encomenda venceu", d => { atualizar(d); avisar("A encomenda expirou.", "erro"); jogo.encomendaExpirada(); })`
