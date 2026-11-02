FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api.py dashboard.py simular.py cenarios.py relatorios.py logo.svg ./
ENV PYTHONUNBUFFERED=1

