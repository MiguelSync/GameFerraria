# Specification Quality Checklist: Identidade Visual da Vila Ferraria

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-22
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Validação 1 (2026-10-22): passaram todos os itens, menos um. Falta resolver 1 marcador
  [NEEDS CLARIFICATION] (o limite é 3), na US5 cenário 3: o progresso da obra para quem entra no
  meio. O estado enviado hoje não diz há quanto tempo cada obra começou, e esta feature não pode
  mudar os dados enviados.
  - Recomendação: opção A, a barra em modo "em andamento" sem a fração exata.
  - A opção B exigiria antes uma emenda da 001, com dados novos no estado.
- Procurei termos de tecnologia em `spec.md` (linguagens, bibliotecas, formatos de arquivo, editor
  de mapas) e não achei nenhum. "Emojis", "pixel art" e "grade de 16 pixels" descrevem aparência,
  não tecnologia.
- Fronteira conferida: a 002 não muda nenhum dos 15 eventos, números, dados enviados, causas ou
  motivos da 001 (FR-001 e FR-002, SC-002). Arquivos da 001 e `docs/especificacao.md` não foram
  tocados.
- A tabela "Reação visual por fato" cobre os 10 fatos que a aba escuta: `estado.sincronizado`,
  `vila.iniciada`, `forja.construcao_iniciada`, `forja.construcao_concluida`, `recurso.produzido`,
  `operacao.recusada`, `encomenda.publicada`, `encomenda.cumprida`, `encomenda.expirada` e
  `vila.encerrada`.
- Ponto de atenção sobre a constituição (VI): ela diz "emojis, CSS ou arte de uso livre", e a
  Assumption trata arte original com licença livre declarada no README como "de uso livre". Se o
  Maestro preferir deixar isso explícito, cabe uma emenda PATCH via `/speckit-constitution`.
- Validação 2 (2026-10-22):
  - Q1 foi respondida pelo Maestro com a opção A. Quem entra no meio de uma obra vê a barra em
    modo "em andamento". Isso ficou registrado na US5 cenário 3, na tabela de reações
    (`estado.sincronizado`), no FR-012, no SC-004 e nas Assumptions. Não resta nenhum marcador.
  - A constituição foi emendada para 1.0.1 (PATCH): o princípio VI agora aceita explicitamente
    arte original criada para o projeto, inclusive a gerada por script versionado, com licença
    livre declarada no README.
  - A spec registra nas Assumptions e no FR-020 que a arte será desenhada por script versionado
    no repositório e que isso entra na declaração de uso de IA do README.
  - "Script versionado" foi mantido de forma genérica, sem citar linguagem ou ferramenta.
  - Todos os itens passam.
- Validação 3 (2026-10-22, após `/speckit-analyze`): a spec foi alinhada às decisões do plano.
  - SC-009 define o observador (pessoa sem contexto do projeto) e o método: vê a vila ou uma
    captura de cada uma das 10 cenas, sem o Painel, e diz qual fato aconteceu. A meta é ≥ 8 de 10.
  - SC-007, FR-018 e o teste da US7: a 1280 × 720, a vila, o estoque e os botões aparecem sem
    rolar a página e sem sobreposição. O Painel de eventos rola por dentro e o rodapé fica ao fim
    da página.
  - `forja.construcao_iniciada`: o "−40 🪨" sobe da entrada da mina, porque o estoque não é
    desenhado na vila.
  - Lanternas: acesas na madrugada e na noite, apagadas no dia. Isso entrou na tabela
    (`vila.iniciada`), na US1#1, na US5#1 e nas Assumptions.
  - Todos os itens continuam passando.
- Próximo passo: `/speckit-clarify` (opcional) ou `/speckit-plan`.
