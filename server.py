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
