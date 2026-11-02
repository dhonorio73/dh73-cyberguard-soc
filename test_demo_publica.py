"""Verifica os fluxos principais da demonstração pública."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).with_name("demo_publica.py"))


def valor(app, rotulo):
    return next(item.value for item in app.metric if item.label == rotulo)


def test_cenario_filtro_e_reinicio():
    app = AppTest.from_file(APP).run(timeout=15)
    assert not app.exception
    assert valor(app, "Eventos filtrados") == "8"

    app.sidebar.selectbox[0].select("Acesso autorizado").run()
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert valor(app, "Eventos filtrados") == "9"

    app.main.selectbox[0].select("login_sucesso").run()
    assert not app.exception
    assert valor(app, "Eventos filtrados") == "2"

    app.sidebar.button[1].click().run()
    assert not app.exception
    assert valor(app, "Eventos filtrados") == "1"


def test_visitantes_tem_sessoes_separadas():
    primeiro = AppTest.from_file(APP).run(timeout=15)
    segundo = AppTest.from_file(APP).run(timeout=15)
    primeiro.sidebar.selectbox[0].select("Acesso autorizado").run()
    primeiro.sidebar.button[0].click().run()
    assert not primeiro.exception
    assert not segundo.exception
    assert valor(primeiro, "Eventos filtrados") == "9"
    assert valor(segundo, "Eventos filtrados") == "8"

