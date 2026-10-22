# Contrato: cenas por fato (Vue `ouvir` → cena Phaser `jogo.*`)

A tabela "Reação visual por fato" da spec, traduzida para a interface entre o bloco Vue e a cena.
Os nomes de eventos, o que o servidor envia e a ordem `atualizar(d)` → `avisar(...)` → `jogo.*`
**não mudam** (contratos da 001). Mudam só: a **frase de reação** de cada `ouvir` (FR-005, é o que
o Painel mostra em "↪ reação"; cada frase descreve a cena **e** cita o que muda no estado,
porque o guia pede que a reação combine com a coluna "O que muda" da especificação) e os argumentos de `jogo.*` (agora todos recebem `d.estado`,
research R12).

Estas frases substituem a linha "Reação no cliente" dos contratos em
`specs/001-vila-ferraria/contracts/`, que não são editados por esta feature.

## Regras comuns a todas as cenas

- **Só reage**: nenhuma cena muda o estado, emite evento ou mostra uma mudança antes do fato
  (FR-003). Números da tela já mudaram em `atualizar(d)` antes da cena começar (SC-003).
- **Sem fila**: cada elemento tem uma chave de cena; uma cena nova na mesma chave completa a
  anterior na hora (`iniciarCena`) (FR-016).
- **Convergência**: ao fim do método, `conferir(estado)`; divergência ⇒ `reconstruir(estado)`
  sem animação (FR-010, SC-008).
- **Modo simples**: todo elemento é criado por `elemento(tipo, ...)`, que cai para a reserva de
  [assets.md](./assets.md) se a imagem dele falhou (FR-019).
- Durações são máximas (tabela da spec).

## 1. `estado.sincronizado` → `jogo.mostrarEstado(d.estado)`

- **Frase**: "desenha a vila como está agora (nada muda): luz da fase, forjas, obras, ferreiros, pilha e encomenda"
- **Cena**: `reconstruir(estado)` sem animação de entrada: luz da fase (madrugada/dia/noite) e
  lanternas/porta da mina coerentes; `concluidas` forjas distribuídas pelos lotes (`usados % 6`,
  "×N" quando ≥ 2), acesas com brasa e fumaça se a fase for aberta, apagadas se encerrada; depois
  `em_obra` canteiros, cada um com um ferreiro (martelando se aberta, parado se encerrada) e barra
  em modo **"em andamento"** (parada se encerrada); `limite − ferreiros` ferreiros livres nas
  esperas; pilha com `lingotes`; se `encomenda` e fase aberta, pergaminho no quadro com a barra em
  `restante/prazo` esvaziando em `restante` s; faixa da temporada pela fase.
- **Duração**: ≤ 1 s para aparecer (≤ 2 s para quem entra no meio, SC-004).
- **Pode ser chamado de novo** (reconexão do Socket.IO): sempre limpa e redesenha, nunca duplica.

## 2. `vila.iniciada` → `jogo.vilaIniciada(d.estado)`

- **Frase**: "amanhece: a temporada abre, a mina abre e a lanterna apaga"
- **Cena** (chave `luz`): tween da luz madrugada → dia em 1,5 s; faixa "☀️ Temporada aberta";
  lanternas apagam (quadro 14 / brilho some); mina troca para "aberta" (quadro 6).
- **Duração**: ≤ 2 s.

## 3. `forja.construcao_iniciada` → `jogo.obraIniciada(d.estado)`

- **Frase**: "um ferreiro vai ao lote e começa a martelar a forja (−40 minérios, +1 ferreiro ocupado)" (exemplo do FR-005 + o que muda)
- **Cena** (chave `ferreiro<i>`): o primeiro ferreiro livre caminha (`andar`) pela rota
  `espera → saida → (lote.x, saida.y) → lote` em ≤ 3 s até o lote `usados++ % 6`; o lote vira
  canteiro (quadro 0) — na frente da forja, se o lote já tiver uma; ao chegar, `martelar` em laço;
  a barra da obra (modo "exata") começa a encher já no recebimento do fato, em
  `estado.tempo_obra` s, sem passar de cheia; "−40 🪨" sobe da entrada da mina.
- **Estado final**: canteiros = `em_obra`; ferreiros livres = `limite − ferreiros`.
- **Duração**: caminhada ≤ 3 s; barra 12 s.

## 4. `forja.construcao_concluida` → `jogo.obraConcluida(d.estado)`

- **Frase**: "o canteiro mais antigo vira forja acesa e o ferreiro volta livre à mina"
- **Cena** (chaves `ferreiro<i>` e `lote<n>`): `obras.shift()` (FIFO); o canteiro some com um
  "puf" de poeira e a forja acesa aparece no lote (escala 0,3 → 1, `Back.Out`, 400 ms) com `brasa`
  e fumaça subindo da chaminé em laço; a barra some; "🔥 Forja pronta!" flutua; o ferreiro daquela
  obra completa qualquer caminhada em curso e volta (`andar`) pela rota inversa até a sua espera;
  marca "×N" atualizada.
