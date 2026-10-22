import math
import time

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
ENCOMENDA_QUANTIDADE = 3     # lingotes pedidos por encomenda
ENCOMENDA_PRAZO = 30         # segundos para entregar
ENCOMENDA_RECOMPENSA = 40    # minérios pagos ao cumprir

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
ultima_encomenda = 0         # contador de ids: cada publicação ganha um id novo


def instantaneo():
    """Cópia do estado para enviar aos clientes. A encomenda é um dict
    aninhado, então também é copiada (a cópia rasa a compartilharia)."""
    copia = dict(estado)
    if estado["encomenda"] is not None:
        encomenda = dict(estado["encomenda"])
        # expira_em é interno (relógio do servidor); o cliente recebe quantos
        # segundos faltam, que vale para qualquer aba, mesmo quem entra no meio.
        expira_em = encomenda.pop("expira_em")
        encomenda["restante"] = max(0, math.ceil(expira_em - time.monotonic()))
        copia["encomenda"] = encomenda
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
    sio.start_background_task(producao)      # a mina começa a produzir sozinha
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
    sio.start_background_task(obra, nome)    # o temporizador termina a obra


async def producao():
    """Temporizador da mina: é uma FONTE de eventos. A cada INTERVALO a vila
    produz e o servidor avisa todos; ninguém precisa perguntar."""
    while estado["fase"] == "aberta":
        await sio.sleep(INTERVALO)            # nunca time.sleep: travaria o servidor
        if estado["fase"] != "aberta":        # encerrou enquanto dormia
            break
        ganho_lingotes = estado["concluidas"]  # cada forja pronta funde 1 lingote
        estado["minerios"] += estado["producao"]
        estado["lingotes"] += ganho_lingotes
        # FATO para todos, causado pelo temporizador e não por um clique.
        await sio.emit("recurso.produzido", fato(
            "temporizador", ganho_minerios=estado["producao"], ganho_lingotes=ganho_lingotes))


async def obra(nome):
    """Temporizador de uma forja: termina a obra TEMPO_OBRA segundos depois
    de forja.construcao_iniciada."""
    await sio.sleep(TEMPO_OBRA)
    if estado["fase"] != "aberta":           # encerrada: a obra fica inacabada
        return
    estado["ferreiros"] -= 1
    estado["em_obra"] -= 1
    estado["concluidas"] += 1
    # FATO para todos: a causa é a obra iniciada antes, via temporizador.
    causa = "forja.construcao_iniciada (temporizador)"
    await sio.emit("forja.construcao_concluida", fato(causa, por=nome))


@sio.on("vila.encerramento_solicitado")
async def encerrar_vila(sid, dados=None):
    # Escuta o PEDIDO do Mestre para encerrar a temporada.
    pedido = "vila.encerramento_solicitado"
    quem = jogadores[sid]
    if quem["papel"] != "mestre":
        await recusar(sid, "Só o Mestre pode encerrar a temporada", pedido)
        return
    if estado["fase"] != "aberta":
        await recusar(sid, "A temporada não está aberta", pedido)
        return
    # Os temporizadores param sozinhos: ao acordar, conferem a fase e veem
    # que ela não está mais aberta (a mina para e as obras ficam inacabadas).
    estado["fase"] = "encerrada"
    # A encomenda ativa é descartada: o prazo dela não expira depois.
    estado["encomenda"] = None
    # FATO para todos: ninguém mais pode agir nesta temporada.
    await sio.emit("vila.encerrada", fato(pedido, por=quem["nome"]))


@sio.on("encomenda.publicacao_solicitada")
async def publicar_encomenda(sid, dados=None):
    # Escuta o PEDIDO do Mestre para publicar uma encomenda de lingotes.
    global ultima_encomenda
    pedido = "encomenda.publicacao_solicitada"
    quem = jogadores[sid]
    if quem["papel"] != "mestre":
        motivo = "Só o Mestre pode publicar encomendas"
    elif estado["fase"] != "aberta":
        motivo = "A temporada não está aberta"
    elif estado["encomenda"] is not None:
        motivo = "Já existe uma encomenda ativa"
    else:
        motivo = None
    if motivo:
        await recusar(sid, motivo, pedido)    # só quem pediu recebe
        return
    ultima_encomenda += 1
    estado["encomenda"] = {
        "id": ultima_encomenda,
        "quantidade": ENCOMENDA_QUANTIDADE,
        "prazo": ENCOMENDA_PRAZO,
        "recompensa": ENCOMENDA_RECOMPENSA,
        "por": quem["nome"],
        "expira_em": time.monotonic() + ENCOMENDA_PRAZO,
    }
    # FATO para todos: todos os jogadores podem tentar cumprir a encomenda.
    await sio.emit("encomenda.publicada", fato(pedido, por=quem["nome"]))
    sio.start_background_task(prazo_encomenda, ultima_encomenda)   # o prazo começa a correr


async def prazo_encomenda(id_encomenda):
    """Temporizador do prazo: se a MESMA encomenda ainda estiver ativa depois
    de ENCOMENDA_PRAZO segundos, ela expira. O id evita expirar uma encomenda
    nova publicada depois que esta foi cumprida."""
    await sio.sleep(ENCOMENDA_PRAZO)
    encomenda = estado["encomenda"]
    if estado["fase"] != "aberta" or encomenda is None or encomenda["id"] != id_encomenda:
        return
    estado["encomenda"] = None
    # FATO para todos, causado pelo temporizador da encomenda publicada.
    await sio.emit("encomenda.expirada", fato("encomenda.publicada (temporizador)"))


@sio.on("encomenda.entrega_solicitada")
async def entregar_encomenda(sid, dados=None):
    # Escuta o PEDIDO de um Jogador para entregar os lingotes da encomenda.
    pedido = "encomenda.entrega_solicitada"
    quem = jogadores[sid]
    # Validar e alterar sem await no meio: se dois Jogadores entregarem ao
    # mesmo tempo, só o primeiro cumpre; o outro vê "Nenhuma encomenda ativa".
    if quem["papel"] != "jogador":
        motivo = "Só Jogadores entregam encomendas"
    elif estado["fase"] != "aberta":
        motivo = "A temporada não está aberta"
    elif estado["encomenda"] is None:
        motivo = "Nenhuma encomenda ativa"
    elif estado["lingotes"] < estado["encomenda"]["quantidade"]:
        motivo = "Lingotes insuficientes"
    else:
        motivo = None
    if motivo:
        await recusar(sid, motivo, pedido)    # só quem pediu recebe
        return
    encomenda = estado["encomenda"]
    estado["lingotes"] -= encomenda["quantidade"]
    estado["minerios"] += encomenda["recompensa"]
    estado["encomenda"] = None
    # FATO para todos: o estoque mudou e a encomenda saiu do quadro.
    await sio.emit("encomenda.cumprida", fato(pedido, por=quem["nome"]))
