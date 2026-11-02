# Dh73 CyberGuard SOC

Laboratório de segurança com eventos fictícios, API REST em Flask, SQLite e painel Streamlit. Criado por Douglas Honório para aprendizado e portfólio.

## Funcionalidades

- Registro e consulta de eventos com validação de IP, data, tipo e severidade.
- Regra demonstrativa: cinco ou mais falhas de login de um IP nos últimos dez minutos.
- Painel com indicadores, filtros e gráfico de severidade.
- Simulador de eventos e testes automatizados.
- Persistência local em SQLite e execução opcional com Docker.

Os IPs de exemplo são reservados para documentação. O projeto não varre redes, não bloqueia IPs e não detecta botnets, rootkits ou malware real. A API não tem autenticação e é destinada somente a uso local. Não exponha os serviços na internet ou use dados sensíveis.

## Executar localmente

Requer Python 3.12. No PowerShell, a partir desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python api.py
```

Em outro terminal, com o mesmo ambiente ativo:

```powershell
python simular.py
streamlit run dashboard.py --server.port 8502
```

Abra http://localhost:8502. O simulador adiciona novos eventos a cada execução. A regra de alerta considera somente os últimos dez minutos em UTC; o alerta desaparece após esse período. A lista é limitada aos 1.000 eventos mais recentes. O banco fica em `data/eventos.db`.

## Docker

Com Docker e Docker Compose instalados:

```bash
docker compose up --build -d
docker compose exec api python simular.py
```

Acesse http://localhost:8502. Para parar: `docker compose down`. O volume nomeado mantém os dados entre reinícios. As portas são publicadas apenas em localhost.

## API

- `GET /saude`: estado básico do serviço.
- `GET /eventos`: eventos, com filtros opcionais `tipo` e `severidade`.
- `POST /eventos`: registra evento JSON com `timestamp` ISO 8601 com fuso, `ip`, `tipo`, `severidade` e `descricao`.
- `GET /alertas`: resultados da regra de falhas de login.

A API é um laboratório sem autenticação, limitação de requisições ou coleta em tempo real; não representa um SIEM de produção. Valores de severidade: `baixa`, `media`, `alta`, `critica`. Tipos: `login_falho`, `login_sucesso`, `alteracao_arquivo`, `conexao_suspeita`.

## Testes

```bash
python -m pytest -q
```

## Possíveis próximos passos

Importação validada de arquivos CSV, controles de acesso, migrações e integração opcional com Supabase. Antes de usar dados reais, avalie segurança, privacidade, autenticação, limites e operação.

**Criado por Douglas Honório.**


## Relatórios e importação

O painel mostra uma linha do tempo por hora em UTC e permite baixar um relatório HTML dos eventos filtrados. O navegador pode imprimir o relatório em PDF. Os alertas no relatório são gerais e representam a janela de dez minutos no instante da consulta.

Para importar dados fictícios, use a seção de importação no painel e selecione `exemplo_eventos.csv`. O arquivo deve ter UTF-8, cabeçalho `timestamp,ip,tipo,severidade,descricao`, no máximo 1 MB e 1.000 registros. A API valida o lote inteiro antes da gravação. A regra adicional identifica três alterações de arquivo do mesmo IP em dez minutos. Esses sinais são educacionais e não confirmam incidentes reais.
