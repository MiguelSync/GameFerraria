# Especificação — Vila em Tempo Real

**Integrante(s):** Miguel Antonio Selhorst — @MiguelSync
**Tipo de vila (sorteio):** Ferraria

> Uma vila de ferreiros: a mina extrai minério de ferro sozinha, os ferreiros erguem forjas e cada
> forja pronta funde lingotes. O Mestre abre e encerra a temporada e publica encomendas de
> lingotes com prazo; os Jogadores constroem forjas e entregam as encomendas.

## 1. Regras da vila

- Recurso primário e recurso refinado: **minério de ferro** (primário, extraído pela mina da vila)
  e **lingotes de ferro** (refinado, fundidos pelas forjas concluídas). A vila começa com
  **120 minérios e 0 lingotes**.
- Custo de uma construção: a única construção é a **forja**, que custa **40 minérios**.
- Tempo da obra: **12 segundos**, contados a partir de `forja.construcao_iniciada`.
- Limite de trabalhadores: **2 ferreiros**. Cada obra ocupa 1 ferreiro do início ao fim.
- Intervalo e quantidade da produção automática: a cada **5 segundos** (o primeiro ciclo 5 s após
  a abertura), a mina produz **+10 minérios** e cada forja concluída produz **+1 lingote**.
- O que muda quando uma obra termina: o ferreiro fica livre, a obra vira forja concluída e, a
  partir do ciclo seguinte, a vila passa a ganhar 1 lingote a mais por ciclo.
- Encomenda (evento próprio): só o Mestre publica; pede **3 lingotes** com prazo de
  **30 segundos** e paga **40 minérios** (o preço de uma forja). Só existe uma encomenda ativa por
  vez. Um Jogador entrega os 3 lingotes de uma só vez; se o prazo acabar antes, ela expira sem
  débito nem pagamento.
- Temporada: aguardando → aberta → encerrada, sem voltar. Só o Mestre abre e encerra. Antes da
  abertura e depois do encerramento, todo pedido de ação é recusado, com o motivo dado pela ordem
  das verificações abaixo.
- Encerramento: a produção para, a encomenda ativa é descartada (não expira depois) e as obras em
  andamento ficam inacabadas (nenhuma termina depois do encerramento).