- **Duração**: ≤ 3 s; brasa e fumaça continuam enquanto a fase for aberta.

## 5. `recurso.produzido` → `jogo.recursoProduzido(d.estado, d)`

- **Frase**: "o carrinho sai da mina com +10 minérios; forjas acesas soltam faíscas e a pilha ganha os lingotes"
- **Cena** (chave `carrinho`): o carrinho (quadro 13, cheio) vai da `mina` ao `trilho_fim` em
  1,2 s e volta vazio (quadro 12) em 1,2 s; "+10 🪨" sobe da mina; se `d.ganho_lingotes > 0`, cada
  forja acesa solta uma faísca (quadro 7), "+N lingotes" sobe da pilha e a pilha passa a
  `min(lingotes, 10)` lingotes (número ao lado se > 10).
- **Duração**: ≤ 3 s (termina antes do ciclo seguinte; um ciclo novo completa a cena anterior).

## 6. `operacao.recusada` → `jogo.recusado(d.motivo)` (só na aba que pediu)

- **Frase**: "a vila treme e um balão mostra o motivo; nada muda (só nesta aba)"
- **Cena** (chave `balao`): `cameras.main.shake(300, 0.006)`; balão creme com borda queimada no
  centro-baixo da vila com "✋ " + motivo exato, visível 3,5 s e depois some (um balão novo
  substitui o anterior).
- **Não altera nada desenhado** (FR-014, US4 #2): não mexe em ferreiros, canteiros, pilha nem
  pergaminho; não chama `conferir`.
- **Duração**: tremida ≤ 1,5 s; balão ≥ 3 s.

## 7. `encomenda.publicada` → `jogo.encomendaPublicada(d.estado)`

- **Frase**: "prega no quadro o pergaminho da encomenda (3 lingotes, +40 minérios) com o prazo correndo"
- **Cena** (chave `pergaminho`): pergaminho (quadro 8) desce sobre o quadro e "prega" (escala
  1,3 → 1 em 600 ms); texto "3 lingotes · +40 🪨" (valores de `estado.encomenda`); barra de prazo
  cheia esvaziando em `restante` s.
- **Duração**: pregar ≤ 1,5 s; barra 30 s.

## 8. `encomenda.cumprida` → `jogo.encomendaCumprida(d.estado)`

- **Frase**: "3 lingotes vão da pilha ao quadro, o pergaminho é carimbado e a vila recebe +40 minérios"
- **Cena** (chave `pergaminho`): 3 lingotes (quadro 11) saem da pilha em arco até o quadro
  (800 ms); a pilha passa a `estado.lingotes`; o carimbo (quadro 16) cai sobre o pergaminho e ele
  troca para "carimbado" (quadro 10); depois sobe e some (600 ms); "+40 🪨" aparece no quadro.
- **Duração**: ≤ 3 s.

## 9. `encomenda.expirada` → `jogo.encomendaExpirada(d.estado)`

- **Frase**: "o pergaminho amarela e se desfaz; nada é debitado nem pago"
- **Cena** (chave `pergaminho`): troca para "amarelado" (quadro 9) por 500 ms; some e solta 3
  pedaços (quadros 17–19) que caem girando e desaparecem; "⌛ prazo vencido" flutua; a pilha não
  muda.
- **Duração**: ≤ 2 s.

## 10. `vila.encerrada` → `jogo.vilaEncerrada(d.estado)`

- **Frase**: "anoitece: a temporada fecha, forjas apagam, lanternas acendem e as obras param"
- **Cena** (chave `luz`): tween da luz dia → noite em 2,5 s; faixa "🌙 Temporada encerrada";
  forjas param a `brasa` e trocam para o quadro 4; fumaça e faíscas param; lanternas da vila e da
  mina acendem com brilho; o carrinho para onde estiver (tween pausado); ferreiros em obra param o
  `martelar` e ficam parados (quadro 0) no canteiro; barras das obras pausam onde estavam; o
  pergaminho (se houver) sobe e some, sem cena de expiração; ferreiros caminhando completam o
  trajeto e param.
- **Duração**: ≤ 3 s.

## Resumo para conferência (SC-001)

| # | Fato | Elemento que mais se mexe | Distinta de |
|---|---|---|---|
| 1 | `estado.sincronizado` | vila inteira aparece pronta | todas (sem animação) |
| 2 | `vila.iniciada` | luz (amanhecer) + porta da mina | 10 (direção oposta) |
| 3 | `forja.construcao_iniciada` | ferreiro caminhando + canteiro | 4 |
| 4 | `forja.construcao_concluida` | canteiro → forja acesa + fumaça | 3 |
| 5 | `recurso.produzido` | carrinho no trilho | 8 |
| 6 | `operacao.recusada` | tremida + balão | todas |
| 7 | `encomenda.publicada` | pergaminho pregado | 8, 9 |
| 8 | `encomenda.cumprida` | lingotes voando + carimbo | 9 |
| 9 | `encomenda.expirada` | pergaminho rasgando | 8 |
| 10 | `vila.encerrada` | luz (anoitecer) + forjas apagando | 2 |
