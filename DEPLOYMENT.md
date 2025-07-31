# 🚀 Guia de Deploy - FinBot

## 📋 Visão Geral

Este guia fornece instruções detalhadas para fazer deploy do FinBot em diferentes ambientes.

## 🏗️ Arquitetura de Deploy

### **Componentes**
- **Aplicação Web**: Streamlit (porta 8501)
- **Dados**: Sistema de arquivos local
- **Cache**: Sistema de cache em memória
- **Logs**: Sistema de logging estruturado

### **Requisitos Mínimos**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB
- **OS**: Linux, Windows, macOS

## 🐳 Deploy com Docker

### **1. Deploy Rápido**
```bash
# Clone o repositório
git clone https://github.com/finbot/finbot_project.git
cd finbot_project

# Configure variáveis de ambiente
cp env.example .env
# Edite .env com suas configurações

# Execute com Docker Compose
docker-compose up -d
```

### **2. Deploy Manual**
```bash
# Construir imagem
docker build -t finbot:latest .

# Executar container
docker run -d \
  --name finbot \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e OPENAI_API_KEY=your-key-here \
  finbot:latest
```

### **3. Docker Compose Completo**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  finbot:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backup:/app/backup
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - finbot
    restart: unless-stopped
```

## ☁️ Deploy na Nuvem

### **AWS (EC2)**
```bash
# 1. Criar instância EC2
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-12345678

# 2. Conectar via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Instalar Docker
sudo apt update
sudo apt install docker.io docker-compose

# 4. Clonar e executar
git clone https://github.com/finbot/finbot_project.git
cd finbot_project
docker-compose up -d
```

### **Google Cloud Platform**
```bash
# 1. Criar instância
gcloud compute instances create finbot \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud

# 2. Conectar
gcloud compute ssh finbot --zone=us-central1-a

# 3. Deploy
git clone https://github.com/finbot/finbot_project.git
cd finbot_project
docker-compose up -d
```

### **Azure**
```bash
# 1. Criar VM
az vm create \
  --resource-group finbot-rg \
  --name finbot-vm \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser

# 2. Conectar
az vm open-port --resource-group finbot-rg --name finbot-vm --port 8501

# 3. Deploy
ssh azureuser@your-vm-ip
git clone https://github.com/finbot/finbot_project.git
cd finbot_project
docker-compose up -d
```

## 🏠 Deploy Local

### **1. Ambiente Virtual**
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp env.example .env
# Editar .env

# Executar
streamlit run app/app.py
```

### **2. Sistema de Serviço (Linux)**
```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/finbot.service

[Unit]
Description=FinBot Financial Assistant
After=network.target

[Service]
Type=simple
User=finbot
WorkingDirectory=/home/finbot/finbot_project
Environment=PATH=/home/finbot/venv/bin
ExecStart=/home/finbot/venv/bin/streamlit run app/app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target

# Habilitar e iniciar
sudo systemctl enable finbot
sudo systemctl start finbot
```

## 🔧 Configuração de Produção

### **1. Variáveis de Ambiente**
```env
# Produção
OPENAI_API_KEY=sk-your-production-key
OPENAI_MODEL=gpt-4.1-nano
ALLOW_DANGEROUS_CODE=true
LOG_LEVEL=WARNING
DEBUG=false

# Segurança
MAX_API_CALLS=50
RATE_LIMIT_WINDOW=60
VALIDATE_FILE_PATHS=true

# Performance
CACHE_ENABLED=true
CACHE_TTL=3600
```

### **2. Nginx (Proxy Reverso)**
```nginx
# /etc/nginx/sites-available/finbot
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### **3. SSL/HTTPS**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d your-domain.com

# Renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoramento

### **1. Logs**
```bash
# Ver logs em tempo real
tail -f logs/finbot.log

# Logs do Docker
docker logs -f finbot-app

# Logs do sistema
journalctl -u finbot -f
```

### **2. Métricas**
```python
# Adicionar ao app.py
import psutil
import streamlit as st

def show_metrics():
    st.metric("CPU Usage", f"{psutil.cpu_percent()}%")
    st.metric("Memory Usage", f"{psutil.virtual_memory().percent}%")
    st.metric("Disk Usage", f"{psutil.disk_usage('/').percent}%")
```

### **3. Health Check**
```bash
# Verificar saúde da aplicação
curl -f http://localhost:8501/_stcore/health

# Script de monitoramento
#!/bin/bash
if ! curl -f http://localhost:8501/_stcore/health; then
    echo "FinBot is down! Restarting..."
    docker-compose restart finbot
fi
```

## 🔒 Segurança

### **1. Firewall**
```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 8501 -j DROP
sudo iptables -A INPUT -p tcp --dport 8501 -s your-ip -j ACCEPT
```

### **2. Usuário Não-Root**
```bash
# Criar usuário
sudo adduser finbot
sudo usermod -aG docker finbot

# Executar como usuário
sudo -u finbot docker-compose up -d
```

### **3. Backup Automático**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup/finbot_$DATE.tar.gz data/
find backup/ -name "finbot_*.tar.gz" -mtime +7 -delete
```

## 🚀 CI/CD

### **1. GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy FinBot

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.4
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.KEY }}
        script: |
          cd finbot_project
          git pull
          docker-compose down
          docker-compose up -d --build
```

### **2. Docker Hub**
```bash
# Build e push
docker build -t finbot/finbot:latest .
docker push finbot/finbot:latest

# Pull e run
docker pull finbot/finbot:latest
docker run -d finbot/finbot:latest
```

## 🔧 Troubleshooting

### **Problemas Comuns**

#### **1. Porta 8501 não acessível**
```bash
# Verificar se está rodando
netstat -tlnp | grep 8501

# Verificar firewall
sudo ufw status
```

#### **2. Erro de permissão**
```bash
# Corrigir permissões
sudo chown -R finbot:finbot /path/to/finbot
sudo chmod -R 755 /path/to/finbot
```

#### **3. Problemas de memória**
```bash
# Verificar uso de memória
free -h
docker stats

# Limpar cache
docker system prune -a
```

#### **4. Logs de erro**
```bash
# Ver logs detalhados
docker logs finbot-app 2>&1 | grep ERROR

# Debug mode
streamlit run app/app.py --logger.level=debug
```

## 📈 Escalabilidade

### **1. Load Balancer**
```nginx
upstream finbot {
    server 127.0.0.1:8501;
    server 127.0.0.1:8502;
    server 127.0.0.1:8503;
}

server {
    listen 80;
    location / {
        proxy_pass http://finbot;
    }
}
```

### **2. Docker Swarm**
```yaml
# docker-stack.yml
version: '3.8'
services:
  finbot:
    image: finbot/finbot:latest
    deploy:
      replicas: 3
    ports:
      - "8501:8501"
```

### **3. Kubernetes**
```yaml
# finbot-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finbot
  template:
    metadata:
      labels:
        app: finbot
    spec:
      containers:
      - name: finbot
        image: finbot/finbot:latest
        ports:
        - containerPort: 8501
```

---

**Última atualização**: Janeiro 2025 