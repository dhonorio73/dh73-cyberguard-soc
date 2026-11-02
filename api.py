import ipaddress
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.environ.get("CYBERGUARD_DB", "data/eventos.db")
TIPOS = {"login_falho", "login_sucesso", "alteracao_arquivo", "conexao_suspeita"}
SEVERIDADES = {"baixa", "media", "alta", "critica"}


def conectar():
    caminho = Path(app.config.get("DB_PATH", DB_PATH))
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(caminho, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def inicializar():
    with conectar() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip TEXT NOT NULL,
            tipo TEXT NOT NULL,
            severidade TEXT NOT NULL,
            descricao TEXT NOT NULL
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_eventos_ip_data ON eventos(ip, timestamp)")


def validar(dados):
    if not isinstance(dados, dict):
        raise ValueError("Envie um objeto JSON.")
    try:
        ip = str(ipaddress.ip_address(dados.get("ip", "")))
    except ValueError as exc:
        raise ValueError("IP inválido.") from exc
    tipo, severidade = dados.get("tipo"), dados.get("severidade")
    if not isinstance(tipo, str) or not isinstance(severidade, str) or tipo not in TIPOS or severidade not in SEVERIDADES:
        raise ValueError("Tipo ou severidade inválidos.")
    descricao = dados.get("descricao")
    if not isinstance(descricao, str) or not 1 <= len(descricao.strip()) <= 500:
        raise ValueError("Descrição deve ter entre 1 e 500 caracteres.")
    timestamp = dados.get("timestamp")
    if not isinstance(timestamp, str):
        raise ValueError("Informe timestamp ISO 8601 com fuso.")
    try:
        data = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if data.tzinfo is None or data.utcoffset() is None:
            raise ValueError
    except ValueError as exc:
        raise ValueError("Informe timestamp ISO 8601 com fuso.") from exc
    return (data.astimezone(timezone.utc).isoformat(timespec="seconds"), ip, tipo, severidade, descricao.strip())


@app.post("/eventos")
def criar_evento():
    try:
        valores = validar(request.get_json(silent=True))
    except ValueError as exc:
        return jsonify(erro=str(exc)), 400
    with conectar() as con:
        cursor = con.execute("INSERT INTO eventos(timestamp, ip, tipo, severidade, descricao) VALUES (?, ?, ?, ?, ?)", valores)
        evento = con.execute("SELECT * FROM eventos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(dict(evento)), 201


@app.post("/eventos/lote")
def criar_lote():
    dados = request.get_json(silent=True)
    if not isinstance(dados, list) or not 1 <= len(dados) <= 1000:
        return jsonify(erro="Envie uma lista de 1 a 1000 eventos."), 400
    valores = []
    for indice, item in enumerate(dados, start=2):
        try:
            valores.append(validar(item))
        except (ValueError, TypeError) as exc:
            return jsonify(erro=f"Linha {indice}: {exc}"), 400
    with conectar() as con:
        con.executemany("INSERT INTO eventos(timestamp, ip, tipo, severidade, descricao) VALUES (?, ?, ?, ?, ?)", valores)
    return jsonify(inseridos=len(valores)), 201

@app.get("/eventos")
def listar_eventos():
    tipo = request.args.get("tipo")
    severidade = request.args.get("severidade")
    if tipo and tipo not in TIPOS or severidade and severidade not in SEVERIDADES:
        return jsonify(erro="Filtro inválido."), 400
    sql = "SELECT * FROM eventos WHERE 1=1"
    parametros = []
    if tipo:
        sql += " AND tipo = ?"
        parametros.append(tipo)
    if severidade:
        sql += " AND severidade = ?"
        parametros.append(severidade)
    with conectar() as con:
        eventos = con.execute(sql + " ORDER BY timestamp DESC, id DESC LIMIT 1000", parametros).fetchall()
    return jsonify([dict(evento) for evento in eventos])


@app.get("/alertas")
def alertas():
    # A regra usa a janela relativa ao horário da consulta, não à data mais recente.
    agora = datetime.now(timezone.utc)
    inicio = (agora - timedelta(minutes=10)).isoformat(timespec="seconds")
    fim = agora.isoformat(timespec="seconds")
    with conectar() as con:
        linhas = con.execute("""SELECT ip, COUNT(*) AS total FROM eventos
            WHERE tipo = 'login_falho' AND timestamp >= ? AND timestamp <= ?
            GROUP BY ip HAVING COUNT(*) >= 5 ORDER BY total DESC, ip""",
            (inicio, fim)).fetchall()
    resultado = [{"ip": r["ip"], "total": r["total"],
                  "regra": "5 ou mais falhas de login em 10 minutos"} for r in linhas]
    with conectar() as con:
        alteracoes = con.execute("""SELECT ip, COUNT(*) AS total FROM eventos
            WHERE tipo = 'alteracao_arquivo' AND timestamp >= ? AND timestamp <= ?
            GROUP BY ip HAVING COUNT(*) >= 3 ORDER BY total DESC, ip""",
            (inicio, fim)).fetchall()
    resultado.extend({"ip": r["ip"], "total": r["total"],
                      "regra": "3 ou mais alterações de arquivo em 10 minutos"} for r in alteracoes)
    return jsonify(resultado)


@app.get("/saude")
def saude():
    return jsonify(status="ok", modo="laboratorio")


@app.cli.command("init-db")
def init_db():
    inicializar()
    print("Banco inicializado.")


inicializar()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

