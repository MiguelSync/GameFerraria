# Quickstart: validar a identidade visual da Ferraria

Contratos em [contracts/](./contracts/README.md); paleta, assets e estado da cena em
[data-model.md](./data-model.md).

## Pré-requisitos

- `.venv` da 001 ativo (`source .venv/bin/activate`) com `requirements.txt`,
  `tests/requirements.txt` e `tools/requirements.txt` instalados (Pillow já está no `.venv`).
- Navegador com acesso a unpkg, cdn.socket.io, jsdelivr e fonts.googleapis.com.

## 1. Gerar a arte (e conferir que é reproduzível)

```bash
pip install -r tools/requirements.txt
python tools/gerar_arte.py --mapa          # 3 PNGs + vila.json em client/assets/
git diff --exit-code client/assets/        # vazio se a arte commitada é a que o script gera
                                           # (antes do 1º commit dos PNGs: comparar `shasum` antes/depois)
python tools/gerar_arte.py --previa        # opcional: tools/previa.png ampliada para revisar
```

## 2. Regressão e fronteira (em TODA etapa, antes do commit)

```bash
python tests/cenarios.py                   # suíte da 001: tem que terminar em TODOS OS CENÁRIOS PASSARAM
git diff --exit-code 5bbf4f8 -- server.py tests/ docs/especificacao.md specs/001-vila-ferraria
grep -c 'ouvir("' client/index.html        # continua 10 (um por fato)
```

O `git diff` vazio prova FR-001 (nada da 001 mudou). A suíte prova FR-002/SC-002.

## 3. Subir e abrir

```bash
uvicorn server:app --reload
```

Abrir `http://localhost:8000` em **portais do Maestri** (skill `maestri-portal`), cada um
redimensionado para **1280 × 720**: portal A = Mestre, portal B = Jogador A, portal C = Jogador B
(quando pedido). Antes de cada roteiro, reiniciar o servidor (a vila volta ao começo) e recarregar
os portais. Em cada passo marcado 📸, tirar screenshot do portal indicado com o nome
`V<n>-<cena>-<portal>.png` e anexar ao relatório da etapa (screenshots não são commitados).

## 4. Roteiro visual

