"""Cenários de teste da Vila Ferraria com clientes simulados (Socket.IO).

Uso, na raiz do repositório e com o venv ativo:

    python tests/cenarios.py                    # todos os cenários (~3 min, tempos reais)
    python tests/cenarios.py disputa encomenda  # só os cenários nomeados

Cada cenário (e cada repetição da disputa) sobe um `uvicorn server:app` novo numa porta livre,
porque a temporada não reabre. Os clientes são `socketio.AsyncClient` conectados com
`auth={"nome", "papel"}`, que gravam todo evento recebido com o horário de chegada. Os tempos são
os reais da especificação (5 s, 12 s, 30 s), conferidos com tolerância de ±1 s.

Fonte da verdade: docs/especificacao.md, specs/001-vila-ferraria/data-model.md e
specs/001-vila-ferraria/contracts/*.md. Dependência só de teste: tests/requirements.txt.
"""

import asyncio
import contextlib
import socket
import subprocess
import sys
import tempfile
import time
import traceback
from collections import Counter, namedtuple
from pathlib import Path

import socketio

RAIZ = Path(__file__).resolve().parent.parent

# Estado da vila logo depois de o servidor subir (data-model.md §1, contrato estado.sincronizado).
ESTADO_INICIAL = {
    "fase": "aguardando", "minerios": 120, "lingotes": 0, "ferreiros": 0, "limite": 2,
    "em_obra": 0, "concluidas": 0, "custo": 40, "tempo_obra": 12, "intervalo": 5,
    "producao": 10, "encomenda": None,
}

FORJA = "forja.construcao_solicitada"
ABRIR = "vila.abertura_solicitada"
ENCERRAR = "vila.encerramento_solicitado"
PUBLICAR = "encomenda.publicacao_solicitada"
ENTREGAR = "encomenda.entrega_solicitada"

TOLERANCIA = 1.0  # segundos de folga nos temporizadores (5/12/30 s)


# --------------------------------------------------------------------------- verificações

class Falha(AssertionError):
    """Comportamento diferente do especificado."""


def confere(condicao, mensagem):
    # Não usa `assert` puro para continuar valendo mesmo com `python -O`.
    if not condicao:
        raise Falha(mensagem)


def invariantes(estado):
    """Limites que nenhum estado da vila pode violar (data-model.md §1)."""
    confere(estado["minerios"] >= 0, f"minérios negativos: {estado}")
    confere(estado["lingotes"] >= 0, f"lingotes negativos: {estado}")
    confere(0 <= estado["ferreiros"] <= estado["limite"], f"ferreiros fora de 0..limite: {estado}")
    confere(estado["ferreiros"] == estado["em_obra"], f"ferreiros != em_obra: {estado}")


def confere_fato(r, causa, por=None, **campos):
    """Confere um fato `{estado, causa, por?}` e campos do estado; devolve o estado."""
    d = r.dados
    confere(isinstance(d, dict) and isinstance(d.get("estado"), dict),
            f"{r.cliente}: {r.nome} sem 'estado' no payload: {d!r}")
    confere(d.get("causa") == causa,
            f"{r.cliente}: {r.nome} com causa {d.get('causa')!r}, esperada {causa!r}")
    if por is not None:
        confere(d.get("por") == por, f"{r.cliente}: {r.nome} com por {d.get('por')!r}, esperado {por!r}")
    for chave, valor in campos.items():
        confere(d["estado"].get(chave) == valor,
                f"{r.cliente}: {r.nome} com estado.{chave} = {d['estado'].get(chave)!r}, "
                f"esperado {valor!r} (estado: {d['estado']})")
    return d["estado"]


def confere_recusa(r, motivo, causa):
    confere(r.dados == {"motivo": motivo, "causa": causa},
            f"{r.cliente}: operacao.recusada = {r.dados!r}, esperado "
            f"{ {'motivo': motivo, 'causa': causa}!r}")


def confere_tempo(r, esperado, rotulo):
    atraso = r.t - esperado
    confere(abs(atraso) <= TOLERANCIA,
            f"{r.cliente}: {r.nome} ({rotulo}) chegou {atraso:+.2f} s fora do previsto "
            f"(tolerância ±{TOLERANCIA:.0f} s)")


# --------------------------------------------------------------------------- servidor

