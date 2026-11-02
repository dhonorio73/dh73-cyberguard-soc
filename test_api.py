from datetime import datetime, timedelta, timezone

import pytest

from api import app, inicializar


@pytest.fixture
def client(tmp_path):
    app.config.update(TESTING=True, DB_PATH=str(tmp_path / "test.db"))
    inicializar()
    with app.test_client() as client:
        yield client


def evento(ip="192.0.2.10", tipo="login_falho", data=None):
    return {"timestamp": (data or datetime.now(timezone.utc)).isoformat(),
            "ip": ip, "tipo": tipo, "severidade": "media", "descricao": "Teste"}


def test_insercao_listagem_e_filtro(client):
    assert client.post("/eventos", json=evento()).status_code == 201
    assert len(client.get("/eventos?tipo=login_falho").get_json()) == 1
    assert client.get("/eventos?tipo=login_sucesso").get_json() == []
    assert client.get("/eventos?tipo=invalido").status_code == 400


def test_validacao_e_parametros(client):
    ruim = evento()
    ruim["ip"] = "não é um IP"
    assert client.post("/eventos", json=ruim).status_code == 400
    ruim = evento()
    ruim["timestamp"] = "2026-01-01T12:00:00"
    assert client.post("/eventos", json=ruim).status_code == 400
    ruim = evento()
    ruim["descricao"] = "<script>alert(1)</script>"
    assert client.post("/eventos", json=ruim).status_code == 201
    assert client.get("/eventos?tipo=login_falho%27%20OR%201%3D1--").status_code == 400


def test_alerta_agrupa_apenas_falhas_na_janela(client):
    agora = datetime.now(timezone.utc)
    for minutos in range(5):
        assert client.post("/eventos", json=evento(data=agora - timedelta(minutes=minutos))).status_code == 201
    client.post("/eventos", json=evento(ip="198.51.100.2", data=agora - timedelta(minutes=20)))
    client.post("/eventos", json=evento(ip="198.51.100.2", tipo="login_sucesso"))
    alertas = client.get("/alertas").get_json()
    assert len(alertas) == 1
    assert alertas[0]["ip"] == "192.0.2.10"
    assert alertas[0]["total"] == 5

