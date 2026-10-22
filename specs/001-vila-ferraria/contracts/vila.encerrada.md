# Contrato: `vila.encerrada`

| Campo | Valor |
|---|---|
| Tipo | Fato |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `vila.encerramento_solicitado` |
| Etapa do guia | 6 (descarte da encomenda: 8) |
| Spec | FR-002, FR-011, FR-012, US5, SC-007 |
| Teste em `tests/cenarios.py` | `encerramento`, `encomenda` |

## Como é emitido / escutado

servidor: `await sio.emit("vila.encerrada", fato(pedido, por=nome))`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "encerrada", "minerios": 0, "lingotes": 0, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "vila.encerramento_solicitado", "por": "<nome do Mestre>" }
```

## Quando acontece

Logo depois de aceitar `vila.encerramento_solicitado`.

## O que muda no estado

`fase`: aberta → encerrada; os temporizadores param de emitir; a encomenda ativa é descartada (`encomenda = None`, sem `encomenda.expirada`); obras em andamento ficam inacabadas (continuam em `em_obra`/`ferreiros`).

## Reação no cliente

`ouvir("vila.encerrada", "escurece a vila e passa a mostrar temporada encerrada", d => { atualizar(d); avisar("Temporada encerrada."); jogo.vilaEncerrada(); })`
