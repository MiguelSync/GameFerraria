# Implementation Plan: Identidade Visual da Vila Ferraria

**Branch**: `002-visual-ferraria` (sem branch git; só o diretório da feature) | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-visual-ferraria/spec.md`

## Summary

Trocar a apresentação da vila desenhada pela de uma **vila de ferreiros em pixel art original**,
gerada por um script versionado (`tools/gerar_arte.py`, Python + Pillow) que desenha tileset,
spritesheets e o mapa Tiled a partir de matrizes e de uma paleta no próprio código. A cena Phaser
de `client/index.html` é reescrita para reagir aos **10 fatos** que a aba escuta com cenas curtas
(ferreiro caminha e martela, forja acende com brasa e fumaça, carrinho sai da mina, pilha de
lingotes cresce, pergaminho no quadro, amanhecer/anoitecer), **sem fila de cenas** e sempre
convergindo para o estado do último fato. Dia e noite são dirigidos só pelos fatos
(`estado.sincronizado`, `vila.iniciada`, `vila.encerrada`). Cada elemento cai para formas/emojis
se a sua imagem não carregar (modo simples). A interface Vue ganha painéis de madeira/pergaminho e
fonte pixel (Google Fonts, OFL), sem esconder o Painel de eventos.

**Fronteira:** `server.py`, `tests/cenarios.py`, `docs/especificacao.md`, `specs/001-*` e
`specs/002-*/spec.md` **não mudam**. Nenhum nome de evento, dado enviado, causa ou número muda; as
únicas mudanças no bloco Vue são as frases de reação (FR-005), os argumentos passados a `jogo.*`
(o `d.estado` que já chega em cada fato) e o CSS/HTML da interface.

## Technical Context

**Language/Version**: Python 3 (script de arte; o `.venv` usa 3.15) · JavaScript ES2020 no navegador (sem build)

**Primary Dependencies**: Pillow (só desenvolvimento, `tools/requirements.txt`; já instalado no
`.venv`); no cliente, as mesmas CDNs da 001 (Vue 3.5.13, Socket.IO 4.7.5, Phaser 3.90.0) + Google
Fonts (Pixelify Sans e VT323, OFL) por `<link>`

**Storage**: N/A — PNGs e `vila.json` versionados em `client/assets/`; nenhum dado novo no servidor

**Testing**: regressão automática `python tests/cenarios.py` (suíte da 001, intocada) +
`git diff --exit-code 5bbf4f8 -- server.py tests/` (fronteira) + determinismo do script
(`python tools/gerar_arte.py --mapa && git diff --exit-code client/assets/`) + roteiro visual manual
V1–V14 em 2–3 abas (portais do Maestri) com screenshots, descrito em [quickstart.md](./quickstart.md)

**Target Platform**: navegador desktop, janela a partir de 1280 × 720 (SC-007); sem celular, sem som

**Project Type**: aplicação web em tempo real (só o cliente muda) + script de geração de arte

**Performance Goals**: números da tela em ≤ 1 s após cada fato (SC-003); vila de quem entra no
meio pronta em ≤ 2 s (SC-004); cenas dentro das durações da tabela da spec; vila parada e batendo
com o estado ≤ 3 s depois do último fato de uma rajada (SC-008)

**Constraints**: a cena só lê o estado recebido (nunca decide, muda estado nem emite); nenhum
relógio do cliente decide fase; nada de fila de cenas; `pedir`/`ouvir` continuam os únicos pontos
de emit/on; comentários do porquê nos `ouvir` mantidos; Painel de eventos, contadores, avisos,
botões por papel e rodapé intactos; arte 100% original (nenhuma peça do kit nem de jogo
comercial no cenário); grade de 16 px, `pixelArt: true`

**Scale/Scope**: 3 PNGs + 1 mapa gerados; mapa 24 × 12 peças; 2 ferreiros; 6 lotes; 10 cenas;
1 script (~500 linhas); a cena Phaser cresce de ~170 para ~600 linhas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.* (constituição 1.0.1)

| Princípio | Como o plano cumpre | Situação |
|---|---|---|
| I. Especificação antes do código | spec 002 commitada (`5bbf4f8`) antes de qualquer código da 002; os 15 nomes de eventos não mudam; nenhuma regra nova | ✅ |
| II. Servidor é a única fonte da verdade | `server.py` intocado; a cena só desenha `d.estado` recebido; animações são decoração e convergem para o último estado (research R5) | ✅ |
| III. Pedido separado de fato; recusa é evento | pedidos continuam sem cena (só o Painel os mostra); a recusa só tem cena na aba que a recebeu (FR-014) | ✅ |
| IV. Temporizadores do servidor são fontes de eventos | dia/noite, fim de obra e prazo vêm só dos fatos; tweens do cliente só animam (barras e caminhadas) e nunca decidem fase nem disparam reação de outro fato | ✅ |
| V. Todo fato carrega a causa, visível no Painel | Painel intocado (só aparência); frases de reação atualizadas para a nova cena (FR-005); comentários do porquê em todo `ouvir`/`pedir` mantidos | ✅ |
| VI. Disciplina de escopo | extra visual feito depois de a 001 estar completa e listado no README; arte ORIGINAL gerada por script versionado com autoria, licença livre e uso de IA declarados (emenda 1.0.1); fontes OFL creditadas; nenhuma arte do kit nem de jogo comercial; nenhum fluxo, evento ou botão novo | ✅ |
| VII. Um commit por etapa | [tasks.md](./tasks.md) em 8 etapas, uma por commit (`feat:`/`docs:`), cada uma validada com 2–3 abas + regressão; nenhum push sem autorização | ✅ |

**Resultado (pré-pesquisa)**: PASSA. **Reavaliação pós-design**: PASSA — o desenho não exige
nenhuma mudança de servidor nem de dado enviado; o único dado que a cena passa a receber a mais é
o `d.estado` que todo fato já traz.

## Project Structure

### Documentation (this feature)

```text
specs/002-visual-ferraria/
├── spec.md              # especificação (commitada; NÃO alterar)
├── plan.md              # este arquivo
├── research.md          # decisões R1–R14
├── data-model.md        # paleta, inventário de assets, pontos do mapa, estado interno da cena
├── quickstart.md        # gerar arte, regressão, roteiro visual V1–V14 com screenshots
├── contracts/
│   ├── README.md        # índice
│   ├── assets.md        # contrato script → cena: arquivos, tamanhos, quadros, animações
│   ├── mapa.md          # contrato vila.json: camadas, tileset, pontos
│   └── cenas.md         # contrato Vue → cena: 10 fatos (método, argumentos, frase, cena, duração, estado final, modo simples)
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
tools/
├── gerar_arte.py          # NOVO: desenha tileset, spritesheets e (com --mapa) o vila.json
└── requirements.txt       # NOVO: Pillow (só desenvolvimento)
client/
├── index.html             # cena Phaser reescrita; CSS/HTML da interface; frases de reação; fontes
└── assets/
    ├── tileset-ferraria.png   # NOVO (gerado): peças 16×16
    ├── sprites16-ferraria.png # NOVO (gerado): quadros 16×16
    ├── sprites32-ferraria.png # NOVO (gerado): quadros 32×32
    ├── vila.json              # REESCRITO (gerado com --mapa; editável no Tiled)
    ├── LEIA-ME.txt            # REESCRITO: lista de peças/quadros e como gerar de novo
    ├── tileset-vila.png       # REMOVIDO (arte do kit)
    └── sprites-vila.png       # REMOVIDO (arte do kit)
