# 🔌 API Documentation - FinBot

## 🤖 Visão Geral

O FinBot expõe uma API interna para processamento de dados financeiros e análise com IA. Esta documentação descreve as funções principais e como utilizá-las.

## 🏗️ Arquitetura

### **Estrutura Modular**
```
app/
├── backend.py          # API principal
├── config.py           # Configurações
├── paginas/            # Endpoints da UI
└── componentes/        # Componentes reutilizáveis
```

## 🔧 Funções Principais

### **Processamento de Dados**

#### `processar_faturas() -> pd.DataFrame`
Processa todas as faturas e extratos disponíveis.

**Parâmetros:**
- Nenhum

**Retorna:**
- `pd.DataFrame`: Dados consolidados com colunas:
  - `Data`: Data da transação
  - `Estabelecimento`: Nome do estabelecimento
  - `Valor`: Valor da transação
  - `Tipo`: 'Despesa' ou 'Receita'
  - `Categoria`: Categoria automática
  - `Pagador`: Quem pagou

**Exemplo:**
```python
from app.backend import processar_faturas

df = processar_faturas()
print(f"Processados {len(df)} registros")
```

#### `obter_periodos_disponiveis() -> dict`
Obtém os períodos disponíveis nos dados processados.

**Retorna:**
```python
{
    "anos": [2024, 2025],
    "meses_por_ano": {
        2024: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        2025: [1, 2, 3, 4, 5, 6, 7, 8]
    }
}
```

### **Análise com IA**

#### `prever_gastos(df_historico: pd.DataFrame, meses_a_frente: int = 6) -> dict`
Sistema avançado de previsão financeira com três cenários.

**Parâmetros:**
- `df_historico`: DataFrame com dados históricos
- `meses_a_frente`: Número de meses para prever (padrão: 6)

**Retorna:**
```python
{
    "previsoes": pd.DataFrame,  # Cenários otimista, normal, pessimista
    "explicacoes": dict,        # Explicações lógicas
    "outliers_detectados": int,  # Número de outliers
    "qualidade_dados": dict      # Métricas de qualidade
}
```

#### `chatbot_financeiro(dfs: list, user_input: str) -> str`
Interface de chat com IA para análise de dados.

**Parâmetros:**
- `dfs`: Lista de DataFrames com dados
- `user_input`: Pergunta do usuário

**Retorna:**
- `str`: Resposta da IA

**Exemplo:**
```python
from app.backend import chatbot_financeiro

resposta = chatbot_financeiro([df], "Qual foi meu maior gasto em julho?")
print(resposta)
```

### **Geração de Relatórios**

#### `gerar_relatorio_pdf(df_completo: pd.DataFrame, ano: int, mes: int) -> str`
Gera relatório PDF mensal com análises.

**Parâmetros:**
- `df_completo`: Dados consolidados
- `ano`: Ano do relatório
- `mes`: Mês do relatório

**Retorna:**
- `str`: Caminho do arquivo PDF gerado

### **Configuração**

#### `salvar_configuracao_modelo(modelo_selecionado: str) -> bool`
Salva configuração do modelo de IA.

**Parâmetros:**
- `modelo_selecionado`: Nome do modelo (ex: "gpt-4.1-nano")

**Retorna:**
- `bool`: True se salvo com sucesso

#### `carregar_configuracao_modelo() -> str`
Carrega configuração do modelo salva.

**Retorna:**
- `str`: Nome do modelo configurado

## 🔒 Segurança

### **Validação de Entrada**
Todas as funções implementam validação rigorosa:

```python
# Exemplo de validação
if not SecurityConfig.validate_input_length(user_input):
    return "Entrada muito longa"
```

### **Rate Limiting**
Controle de chamadas de API:

```python
if not rate_limiter.can_call():
    raise Exception("Rate limit exceeded")
```

### **Sanitização de Dados**
Proteção contra dados maliciosos:

```python
if not SecurityConfig.validate_file_path(file_path):
    raise ValueError("Invalid file path")
```

## 📊 Exemplos de Uso

### **Análise Completa de Dados**
```python
from app.backend import processar_faturas, prever_gastos, chatbot_financeiro

# 1. Processar dados
df = processar_faturas()

# 2. Gerar previsões
previsoes = prever_gastos(df, meses_a_frente=6)

# 3. Fazer perguntas
resposta = chatbot_financeiro([df], "Analise meus gastos por categoria")
print(resposta)
```

### **Geração de Relatório**
```python
from app.backend import gerar_relatorio_pdf

# Gerar relatório para janeiro de 2025
pdf_path = gerar_relatorio_pdf(df, 2025, 1)
print(f"Relatório gerado: {pdf_path}")
```

### **Configuração de Modelo**
```python
from app.backend import salvar_configuracao_modelo, carregar_configuracao_modelo

# Salvar novo modelo
salvar_configuracao_modelo("gpt-4o")

# Carregar modelo atual
modelo_atual = carregar_configuracao_modelo()
print(f"Modelo atual: {modelo_atual}")
```

## 🧪 Testes

### **Executar Testes da API**
```bash
# Testes unitários
pytest tests/test_backend.py -v

# Testes de integração
pytest tests/test_api_integration.py -v

# Cobertura de código
pytest --cov=app.backend tests/
```

### **Exemplo de Teste**
```python
def test_processar_faturas():
    """Testa processamento de faturas."""
    df = processar_faturas()
    assert not df.empty
    assert 'Data' in df.columns
    assert 'Valor' in df.columns
```

## 🔍 Debugging

### **Função de Debug**
```python
from app.backend import debug_dados_previsao

# Analisar qualidade dos dados
debug_info = debug_dados_previsao(df)
print(debug_info)
```

### **Logs Detalhados**
```python
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Usar em funções
logger.info("Processando dados...")
logger.error("Erro encontrado: %s", error)
```

## 📈 Performance

### **Otimizações Implementadas**
- ✅ **Cache Inteligente**: Evita reprocessamento
- ✅ **Processamento Lazy**: Carrega dados sob demanda
- ✅ **Compressão**: Reduz uso de memória
- ✅ **Paralelização**: Processamento em threads

### **Métricas de Performance**
```python
import time

start_time = time.time()
df = processar_faturas()
end_time = time.time()

print(f"Tempo de processamento: {end_time - start_time:.2f}s")
print(f"Registros processados: {len(df)}")
```

## 🚀 Extensibilidade

### **Adicionando Novas Funções**
```python
# 1. Adicionar função no backend.py
def nova_analise(df: pd.DataFrame) -> dict:
    """Nova análise personalizada."""
    # Implementação
    return resultado

# 2. Adicionar teste
def test_nova_analise():
    """Testa nova análise."""
    df = criar_dados_teste()
    resultado = nova_analise(df)
    assert resultado is not None

# 3. Documentar na API
```

---

**Última atualização**: Janeiro 2025 