# 🤖 Configuração do Chatbot FinBot

## ⚠️ Aviso de Segurança

O chatbot do FinBot utiliza execução de código Python para análise de dados. Esta funcionalidade requer configuração explícita de segurança.

## 🔧 Configuração Necessária

### 1. Arquivo .env

Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```env
# OpenAI Configuration (OBRIGATÓRIO)
OPENAI_API_KEY=sk-sua-chave-api-aqui

# Security Configuration (OBRIGATÓRIO para chatbot)
ALLOW_DANGEROUS_CODE=true
```

### 2. Obter Chave da API OpenAI

1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Faça login ou crie uma conta
3. Vá para "API Keys"
4. Clique em "Create new secret key"
5. Copie a chave e cole no arquivo `.env`

### 3. Configurações Opcionais

```env
# Modelo OpenAI (padrão: gpt-4.1-nano - mais rápido e econômico)
OPENAI_MODEL=gpt-4.1-nano

# Temperatura (padrão: 0.0)
OPENAI_TEMPERATURE=0.0

# Máximo de tokens (padrão: 4000)
MAX_TOKENS=4000

# Limite de chamadas API (padrão: 10)
MAX_API_CALLS=10

# Nível de log (padrão: INFO)
LOG_LEVEL=INFO
```

## 🚀 Como Usar

1. **Configure o arquivo .env** conforme instruções acima
2. **Processe seus dados** na aba "Processamento"
3. **Acesse a aba "Converse com seus Dados"**
4. **Faça perguntas** como:
   - "Qual foi meu maior gasto em julho?"
   - "Mostre meus gastos por categoria"
   - "Compare meus gastos de junho com julho"
   - "Quem gasta mais: eu ou meu pai?"
   - "Identifique gastos anômalos"
   - "Calcule minha taxa de poupança"

## 🔒 Segurança

- ✅ O código é executado em ambiente controlado
- ✅ Apenas operações de análise são permitidas
- ✅ Não há acesso a sistema de arquivos externo
- ✅ Validação de entrada rigorosa
- ✅ Rate limiting para evitar abuso

## ❗ Solução de Problemas

### Erro: "Dangerous code execution is disabled"
**Solução**: Configure `ALLOW_DANGEROUS_CODE=true` no arquivo `.env`

### Erro: "Invalid or missing OpenAI API key"
**Solução**: Configure sua chave da API OpenAI no arquivo `.env`

### Erro: "Não há dados disponíveis"
**Solução**: Processe seus dados primeiro na aba "Processamento"

### Erro: "Rate limit exceeded"
**Solução**: Aguarde alguns minutos e tente novamente

## 📊 Funcionalidades do Chatbot

- **Análise de Gastos**: Identifica padrões e anomalias
- **Comparações Temporais**: Compara períodos diferentes
- **Análise por Categoria**: Agrupa gastos por categoria
- **Análise por Pagador**: Compara gastos entre pessoas
- **Cálculos Financeiros**: Taxa de poupança, médias, etc.
- **Geração de Gráficos**: Visualizações automáticas
- **Recomendações**: Sugestões baseadas nos dados

## 🎯 Exemplos de Perguntas

```
"Qual foi meu maior gasto em julho?"
"Mostre meus gastos por categoria"
"Compare meus gastos de junho com julho"
"Quem gasta mais: eu ou meu pai?"
"Identifique gastos anômalos"
"Calcule minha taxa de poupança"
"Gere um gráfico de pizza dos gastos por categoria"
"Qual categoria tem o maior crescimento?"
"Quais são os estabelecimentos onde mais gasto?"
"Como estão meus gastos este mês comparado ao anterior?"
``` 