# Vila em Tempo Real — Ferraria

Trabalho 01 de Linguagem de Programação e Paradigmas (Programação Orientada a Eventos, 2026/2).

Uma vila de ferreiros em tempo real: a mina extrai minério de ferro sozinha, os Jogadores erguem
forjas e cada forja pronta funde lingotes. O Mestre abre e encerra a temporada e publica
encomendas de lingotes com prazo. Todas as abas veem tudo na hora, sem recarregar a página.

A especificação (regras, tabela de eventos e cenários de teste) está em
[`docs/especificacao.md`](docs/especificacao.md) e foi commitada antes do código.

## Integrantes
- Miguel Antonio Selhorst — [@MiguelSync](https://github.com/MiguelSync)

## Linguagem e bibliotecas
- Servidor: Python 3, [python-socketio](https://python-socketio.readthedocs.io/) e uvicorn
- Comunicação em tempo real: Socket.IO
- Tela: Vue 3 (painel e botões) e Phaser 3 (vila desenhada), carregados por CDN
- Mapa: Tiled (`client/assets/vila.json`)

## Como instalar e executar
Pré-requisitos: Python 3 e Git.

```bash
git clone https://github.com/MiguelSync/lpp-trabalho01-miguel.git
cd lpp-trabalho01-miguel
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload
```

Abra **http://localhost:8000** no navegador (não abra o arquivo direto, com `file://`).

O estado da vila fica na memória do servidor: ao reiniciar o servidor, a vila volta ao começo.

## Como testar com duas abas
Abra duas abas lado a lado em http://localhost:8000. Na primeira, digite um nome e clique em
**Entrar como Mestre**; na segunda, **Entrar como Jogador**.

1. **Antes de abrir:** o Jogador clica em **Construir forja** → só na aba dele aparece em vermelho
   "A temporada não está aberta" e a vila treme (✋). O Mestre não recebe nada.
2. **Abrir:** o Mestre clica em **Abrir temporada** → as duas abas mudam para *aberta* e a faixa vira
   "☀️ Temporada aberta". A cada 5 s os minérios sobem +10 sozinhos (`recurso.produzido`, causa
   *temporizador*).
3. **Construir:** o Jogador constrói duas forjas → 40 minérios, ferreiros 2/2 nas duas abas, com o
   canteiro e a barra de progresso. A terceira é recusada com "Sem ferreiro livre" só para ele.
4. **Passagem do tempo:** 12 s depois, cada canteiro vira uma forja com o fogo aceso
   (`forja.construcao_concluida`) e, a partir do ciclo seguinte, cada forja funde +1 lingote.
5. **Encomenda:** o Mestre clica em **Publicar encomenda** → aparece o pergaminho 📜 com o prazo de
   30 s em todas as abas. Com 3 lingotes ou mais, o Jogador clica em **Entregar encomenda** →
   lingotes −3 e minérios +40 para todos. Se ninguém entregar, ela expira sozinha.
6. **Disputa (três abas: Mestre, Jogador A e Jogador B):** com 1 de 2 ferreiros ocupado, A e B
   clicam em **Construir forja** quase ao mesmo tempo → só um consegue (2/2); o outro vê
   "Sem ferreiro livre". Os ferreiros nunca passam do limite.
7. **Encerrar:** o Mestre clica em **Encerrar temporada** → a vila escurece em todas as abas, a
   produção para, obras em andamento ficam inacabadas e qualquer ação é recusada.

Em cada passo, o **Painel de eventos** de cada aba mostra o que ela pediu (⬆ emit, azul) e o que
ela escutou (⬇ on, verde; recusa em vermelho), com horário, causa, dados e a reação do cliente.
Os contadores no topo do painel mostram quantas vezes cada evento ocorreu naquela aba.

### Testes automáticos
Os cenários da especificação (recusa, passagem do tempo e disputa) e os demais fluxos também são
verificados com clientes simulados, que sobem o servidor e conectam Mestre e Jogadores ao mesmo
tempo:

```bash
pip install -r tests/requirements.txt
python tests/cenarios.py              # todos (usa os tempos reais: alguns minutos)
python tests/cenarios.py disputa      # só um cenário
```

## Perguntas

### 1. Quais eventos o seu sistema emite e escuta?
São 15 eventos (tabela completa em [`docs/especificacao.md`](docs/especificacao.md)).

**O cliente emite (pedidos, via `pedir`)** e o servidor escuta (`@sio.on`):
`vila.abertura_solicitada` e `vila.encerramento_solicitado` (Mestre),
`forja.construcao_solicitada` (Jogador), `encomenda.publicacao_solicitada` (Mestre) e
`encomenda.entrega_solicitada` (Jogador).

**O servidor emite (fatos)** e o cliente escuta (via `ouvir`):
- para um cliente só: `estado.sincronizado` (quem acabou de conectar) e `operacao.recusada` (só
  quem fez o pedido recusado);
- para todos: `vila.iniciada`, `forja.construcao_iniciada`, `recurso.produzido`,
  `forja.construcao_concluida`, `vila.encerrada`, `encomenda.publicada`, `encomenda.cumprida` e
  `encomenda.expirada`.

### 2. Como o sistema sabe quando deve atualizar os outros jogadores?
O cliente nunca pergunta nem muda o estado sozinho: ele só pede. O servidor é a fonte da verdade:
quando aceita um pedido, ele altera o estado e **emite um fato para todos** (`sio.emit(...)` sem
`to`), levando o estado novo e a causa. Todas as abas escutam esse fato e redesenham a tela. Quando
o fato só interessa a uma pessoa, o servidor emite com `to=sid` (a recusa, para quem pediu; o
estado inicial, para quem conectou). Fatos também nascem de **temporizadores** no servidor (a
produção da mina, o fim da obra e o prazo da encomenda): eles emitem para todos sem que ninguém
clique.

### 3. Que parte do código mostra claramente o uso do paradigma orientado a eventos?
- `client/index.html`, função `entrar()`, região **ESCUTAS**: cada `ouvir("evento", "reação", ...)`
  registra um handler que reage a um fato do servidor; e as funções `abrirVila()`, `construir()`,
  `publicarEncomenda()`, `entregarEncomenda()` e `encerrarVila()` só fazem `pedir("..._solicitada")`.
- `server.py`, handlers `@sio.on(...)` como `construir`: validam o pedido, recusam com
  `recusar(...)` (evento só para quem pediu) ou alteram o estado e emitem o fato, **sem `await`
  entre validar e alterar**, para que dois pedidos simultâneos sejam decididos um de cada vez.
- `server.py`, temporizadores `producao()`, `obra()` e `prazo_encomenda()`: são fontes de eventos
  (`await sio.sleep(...)` e depois `sio.emit(...)`), com causa `temporizador`.
- `fato(causa, ...)`: todo fato carrega a sua causa, que o Painel de eventos mostra.

## Uso de IA
Usei IA no desenvolvimento, com o fluxo de especificação antes do código:

- **GitHub Spec Kit** (`specify`, via Homebrew) para o fluxo constitution → specify → plan → tasks
  → analyze. Os artefatos estão em `.specify/` e `specs/001-vila-ferraria/` (plano, modelo de dados,
  um contrato por evento e a lista de tarefas por etapa).
- **Claude Code** como orquestrador e para implementar etapa por etapa, com agentes de apoio
  definidos em `.claude/agents/`: redator da especificação, planejador, revisor de eventos e
  testador de cenários.
- **Codex** como revisor independente do código contra a especificação.

O que eu decidi e revisei: o tipo de vila (Ferraria, sorteado) e a proposta de regras e números,
o fluxo próprio (encomenda com prazo), a aprovação da especificação antes de qualquer código, a
revisão de cada etapa antes do commit e os testes com duas e três abas. A IA propôs a primeira
versão da especificação e do código; ajustes apontados na análise (ordem das recusas, quem pediu
cada fato) voltaram primeiro para a especificação e só depois para o código.

## Extras
- **Contadores por evento** no Painel de eventos (obrigatório só para duplas).
- **Recurso refinado:** lingotes, fundidos pelas forjas concluídas.
- **Evento próprio:** encomenda com prazo (`encomenda.*`), com expiração por temporizador.
- **Mapa personalizado** a partir do mapa do kit: toras e hortas trocadas por pedras e tocos de
  pedreira; o ponto `acampamento` virou `mina`.
- **Testes automatizados** com clientes simulados (`tests/cenarios.py`).

## Créditos
- Arte do mapa, peças e sprites: Kit Inicial da disciplina (`client/assets/LEIA-ME.txt`), arte
  original de uso livre nos trabalhos da disciplina.
- Ícones: emojis do sistema.
- Nenhuma arte de jogo comercial foi usada.
