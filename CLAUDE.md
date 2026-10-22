# Vila em Tempo Real — Ferraria

Trabalho 01 de Linguagem de Programação e Paradigmas (Programação Orientada a Eventos, 2026/2).
Entrega: **04/11/2026**. Tipo de vila sorteado: **Ferraria**. Inspiração de clima: Stardew Valley
(só a "pegada" — nenhuma arte, nome ou asset de jogo comercial pode ser usado).

## Material de referência (local, fora do git)
- `instruções/enunciado-trabalho01.txt` — regras, eventos mínimos, critérios de avaliação e penalizações
- `instruções/guia-implementacao.txt` — passo a passo Etapas 0–8 e Anexo A (Tiled)
- `instruções/kit-original/` — Kit Inicial intacto (server.py, client/index.html, assets, modelos de docs)

## Regras do projeto (não negociáveis)
1. **Spec-driven, sem vibe coding.** Toda mudança de comportamento começa na especificação
   (`docs/especificacao.md` e `specs/`), e só depois vira código. Fluxo do Spec Kit:
   `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`.
2. **`docs/especificacao.md` é commitado antes de qualquer código** (vale 2,0 pts; perde tudo se vier depois).
   Ele não cita tecnologia.
3. **Um commit por etapa** do guia, mensagens no padrão `feat: ...` / `docs: ...` / `fix: ...`.
4. **Nunca dar `git push` sem pedir autorização ao usuário.** Commits locais são livres.
5. Nomes de eventos idênticos na especificação, no `server.py` e no `client/index.html`.
   Padrão: `objeto.acao_no_passado` (fato do servidor) e `objeto.acao_solicitada` (pedido do cliente).
6. Servidor é a fonte da verdade; cliente só pede (`pedir`) e reage (`ouvir`). Nunca usar `socket.emit`/`socket.on` direto.
7. Validar e alterar o estado **sem `await` no meio** (disputa pelo último recurso).
8. Temporizadores com `await sio.sleep(...)`, nunca `time.sleep(...)`.
9. Comentário em todo ponto de emit/on explicando o porquê.
10. Painel de eventos não pode ser removido; contadores por evento (Etapa 7) incluídos.
11. Nome do desenvolvedor no rodapé; README com integrantes/@, execução, teste com duas abas,
    as três perguntas e declaração de uso de IA (Claude Code + Spec Kit).

## Stack (do kit)
Python 3 + python-socketio + uvicorn · Vue 3 (CDN) · Phaser 3 (CDN) · Socket.IO · mapa Tiled em `client/assets/vila.json`.

Rodar: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn server:app --reload` → http://localhost:8000

## Agentes do projeto (`.claude/agents/`)
- `spec-writer` — escreve/atualiza a especificação (Spec Kit + `docs/especificacao.md`). Não escreve código.
- `planejador` — transforma a spec em plano e tarefas por etapa do guia.
- `revisor-eventos` — audita código x spec x critérios de avaliação.
- `testador-cenarios` — sobe o servidor e roda os cenários de teste com vários clientes simulados.

Idioma: português do Brasil em código, comentários, commits e documentos.