| # | Etapa | Portais | Passos | Esperado (📸 = screenshot) |
|---|---|---|---|---|
| V1 | 2 | A | Entrar como Mestre antes de abrir | 📸 vila de ferreiros: entrada da mina com trilho e carrinho, pedreira, rua de terra ligando 6 lotes vazios, lagoa, quadro vazio, pilha vazia, luz de madrugada (lanternas acesas a partir da Etapa 4; 2 ferreiros na mina a partir da Etapa 3). Nenhuma peça do kit (casa, horta, toras). (US1 #1–#3) |
| V2 | 2 | A | `ls client/assets/` | só `tileset-ferraria.png`, `sprites16-ferraria.png`, `sprites32-ferraria.png`, `vila.json`, `LEIA-ME.txt` (US1 #2, SC-006) |
| V3 | 3 | A + B | Abrir; B constrói 1 forja | nas duas: 📸 ferreiro sai da mina, caminha pela rua (≤ 3 s), lote 1 vira canteiro com andaime e bigorna, ferreiro martela, barra enchendo, "−40 🪨" na mina; estoque 80 e ferreiros 1/2 no mesmo instante do fato; 1 ferreiro continua na mina (US2 #1, FR-009) |
| V4 | 3 | A + B | Esperar 12 s | barra cheia sem recomeçar; 📸 canteiro vira forja de pedra acesa com brasa e fumaça; ferreiro volta à mina (US2 #2–#3) |
| V5 | 3 | A + B | Esperar os ciclos seguintes | 📸 carrinho sai pelo trilho e volta antes do próximo ciclo; "+10 🪨"; a forja solta faísca e "+1 lingote"; pilha mostra os lingotes atuais (US3 #1–#3) |
| V6 | 3 | A + B + C | B constrói 2 (2/2) e clica uma 3ª vez; C só observa | 📸 só em B: tremida + balão "✋ Sem ferreiro livre" ≥ 3 s; em A e C nada treme; nenhum ferreiro sai (US4 #1–#2, SC-003 da 001) |
| V7 | 3 | A + B | Esperar as 2 obras concluírem | os 2 canteiros viram forjas na ordem em que começaram; os 2 ferreiros voltam (US2 #4) |
| V8 | 3 | A + B | Construir até passar de 6 forjas (~2 min: o minério sobe 10 a cada 5 s; dá para acelerar entregando encomendas) | 📸 7ª obra aparece num lote já usado com "×2" (US2 #5) |
| V9 | 4 | A + B | Na madrugada, Mestre abre | 📸 amanhecer em ≤ 2 s, faixa "aberta", lanterna da mina apaga, porta da mina abre (US5 #1) |
| V10 | 4+5 | A + B, depois C | Aberta com 1 forja pronta, 1 obra em andamento, 4 lingotes e encomenda ativa; abrir C e entrar | 📸 C em ≤ 2 s: dia, 1 forja acesa, 1 canteiro com ferreiro martelando e barra "em andamento", 1 ferreiro livre na mina, pilha com 4, pergaminho com a barra no prazo restante (US5 #3, SC-004) |
| V11 | 4+5 | A + B | Com obra e encomenda ativas, Mestre encerra; depois abrir uma aba nova | 📸 anoitecer ≤ 3 s: forjas apagam, fumaça para, lanternas acendem, ferreiro fica parado no canteiro, barra para, pergaminho sai, carrinho para; a aba nova já abre de noite sem passar pelo anoitecer (US5 #2, #4) |
| V12 | 5 | A + B | Mestre publica; com ≥ 3 lingotes B entrega; publicar de novo e esperar 30 s | 📸 pergaminho pregado com "3 lingotes · +40 🪨" e prazo esvaziando; 📸 lingotes voam da pilha ao quadro, carimbo, pergaminho recolhido, "+40 🪨", pilha −3; 📸 na outra rodada o pergaminho amarela e rasga, pilha igual (US6 #1–#4) |
| V13 | 7 | A + B | Parar o servidor; `mv client/assets/sprites16-ferraria.png /tmp/`; subir; rodar V3–V6 | só ferreiro, carrinho, lingotes, lanternas e pedaços viram emojis/formas; o resto da arte nova continua; 📸 aviso "arte indisponível — modo simples" na vila; Painel e números normais. Devolver o arquivo depois (edge case "só uma imagem falhou") |
| V14 | 7 | A + B + C | Mover os 3 PNGs e o `vila.json` para `/tmp/`; subir; rodar os 3 cenários de `docs/especificacao.md` (recusa, passagem do tempo, disputa) e uma encomenda | 📸 vila em modo simples (chão de formas, emojis), cada um dos 10 fatos com reação visível e números certos; devolver os arquivos e conferir `git status` limpo (US8, SC-005) |
| V15 | 6 | A | Janela 1280 × 720, passar por V3–V12 | 📸 vila, estoque, botões, avisos, Painel (com contadores e cores de pedido/fato/recusa) e rodapé visíveis e sem sobreposição; nomes de eventos legíveis letra por letra na fonte pixel (US7 #1–#3, SC-007) |
| V16 | 4 | A + B | Em B, trocar para outra aba do navegador por 20 s e voltar | B mostra na hora o estado atual, sem reproduzir as cenas perdidas (edge case) |
| V17 | 3 | A + B | Rajada: 2 obras, 3 ciclos e uma encomenda em 20 s | 📸 até 3 s depois do último fato a vila para e bate com os números (SC-008) |

## 5. Conferências finais (Etapa 8)

- **SC-001**: marcar 10/10 na tabela "Resumo para conferência" de [contracts/cenas.md](./contracts/cenas.md).
- **SC-009**: entregar a um observador sem contexto (o usuário ou um agente novo, sem acesso ao
  Painel nem ao código) os 📸 das 10 cenas em ordem aleatória e pedir que diga o que aconteceu em
  cada uma; meta ≥ 8/10.
- **FR-005**: no Painel de cada aba, a "↪ reação" de cada fato é a frase de [contracts/cenas.md](./contracts/cenas.md).
- **SC-006 / FR-020**: cada item de arte e cada fonte aparece nos créditos do README.
