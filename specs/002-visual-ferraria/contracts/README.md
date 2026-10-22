# Contratos — Identidade Visual da Vila Ferraria

A 002 **não cria nem altera eventos**: os 15 contratos de eventos continuam sendo os de
`specs/001-vila-ferraria/contracts/` (nomes, quem emite/recebe, payload e causa). Esta pasta
define as três interfaces novas da apresentação:

| Contrato | Entre | O que fixa |
|---|---|---|
| [assets.md](./assets.md) | `tools/gerar_arte.py` → cena Phaser | arquivos, tamanhos, índices de peças e quadros, animações, reserva do modo simples |
| [mapa.md](./mapa.md) | `vila.json` (script/Tiled) → cena Phaser | formato Tiled, tileset embutido, camadas, 17 pontos e regras de layout |
| [cenas.md](./cenas.md) | bloco Vue (`ouvir`) → cena Phaser (`jogo.*`) | para cada um dos 10 fatos: método, argumentos, frase de reação (FR-005), cena, duração, estado final e regras comuns (sem fila, convergência, modo simples) |
