# Quickstart: validar a Vila Ferraria

Guia de execução e validação. Os detalhes de cada evento estão em [contracts/](./contracts/README.md)
e os campos do estado em [data-model.md](./data-model.md).

## Pré-requisitos

- Python 3.10+ e Git; navegador com acesso aos CDNs (unpkg, cdn.socket.io, jsdelivr).
- Na raiz do repositório (`/Users/miguel/Documents/GameFerraria`).

## Subir o servidor

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload          # porta ocupada? --port 8001
```

Abrir `http://localhost:8000` (nunca `file://`). Cada reinício do `--reload` zera a vila:
recarregue as abas e entre de novo.

## Validação manual com abas (fazer antes de cada commit de etapa)

| # | Abas | Passos | Resultado esperado | Etapa |
|---|---|---|---|---|
| M0 | 1 | Entrar como Jogador | Tela, vila desenhada, painel "Nenhum evento ainda", rodapé "Desenvolvido por: Miguel Antonio Selhorst" | 0 |
| M1 | 2 | Entrar nas duas | Ambas: 120 minérios, 0 lingotes, ferreiros 0/2, 0 forjas, fase aguardando; painel com ⬇ on `estado.sincronizado` causa `conexao` (só na aba que acabou de entrar) | 1 |
| M2 | Mestre + Jogador | Mestre: "Abrir temporada" | As duas mudam para aberta sem recarregar; Mestre vê ⬆ emit `vila.abertura_solicitada` + ⬇ on `vila.iniciada`; Jogador só o ⬇ on | 2 |
| M3 | Mestre + Jogador | Abrir; Jogador: "Construir forja" | 80 minérios, ferreiros 1/2, 1 em obra nas duas abas; canteiro na vila; causa `forja.construcao_solicitada` | 3 |
| M4 | Mestre + Jogador | Jogador constrói antes de abrir; depois Mestre abre; Jogador constrói 3× | 1º: "A temporada não está aberta" só no Jogador (vermelho no painel, vila treme); depois 2 obras (40 minérios, 2/2) e a 3ª recusada com "Sem ferreiro livre" só no Jogador; Mestre clica "Abrir" de novo → "A temporada já foi aberta" só no Mestre | 4 |
| M5 | Mestre + Jogador | Abrir, construir 1 forja, só observar 15 s | Cenário **Passagem do tempo** da spec: 90 (5 s), 100 (10 s), `forja.construcao_concluida` aos 12 s (0/2, 1 concluída), 110 minérios + 1 lingote aos 15 s; causas `temporizador` e `forja.construcao_iniciada (temporizador)` | 5 |
| M6 | Mestre + Jogador | Cenário **Recusa** da spec: abrir, construir 2, esperar as duas concluírem (~12 s, 60 minérios), construir 1 (20, 1/2) e logo de novo | "Minério insuficiente" só no Jogador; estoque 20 e 1/2 mantidos | 5 |
| M7 | Mestre + A + B | Cenário **Disputa** da spec: abrir, A constrói 1×, A e B clicam "Construir forja" quase juntos | Um único `forja.construcao_iniciada` (40, 2/2) com o nome do vencedor; só o outro vê "Sem ferreiro livre" | 6 |
| M8 | Mestre + Jogador | Com 1 obra em andamento, Mestre: "Encerrar temporada"; esperar 15 s; Jogador constrói | Todos: encerrada, vila escurece; nenhum `recurso.produzido` nem `forja.construcao_concluida` depois; construir → "A temporada não está aberta" | 6 |
| M9 | 2 | Fazer algumas ações | Etiquetas `nome ×N` no alto do painel crescem a cada evento emitido ou escutado | 7 |
| M10 | Mestre + A + B | Abrir, A constrói 2, esperar lingotes ≥ 3, Mestre publica encomenda, A entrega | `encomenda.publicada` (3 lingotes, 30 s, +40) em todas; `encomenda.cumprida` com nome de A: lingotes −3, minérios +40; Mestre publica de novo e ninguém entrega por 30 s → `encomenda.expirada` causa `encomenda.publicada (temporizador)` | 8 |
| M11 | Mestre + Jogador + nova aba | Com 1 obra e 1 encomenda ativas, abrir uma 3ª aba e entrar | A nova aba recebe só `estado.sincronizado` e desenha a obra e a encomenda (US1 #5) | 8 |

## Validação automática (clientes simulados)

```bash
pip install -r tests/requirements.txt     # python-socketio[asyncio_client] (traz aiohttp)
python tests/cenarios.py                  # todos os cenários (~3 min, tempos reais)
python tests/cenarios.py disputa          # um só cenário
```

O script sobe um `uvicorn server:app` novo por cenário (porta livre), conecta clientes com
`auth={"nome", "papel"}` e falha com mensagem clara se um evento, número, destinatário ou tempo
(± 1 s) divergir da spec.

| Cenário | Cobre | Disponível a partir da etapa |
|---|---|---|
| `sincronizacao` | US1 #1, FR-004/005 | 1 |
| `abertura` | US1 #2 | 2 |
| `recusas_basicas` | US1 #3/#4, US2 #2/#4/#5, SC-003 | 4 |
| `passagem_do_tempo` | cenário "Passagem do tempo", US3 #1–#3, SC-005 | 5 |
| `recusa` | cenário "Recusa" (Minério insuficiente), US2 #3 | 5 |
| `disputa` | cenário "Disputa" ×10, US4, SC-002 | 6 |
| `encerramento` | US5, SC-007 | 6 |
| `encomenda` | US6 #1–#8, US1 #5 | 8 |

Saída esperada: uma linha `OK <cenário>` por cenário e `TODOS OS CENÁRIOS PASSARAM` no fim;
código de saída 0.
