import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio, static_files={
    "/": "client/index.html",
    "/assets": "client/assets",      # mapa, tileset e sprites da vila
})

# A partir da Etapa 1, adicione o seu código ABAIXO desta linha.

CUSTO = 40          # minérios por forja
TEMPO_OBRA = 12     # segundos até a forja ficar pronta
INTERVALO = 5       # segundos entre as produções da mina

estado = {
    "fase": "aguardando",     # aguardando -> aberta -> encerrada (nunca volta)
    "minerios": 120,          # recurso primário, extraído pela mina
    "lingotes": 0,            # recurso refinado, fundido pelas forjas concluídas
    "ferreiros": 0,           # ferreiros ocupados agora (um por obra)
    "limite": 2,              # máximo de ferreiros
    "em_obra": 0,             # forjas sendo construídas
    "concluidas": 0,          # forjas prontas (cada uma funde 1 lingote por ciclo)
    "custo": CUSTO,
    "tempo_obra": TEMPO_OBRA,
    "intervalo": INTERVALO,
    "producao": 10,           # minérios que a mina produz a cada INTERVALO
    "encomenda": None,        # encomenda ativa do Mestre (no máximo uma)
}
jogadores = {}                # sid -> {"nome": ..., "papel": "mestre" | "jogador"}


def instantaneo():
    """Cópia do estado para enviar aos clientes. A encomenda é um dict
    aninhado, então também é copiada (a cópia rasa a compartilharia)."""
    copia = dict(estado)
    if estado["encomenda"] is not None:
        copia["encomenda"] = dict(estado["encomenda"])
    return copia


def fato(causa, **extras):
    """Monta o payload de um FATO: o estado atual, a CAUSA (o pedido ou o
    temporizador que gerou o fato) e dados extras, como quem pediu (por)."""
    return {"estado": instantaneo(), "causa": causa, **extras}


@sio.event
async def connect(sid, environ, auth):
    auth = auth or {}
    jogadores[sid] = {
        "nome": auth.get("nome") or "Anônimo",
        "papel": "mestre" if auth.get("papel") == "mestre" else "jogador",
    }
    # servidor -> UM cliente: quem acabou de entrar precisa do estado atual;
    # quem já estava conectado já o tem, por isso to=sid e não para todos.
    await sio.emit("estado.sincronizado", fato("conexao"), to=sid)


@sio.event
async def disconnect(sid):
    # Sair não gera evento: obras e encomendas continuam sem essa aba.
    jogadores.pop(sid, None)


async def recusar(sid, motivo, causa):
    """Recusa um pedido. A recusa também é um evento, mas só quem pediu
    recebe (to=sid): para os outros nada aconteceu."""
    await sio.emit("operacao.recusada", {"motivo": motivo, "causa": causa}, to=sid)


@sio.on("vila.abertura_solicitada")
async def abrir_vila(sid, dados=None):
    # Escuta o PEDIDO do Mestre; o servidor decide se a temporada abre.
    pedido = "vila.abertura_solicitada"
    quem = jogadores[sid]
    if quem["papel"] != "mestre":
        await recusar(sid, "Só o Mestre pode abrir a temporada", pedido)
        return
    if estado["fase"] != "aguardando":
        await recusar(sid, "A temporada já foi aberta", pedido)
        return
    estado["fase"] = "aberta"
    # FATO para todos: a temporada mudou para todo mundo ao mesmo tempo.
    await sio.emit("vila.iniciada", fato(pedido, por=quem["nome"]))


@sio.on("forja.construcao_solicitada")
async def construir(sid, dados=None):
    # Escuta o PEDIDO de um Jogador para erguer uma forja.
    pedido = "forja.construcao_solicitada"
    quem = jogadores[sid]
    # Valide TUDO antes de alterar o estado e sem await no meio: o servidor
    # trata um evento por vez, então dois pedidos simultâneos são decididos
    # em sequência (um vence, o outro é recusado). Um await entre validar e
    # alterar deixaria os dois passarem pela validação.
    if quem["papel"] != "jogador":
        motivo = "Só Jogadores constroem forjas"
    elif estado["fase"] != "aberta":
        motivo = "A temporada não está aberta"
    elif estado["minerios"] < CUSTO:
        motivo = "Minério insuficiente"
    elif estado["ferreiros"] >= estado["limite"]:
        motivo = "Sem ferreiro livre"
    else:
        motivo = None

    if motivo:
        await recusar(sid, motivo, pedido)    # só quem pediu recebe
        return

    estado["minerios"] -= CUSTO
    estado["ferreiros"] += 1
    estado["em_obra"] += 1
    nome = quem["nome"]
    # FATO para todos: o estoque e os ferreiros mudaram para a vila inteira.
    await sio.emit("forja.construcao_iniciada", fato(pedido, por=nome))
