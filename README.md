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
- Arte: pixel art original gerada por `tools/gerar_arte.py` (Python + Pillow, só para desenvolvimento)
- Fontes: Pixelify Sans e VT323 (Google Fonts)

## Como instalar e executar
Pré-requisitos: Python 3 e Git.

```bash
git clone https://github.com/MiguelSync/lpp-trabalho01-miguel.git
cd lpp-trabalho01-miguel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload
```

No Windows, troque as duas primeiras linhas por `py -m venv .venv` e `.venv\Scripts\activate`.

Abra **http://localhost:8000** no navegador (não abra o arquivo direto, com `file://`).

O estado da vila fica na memória do servidor: ao reiniciar o servidor, a vila volta ao começo.

## Como testar com duas abas
Abra duas abas lado a lado em http://localhost:8000. Na primeira, digite um nome e clique em
**Entrar como Mestre**; na segunda, **Entrar como Jogador**.

1. **Antes de abrir:** a vila está de madrugada, com as lanternas acesas e a porta da mina fechada.
   O Jogador clica em **Construir forja** → só na aba dele a vila treme e um balão mostra
   "A temporada não está aberta". O Mestre não recebe nada.
2. **Abrir:** o Mestre clica em **Abrir temporada** → nas duas abas amanhece, as lanternas apagam, a
   mina abre e a fase muda para *aberta*. A cada 5 s o carrinho sai da mina pelo trilho e os
   minérios sobem +10 sozinhos (`recurso.produzido`, causa *temporizador*).
3. **Construir:** o Jogador constrói duas forjas → 40 minérios, ferreiros 2/2 nas duas abas. Um
   ferreiro sai da mina, anda pela rua até o lote e martela no canteiro, com a barra da obra
   enchendo. A terceira é recusada com "Sem ferreiro livre" só para ele.
4. **Passagem do tempo:** 12 s depois, cada canteiro vira uma forja de pedra acesa, com fumaça na
   chaminé (`forja.construcao_concluida`), e o ferreiro volta para a mina. A partir do ciclo
   seguinte, as forjas soltam faíscas e a pilha de lingotes cresce (+1 lingote por forja).
5. **Encomenda:** o Mestre clica em **Publicar encomenda** → um pergaminho é pregado no quadro de
   avisos de todas as abas, com o prazo de 30 s esvaziando. Com 3 lingotes ou mais, o Jogador clica
   em **Entregar encomenda** → três lingotes voam da pilha, o pergaminho é carimbado e a vila recebe
   +40 minérios. Se ninguém entregar, o pergaminho amarela e se desfaz.
6. **Disputa (três abas: Mestre, Jogador A e Jogador B):** com 1 de 2 ferreiros ocupado, A e B
   clicam em **Construir forja** quase ao mesmo tempo → só um consegue (2/2); o outro vê
   "Sem ferreiro livre". Os ferreiros nunca passam do limite.
7. **Encerrar:** o Mestre clica em **Encerrar temporada** → anoitece em todas as abas, as forjas
   apagam, as lanternas acendem, o carrinho e as obras param e qualquer ação é recusada.
8. **Entrar no meio:** abra uma terceira aba a qualquer momento → ela vê a vila exatamente como
   está (forjas, obras, ferreiros, pilha, encomenda e a luz da fase), pelo `estado.sincronizado`.

Em cada passo, o **Painel de eventos** de cada aba mostra o que ela pediu (⬆ emit, azul) e o que
ela escutou (⬇ on, verde; recusa em vermelho), com horário, causa, dados e a reação do cliente.
Os contadores no topo do painel mostram quantas vezes cada evento ocorreu naquela aba.

### Testes automáticos
Os cenários da especificação (recusa, passagem do tempo e disputa) e os demais fluxos também são
verificados com clientes simulados, que sobem o servidor e conectam Mestre e Jogadores ao mesmo
tempo:

