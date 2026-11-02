# Autoria: Douglas Honório · Projeto Dh73 CyberGuard SOC · 2026
"""Relatório HTML e leitura segura de exemplos CSV."""
import csv
import html
import io
from collections import Counter
from datetime import datetime, timezone

COLUNAS = ["timestamp", "ip", "tipo", "severidade", "descricao"]


def ler_csv(conteudo):
    if len(conteudo) > 1_000_000:
        raise ValueError("O arquivo deve ter no máximo 1 MB.")
    try:
        texto = conteudo.decode("utf-8-sig")
        leitor = csv.DictReader(io.StringIO(texto, newline=""), strict=True)
        if leitor.fieldnames != COLUNAS:
            raise ValueError("Cabeçalho esperado: " + ",".join(COLUNAS))
        registros = []
        for linha, registro in enumerate(leitor, start=2):
            if None in registro or any(v is None for v in registro.values()):
                raise ValueError(f"Linha {linha}: quantidade de colunas inválida.")
            registros.append(registro)
            if len(registros) > 1000:
                raise ValueError("O arquivo pode conter até 1.000 registros.")
        if not registros:
            raise ValueError("O arquivo não contém registros.")
        return registros
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("CSV inválido. Use UTF-8 e vírgula como separador.") from exc


def criar_relatorio(eventos, alertas, filtros):
    esc = lambda x: html.escape(str(x), quote=True)
    totais = Counter(e.get("tipo", "") for e in eventos)
    categorias = "".join(f"<li>{esc(k)}: <strong>{v}</strong></li>" for k, v in sorted(totais.items())) or "<li>Sem registros.</li>"
    linhas = "".join("<tr>" + "".join(f"<td>{esc(e.get(k, ''))}</td>" for k in COLUNAS) + "</tr>" for e in eventos)
    alertas_html = "".join(f"<li>{esc(a.get('ip', ''))} — {esc(a.get('regra', ''))} ({esc(a.get('total', 0))})</li>" for a in alertas) or "<li>Nenhum alerta no momento da consulta.</li>"
    gerado = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório CyberGuard SOC</title><style>body{{font:15px Arial;color:#122236;margin:40px}}
h1,h2{{color:#075277}}small{{color:#566}}table{{border-collapse:collapse;width:100%;font-size:12px}}
td,th{{border:1px solid #cad9e1;text-align:left;padding:7px;overflow-wrap:anywhere}}
th{{background:#e2f3f7}}@media print{{body{{margin:15px}}}}</style></head>
<body><h1>Dh73 CyberGuard SOC — Relatório de laboratório</h1>
<p>Gerado em {gerado} · Dados simulados · Até 1.000 eventos da consulta.</p>
<p>Filtros: tipo {esc(filtros.get('tipo', 'Todos'))}; severidade {esc(filtros.get('severidade', 'Todas'))}.</p>
<h2>Resumo</h2><p>Total de eventos filtrados: <strong>{len(eventos)}</strong></p><ul>{categorias}</ul>
<h2>Alertas gerais — janela de 10 minutos</h2><p>Os alertas não seguem os filtros da tabela e são uma fotografia no momento da consulta.</p><ul>{alertas_html}</ul>
<h2>Eventos filtrados</h2><table><thead><tr>{''.join(f'<th>{esc(k)}</th>' for k in COLUNAS)}</tr></thead><tbody>{linhas}</tbody></table>
<p><small>Projeto educacional · Criado por Douglas Honório.</small></p></body></html>"""

