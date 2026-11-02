# Autoria: Douglas Honório · Projeto Dh73 CyberGuard SOC · 2026
"""Cenários educativos: geram registros fictícios, sem executar ações reais."""
from datetime import datetime, timedelta, timezone

CENARIOS = {
    "Falhas de autenticação": "Cinco falhas de login do mesmo IP; aciona a regra de dez minutos.",
    "Acesso autorizado": "Um login bem-sucedido de exemplo para comparar eventos normais.",
    "Alteração de arquivo": "Registra uma suposta alteração em arquivo de teste, sem acessar arquivos reais.",
    "Conexão suspeita": "Registra uma conexão fictícia para análise; não faz conexão de rede.",
    "Cenário completo": "Gera todos os eventos anteriores em um único lote.",
}


def gerar_cenario(nome, agora=None):
    if nome not in CENARIOS:
        raise ValueError("Cenário desconhecido.")
    agora = agora or datetime.now(timezone.utc)

    def evento(ip, tipo, severidade, descricao, minutos=0):
        return {"timestamp": (agora - timedelta(minutes=minutos)).isoformat(),
                "ip": ip, "tipo": tipo, "severidade": severidade, "descricao": descricao}

    conjuntos = {
        "Falhas de autenticação": [
            evento("192.0.2.10", "login_falho", "media",
                   "Simulação: tentativa de autenticação sem sucesso.", i) for i in range(5)
        ],
        "Acesso autorizado": [
            evento("192.0.2.21", "login_sucesso", "baixa", "Simulação: acesso autorizado.")
        ],
        "Alteração de arquivo": [
            evento("198.51.100.7", "alteracao_arquivo", "alta", "Simulação: arquivo de teste alterado.")
        ],
        "Conexão suspeita": [
            evento("203.0.113.4", "conexao_suspeita", "alta", "Simulação: conexão hipotética para análise.")
        ],
    }
    if nome == "Cenário completo":
        return [item for conjunto in conjuntos.values() for item in conjunto]
    return conjuntos[nome]

