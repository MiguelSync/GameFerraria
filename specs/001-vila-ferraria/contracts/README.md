# Contratos de eventos — Vila Ferraria

Um arquivo por evento do catálogo da spec (15). Nomes **letra por letra** iguais em
`docs/especificacao.md`, `spec.md`, `server.py` e `client/index.html` (FR-022).

Convenções comuns a todos os contratos:

- **Pedido** (`*_solicitada` / `*_solicitado`): o cliente chama `pedir(nome)` (nunca `socket.emit`
  direto); não leva dados; o servidor identifica quem pediu pelo `sid` em `jogadores[sid]`;
  o handler é `@sio.on(nome) async def f(sid, dados=None)` e valida e altera o estado **sem
  `await` no meio**.
- **Fato**: o servidor emite `fato(causa, **extras)` = `{estado, causa, ...}`; vai para todos
  (sem `to`), exceto `estado.sincronizado` (`to=sid`). Fatos ligados a uma pessoa levam `por`.
- **Recusa**: `operacao.recusada` com `{motivo, causa}`, sempre `to=sid` (só quem pediu).
- O cliente escuta com `ouvir(nome, "reação", função)` (nunca `socket.on` direto); toda função
  chama `atualizar(d)` antes de reagir (exceto na recusa, que não traz estado).

| Evento | Tipo | Emite → Recebe | Causa | Etapa |
|---|---|---|---|---|
| [`estado.sincronizado`](./estado.sincronizado.md) | Fato de sincronização | Servidor → Só quem conectou | `conexao` | 1 (desenho da encomenda: 8) |
| [`vila.abertura_solicitada`](./vila.abertura_solicitada.md) | Pedido | Mestre (cliente) → Servidor | — (é um pedido) | 2 (recusas visíveis na tela a partir da 4) |
| [`vila.iniciada`](./vila.iniciada.md) | Fato | Servidor → Todos | `vila.abertura_solicitada` | 2 |
| [`forja.construcao_solicitada`](./forja.construcao_solicitada.md) | Pedido | Jogador (cliente) → Servidor | — (é um pedido) | 3 (sem validação, como no guia) · 4 (validações) |
| [`forja.construcao_iniciada`](./forja.construcao_iniciada.md) | Fato | Servidor → Todos | `forja.construcao_solicitada` | 3 |
| [`operacao.recusada`](./operacao.recusada.md) | Recusa (fato só para quem pediu) | Servidor → Só quem pediu | o nome do pedido recusado (um dos 5 `*_solicitada`/`*_solicitado`) | servidor: 2 · tela: 4 |
| [`recurso.produzido`](./recurso.produzido.md) | Fato (temporizador) | Servidor → Todos | `temporizador` | 5 |
| [`forja.construcao_concluida`](./forja.construcao_concluida.md) | Fato (temporizador) | Servidor → Todos | `forja.construcao_iniciada (temporizador)` | 5 |
| [`vila.encerramento_solicitado`](./vila.encerramento_solicitado.md) | Pedido | Mestre (cliente) → Servidor | — (é um pedido) | 6 |
| [`vila.encerrada`](./vila.encerrada.md) | Fato | Servidor → Todos | `vila.encerramento_solicitado` | 6 (descarte da encomenda: 8) |
| [`encomenda.publicacao_solicitada`](./encomenda.publicacao_solicitada.md) | Pedido | Mestre (cliente) → Servidor | — (é um pedido) | 8 |
| [`encomenda.publicada`](./encomenda.publicada.md) | Fato | Servidor → Todos | `encomenda.publicacao_solicitada` | 8 |
| [`encomenda.entrega_solicitada`](./encomenda.entrega_solicitada.md) | Pedido | Jogador (cliente) → Servidor | — (é um pedido) | 8 |
| [`encomenda.cumprida`](./encomenda.cumprida.md) | Fato | Servidor → Todos | `encomenda.entrega_solicitada` | 8 |
| [`encomenda.expirada`](./encomenda.expirada.md) | Fato (temporizador) | Servidor → Todos | `encomenda.publicada (temporizador)` | 8 |
