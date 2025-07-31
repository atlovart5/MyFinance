# 🤖 Modelos de IA Disponíveis no FinBot

## 📋 Visão Geral

O FinBot oferece suporte a múltiplos modelos da OpenAI, permitindo que você escolha o modelo mais adequado para suas necessidades de análise financeira.

### 🎯 Modelo Padrão: GPT-4.1 Nano

O **GPT-4.1 Nano** é configurado como modelo padrão do sistema por ser:
- ⚡ **Mais rápido** - Respostas em tempo real
- 💰 **Mais econômico** - Menor custo por token  
- 🎯 **Ideal para análises financeiras** - Focado em tarefas práticas
- ✅ **Configurado automaticamente** - Não requer configuração manual

## 🚀 Modelos Disponíveis

### 1. GPT-4.1 Nano 🚀 (PADRÃO)
**Características:**
- ⚡ **Mais rápido** - Respostas em tempo real
- 💰 **Mais econômico** - Menor custo por token
- 🎯 **Focado** - Ideal para análises rápidas
- 📊 **Eficiente** - Boa performance para tarefas básicas
- ✅ **Modelo Padrão** - Configurado automaticamente

**Melhor para:**
- Perguntas simples sobre gastos
- Cálculos básicos
- Resumos rápidos
- Análises de padrões simples

**Custo:** ~$0.0001 por 1K tokens

---

### 2. GPT-4o Mini ⚡
**Características:**
- ⚖️ **Equilibrado** - Boa relação custo-benefício
- 🎯 **Preciso** - Análises moderadamente complexas
- ⚡ **Rápido** - Performance otimizada
- 💡 **Inteligente** - Boa compreensão de contexto

**Melhor para:**
- Análises comparativas
- Identificação de padrões
- Recomendações financeiras
- Relatórios detalhados

**Custo:** ~$0.00015 por 1K tokens

---

### 3. GPT-4o 🧠
**Características:**
- 🧠 **Mais avançado** - Máxima precisão
- 🎯 **Contexto profundo** - Melhor compreensão
- 📈 **Análises complexas** - Insights sofisticados
- 🔍 **Detalhado** - Respostas mais elaboradas

**Melhor para:**
- Análises financeiras complexas
- Estratégias de investimento
- Relatórios executivos
- Insights avançados

**Custo:** ~$0.005 por 1K tokens

---

### 4. GPT-3.5 Turbo 💡
**Características:**
- 🛡️ **Estável** - Performance consistente
- 💰 **Acessível** - Custo moderado
- ⚡ **Confiável** - Respostas previsíveis
- 🎯 **Versátil** - Boa para tarefas gerais

**Melhor para:**
- Tarefas gerais de análise
- Explicações simples
- Resumos básicos
- Consultas frequentes

**Custo:** ~$0.0005 por 1K tokens

## 🎯 Como Escolher o Modelo Ideal

### Para Análises Rápidas e Simples
**Recomendação:** GPT-4.1 Nano
- Perguntas como "Qual foi meu maior gasto?"
- Cálculos básicos
- Resumos mensais

### Para Análises Moderadas
**Recomendação:** GPT-4o Mini
- Comparações entre períodos
- Identificação de padrões
- Recomendações básicas

### Para Análises Complexas
**Recomendação:** GPT-4o
- Estratégias financeiras
- Relatórios executivos
- Insights avançados

### Para Uso Geral
**Recomendação:** GPT-3.5 Turbo
- Tarefas diárias
- Consultas frequentes
- Análises básicas

## ⚙️ Como Alterar o Modelo

### Modelo Padrão
O **GPT-4.1 Nano** é usado automaticamente como padrão. Não é necessário fazer nenhuma configuração para começar a usar o sistema.

### Alterar o Modelo
1. **Acesse a aba "Configurações"**
2. **Vá para a seção "Configurações"**
3. **Selecione o modelo desejado** no dropdown (GPT-4.1 Nano é o primeiro)
4. **Clique em "Salvar Configurações"**

## 💰 Considerações de Custo

### Estimativa de Custos (por 1000 tokens)

| Modelo | Custo Aproximado |
|--------|------------------|
| GPT-4.1 Nano | $0.0001 |
| GPT-4o Mini | $0.00015 |
| GPT-3.5 Turbo | $0.0005 |
| GPT-4o | $0.005 |

### Exemplo de Uso
Uma análise típica de gastos mensais usa aproximadamente:
- **Pergunta simples:** 50-100 tokens
- **Análise moderada:** 200-500 tokens
- **Relatório detalhado:** 1000-2000 tokens

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```env
# Modelo padrão
OPENAI_MODEL=gpt-4.1-nano

# Configurações de performance
OPENAI_TEMPERATURE=0.0
MAX_TOKENS=4000
```

### Configuração via Interface
- Acesse **Configurações > Configurações**
- Selecione o modelo desejado
- Ajuste temperatura e tokens conforme necessário
- Salve as configurações

## 📊 Comparação de Performance

| Aspecto | GPT-4.1 Nano | GPT-4o Mini | GPT-4o | GPT-3.5 Turbo |
|---------|--------------|-------------|--------|---------------|
| Velocidade | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Precisão | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Custo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Complexidade | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🎯 Dicas de Uso

### Para Economizar Custos
1. Use GPT-4.1 Nano para perguntas simples
2. Faça perguntas específicas e diretas
3. Evite análises desnecessariamente complexas

### Para Máxima Precisão
1. Use GPT-4o para análises críticas
2. Forneça contexto detalhado
3. Peça explicações específicas

### Para Uso Diário
1. Use GPT-4o Mini como padrão
2. Ajuste conforme a complexidade da análise
3. Monitore os custos regularmente

## 🔄 Mudança de Modelo

O modelo selecionado será usado em:
- ✅ Chatbot (Converse com seus Dados)
- ✅ Geração de relatórios PDF
- ✅ Análises automáticas
- ✅ Recomendações financeiras

A mudança é aplicada imediatamente após salvar as configurações. 