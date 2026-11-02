from datetime import datetime, timezone

import pytest
from cenarios import CENARIOS, gerar_cenario
from api import validar


def test_cenarios_geram_eventos_validos():
    agora = datetime.now(timezone.utc)
    for nome in CENARIOS:
        eventos = gerar_cenario(nome, agora)
        assert eventos
        for evento in eventos:
            validar(evento)
    assert len(gerar_cenario("Falhas de autenticação", agora)) == 5
    assert len(gerar_cenario("Cenário completo", agora)) == 8


def test_cenario_desconhecido():
    with pytest.raises(ValueError):
        gerar_cenario("não existe")