- Ordem das verificações de cada pedido (a primeira que falhar define o motivo de recusa; as
  demais não são avaliadas):
  - `vila.abertura_solicitada`: é Mestre? ("Só o Mestre pode abrir a temporada") → fase é
    aguardando? ("A temporada já foi aberta", inclusive depois do encerramento).
  - `vila.encerramento_solicitado`: é Mestre? ("Só o Mestre pode encerrar a temporada") → fase é
    aberta? ("A temporada não está aberta").
  - `forja.construcao_solicitada`: é Jogador? ("Só Jogadores constroem forjas") → fase é aberta?
    ("A temporada não está aberta") → há 40 minérios? ("Minério insuficiente") → há ferreiro
    livre? ("Sem ferreiro livre").
  - `encomenda.publicacao_solicitada`: é Mestre? ("Só o Mestre pode publicar encomendas") → fase
    é aberta? ("A temporada não está aberta") → não há encomenda ativa? ("Já existe uma encomenda
    ativa").
  - `encomenda.entrega_solicitada`: é Jogador? ("Só Jogadores entregam encomendas") → fase é
    aberta? ("A temporada não está aberta") → há encomenda ativa? ("Nenhuma encomenda ativa") →
    há 3 lingotes? ("Lingotes insuficientes").
- Consequência da ordem: o papel é sempre verificado antes da fase. Fora da temporada, quem tem o
  papel certo recebe "A temporada não está aberta"; quem tem o papel errado recebe o motivo de
  papel (ex.: o Mestre que pede uma forja depois do encerramento recebe "Só Jogadores constroem
  forjas"). Na abertura, o Mestre que pede de novo recebe "A temporada já foi aberta".
- Consequência dos números: o estoque inicial pagaria 3 forjas, mas só há 2 ferreiros; por isso,
  logo após a abertura, a 3ª forja é recusada por falta de ferreiro com 40 minérios no estoque.

## 2. Eventos

| Evento | Emite | Recebe | O que muda no estado |
|---|---|---|---|
| `estado.sincronizado` | Servidor | Só quem conectou | Nada muda; entrega o estado atual da vila a quem acabou de entrar |
| `vila.abertura_solicitada` | Mestre | Servidor | (é um pedido; nada muda) |
| `vila.iniciada` | Servidor | Todos | Fase: aguardando → aberta; a produção automática começa |
| `forja.construcao_solicitada` | Jogador | Servidor | (é um pedido; nada muda) |
| `forja.construcao_iniciada` | Servidor | Todos | Minérios −40; ferreiros ocupados +1; forjas em obra +1 |
| `operacao.recusada` | Servidor | Só quem pediu | Nada muda; informa o motivo e o pedido recusado |
| `recurso.produzido` | Servidor | Todos | Minérios +10; lingotes +1 por forja concluída |
| `forja.construcao_concluida` | Servidor | Todos | Ferreiros ocupados −1; forjas em obra −1; forjas concluídas +1 |
| `vila.encerramento_solicitado` | Mestre | Servidor | (é um pedido; nada muda) |
| `vila.encerrada` | Servidor | Todos | Fase: aberta → encerrada; produção e prazos param; encomenda ativa descartada; obras em andamento ficam inacabadas |
| `encomenda.publicacao_solicitada` | Mestre | Servidor | (é um pedido; nada muda) |
| `encomenda.publicada` | Servidor | Todos | Encomenda ativa: nenhuma → 3 lingotes, prazo 30 s, recompensa 40 minérios |
| `encomenda.entrega_solicitada` | Jogador | Servidor | (é um pedido; nada muda) |
| `encomenda.cumprida` | Servidor | Todos | Lingotes −3; minérios +40; encomenda ativa → nenhuma |
| `encomenda.expirada` | Servidor | Todos | Encomenda ativa → nenhuma (nada é debitado nem pago) |

Causa que cada fato carrega (aparece no Painel de eventos), junto com o estado atual da vila:

- `estado.sincronizado` → causa `conexao`.
- `vila.iniciada` → causa `vila.abertura_solicitada` + nome do Mestre que pediu.
- `forja.construcao_iniciada` → causa `forja.construcao_solicitada` + nome de quem pediu.
- `operacao.recusada` → causa: o nome do pedido recusado + o motivo.
- `recurso.produzido` → causa `temporizador`.
- `forja.construcao_concluida` → causa `forja.construcao_iniciada (temporizador)` + nome de quem
  pediu a obra.
- `vila.encerrada` → causa `vila.encerramento_solicitado` + nome do Mestre que pediu.
- `encomenda.publicada` → causa `encomenda.publicacao_solicitada` + nome do Mestre que publicou.
- `encomenda.cumprida` → causa `encomenda.entrega_solicitada` + nome de quem entregou.
- `encomenda.expirada` → causa `encomenda.publicada (temporizador)`.

Nomes: pedidos terminam em `_solicitada`/`_solicitado` e fatos usam o verbo no passado. Os eventos
de construção viraram `forja.*` porque a única construção da Ferraria é a forja;
`recurso.produzido` foi mantido porque um mesmo ciclo produz os dois recursos (minério e
lingotes); o fluxo próprio da vila é `encomenda.*`.

## 3. Cenários de teste (Dado / Quando / Então, escritos com eventos)

### Recusa
Dado que a temporada está aberta, há 20 minérios no estoque e 1 de 2 ferreiros ocupado, quando o
Jogador A emite `forja.construcao_solicitada`, então o servidor emite `operacao.recusada` só para A,
com o motivo "Minério insuficiente" e a causa `forja.construcao_solicitada`; o estoque continua em
20 minérios, os ferreiros continuam 1/2, nenhuma obra começa e nenhum outro jogador recebe
`operacao.recusada` nem `forja.construcao_iniciada` (um `recurso.produzido` do temporizador pode
coincidir com o pedido e chega a todos normalmente).

(Como chegar a esse estado: logo após `vila.iniciada`, A pede duas forjas — 40 minérios, 2/2.
Quando as duas recebem `forja.construcao_concluida`, cerca de 12 s depois, o estoque está em 60;
A pede mais uma — 20 minérios, 1/2 — e logo em seguida pede de novo, antes de o estoque voltar a 40.)

### Passagem do tempo
Dado que o Mestre emitiu `vila.abertura_solicitada`, todos receberam `vila.iniciada` (120 minérios,
0 lingotes) e o Jogador A recebeu logo em seguida `forja.construcao_iniciada` (80 minérios,
ferreiros 1/2), quando passam 15 segundos sem nenhum clique, então: aos 5 s e aos 10 s todos
recebem `recurso.produzido` com causa `temporizador` (90 e depois 100 minérios, 0 lingotes); 12 s
depois do início da obra todos recebem `forja.construcao_concluida` com causa `forja.construcao_iniciada (temporizador)`
(ferreiros 0/2, 1 forja concluída); e aos 15 s todos recebem `recurso.produzido` com 110 minérios e
1 lingote.

### Disputa entre dois jogadores
Dado que a temporada está aberta, há 80 minérios e 1 de 2 ferreiros ocupado (A iniciou uma forja
logo após a abertura), quando os jogadores A e B emitem `forja.construcao_solicitada` ao mesmo
tempo, então o servidor trata um pedido de cada vez: emite `forja.construcao_iniciada` para todos,
com causa `forja.construcao_solicitada` e o nome de quem foi atendido primeiro (40 minérios,
ferreiros 2/2), e emite `operacao.recusada` com o motivo "Sem ferreiro livre" apenas para o outro;
os ferreiros nunca passam de 2/2 e o estoque nunca fica negativo.