README.md                  # Etapa 8: extras, créditos, geração da arte, uso de IA
server.py, tests/          # INTOCADOS (fronteira da 002)
```

**Structure Decision**: estrutura plana do kit mantida; a única pasta nova é `tools/` para o
script de arte, que não é servido pelo servidor (o `static_files` só expõe `client/`).

## Etapas (resumo; detalhes em [tasks.md](./tasks.md))

| Etapa | Entrega | Fatos cobertos | Commit |
|---|---|---|---|
| 1 | Script de arte + PNGs gerados (ainda não usados pela cena) | — | `feat: script de arte original da Ferraria e assets gerados` |
| 2 | Mapa novo gerado (24×12, pontos novos), cena carrega a arte nova, arte do kit removida, fábrica de elementos com reserva | `estado.sincronizado` (cenário estático) + as reações da 001 portadas para os sprites novos | `feat: mapa da Ferraria gerado por script e arte do kit removida` |
| 3 | Ferreiros, canteiro, forja acesa, carrinho, pilha, recusa; cenas sem fila e convergência | `forja.construcao_iniciada`, `forja.construcao_concluida`, `recurso.produzido`, `operacao.recusada` | `feat: ferreiros, forjas e carrinho reagem aos fatos de obra, produção e recusa` |
| 4 | Luz de madrugada/dia/noite, lanternas, porta da mina, sincronização completa, aba em segundo plano | `estado.sincronizado`, `vila.iniciada`, `vila.encerrada` | `feat: dia e noite pelos fatos e vila sincronizada para quem entra no meio` |
| 5 | Quadro de encomendas: pergaminho, prazo, carimbo, rasgo | `encomenda.publicada`, `encomenda.cumprida`, `encomenda.expirada` (+ retirada em `vila.encerrada` e no sync) | `feat: quadro de encomendas com pergaminho, carimbo e prazo` |
| 6 | Interface de vila (madeira/pergaminho), fontes pixel, layout 1280×720 | todos (só aparência) | `feat: interface de vila com fonte pixel e painéis de madeira` |
| 7 | Modo simples completo (falha por asset, mapa reserva, aviso) | os 10, em modo simples | `feat: modo simples quando a arte não carrega` |
| 8 | README (extras, créditos, como gerar a arte, uso de IA) e auditoria final | — | `docs: README com a identidade visual, créditos e geração da arte` |

## Complexity Tracking

Nenhuma violação da constituição. Uma escolha que merece registro:

| Escolha | Por quê | Alternativa simples rejeitada porque |
|---|---|---|
| Fábrica de elementos com reserva (emoji/forma) já na Etapa 2, antes do modo simples (Etapa 7) | Toda cena das Etapas 3–5 já nasce criando seus elementos pela mesma função; a Etapa 7 só acrescenta a detecção de falha, o mapa reserva e o aviso | Fazer o modo simples só no fim obrigaria reabrir cada cena das Etapas 3–5 e misturaria etapas num commit |
