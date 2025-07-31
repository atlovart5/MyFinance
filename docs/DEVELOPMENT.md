# 🛠️ Guia de Desenvolvimento - FinBot

## 🎯 Visão Geral

Este guia fornece informações detalhadas para desenvolvedores que desejam contribuir ou modificar o FinBot.

## 🏗️ Arquitetura do Sistema

### **Estrutura Modular**
```
finbot_project/
├── app/                    # Código principal da aplicação
│   ├── app.py             # Ponto de entrada Streamlit
│   ├── backend.py         # Lógica de negócio e IA
│   ├── config.py          # Configurações centralizadas
│   ├── layout.py          # Layout da interface
│   ├── paginas/           # Páginas da aplicação
│   └── componentes/       # Componentes reutilizáveis
├── data/                  # Dados do usuário
├── tests/                 # Testes automatizados
├── docs/                  # Documentação
└── logs/                  # Logs da aplicação
```

### **Fluxo de Dados**
```
1. Upload de CSV → 2. Processamento → 3. Análise IA → 4. Visualização
```

## 🔧 Configuração do Ambiente

### **1. Pré-requisitos**
```bash
# Python 3.8+
python --version

# Git
git --version

# Docker (opcional)
docker --version
```

### **2. Setup do Ambiente**
```bash
# Clone o repositório
git clone https://github.com/finbot/finbot_project.git
cd finbot_project

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure ambiente
cp env.example .env
# Edite .env com suas configurações
```

### **3. Configuração de Desenvolvimento**
```env
# .env para desenvolvimento
DEBUG=true
LOG_LEVEL=DEBUG
TESTING=true
ALLOW_DANGEROUS_CODE=true
OPENAI_API_KEY=sk-your-test-key
```

## 🧪 Testes

### **Executar Testes**
```bash
# Todos os testes
python run_tests.py

# Testes específicos
pytest tests/test_backend.py -v

# Com cobertura
pytest --cov=app tests/ --cov-report=html

# Testes de performance
pytest tests/test_performance.py -v
```

### **Escrever Testes**
```python
# tests/test_backend.py
import pytest
from app.backend import processar_faturas

def test_processar_faturas():
    """Testa processamento de faturas."""
    # Arrange
    # Criar dados de teste
    
    # Act
    resultado = processar_faturas()
    
    # Assert
    assert resultado is not None
    assert len(resultado) > 0
    assert 'Data' in resultado.columns
```

### **Testes de Integração**
```python
# tests/test_integration.py
def test_fluxo_completo():
    """Testa fluxo completo da aplicação."""
    # 1. Upload de dados
    # 2. Processamento
    # 3. Análise IA
    # 4. Geração de relatório
    pass
```

## 🔍 Debugging

### **1. Logs Detalhados**
```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/finbot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### **2. Debug no Streamlit**
```python
# Adicionar ao app.py
import streamlit as st

if st.checkbox("Debug Mode"):
    st.write("Debug info:", debug_info)
    st.write("Session state:", st.session_state)
```

### **3. Profiling**
```python
import cProfile
import pstats

def profile_function(func):
    """Decorator para profiling."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        return result
    return wrapper
```

## 📊 Análise de Performance

### **1. Métricas de Performance**
```python
import time
import psutil

def measure_performance(func):
    """Decorator para medir performance."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        print(f"Tempo: {end_time - start_time:.2f}s")
        print(f"Memória: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
        
        return result
    return wrapper
```

### **2. Otimizações**
```python
# Cache inteligente
@st.cache_data(ttl=3600)
def processar_dados_cached():
    return processar_faturas()

# Processamento lazy
def lazy_load_data():
    if 'data' not in st.session_state:
        st.session_state.data = processar_faturas()
    return st.session_state.data
```

## 🔒 Segurança

### **1. Validação de Entrada**
```python
import re
from typing import Optional

def validate_input(text: str, max_length: int = 1000) -> Optional[str]:
    """Valida entrada do usuário."""
    if len(text) > max_length:
        return "Entrada muito longa"
    
    # Remover caracteres perigosos
    text = re.sub(r'[<>"\']', '', text)
    
    return text
```

### **2. Sanitização de Arquivos**
```python
import os
from pathlib import Path

def validate_file_path(file_path: str) -> bool:
    """Valida caminho de arquivo."""
    try:
        path = Path(file_path).resolve()
        return str(path).startswith(str(Path.cwd()))
    except:
        return False
```

## 🚀 Deploy de Desenvolvimento

### **1. Docker Development**
```bash
# Build para desenvolvimento
docker build -t finbot:dev .

# Run com volumes para desenvolvimento
docker run -d \
  --name finbot-dev \
  -p 8501:8501 \
  -v $(pwd)/app:/app/app \
  -v $(pwd)/data:/app/data \
  -e DEBUG=true \
  finbot:dev
```

### **2. Hot Reload**
```bash
# Streamlit com hot reload
streamlit run app/app.py --server.runOnSave=true
```

## 📝 Documentação

### **1. Docstrings**
```python
def processar_faturas() -> pd.DataFrame:
    """
    Processa todas as faturas e extratos disponíveis.
    
    Returns:
        pd.DataFrame: Dados consolidados com colunas:
            - Data: Data da transação
            - Estabelecimento: Nome do estabelecimento
            - Valor: Valor da transação
            - Tipo: 'Despesa' ou 'Receita'
            - Categoria: Categoria automática
            - Pagador: Quem pagou
    
    Raises:
        FileNotFoundError: Se não encontrar arquivos CSV
        ValueError: Se formato de arquivo for inválido
    
    Example:
        >>> df = processar_faturas()
        >>> print(f"Processados {len(df)} registros")
    """
    pass
```

### **2. Type Hints**
```python
from typing import Dict, List, Optional, Union
import pandas as pd

def prever_gastos(
    df_historico: pd.DataFrame,
    meses_a_frente: int = 6
) -> Dict[str, Union[pd.DataFrame, Dict, int]]:
    """Previsão de gastos com IA."""
    pass
```

## 🔄 CI/CD

### **1. GitHub Actions**
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### **2. Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## 🎯 Boas Práticas

### **1. Código Limpo**
- ✅ Use nomes descritivos
- ✅ Funções pequenas e focadas
- ✅ Evite duplicação de código
- ✅ Documente funções complexas

### **2. Performance**
- ✅ Use cache quando apropriado
- ✅ Evite processamento desnecessário
- ✅ Monitore uso de memória
- ✅ Otimize consultas de dados

### **3. Segurança**
- ✅ Valide todas as entradas
- ✅ Sanitize dados do usuário
- ✅ Use HTTPS em produção
- ✅ Mantenha dependências atualizadas

### **4. Testes**
- ✅ Escreva testes para novas funcionalidades
- ✅ Mantenha cobertura de código alta
- ✅ Teste casos de erro
- ✅ Use mocks para dependências externas

## 🆘 Troubleshooting

### **Problemas Comuns**

#### **1. Erro de Import**
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Verificar instalação
pip list | grep streamlit
```

#### **2. Erro de Memória**
```python
# Limpar cache
st.cache_data.clear()
st.cache_resource.clear()

# Garbage collection
import gc
gc.collect()
```

#### **3. Erro de API**
```python
# Verificar configuração
import os
print("API Key:", os.getenv("OPENAI_API_KEY")[:10] + "...")

# Testar conexão
import openai
try:
    openai.Model.list()
    print("API conectada!")
except Exception as e:
    print("Erro na API:", e)
```

---

**Última atualização**: Janeiro 2025 