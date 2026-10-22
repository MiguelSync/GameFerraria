<!--
Sync Impact Report
- Versão: (modelo sem versão) → 1.0.0 (primeira ratificação; todos os princípios são novos)
- Princípios definidos:
  - [PRINCIPLE_1] → I. Especificação antes do código (NÃO NEGOCIÁVEL)
  - [PRINCIPLE_2] → II. Servidor é a única fonte da verdade, um evento por vez
  - [PRINCIPLE_3] → III. Pedido separado de fato; a recusa também é um evento
  - [PRINCIPLE_4] → IV. Temporizadores do servidor são fontes de eventos
  - [PRINCIPLE_5] → V. Todo fato carrega a sua causa, visível no Painel de eventos
  - (novo)        → VI. Disciplina de escopo
  - (novo)        → VII. Um commit por etapa
- Seções adicionadas: "Restrições do trabalho", "Fluxo de desenvolvimento", "Governança"
- Seções removidas: nenhuma
- Templates (.specify/templates/*): lidos em tempo de execução; nenhum alterado por este comando
  ✅ plan-template.md (o "Constitution Check" deve verificar os princípios I–VII)
  ✅ spec-template.md (sem mudança necessária)
  ✅ tasks-template.md (as tarefas devem ser agrupadas por etapa do guia, ver princípio VII)
- TODOs adiados: nenhum
-->

# Vila em Tempo Real — Ferraria Constitution

## Core Principles

### I. Especificação antes do código (NÃO NEGOCIÁVEL)

- Todo comportamento novo ou alterado MUST nascer primeiro na especificação (`docs/especificacao.md`
  e `specs/`) e só depois virar código.
- `docs/especificacao.md` MUST ser commitado antes de qualquer arquivo de código do projeto.
  Especificação commitada depois do código perde os 2,0 pontos do critério "Especificação".
- A especificação MUST ser escrita na linguagem da vila e MUST NOT citar tecnologia
  (linguagem, biblioteca, protocolo, servidor web). "Servidor", "Mestre", "Jogador" e "Todos"
  são papéis e podem ser citados.
- Os nomes de eventos definidos na especificação são a fonte da verdade: servidor, tela e
  README MUST usá-los letra por letra.

Justificativa: o enunciado avalia a especificação feita antes do código e exige que cada membro
saiba explicar qualquer evento (quem emite, quem escuta e o que muda).

### II. Servidor é a única fonte da verdade, um evento por vez

- O estado da vila (estoques, ferreiros, forjas, fase da temporada, encomenda) MUST existir
  apenas no servidor. O cliente MUST NOT alterar o estado por conta própria: ele só muda a tela
  quando recebe um fato do servidor.
- O servidor MUST tratar um evento por vez. A validação de um pedido e a alteração do estado
  correspondente MUST acontecer sem nenhuma pausa ou espera entre os dois passos, para que dois
  pedidos simultâneos sejam decididos em sequência (um vence, o outro é recusado).
- Toda validação MUST acontecer no servidor; esconder ou desabilitar botões na tela é apenas
  conforto visual e nunca substitui a validação.

Justificativa: vários jogadores pedem ao mesmo tempo; só um árbitro central garante que todos
vejam a mesma vila e que a disputa pelo último recurso ou trabalhador tenha um único vencedor.

### III. Pedido separado de fato; a recusa também é um evento

- O que o cliente pede MUST ter nome no padrão `objeto.acao_solicitada` (ou `_solicitado`) e
  MUST NOT mudar o estado por si só.
- O que o servidor confirma MUST ter nome no padrão `objeto.acao_no_passado` (por exemplo
  `forja.construcao_iniciada`). Nomes de eventos MUST NOT ter acento nem espaço.
- Quando um pedido não pode ser atendido, o servidor MUST emitir `operacao.recusada`, com o
  motivo e a causa, somente para quem pediu. Os demais clientes MUST NOT receber a recusa.
- Fatos que mudam a vila MUST ser enviados a todos; a sincronização inicial MUST ser enviada
  apenas a quem acabou de conectar.

Justificativa: separar pedido de fato é o núcleo do paradigma orientado a eventos avaliado no
critério "Eventos (emit/on)" (2,5 pts).

### IV. Temporizadores do servidor são fontes de eventos

- A produção automática, o término das obras e o prazo da encomenda MUST ser disparados por
  temporizadores do servidor, que emitem fatos para todos.
- O cliente MUST NOT perguntar periodicamente ao servidor se algo mudou; ele apenas escuta.
- A espera de um temporizador MUST NOT bloquear o servidor: enquanto um temporizador aguarda,
  outros pedidos continuam sendo tratados.
- Todos os temporizadores MUST parar de produzir fatos quando a temporada é encerrada.

Justificativa: "passagem do tempo" é requisito explícito e faz parte do critério
"Fluxo em tempo real" (2,0 pts).

### V. Todo fato carrega a sua causa, visível no Painel de eventos

- Todo fato emitido pelo servidor MUST levar a sua causa: o nome do pedido que o gerou
  (por exemplo `forja.construcao_solicitada`), `temporizador`, ou o fato anterior seguido de
  `(temporizador)` (por exemplo `forja.construcao_iniciada (temporizador)`), ou `conexao`.
- Todo fato que muda a vila MUST levar o estado atual da vila; fatos ligados a uma pessoa MUST
  levar quem pediu.
- O Painel de eventos MUST mostrar, para cada evento emitido (⬆ emit) ou escutado (⬇ on), o
  nome, o horário, os dados, a causa e a reação do cliente. O painel MUST NOT ser removido.
- Todo ponto do código em que um evento é emitido ou escutado MUST ter um comentário explicando
  o porquê.

Justificativa: o painel é o que mostra o paradigma funcionando e é avaliado no critério
"Painel de eventos e interface" (1,5 pts).

### VI. Disciplina de escopo

- Cada funcionalidade especificada MUST ser entregue completa e testável; cada funcionalidade
  incompleta ou fora do escopo custa −0,10 ponto.
- O projeto MUST ter exatamente um fluxo de eventos próprio além dos mínimos (a encomenda
  com prazo). Novos fluxos, recursos ou construções MUST NOT ser adicionados sem emenda prévia
  da especificação.
- Extras (como os contadores por evento, no trabalho individual) MUST ser feitos só depois de
  tudo o que é obrigatório funcionar e MUST ser listados no README.
- O visual MUST usar apenas emojis, CSS ou arte de uso livre com crédito no README. Arte, nomes
  ou assets de jogos comerciais MUST NOT ser usados; a inspiração de "vila aconchegante" é só de
  clima.

Justificativa: o enunciado penaliza escopo incompleto ou excedente, e proíbe arte de jogos
comerciais.

### VII. Um commit por etapa

- O histórico MUST mostrar a especificação primeiro e depois um commit por etapa do guia
  (Etapas 0 a 8), cada uma testada com pelo menos duas abas abertas antes do commit.
- Mensagens de commit MUST seguir o padrão `docs: ...`, `feat: ...` ou `fix: ...`, em português.
- `git push` MUST NOT ser feito sem autorização explícita do usuário.

Justificativa: o critério "README e GitHub" e a regra de histórico exigem commits ao longo do
trabalho, com a especificação antes do código.

## Restrições do trabalho

- Entrega: 04/11/2026. Tipo de vila sorteado: Ferraria. Integrante: Miguel Antonio Selhorst
  (@MiguelSync).
- Dois papéis: o Mestre abre e encerra a temporada (e publica encomendas); o Jogador constrói
  forjas (e entrega encomendas).
- Não fazem parte do escopo: login e senha, banco de dados (a memória do servidor basta),
  publicação na internet, gráficos feitos do zero.
- Idioma: português do Brasil em documentos, textos da tela, comentários e commits.
- Rodapé da aplicação MUST mostrar o nome do desenvolvedor. O README MUST ter integrantes com @,
  como instalar e executar, como testar com duas abas, as três perguntas do enunciado e a
  declaração de uso de IA.

## Fluxo de desenvolvimento

1. `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` →
   `/speckit-tasks` → `/speckit-implement`.
2. `docs/especificacao.md` (modelo do kit) e `specs/<feature>/spec.md` MUST ficar coerentes
   entre si: mesmos nomes de eventos, mesmos números e mesmas regras.
3. Qualquer mudança de regra, número ou evento MUST ser feita primeiro na especificação e só
   depois no código, em commit `docs: ...` próprio.
4. Antes de cada commit de etapa, os cenários de teste da especificação aplicáveis àquela etapa
   MUST ser executados com duas ou mais abas.

## Governance

- Esta constituição prevalece sobre qualquer outra prática do projeto. `CLAUDE.md` traz as
  orientações operacionais e MUST permanecer coerente com ela.
- Emendas: MUST ser feitas por `/speckit-constitution`, registradas no Sync Impact Report e
  commitadas como `docs: ...` antes do código que dependa delas.
- Versionamento semântico: MAJOR para remover ou redefinir princípio; MINOR para princípio ou
  seção nova ou ampliada; PATCH para redação e correções.
- Conformidade: o plano (`/speckit-plan`) MUST passar pelo "Constitution Check" contra os
  princípios I–VII, e a revisão de código (agente `revisor-eventos`) MUST verificá-los antes
  da entrega.

**Version**: 1.0.0 | **Ratified**: 2026-10-22 | **Last Amended**: 2026-10-22
