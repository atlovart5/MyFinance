# FinBot - Assistente Financeiro com IA
# Dockerfile para containerização

# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .
COPY setup.py .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/
COPY data/ ./data/
COPY fonts/ ./fonts/
COPY tests/ ./tests/

# Copiar arquivos de configuração
COPY *.md .
COPY *.py .
COPY .env.example .env

# Criar diretórios necessários
RUN mkdir -p logs backup

# Definir usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash finbot && \
    chown -R finbot:finbot /app
USER finbot

# Expor porta do Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando padrão
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"] 