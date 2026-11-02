# Dh73 CyberGuard SOC

Laboratório de segurança com eventos fictícios, API REST em Flask, SQLite e painel Streamlit. Criado por Douglas Honório para aprendizado e portfólio.

## Experimentar

[Abrir demonstração pública](https://dh73-cyberguard-soc.streamlit.app/) — eventos fictícios isolados na sessão, sem monitoramento real. A versão local inclui API, banco SQLite e importação de CSV.
## Funcionalidades

- Registro e consulta de eventos com validação de IP, data, tipo e severidade.
- Regras demonstrativas: cinco falhas de login ou três alterações de arquivo do mesmo IP em dez minutos.
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

## Demonstração para portfólio

O arquivo demo_publica.py funciona com dados fictícios isolados em cada sessão, sem iniciar a API nem persistir dados. Para executar: streamlit run demo_publica.py. Ao encerrar a sessão, os dados são perdidos. Esta versão educacional não aceita logs reais de clientes.

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

## Evolução para uso comercial

O CyberGuard é atualmente um laboratório local com dados fictícios. Os itens abaixo são objetivos futuros e ainda não são funcionalidades prontas para clientes.

1. **Acesso seguro:** adicionar autenticação, permissões por função, proteção das credenciais, limitação de requisições e conexões HTTPS.
2. **Dados e clientes:** avaliar PostgreSQL ou Supabase, migrações, backups com testes de restauração, retenção e isolamento comprovado entre clientes.
3. **Coleta e análise reais:** integrar fontes autorizadas, validar e normalizar logs, desenvolver novas regras e medir sua precisão e seus falsos positivos. As simulações atuais não comprovam a detecção de malware.
4. **Privacidade e governança:** definir quais dados serão tratados, sua finalidade e período de retenção; avaliar obrigações aplicáveis, inclusive a LGPD, e responsabilidades contratuais com orientação especializada.
5. **Operação e segurança:** estabelecer monitoramento da aplicação, trilhas de auditoria, resposta a incidentes, gestão de vulnerabilidades, atualizações e testes de segurança independentes.
6. **Qualidade e entrega:** ampliar testes de integração, carga e recuperação; automatizar verificações e testar o Docker em ambiente adequado.
7. **Oferta comercial:** validar o problema com potenciais clientes, definir público, funcionalidades, custos, suporte, termos de uso e modelo de cobrança.

A escolha da hospedagem deve considerar os termos de uso, a proteção dos dados e a continuidade do serviço. No Streamlit Community Cloud, o armazenamento local não garante persistência; não use esta demonstração para dados reais de clientes. Referências: [documentação do Streamlit](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data) e [guia de segurança da ANPD](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-publica-guia-de-seguranca-da-informacao-para-agentes-de-tratamento-de-pequeno-porte).



## Relatórios e importação

O painel mostra uma linha do tempo por hora em UTC e permite baixar um relatório HTML dos eventos filtrados. O navegador pode imprimir o relatório em PDF. Os alertas no relatório são gerais e representam a janela de dez minutos no instante da consulta.

Para importar dados fictícios, use a seção de importação no painel e selecione `exemplo_eventos.csv`. O arquivo deve ter UTF-8, cabeçalho `timestamp,ip,tipo,severidade,descricao`, no máximo 1 MB e 1.000 registros. A API valida o lote inteiro antes da gravação. A regra adicional identifica três alterações de arquivo do mesmo IP em dez minutos. Esses sinais são educacionais e não confirmam incidentes reais.

**Criado por Douglas Honório.**
