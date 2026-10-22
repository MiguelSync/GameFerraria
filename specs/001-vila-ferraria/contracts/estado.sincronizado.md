# Contrato: `estado.sincronizado`

| Campo | Valor |
|---|---|
| Tipo | Fato de sincronização |
| Emite | Servidor |
| Recebe | Só quem conectou |
| Causa que carrega | `conexao` |
| Etapa do guia | 1 (desenho da encomenda: 8) |
| Spec | FR-004, FR-005, US1 #1, US1 #5 |
| Teste em `tests/cenarios.py` | `sincronizacao` (só quem conectou recebe; números iniciais), `encomenda` (entrada no meio com encomenda ativa) |

## Como é emitido / escutado

servidor: `await sio.emit("estado.sincronizado", fato("conexao"), to=sid)` dentro de `connect`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aguardando", "minerios": 120, "lingotes": 0, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "conexao" }
```

## Quando acontece

Sempre que uma aba conecta (em qualquer fase), logo depois de registrar `jogadores[sid] = {nome, papel}`. Nunca é recusado.

## O que muda no estado

Nada muda. Entrega o estado completo atual (inclusive obras em andamento, `concluidas` e a encomenda ativa com `restante`).

## Reação no cliente

`ouvir("estado.sincronizado", "guarda o estado e desenha a vila como está agora", d => { atualizar(d); jogo.mostrarEstado(d.estado); })`. A partir da Etapa 8, `mostrarEstado` também desenha a encomenda ativa (US1 #5).