```bash
pip install -r tests/requirements.txt
python3 tests/cenarios.py              # todos (usa os tempos reais: alguns minutos)
python3 tests/cenarios.py disputa      # só um cenário
```
(Com o ambiente `.venv` ativado, `python` também funciona; no Windows use `py`.)

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

## Arte da vila (como é gerada)
Toda a arte da vila é **original**, desenhada pixel a pixel por um script do próprio repositório
(paleta de 31 cores, sem imagens de terceiros). O resultado é determinístico: rodar de novo gera os
mesmos arquivos.

```bash
pip install -r tools/requirements.txt   # Pillow, só para desenvolvimento
python3 tools/gerar_arte.py              # tileset e sprites em client/assets/
python3 tools/gerar_arte.py --mapa       # + o mapa client/assets/vila.json (abre no Tiled)
python3 tools/gerar_arte.py --previa     # + tools/previa.png, a folha de contato numerada
```

A vila reage a cada fato do servidor: amanhecer e anoitecer, ferreiros caminhando e martelando,
forjas acesas com fumaça, carrinho de minério no trilho, pilha de lingotes e o quadro de avisos
com o pergaminho da encomenda. Se alguma imagem não carregar, só aquele elemento vira emoji
(modo simples) e o jogo continua. Detalhes em `specs/002-visual-ferraria/`.

## Uso de IA
Usei IA no desenvolvimento, com o fluxo de especificação antes do código:

- **GitHub Spec Kit** (`specify`, via Homebrew) para o fluxo constitution → specify → plan → tasks
  → analyze. Os artefatos estão em `.specify/` e em duas features: `specs/001-vila-ferraria/` (as
  regras e os eventos da vila) e `specs/002-visual-ferraria/` (a identidade visual, só de
  apresentação, sem mudar nenhuma regra ou evento).
- **Claude Code** como orquestrador e para implementar etapa por etapa, com agentes de apoio
  definidos em `.claude/agents/`: redator da especificação, planejador, revisor de eventos e
  testador de cenários.
- **Codex** como revisor independente do código contra a especificação.
- **Arte:** o script `tools/gerar_arte.py`, que desenha toda a pixel art e o mapa, foi escrito com
  ajuda do Claude Code a partir da especificação 002; eu revisei a folha de contato e cada cena na
  vila antes de cada commit.

O que eu decidi e revisei: o tipo de vila (Ferraria, sorteado) e a proposta de regras e números,
o fluxo próprio (encomenda com prazo), a aprovação da especificação antes de qualquer código, a
revisão de cada etapa antes do commit e os testes com duas e três abas. A IA propôs a primeira
versão da especificação e do código; ajustes apontados na análise (ordem das recusas, quem pediu
cada fato) voltaram primeiro para a especificação e só depois para o código.

## Extras
- **Contadores por evento** no Painel de eventos (obrigatório só para duplas).
- **Recurso refinado:** lingotes, fundidos pelas forjas concluídas.
- **Evento próprio:** encomenda com prazo (`encomenda.*`), com expiração por temporizador.
- **Identidade visual própria (feature 002):** pixel art original gerada por script, mapa novo da
  Ferraria (pedreira, mina com trilho, rua, lagoa, quadro de avisos), ferreiros animados, dia e
  noite dirigidos pelos fatos, quadro de encomendas, interface de madeira e pergaminho com fonte
  pixel e modo simples se a arte falhar.
- **Testes automatizados** com clientes simulados (`tests/cenarios.py`).

## Créditos
- Arte da vila (tileset, sprites e mapa): original, criada para este trabalho por Miguel Antonio
  Selhorst com `tools/gerar_arte.py`, licença **CC BY 4.0** (detalhes em `client/assets/LEIA-ME.txt`).
  A arte do Kit Inicial da disciplina foi usada na primeira versão e substituída na feature 002.
- Fontes: [Pixelify Sans](https://fonts.google.com/specimen/Pixelify+Sans) e
  [VT323](https://fonts.google.com/specimen/VT323), via Google Fonts, licença SIL Open Font License.
- Ícones: emojis do sistema.
- Nenhuma arte de jogo comercial foi usada.