@contextlib.asynccontextmanager
async def subir_servidor():
    """Sobe `uvicorn server:app` numa porta livre; entrega (url, ler_log) e derruba no fim."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        porta = s.getsockname()[1]
    log = tempfile.TemporaryFile(mode="w+")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(porta)],
        cwd=RAIZ, stdout=log, stderr=subprocess.STDOUT, text=True,
    )

    def ler_log():
        log.flush()
        log.seek(0)
        return log.read()

    try:
        limite = time.monotonic() + 15
        while True:
            if proc.poll() is not None:
                raise Falha(f"o servidor terminou ao subir (código {proc.returncode}):\n{ler_log()}")
            try:
                _, w = await asyncio.open_connection("127.0.0.1", porta)
                w.close()
                break
            except OSError:
                if time.monotonic() > limite:
                    raise Falha(f"o servidor não abriu a porta {porta} em 15 s:\n{ler_log()}")
                await asyncio.sleep(0.1)
        yield f"http://127.0.0.1:{porta}", ler_log
    finally:
        proc.terminate()
        try:
            await asyncio.to_thread(proc.wait, 5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        log.close()


# --------------------------------------------------------------------------- clientes

Registro = namedtuple("Registro", "cliente indice nome dados t")


class Cliente:
    """Uma aba simulada: conecta com nome/papel e grava tudo o que o servidor manda."""

    def __init__(self, nome, papel):
        self.nome, self.papel = nome, papel
        self.eventos = []
        self.sio = socketio.AsyncClient(reconnection=False)
        # O handler "*" grava qualquer evento, sem lista fixa: assim o teste também enxerga o
        # que NÃO devia chegar (ex.: uma recusa endereçada a outro jogador).
        self.sio.on("*", self._gravar)

    async def _gravar(self, evento, *args):
        dados = args[0] if args else None
        self.eventos.append(Registro(self.nome, len(self.eventos), evento, dados, time.monotonic()))

    async def conectar(self, url):
        await self.sio.connect(url, auth={"nome": self.nome, "papel": self.papel},
                               transports=["websocket"], wait_timeout=5)

    async def desconectar(self):
        with contextlib.suppress(Exception):
            await self.sio.disconnect()

    async def pedir(self, evento):
        # Pedidos não levam dados: o servidor sabe quem pediu pelo sid (contracts/README.md).
        await self.sio.emit(evento)

    def marca(self):
        """Posição atual da lista de eventos, para olhar só o que chegar depois."""
        return len(self.eventos)

    def recebidos(self, evento=None, desde=0):
        return [r for r in self.eventos[desde:] if evento is None or r.nome == evento]

    async def esperar_que(self, condicao, timeout, desde=0, n=1, descricao="evento"):
        """Espera o n-ésimo registro (a partir de `desde`) que satisfaz `condicao`."""
        limite = time.monotonic() + max(timeout, 0.05)
        while True:
            achados = [r for r in self.eventos[desde:] if condicao(r)]
            if len(achados) >= n:
                return achados[n - 1]
            if time.monotonic() >= limite:
                chegou = [r.nome for r in self.eventos[desde:]] or "nada"
                raise Falha(f"{self.nome}: esperava {descricao} (nº {n}) em até {timeout:.1f} s; "
                            f"chegou: {chegou}")
            await asyncio.sleep(0.01)

    async def esperar(self, evento, timeout, desde=0, n=1):
        return await self.esperar_que(lambda r: r.nome == evento, timeout, desde, n, evento)

    def confere_nada(self, evento, desde, motivo=""):
        extras = self.recebidos(evento, desde)
        confere(not extras, f"{self.nome} recebeu {[r.nome for r in extras]} e não devia{motivo}")

    async def nada_de(self, evento, janela, desde=None):
        """Confere que `evento` (None = qualquer um) não chega durante `janela` segundos."""
        desde = self.marca() if desde is None else desde
        await asyncio.sleep(janela)
        self.confere_nada(evento, desde, f" (janela de {janela} s)")

    def confere_invariantes(self):
        for r in self.eventos:
            if isinstance(r.dados, dict) and isinstance(r.dados.get("estado"), dict):
                try:
                    invariantes(r.dados["estado"])
                except Falha as e:
                    raise Falha(f"{self.nome}: {r.nome} violou um invariante: {e}") from None


class Vila:
    """Um servidor novo e os clientes conectados a ele (um por cenário ou repetição)."""

    async def __aenter__(self):
        self._servidor = subir_servidor()
        self.url, self._ler_log = await self._servidor.__aenter__()
        self.clientes = []
        self.t0 = time.monotonic()
        return self

    async def conectar(self, nome, papel, sincronizar=True):
        c = Cliente(nome, papel)
        self.clientes.append(c)
        await c.conectar(self.url)
        if sincronizar:
            await c.esperar("estado.sincronizado", 2)
        return c

    def marcas(self):
        return {c: c.marca() for c in self.clientes}

    async def __aexit__(self, tipo, exc, tb):
        erro = exc
        try:
            if erro is None:
                for c in self.clientes:
                    c.confere_invariantes()
                log = self._ler_log()
                confere("Traceback" not in log, f"o servidor levantou exceção:\n{log}")
        except Falha as e:
            erro = e
        if erro is not None:
            self._despejar()
        for c in self.clientes:
            await c.desconectar()
        await self._servidor.__aexit__(None, None, None)
        if erro is not None and exc is None:
            raise erro
        return False

    def _despejar(self):
        """Evidência da falha: tudo o que cada cliente recebeu e o fim do log do servidor."""
        print("--- eventos recebidos (tempo desde a subida do servidor) ---")
        for c in self.clientes:
            for r in c.eventos:
                print(f"  {c.nome:<7}{r.t - self.t0:7.2f}s  {r.nome:<28} {resumo(r.dados)}")
        print("--- fim do log do servidor ---")
        print("\n".join(self._ler_log().splitlines()[-25:]) or "  (vazio)")


def resumo(d):
    if not isinstance(d, dict):
        return repr(d)
    if "motivo" in d:
        return f"motivo={d.get('motivo')!r} causa={d.get('causa')!r}"
    e = d.get("estado") or {}
    enc = e.get("encomenda")
    enc = f"id={enc.get('id')} rest={enc.get('restante')}" if isinstance(enc, dict) else "-"
    por = f" por={d['por']}" if "por" in d else ""
    return (f"causa={d.get('causa')!r}{por} | {e.get('fase')} min={e.get('minerios')} "
            f"lin={e.get('lingotes')} ferr={e.get('ferreiros')}/{e.get('limite')} "
            f"obra={e.get('em_obra')} conc={e.get('concluidas')} enc={enc}")


# --------------------------------------------------------------------------- passos comuns

async def todos_recebem(clientes, evento, marcas, timeout=2.0, n=1):
    return {c: await c.esperar(evento, timeout, desde=marcas[c], n=n) for c in clientes}


async def abrir(vila, mestre):
    """O Mestre abre a temporada e todos recebem vila.iniciada (120 minérios, 0 lingotes)."""
    marcas = vila.marcas()
    await mestre.pedir(ABRIR)
    ini = await todos_recebem(vila.clientes, "vila.iniciada", marcas)
    for r in ini.values():
        confere_fato(r, ABRIR, por=mestre.nome, fase="aberta", minerios=120, lingotes=0)
    return ini


async def pedir_e_recusar(vila, quem, pedido, motivo, janela=0.5):
    """`quem` pede e só ele recebe operacao.recusada {motivo, causa=pedido}; nada mais muda.

    Na janela, o único outro evento tolerado é recurso.produzido, que pode coincidir com o
    pedido e chega a todos normalmente (especificação, cenário Recusa).
    """
    marcas = vila.marcas()
    await quem.pedir(pedido)
    recusa = await quem.esperar("operacao.recusada", 2, desde=marcas[quem])
    confere_recusa(recusa, motivo, pedido)
    await asyncio.sleep(janela)
    for c, m in marcas.items():
        extras = [r.nome for r in c.recebidos(desde=m)
                  if r is not recusa and r.nome != "recurso.produzido"]
        confere(not extras, f"{c.nome} recebeu {extras} depois de {quem.nome} pedir {pedido} "
                            f"(devia chegar só a recusa, e só para {quem.nome})")
    return recusa


# --------------------------------------------------------------------------- cenários

CENARIOS = {}


def cenario(funcao):
    CENARIOS[funcao.__name__] = funcao
    return funcao


@cenario
async def sincronizacao():
    """T007 — só quem conecta recebe estado.sincronizado, com o estado inicial completo."""
    async with Vila() as vila:
        a = await vila.conectar("A", "jogador", sincronizar=False)
        ra = await a.esperar("estado.sincronizado", 2)
        confere(ra.dados.get("causa") == "conexao", f"A: causa {ra.dados.get('causa')!r} != 'conexao'")
        confere(ra.dados.get("estado") == ESTADO_INICIAL,
                f"A: estado inicial {ra.dados.get('estado')} != {ESTADO_INICIAL}")
        b = await vila.conectar("B", "mestre", sincronizar=False)
        rb = await b.esperar("estado.sincronizado", 2)
        confere(rb.dados.get("causa") == "conexao", f"B: causa {rb.dados.get('causa')!r} != 'conexao'")
        confere(rb.dados.get("estado") == ESTADO_INICIAL,
                f"B: estado {rb.dados.get('estado')} != {ESTADO_INICIAL}")
        await asyncio.sleep(0.5)
        confere(len(a.recebidos("estado.sincronizado")) == 1,
                "A recebeu um segundo estado.sincronizado quando B conectou")
        confere(len(b.recebidos("estado.sincronizado")) == 1, "B recebeu mais de um estado.sincronizado")


@cenario
async def abertura():
    """T014 — Mestre abre; todos recebem um vila.iniciada em até 1 s (SC-001)."""
    async with Vila() as vila:
        m = await vila.conectar("Mestre", "mestre")
        a = await vila.conectar("A", "jogador")
        marcas = vila.marcas()
        t = time.monotonic()
        await m.pedir(ABRIR)
        for c in (m, a):
            r = await c.esperar("vila.iniciada", 1.5, desde=marcas[c])
            confere_fato(r, ABRIR, por="Mestre", fase="aberta", minerios=120, lingotes=0)
            confere(r.t - t <= 1.0, f"{c.nome}: vila.iniciada chegou {r.t - t:.2f} s depois do pedido (SC-001: até 1 s)")
        await asyncio.sleep(0.5)
        for c in (m, a):
            confere(len(c.recebidos("vila.iniciada", marcas[c])) == 1, f"{c.nome} recebeu mais de um vila.iniciada")
            c.confere_nada("operacao.recusada", marcas[c])


@cenario
async def recusas_basicas():
    """T022 — papel antes da fase, recusa só para quem pediu, 3ª forja sem ferreiro."""
    async with Vila() as vila:
        m = await vila.conectar("Mestre", "mestre")
        a = await vila.conectar("A", "jogador")
        # (a) forja antes da abertura
        await pedir_e_recusar(vila, a, FORJA, "A temporada não está aberta")
        # (b) Jogador tenta abrir; a fase continua aguardando
        await pedir_e_recusar(vila, a, ABRIR, "Só o Mestre pode abrir a temporada")
        sonda = await vila.conectar("Sonda", "jogador")
        confere_fato(sonda.recebidos("estado.sincronizado")[0], "conexao", fase="aguardando")
        # (c) Mestre abre e pede forja
        await abrir(vila, m)
        await pedir_e_recusar(vila, m, FORJA, "Só Jogadores constroem forjas")
        # (d) Mestre abre de novo
        await pedir_e_recusar(vila, m, ABRIR, "A temporada já foi aberta")
        # (e) A pede 3 forjas seguidas: 2 começam, a 3ª fica sem ferreiro
        marcas = vila.marcas()
        for _ in range(3):
            await a.pedir(FORJA)
        for c in vila.clientes:
            r1 = await c.esperar("forja.construcao_iniciada", 2, desde=marcas[c], n=1)
            r2 = await c.esperar("forja.construcao_iniciada", 2, desde=marcas[c], n=2)
            confere_fato(r1, FORJA, por="A", minerios=80, ferreiros=1, em_obra=1)
            confere_fato(r2, FORJA, por="A", minerios=40, ferreiros=2, em_obra=2)
        recusa = await a.esperar("operacao.recusada", 2, desde=marcas[a])
        confere_recusa(recusa, "Sem ferreiro livre", FORJA)
        await asyncio.sleep(0.5)
        for c in vila.clientes:
            confere(len(c.recebidos("forja.construcao_iniciada", marcas[c])) == 2,
                    f"{c.nome} não recebeu exatamente 2 forja.construcao_iniciada")
            confere(len(c.recebidos("operacao.recusada", marcas[c])) == (1 if c is a else 0),
                    f"{c.nome} recebeu operacao.recusada errada no pedido triplo de A")


@cenario
async def passagem_do_tempo():
    """T026 — cenário da especificação: produção aos 5/10/15 s e obra pronta aos 12 s."""
    async with Vila() as vila:
        m = await vila.conectar("Mestre", "mestre")
        a = await vila.conectar("A", "jogador")
        ini = await abrir(vila, m)
        marcas = vila.marcas()
        await a.pedir(FORJA)
        obra = await todos_recebem(vila.clientes, "forja.construcao_iniciada", marcas)
        for r in obra.values():
            confere_fato(r, FORJA, por="A", minerios=80, ferreiros=1, em_obra=1)
        for c in vila.clientes:
            t0, ti, base = ini[c].t, obra[c].t, ini[c].indice
            # Nenhum clique daqui em diante: tudo o que chega vem dos temporizadores.
            r1 = await c.esperar("recurso.produzido", t0 + 6.5 - time.monotonic(), desde=base, n=1)
            confere_tempo(r1, t0 + 5, "1º ciclo, t0+5 s")
            confere_fato(r1, "temporizador", minerios=90, lingotes=0)
            confere(r1.dados.get("ganho_minerios") == 10 and r1.dados.get("ganho_lingotes") == 0,
                    f"{c.nome}: ganhos do 1º ciclo {r1.dados!r}")
            r2 = await c.esperar("recurso.produzido", t0 + 11.5 - time.monotonic(), desde=base, n=2)
            confere_tempo(r2, t0 + 10, "2º ciclo, t0+10 s")
            confere_fato(r2, "temporizador", minerios=100, lingotes=0)
            fim = await c.esperar("forja.construcao_concluida", ti + 13.5 - time.monotonic(), desde=base)
            confere_tempo(fim, ti + 12, "obra, 12 s após forja.construcao_iniciada")
            confere_fato(fim, "forja.construcao_iniciada (temporizador)", por="A",
                         ferreiros=0, em_obra=0, concluidas=1, minerios=100)
            r3 = await c.esperar("recurso.produzido", t0 + 16.5 - time.monotonic(), desde=base, n=3)
            confere_tempo(r3, t0 + 15, "3º ciclo, t0+15 s")
            confere_fato(r3, "temporizador", minerios=110, lingotes=1, concluidas=1)
            confere(r3.dados.get("ganho_lingotes") == 1, f"{c.nome}: ganho_lingotes do 3º ciclo {r3.dados!r}")
            confere(r2.indice < fim.indice < r3.indice,
                    f"{c.nome}: ordem errada entre recurso.produzido e forja.construcao_concluida")
            confere(len(c.recebidos("forja.construcao_concluida", base)) == 1,
                    f"{c.nome} recebeu mais de uma forja.construcao_concluida")


@cenario
async def recusa():
    """T027 — cenário da especificação: 20 minérios, 1/2 ferreiros, 'Minério insuficiente'."""
    async with Vila() as vila:
        m = await vila.conectar("Mestre", "mestre")
        a = await vila.conectar("A", "jogador")
        await abrir(vila, m)
        # Como chegar ao estado do cenário: 2 forjas, esperar ficarem prontas (60 minérios, 0/2).
        marcas = vila.marcas()
        await a.pedir(FORJA)
        await a.pedir(FORJA)
        for r in (await todos_recebem(vila.clientes, "forja.construcao_iniciada", marcas, n=2)).values():
            confere_fato(r, FORJA, por="A", minerios=40, ferreiros=2)
        for r in (await todos_recebem(vila.clientes, "forja.construcao_concluida", marcas, 15, n=2)).values():
            confere_fato(r, "forja.construcao_iniciada (temporizador)", minerios=60, ferreiros=0,
                         em_obra=0, concluidas=2)
        # A pede uma forja (20, 1/2) e logo de novo, antes de o estoque voltar a 40.
        marcas = vila.marcas()
        await a.pedir(FORJA)
        await a.pedir(FORJA)
        obra = await todos_recebem(vila.clientes, "forja.construcao_iniciada", marcas)
        for r in obra.values():
            confere_fato(r, FORJA, por="A", minerios=20, ferreiros=1, em_obra=1)
        rec = await a.esperar("operacao.recusada", 2, desde=marcas[a])
        confere_recusa(rec, "Minério insuficiente", FORJA)
        confere(obra[a].indice < rec.indice, "A recebeu a recusa antes da forja aceita")
        await asyncio.sleep(0.5)
        for c in vila.clientes:
            confere(len(c.recebidos("forja.construcao_iniciada", marcas[c])) == 1,
                    f"{c.nome} recebeu uma 2ª forja.construcao_iniciada (o pedido devia ser recusado)")
            confere(len(c.recebidos("operacao.recusada", marcas[c])) == (1 if c is a else 0),
                    f"{c.nome} recebeu operacao.recusada errada (só A devia receber, uma vez)")
        # O estoque continua em 20 e os ferreiros em 1/2 (+10 se um ciclo coincidiu).
        ciclos = len(m.recebidos("recurso.produzido", marcas[m]))
        sonda = await vila.conectar("Sonda", "jogador")
        confere_fato(sonda.recebidos("estado.sincronizado")[0], "conexao",
                     minerios=20 + 10 * ciclos, ferreiros=1, em_obra=1, concluidas=2)
        # US3 #4: o próximo ciclo rende 1 lingote por forja concluída.
        prox = await m.esperar("recurso.produzido", 7, desde=marcas[m], n=ciclos + 1)
        confere_fato(prox, "temporizador", ferreiros=1, concluidas=2)
        confere(prox.dados.get("ganho_lingotes") == 2, f"ganho_lingotes {prox.dados.get('ganho_lingotes')!r} != 2")


@cenario
async def disputa():
    """T033 — cenário da especificação, 10 vezes: um vence, o outro 'Sem ferreiro livre'."""
    placar = Counter()
    for rodada in range(1, 11):
        async with Vila() as vila:
            m = await vila.conectar("Mestre", "mestre")
            a = await vila.conectar("A", "jogador")
            b = await vila.conectar("B", "jogador")
            await abrir(vila, m)
            marcas = vila.marcas()
            await a.pedir(FORJA)
            for r in (await todos_recebem(vila.clientes, "forja.construcao_iniciada", marcas)).values():
                confere_fato(r, FORJA, por="A", minerios=80, ferreiros=1)
            # A e B pedem "ao mesmo tempo": o servidor precisa tratar um pedido de cada vez.
            marcas = vila.marcas()
            t = time.monotonic()
            # A ordem de envio alterna a cada rodada para os dois poderem vencer.
            primeiro, segundo = (a, b) if rodada % 2 else (b, a)
            await asyncio.gather(primeiro.pedir(FORJA), segundo.pedir(FORJA))
            obra = await todos_recebem(vila.clientes, "forja.construcao_iniciada", marcas)
            vencedor = obra[m].dados.get("por")
            confere(vencedor in ("A", "B"), f"rodada {rodada}: por = {vencedor!r}")
            perdedor = a if vencedor == "B" else b
            for c, r in obra.items():
                confere_fato(r, FORJA, por=vencedor, minerios=40, ferreiros=2, em_obra=2)
                confere(r.t - t <= 1.0, f"rodada {rodada}: {c.nome} recebeu o fato {r.t - t:.2f} s depois (SC-001)")
            rec = await perdedor.esperar("operacao.recusada", 2, desde=marcas[perdedor])
            confere_recusa(rec, "Sem ferreiro livre", FORJA)
            await asyncio.sleep(0.5)
            for c in vila.clientes:
                confere(len(c.recebidos("forja.construcao_iniciada", marcas[c])) == 1,
                        f"rodada {rodada}: {c.nome} recebeu mais de uma forja.construcao_iniciada")
                confere(len(c.recebidos("operacao.recusada", marcas[c])) == (1 if c is perdedor else 0),
                        f"rodada {rodada}: {c.nome} recebeu operacao.recusada errada (só {perdedor.nome} devia)")
            placar[vencedor] += 1
    print(f"    placar da disputa (SC-002): A venceu {placar['A']}, B venceu {placar['B']}")


@cenario
async def encerramento():
    """T034 — encerrar para tudo: sem produção, obra inacabada, todo pedido recusado."""
    async with Vila() as vila:
        m = await vila.conectar("Mestre", "mestre")
        a = await vila.conectar("A", "jogador")
        await abrir(vila, m)
        marcas = vila.marcas()
        await a.pedir(FORJA)
        await todos_recebem(vila.clientes, "forja.construcao_iniciada", marcas)
        await pedir_e_recusar(vila, a, ENCERRAR, "Só o Mestre pode encerrar a temporada")
        marcas = vila.marcas()
        await m.pedir(ENCERRAR)
        fim = await todos_recebem(vila.clientes, "vila.encerrada", marcas)
        for r in fim.values():
            confere_fato(r, ENCERRAR, por="Mestre", fase="encerrada", em_obra=1, ferreiros=1)
        # SC-007: nada de temporizador depois do encerramento (a obra venceria ~11 s depois).
        await asyncio.sleep(13)
        for c in vila.clientes:
            depois = fim[c].indice + 1
            c.confere_nada("recurso.produzido", depois, " depois de vila.encerrada")
            c.confere_nada("forja.construcao_concluida", depois, " depois de vila.encerrada")
        await pedir_e_recusar(vila, a, FORJA, "A temporada não está aberta")
        await pedir_e_recusar(vila, m, ABRIR, "A temporada já foi aberta")
        await pedir_e_recusar(vila, m, ENCERRAR, "A temporada não está aberta")
        # Quem chega depois vê a vila encerrada, com a obra inacabada ainda contada.
        novo = await vila.conectar("C", "jogador")
        estado = novo.recebidos("estado.sincronizado")[0].dados.get("estado")
        confere(estado == fim[m].dados["estado"],
                f"C: estado.sincronizado {estado} != estado de vila.encerrada {fim[m].dados['estado']}")


@cenario
async def encomenda():
    """T041 — publicar, recusas, entrada no meio, entrega simultânea, expiração e encerramento."""
    async with Vila() as vila:
        m = await vila.conectar("Mestre", "mestre")
        a = await vila.conectar("A", "jogador")
        b = await vila.conectar("B", "jogador")
        await abrir(vila, m)
        marcas = vila.marcas()
        await a.pedir(FORJA)
        await a.pedir(FORJA)
        await todos_recebem(vila.clientes, "forja.construcao_iniciada", marcas, n=2)

        # US6 #1 — publicação
        antes_pub1 = vila.marcas()
        await m.pedir(PUBLICAR)
        pub1 = await todos_recebem(vila.clientes, "encomenda.publicada", antes_pub1)
        for r in pub1.values():
            enc = confere_fato(r, PUBLICAR, por="Mestre")["encomenda"]
            confere(isinstance(enc, dict) and enc.get("quantidade") == 3 and enc.get("prazo") == 30
                    and enc.get("recompensa") == 40 and enc.get("por") == "Mestre"
                    and 29 <= (enc.get("restante") or -1) <= 30,
                    f"{r.cliente}: encomenda publicada {enc!r}")
        tp1 = pub1[m].t

        # US6 #5, #3 e recusas de papel
        await pedir_e_recusar(vila, m, PUBLICAR, "Já existe uma encomenda ativa")
        await pedir_e_recusar(vila, a, ENTREGAR, "Lingotes insuficientes")
        await pedir_e_recusar(vila, m, ENTREGAR, "Só Jogadores entregam encomendas")
        await pedir_e_recusar(vila, a, PUBLICAR, "Só o Mestre pode publicar encomendas")

        # US1 #5 — quem entra no meio vê as obras e a encomenda com o prazo correndo
        await asyncio.sleep(max(0.0, tp1 + 1.2 - time.monotonic()))
        c = await vila.conectar("C", "jogador")
        est = confere_fato(c.recebidos("estado.sincronizado")[0], "conexao", em_obra=2, ferreiros=2)
        enc = est.get("encomenda")
        confere(isinstance(enc, dict) and enc.get("id") == pub1[m].dados["estado"]["encomenda"]["id"]
                and isinstance(enc.get("restante"), int) and 0 <= enc["restante"] < 30,
                f"C: encomenda no estado.sincronizado {enc!r}")

        # US6 #2/#6 — espera 3+ lingotes e A e B entregam ao mesmo tempo
        pronto = await a.esperar_que(
            lambda r: r.nome == "recurso.produzido" and r.dados["estado"]["lingotes"] >= 3,
            tp1 + 28 - time.monotonic(), desde=antes_pub1[a], descricao="recurso.produzido com 3+ lingotes")
        antes = pronto.dados["estado"]
        marcas = vila.marcas()
        await asyncio.gather(a.pedir(ENTREGAR), b.pedir(ENTREGAR))
        feito = await todos_recebem(vila.clientes, "encomenda.cumprida", marcas)
        vencedor = feito[m].dados.get("por")
        confere(vencedor in ("A", "B"), f"encomenda.cumprida com por = {vencedor!r}")
        perdedor = a if vencedor == "B" else b
        for r in feito.values():
            confere_fato(r, ENTREGAR, por=vencedor, encomenda=None,
                         lingotes=antes["lingotes"] - 3, minerios=antes["minerios"] + 40)
        rec = await perdedor.esperar("operacao.recusada", 2, desde=marcas[perdedor])
        confere_recusa(rec, "Nenhuma encomenda ativa", ENTREGAR)
        await asyncio.sleep(0.5)
        for cli in vila.clientes:
            confere(len(cli.recebidos("encomenda.cumprida", marcas[cli])) == 1,
                    f"{cli.nome} recebeu mais de uma encomenda.cumprida")
            confere(len(cli.recebidos("operacao.recusada", marcas[cli])) == (1 if cli is perdedor else 0),
                    f"{cli.nome} recebeu operacao.recusada errada na entrega simultânea")

        # US6 #7 — a encomenda cumprida não expira depois
        await asyncio.sleep(max(0.0, tp1 + 31 - time.monotonic()))
        for cli in vila.clientes:
            cli.confere_nada("encomenda.expirada", antes_pub1.get(cli, 0), " (a encomenda já foi cumprida)")

        # US6 #4 — encomenda sem entrega expira 30 s depois, sem débito nem pagamento
        antes_pub2 = vila.marcas()
        await m.pedir(PUBLICAR)
        pub2 = await todos_recebem(vila.clientes, "encomenda.publicada", antes_pub2)
        id2 = confere_fato(pub2[m], PUBLICAR, por="Mestre")["encomenda"]["id"]
        confere(id2 != pub1[m].dados["estado"]["encomenda"]["id"], "a 2ª encomenda repetiu o id da 1ª")
        venceu = {}
        for cli in vila.clientes:
            venceu[cli] = await cli.esperar("encomenda.expirada", pub2[cli].t + 32 - time.monotonic(),
                                            desde=antes_pub2[cli])
            r = venceu[cli]
            confere_tempo(r, pub2[cli].t + 30, "prazo de 30 s")
            est = confere_fato(r, "encomenda.publicada (temporizador)", encomenda=None)
            anterior = [x for x in cli.eventos[:r.indice]
                        if isinstance(x.dados, dict) and isinstance(x.dados.get("estado"), dict)][-1]
            confere(est["minerios"] == anterior.dados["estado"]["minerios"]
                    and est["lingotes"] == anterior.dados["estado"]["lingotes"],
                    f"{cli.nome}: encomenda.expirada mudou o estoque ({anterior.dados['estado']} -> {est})")
        await pedir_e_recusar(vila, a, ENTREGAR, "Nenhuma encomenda ativa")

        # FR-011/FR-012 — encerrar descarta a encomenda ativa, que não expira depois
        antes_pub3 = vila.marcas()
        await m.pedir(PUBLICAR)
        pub3 = await todos_recebem(vila.clientes, "encomenda.publicada", antes_pub3)
        marcas = vila.marcas()
        await m.pedir(ENCERRAR)
        for r in (await todos_recebem(vila.clientes, "vila.encerrada", marcas)).values():
            confere_fato(r, ENCERRAR, por="Mestre", fase="encerrada", encomenda=None)
        await asyncio.sleep(max(0.0, pub3[m].t + 31 - time.monotonic()))
        for cli in vila.clientes:
            cli.confere_nada("encomenda.expirada", antes_pub3[cli], " (a encomenda foi descartada no encerramento)")
        await pedir_e_recusar(vila, m, PUBLICAR, "A temporada não está aberta")
        await pedir_e_recusar(vila, a, ENTREGAR, "A temporada não está aberta")


# --------------------------------------------------------------------------- execução

def main():
    nomes = sys.argv[1:] or list(CENARIOS)
    desconhecidos = [n for n in nomes if n not in CENARIOS]
    if desconhecidos:
        print(f"cenário desconhecido: {', '.join(desconhecidos)}; existem: {', '.join(CENARIOS)}")
        sys.exit(2)
    inicio = time.monotonic()
    for nome in nomes:
        t = time.monotonic()
        try:
            asyncio.run(CENARIOS[nome]())
        except Falha as e:
            print(f"FALHOU {nome} ({time.monotonic() - t:.1f} s): {e}")
            sys.exit(1)
        except Exception:
            traceback.print_exc()
            print(f"FALHOU {nome} ({time.monotonic() - t:.1f} s): erro inesperado (acima)")
            sys.exit(1)
        print(f"OK {nome} ({time.monotonic() - t:.1f} s)", flush=True)
    print(f"TODOS OS CENÁRIOS PASSARAM ({time.monotonic() - inicio:.0f} s)")


if __name__ == "__main__":
    main()
