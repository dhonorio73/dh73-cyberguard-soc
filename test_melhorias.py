from datetime import datetime, timezone
from relatorios import criar_relatorio, ler_csv
from test_api import client, evento


def test_importacao_atomica(client):
    bom = evento()
    ruim = evento()
    ruim["ip"] = "inválido"
    assert client.post("/eventos/lote", json=[bom, ruim]).status_code == 400
    assert client.get("/eventos").get_json() == []
    assert client.post("/eventos/lote", json=[bom, bom]).get_json()["inseridos"] == 2


def test_regra_alteracoes(client):
    for _ in range(3):
        assert client.post("/eventos", json=evento(tipo="alteracao_arquivo")).status_code == 201
    resultado = client.get("/alertas").get_json()
    assert len(resultado) == 1
    assert "alterações de arquivo" in resultado[0]["regra"]


def test_relatorio_escapa_e_csv():
    texto = b'timestamp,ip,tipo,severidade,descricao\n2026-01-01T00:00:00Z,192.0.2.1,login_falho,media,<script>\n'
    eventos = ler_csv(texto)
    html = criar_relatorio(eventos, [], {"tipo": "<todos>"})
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;todos&gt;" in html

