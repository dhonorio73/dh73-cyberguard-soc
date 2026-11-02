"""Gera o cenário completo na API do laboratório."""
import os

import requests
from cenarios import gerar_cenario

API = os.environ.get("CYBERGUARD_API", "http://127.0.0.1:5000").rstrip("/")


def main():
    enviados = 0
    try:
        for evento in gerar_cenario("Cenário completo"):
            resposta = requests.post(f"{API}/eventos", json=evento, timeout=5)
            resposta.raise_for_status()
            enviados += 1
    except requests.RequestException as exc:
        raise SystemExit(f"Falha após registrar {enviados} evento(s): {exc}") from exc
    print(f"{enviados} eventos fictícios inseridos.")


if __name__ == "__main__":
    main()

