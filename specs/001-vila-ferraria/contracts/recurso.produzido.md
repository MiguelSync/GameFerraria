# Contrato: `recurso.produzido`

| Campo | Valor |
|---|---|
| Tipo | Fato (temporizador) |
| Emite | Servidor |
| Recebe | Todos |
| Causa que carrega | `temporizador` |
| Etapa do guia | 5 |
| Spec | FR-009, FR-011, US3 #1/#3/#4, US5 #2, SC-005 |
| Teste em `tests/cenarios.py` | `passagem_do_tempo`, `encerramento` |

## Como é emitido / escutado

servidor: dentro de `producao()`: `await sio.sleep(INTERVALO)` → confere a fase → altera → `await sio.emit("recurso.produzido", fato("temporizador", ganho_minerios=10, ganho_lingotes=n))`

Todo ponto de emit/on recebe um comentário explicando o porquê (regra 9 do CLAUDE.md).

## Payload

```json
{ "estado": { "fase": "aberta", "minerios": 110, "lingotes": 1, "ferreiros": 0, "limite": 2, "em_obra": 0, "concluidas": 1, "custo": 40, "tempo_obra": 12, "intervalo": 5, "producao": 10, "encomenda": null }, "causa": "temporizador", "ganho_minerios": 10, "ganho_lingotes": 1 }
```

## Quando acontece

A cada 5 s enquanto `fase == "aberta"`; o primeiro ciclo 5 s após `vila.iniciada`. Sai mesmo quando `ganho_lingotes` é 0. Nunca sai depois de `vila.encerrada`.

## O que muda no estado

`minerios +10`; `lingotes + concluidas` (1 lingote por forja concluída **antes** deste ciclo).

## Reação no cliente

`ouvir("recurso.produzido", "atualiza o estoque e mostra +10 minérios (e +N lingotes)", d => { atualizar(d); jogo.recursoProduzido(d.estado, d); })`. Pode ser ocultado no painel pela caixa "ocultar recurso.produzido" do kit.
