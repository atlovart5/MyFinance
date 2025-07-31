# CÓDIGO CORRIGIDO
# finbot_project/app/backend.py

import pandas as pd
import glob
import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import RobustScaler
import time
from typing import Optional, Dict, Any, Tuple, List, Union
import logging
import functools
import pickle
import hashlib
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
import warnings


# Import configuration
from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# --- Security and Configuration ---
class SecurityConfig:
    """Security configuration and validation."""

    @staticmethod
    def validate_api_key() -> bool:
        """Validate OpenAI API key format."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            return False
        if not api_key.startswith('sk-'):
            logger.error("Invalid OpenAI API key format")
            return False
        return True

    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path for security."""
        if not config.VALIDATE_FILE_PATHS:
            return True
        if not file_path or '..' in file_path:
            return False
        return True

    @staticmethod
    def validate_input_length(text: str) -> bool:
        """Validate input length for security."""
        return len(text) <= config.MAX_INPUT_LENGTH

class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int = None, time_window: int = None):
        self.max_calls = max_calls or config.MAX_API_CALLS
        self.time_window = time_window or config.RATE_LIMIT_WINDOW
        self.calls = []

    def can_call(self) -> bool:
        """Check if API call is allowed."""
        now = time.time()
        # Remove old calls
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False

# Global rate limiter
rate_limiter = RateLimiter()

# --- Performance Optimizations ---
class DataCache:
    """Simple caching system for processed data."""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or config.PASTA_CACHE
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, data: Any) -> str:
        """Generate cache key from data."""
        if isinstance(data, str):
            return hashlib.md5(data.encode()).hexdigest()
        return hashlib.md5(str(data).encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get cached data."""
        if not config.CACHE_ENABLED:
            return None

        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache {key}: {e}")
        return None

    def set(self, key: str, data: Any):
        """Set cached data."""
        if not config.CACHE_ENABLED:
            return

        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to save cache {key}: {e}")

# Global cache instance
data_cache = DataCache()

def cached_function(func):
    """Decorator for caching function results."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not config.CACHE_ENABLED:
            return func(*args, **kwargs)

        # Create cache key from function name and arguments
        cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"

        # Try to get from cache
        cached_result = data_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Execute function and cache result
        result = func(*args, **kwargs)
        data_cache.set(cache_key, result)
        return result
    return wrapper

# --- Funções de Manipulação de JSON ---
def carregar_json(caminho_arquivo: str) -> dict:
    if not os.path.exists(caminho_arquivo): return {}
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return {}

def salvar_json(caminho_arquivo: str, dados: dict):
    os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
    with open(caminho_arquivo, 'w', encoding='utf-8') as f: json.dump(dados, f, indent=4, ensure_ascii=False)

def atualizar_contexto_pagador(estabelecimento: str, pagador: str):
    contexto = carregar_json(str(config.ARQUIVO_CONTEXTO))
    if estabelecimento in contexto: contexto[estabelecimento]['pagador'] = pagador
    else: contexto[estabelecimento] = {"pagador": pagador, "categoria": "Não Definida"}
    salvar_json(str(config.ARQUIVO_CONTEXTO), contexto)

# --- Funções de processamento específicas para cada tipo de extrato ---
def processar_extrato_credito(caminho_arquivo: str) -> pd.DataFrame:
    """Lê e padroniza um arquivo de extrato de CRÉDITO."""
    try:
        if not SecurityConfig.validate_file_path(caminho_arquivo):
            raise ValueError("Invalid file path")
            
        # Check file size
        file_size = os.path.getsize(caminho_arquivo)
        if file_size > config.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max: {config.MAX_FILE_SIZE})")
            
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', dayfirst=True, skipinitialspace=True)
        df = df.rename(columns=lambda col: col.strip())
        
        mapeamento = {
            'Data movimento': 'Data',
            'Nome do fornecedor/cliente': 'Estabelecimento',
            'Valor (R$)': 'Valor'
        }
        df = df.rename(columns=mapeamento)

        if 'Valor' in df.columns:
            df['Valor'] = (df['Valor'].astype(str)
                           .str.replace('R$', '', regex=False).str.replace('.', '', regex=False)
                           .str.strip().str.replace(',', '.', regex=False))
            
            # Better error handling for numeric conversion
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            invalid_values = df['Valor'].isna().sum()
            if invalid_values > 0:
                logger.warning(f"Found {invalid_values} invalid values in 'Valor' column")
            
            # --- LÓGICA PARA CRÉDITO ---
            # No crédito, todas as transações são despesas e vêm com valor positivo.
            # Convertemos para negativo para padronizar.
            df['Valor'] = -abs(df['Valor'])
        
        df['Tipo'] = 'Despesa'
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce', dayfirst=True)
            
        # Validate required columns
        required_cols = ['Data', 'Estabelecimento', 'Valor', 'Tipo']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        return df[required_cols]
        
    except Exception as e:
        logger.error(f"Error processing credit file {caminho_arquivo}: {str(e)}")
        raise

def processar_extrato_debito(caminho_arquivo: str) -> pd.DataFrame:
    """Lê e padroniza um arquivo de extrato de DÉBITO."""
    try:
        if not SecurityConfig.validate_file_path(caminho_arquivo):
            raise ValueError("Invalid file path")
            
        # Check file size
        file_size = os.path.getsize(caminho_arquivo)
        if file_size > config.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max: {config.MAX_FILE_SIZE})")
            
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', dayfirst=True, skipinitialspace=True)
        df = df.rename(columns=lambda col: col.strip())
        
        mapeamento = {
            'Data': 'Data',
            'Descricao': 'Estabelecimento',
            'Valor': 'Valor' 
        }
        df = df.rename(columns=mapeamento)

        if 'Data' in df.columns:
            df['Data'] = df['Data'].astype(str).str.split(' às').str[0]
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce', dayfirst=True)

        if 'Valor' in df.columns:
            df['Valor'] = (df['Valor'].astype(str)
                           .str.replace('R$', '', regex=False).str.replace('.', '', regex=False)
                           .str.strip().str.replace(',', '.', regex=False))
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

        # --- LÓGICA PARA DÉBITO ---
        # No débito, o sinal do valor já indica se é entrada ou saída.
        # Criamos a coluna 'Tipo' com base nesse sinal.
        df['Tipo'] = np.where(df['Valor'] >= 0, 'Receita', 'Despesa')

        required_cols = ['Data', 'Estabelecimento', 'Valor', 'Tipo']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        return df[required_cols].dropna()
        
    except Exception as e:
        logger.error(f"Error processing debit file {caminho_arquivo}: {str(e)}")
        raise

def carregar_dados_brutos() -> pd.DataFrame | None:
    """Carrega e consolida dados de múltiplas fontes (crédito e débito)."""
    lista_dataframes = []
    
    try:
        config.PASTA_CREDITO.mkdir(parents=True, exist_ok=True)
        for arquivo in glob.glob(str(config.PASTA_CREDITO / "*.csv")):
            try:
                logger.info(f"Processando crédito: {os.path.basename(arquivo)}")
                df_credito = processar_extrato_credito(arquivo)
                if not df_credito.empty:
                    lista_dataframes.append(df_credito)
            except Exception as e:
                logger.error(f"Erro ao processar '{os.path.basename(arquivo)}': {e}")
                continue

        config.PASTA_DEBITO.mkdir(parents=True, exist_ok=True)
        for arquivo in glob.glob(str(config.PASTA_DEBITO / "*.csv")):
            try:
                logger.info(f"Processando débito: {os.path.basename(arquivo)}")
                df_debito = processar_extrato_debito(arquivo)
                if not df_debito.empty:
                    lista_dataframes.append(df_debito)
            except Exception as e:
                logger.error(f"Erro ao processar '{os.path.basename(arquivo)}': {e}")
                continue

        if not lista_dataframes:
            logger.warning("No valid data files found")
            return None

        df_completo = pd.concat(lista_dataframes, ignore_index=True).dropna(subset=['Data', 'Valor'])
        
        estabelecimentos_a_ignorar = ['pagamento de fatura', 'pagamentos validos normais']
        if 'Estabelecimento' in df_completo.columns:
            df_completo['Estabelecimento'] = df_completo['Estabelecimento'].astype(str)
            mascara_ignorar = df_completo['Estabelecimento'].str.strip().str.lower().isin(estabelecimentos_a_ignorar)
            df_completo = df_completo[~mascara_ignorar]

        return df_completo.sort_values(by='Data', ascending=False).reset_index(drop=True)

    except Exception as e:
        logger.error(f"Error loading raw data: {str(e)}")
        return None

# --- Funções existentes ---
@pd.api.extensions.register_dataframe_accessor("finbot")
class FinBotAccessor:
    def __init__(self, pandas_obj): self._obj = pandas_obj
    def limpar_valor(self): pass
    def limpar_data(self): pass
    def renomear_colunas_padrao(self): pass

# --- Enhanced Categorization Algorithm ---
class CategorizadorInteligente:
    """Sistema inteligente de categorização de estabelecimentos."""
    
    def __init__(self):
        self.palavras_chave = {
            'Alimentação': [
                'restaurante', 'lanche', 'pizza', 'hamburger', 'cafe', 'bar', 'padaria',
                'supermercado', 'mercado', 'ifood', 'uber eats', 'rappi', 'delivery',
                'fast food', 'sorveteria', 'doceria', 'confeitaria', 'açougue', 'hortifruti'
            ],
            'Transporte': [
                'uber', '99', 'taxi', 'onibus', 'metro', 'trem', 'posto', 'combustivel',
                'gasolina', 'etanol', 'diesel', 'estacionamento', 'pedagio', 'uber*',
                'lyft', 'cabify', 'estacionamento', 'parking', 'whoosh', 'ec'
            ],
            'Saúde': [
                'farmacia', 'drogaria', 'hospital', 'clinica', 'medico', 'dentista',
                'laboratorio', 'exame', 'consulta', 'remedio', 'panvel', 'raia',
                'drogasil', 'drogaraia', 'ultrafarma'
            ],
            'Educação': [
                'universidade', 'faculdade', 'escola', 'curso', 'livraria', 'papelaria',
                'material escolar', 'mensalidade', 'matricula', 'saraiva', 'cultura',
                'livraria', 'estante virtual'
            ],
            'Lazer': [
                'cinema', 'teatro', 'show', 'concerto', 'museu', 'parque', 'jogos',
                'steam', 'netflix', 'spotify', 'youtube', 'disney', 'hbo', 'amazon',
                'shopping', 'mall', 'loja', 'renner', 'riachuelo', 'c&a'
            ],
            'Moradia': [
                'aluguel', 'condominio', 'iptu', 'agua', 'luz', 'gas', 'internet',
                'energia', 'sabesp', 'enel', 'energisa', 'oi', 'vivo', 'claro',
                'tim', 'net', 'claro', 'sky', 'directv'
            ],
            'Assinatura': [
                'netflix', 'spotify', 'youtube', 'disney', 'hbo', 'amazon prime',
                'apple', 'google', 'microsoft', 'adobe', 'canva', 'notion',
                'ifood club', 'uber pass', '99 pass'
            ],
            'Investimento': [
                'nubank', 'inter', 'itau', 'bradesco', 'santander', 'bb',
                'rico', 'xp', 'clear', 'easynvest', 'btg', 'modalmais'
            ]
        }
    
    def calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """Calcula a similaridade entre dois textos."""
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()
    
    def encontrar_melhor_categoria(self, estabelecimento: str) -> tuple:
        """Encontra a melhor categoria para um estabelecimento."""
        estabelecimento_limpo = re.sub(r'[^\w\s]', '', estabelecimento.lower())
        
        melhor_categoria = "Outros"
        melhor_score = 0.0
        
        for categoria, palavras in self.palavras_chave.items():
            for palavra in palavras:
                # Verificar se a palavra está contida no estabelecimento
                if palavra in estabelecimento_limpo:
                    score = len(palavra) / len(estabelecimento_limpo)
                    if score > melhor_score:
                        melhor_score = score
                        melhor_categoria = categoria
                
                # Calcular similaridade
                similaridade = self.calcular_similaridade(estabelecimento_limpo, palavra)
                if similaridade > 0.8 and similaridade > melhor_score:
                    melhor_score = similaridade
                    melhor_categoria = categoria
        
        return melhor_categoria, melhor_score
    
    def categorizar_estabelecimento(self, estabelecimento: str) -> str:
        """Categoriza um estabelecimento usando IA e regras."""
        categoria, score = self.encontrar_melhor_categoria(estabelecimento)
        
        # Se o score for muito baixo, usar "Outros"
        if score < 0.3:
            return "Outros"
        
        return categoria

# Instância global do categorizador
categorizador = CategorizadorInteligente()

def aplicar_regras_contexto(df: pd.DataFrame, contexto: dict) -> pd.DataFrame:
    """Aplica regras de contexto com categorização inteligente."""
    df_copy = df.copy()
    
    def get_info(estabelecimento, tipo_info):
        # Primeiro, verificar se já existe no contexto
        if estabelecimento in contexto:
            return contexto[estabelecimento].get(tipo_info)
        
        # Verificar por correspondência parcial
        for keyword, info in contexto.items():
            if keyword.lower() in str(estabelecimento).lower():
                return info.get(tipo_info)
        
        return None
    
    # Aplicar categorização
    df_copy['Categoria'] = df_copy['Estabelecimento'].apply(
        lambda x: get_info(x, 'categoria') or categorizador.categorizar_estabelecimento(x)
    )
    
    # Aplicar pagador
    df_copy['Pagador'] = df_copy['Estabelecimento'].apply(
        lambda x: get_info(x, 'pagador')
    )
    
    return df_copy

@cached_function
def processar_faturas() -> pd.DataFrame:
    """Processa todas as faturas usando o sistema avançado de processamento."""
    try:
        # Use the new data processor
        df_completo, validation_results = data_processor.process_all_files()
        
        if df_completo.empty:
            logger.warning("No data found to process")
            return pd.DataFrame()
        
        # Log validation results
        total_processed = sum(v.processed_rows for v in validation_results)
        total_invalid = sum(v.invalid_rows for v in validation_results)
        total_errors = sum(len(v.errors) for v in validation_results)
        total_warnings = sum(len(v.warnings) for v in validation_results)
        
        logger.info(f"Data processing completed:")
        logger.info(f"  - Total rows processed: {total_processed}")
        logger.info(f"  - Invalid rows: {total_invalid}")
        logger.info(f"  - Errors: {total_errors}")
        logger.info(f"  - Warnings: {total_warnings}")
        
        # Carregar contexto financeiro
        contexto = carregar_json(str(config.ARQUIVO_CONTEXTO))
        
        # Aplicar regras de contexto
        df_completo = aplicar_regras_contexto(df_completo, contexto)
        
        # Salvar dados consolidados
        config.PASTA_PROCESSADOS.mkdir(parents=True, exist_ok=True)
        df_completo.to_csv(str(config.ARQUIVO_CONSOLIDADO), index=False, sep=';', encoding='utf-8')
        
        return df_completo
        
    except Exception as e:
        logger.error(f"Error processing invoices: {str(e)}")
        return pd.DataFrame()

def obter_periodos_disponiveis() -> dict:
    """
    Obtém os períodos disponíveis nos dados processados.
    Retorna um dicionário com anos e meses disponíveis.
    """
    try:
        if config.ARQUIVO_CONSOLIDADO.exists():
            df = pd.read_csv(config.ARQUIVO_CONSOLIDADO, sep=';', parse_dates=['Data'])
            if df.empty:
                return {"anos": [], "meses_por_ano": {}}
            
            # Obter anos únicos
            anos = sorted(df['Data'].dt.year.unique())
            
            # Obter meses por ano
            meses_por_ano = {}
            for ano in anos:
                dados_ano = df[df['Data'].dt.year == ano]
                meses = sorted(dados_ano['Data'].dt.month.unique())
                meses_por_ano[ano] = meses
            
            return {
                "anos": anos,
                "meses_por_ano": meses_por_ano
            }
        else:
            return {"anos": [], "meses_por_ano": {}}
    except Exception as e:
        logger.error(f"Erro ao obter períodos disponíveis: {e}")
        return {"anos": [], "meses_por_ano": {}}

def criar_graficos(df: pd.DataFrame):
    if df.empty: return go.Figure(), go.Figure()
    
    df_despesas = df[df['Tipo'] == 'Despesa'].copy()
    
    if df_despesas.empty: return go.Figure(), go.Figure()

    gastos_categoria = df_despesas.groupby('Categoria')['Valor'].sum().abs().sort_values(ascending=False).reset_index()
    fig_coluna = px.bar(gastos_categoria, x='Categoria', y='Valor', title='Gastos por Categoria', labels={'Valor': 'Total Gasto (R$)', 'Categoria': 'Categoria'}, text_auto='.2s')
    fig_coluna.update_layout(title_x=0.5, xaxis_title=None)
    
    df_despesas['Mes'] = df_despesas['Data'].dt.to_period('M').astype(str)
    gastos_mensais = df_despesas.groupby('Mes')['Valor'].sum().abs().reset_index()
    fig_linha = px.line(gastos_mensais, x='Mes', y='Valor', title='Evolução dos Gastos Mensais', labels={'Valor': 'Total Gasto (R$)', 'Mes': 'Mês'}, markers=True)
    fig_linha.update_layout(title_x=0.5, xaxis_title=None)
    
    return fig_coluna, fig_linha

# Agent caching to avoid recreating agents
_agent_cache: Dict[str, Any] = {}

def criar_agente(dfs: list):
    """Create agent with enhanced capabilities and better prompts."""
    # Security validation
    if not SecurityConfig.validate_api_key():
        raise ValueError("Invalid or missing OpenAI API key")
    
    # Rate limiting
    if not rate_limiter.can_call():
        raise Exception("Rate limit exceeded. Please try again later.")
    
    # Validate dangerous code setting
    if not config.ALLOW_DANGEROUS_CODE:
        raise ValueError("Dangerous code execution is disabled. Set ALLOW_DANGEROUS_CODE=True in config to enable chatbot functionality.")
    
    # Create cache key for agent
    dfs_hash = hashlib.md5(str([df.shape for df in dfs]).encode()).hexdigest()
    cache_key = f"agent_{dfs_hash}"
    
    # Return cached agent if available
    if cache_key in _agent_cache:
        return _agent_cache[cache_key]
    
    load_dotenv(config.PROJECT_ROOT / ".env")
    
    # Carregar configuração do modelo
    modelo_atual = carregar_configuracao_modelo()
    
    llm = ChatOpenAI(
        model=modelo_atual, 
        temperature=config.OPENAI_TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )
    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", input_key="input", return_messages=True)
    
    prefixo = f"""Você é o FinBot, um assistente financeiro pessoal especializado em análise de dados financeiros brasileiros.

    **CAPACIDADES ESPECIAIS:**
    - Análise de padrões de gastos e receitas
    - Identificação de anomalias financeiras
    - Recomendações de economia baseadas em dados
    - Análise de tendências temporais
    - Comparações entre períodos
    - Cálculos de métricas financeiras

    **REGRAS CRÍTICAS DE FORMATAÇÃO DE SAÍDA:**
    1. Sua resposta DEVE SEMPRE terminar com um bloco 'Action' e 'Action Input'.
    2. O bloco 'Action:' deve conter APENAS o nome da ferramenta, que é `python_repl_ast`.
    3. O bloco 'Action Input:' deve conter APENAS o código Python para ser executado.

    **REGRAS CRÍTICAS DE LÓGICA:**
    1. O DataFrame `df1` contém uma coluna 'Tipo' que classifica cada transação como 'Receita' (valores positivos) ou 'Despesa' (valores negativos).
    2. Para perguntas sobre "gastos", "despesas" ou "custos", você DEVE filtrar o DataFrame por `df1[df1['Tipo'] == 'Despesa']`.
    3. Para perguntas sobre "ganhos", "entradas" ou "recebimentos", você DEVE filtrar por `df1[df1['Tipo'] == 'Receita']`.
    4. Para encontrar o "maior gasto", procure pelo menor valor numérico (o mais negativo) nas despesas.
    5. Para encontrar o "menor gasto", procure pelo maior valor numérico (o mais próximo de zero) nas despesas.
    6. SEMPRE converta valores para reais (R$) quando exibir resultados.
    7. Use formatação brasileira para números (vírgula como separador decimal).

    **FERRAMENTAS DISPONÍVEIS:**
    `df1`: Todas as transações. Contém as colunas 'Data', 'Estabelecimento', 'Valor', 'Tipo', 'Categoria', 'Pagador'.
    `df2`: Resumo de gastos por Estabelecimento.
    `df3`: Resumo mensal de gastos por Categoria e Pagador.
    
    **BIBLIOTECAS DISPONÍVEIS:**
    - `matplotlib.pyplot` como `plt`
    - `pandas` como `pd`
    - `numpy` como `np`
    - `plotly.express` como `px`
    - `plotly.graph_objects` como `go`

    **EXEMPLOS DE ANÁLISES QUE VOCÊ PODE FAZER:**
    - "Qual foi meu maior gasto em julho?" → Filtra por mês e tipo 'Despesa', encontra o menor valor
    - "Mostre meus gastos por categoria" → Agrupa despesas por categoria e soma
    - "Compare meus gastos de junho com julho" → Análise comparativa entre meses
    - "Quem gasta mais: eu ou meu pai?" → Análise por pagador
    - "Identifique gastos anômalos" → Estatísticas para detectar outliers
    - "Calcule minha taxa de poupança" → (Receitas - Despesas) / Receitas
    - "Gere um gráfico de pizza dos gastos por categoria" → Visualização com plotly

    **REGRA PARA GRÁFICOS:**
    Ao criar um gráfico, salve-o em um arquivo (ex: `plt.savefig('grafico.png')`) e adicione a tag `[chart_path:NOME_DO_ARQUIVO.png]` no final da sua resposta.
    
    **DICAS IMPORTANTES:**
    - Sempre seja específico e detalhado em suas análises
    - Forneça insights acionáveis quando possível
    - Use linguagem clara e acessível
    - Quando apropriado, sugira ações para melhorar a situação financeira
    """
    agent_executor_kwargs = {"memory": memory, "handle_parsing_errors": True}
    agent = create_pandas_dataframe_agent(
        llm, dfs, prefix=prefixo, verbose=True, 
        allow_dangerous_code=config.ALLOW_DANGEROUS_CODE, 
        agent_executor_kwargs=agent_executor_kwargs
    )
    
    # Cache the agent
    _agent_cache[cache_key] = agent
    return agent

def chatbot_financeiro(dfs: list, user_input: str):
    try:
        # Validate input
        if not SecurityConfig.validate_input_length(user_input):
            return "Entrada muito longa. Por favor, seja mais conciso."
        
        # Validate dataframes
        if not dfs or not any(len(df) > 0 for df in dfs):
            return "Não há dados disponíveis para análise. Processe seus dados primeiro."
            
        agente = criar_agente(dfs)
        resposta = agente.invoke({"input": user_input})
        return resposta.get("output", "Não consegui processar sua pergunta.")
    except ValueError as e:
        if "Dangerous code execution is disabled" in str(e):
            return "❌ Funcionalidade do chatbot desabilitada por segurança. Para habilitar, configure ALLOW_DANGEROUS_CODE=True no arquivo de configuração."
        elif "Invalid or missing OpenAI API key" in str(e):
            return "❌ Chave da API OpenAI não encontrada ou inválida. Configure sua chave no arquivo .env"
        else:
            logger.error(f"Chatbot validation error: {str(e)}")
            return f"Erro de validação: {e}"
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        return f"Ocorreu um erro inesperado no chatbot: {e}"

class PDF(FPDF):
    def __init__(self, periodo, *args, **kwargs): super().__init__(*args, **kwargs); self.periodo = periodo
    def header(self): self.set_font('DejaVu', 'B', 12); self.cell(0, 10, f'Relatório Financeiro, {self.periodo}', 0, 1, 'C'); self.ln(5)
    def footer(self): self.set_y(-20); self.set_font('DejaVu', 'I', 8); self.cell(0, 10, 'Provenzano, Analista Financeiro EPR', 0, 0, 'C'); self.set_y(-15); self.set_font('DejaVu', 'I', 8); self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def gerar_relatorio_pdf(df_completo: pd.DataFrame, ano: int, mes: int) -> str:
    data_relatorio = datetime(ano, mes, 1)
    df_mes_atual = df_completo[(df_completo['Data'].dt.year == ano) & (df_completo['Data'].dt.month == mes)].copy()
    if df_mes_atual.empty: return None

    df_despesas_mes = df_mes_atual[df_mes_atual['Tipo'] == 'Despesa']
    df_receitas_mes = df_mes_atual[df_mes_atual['Tipo'] == 'Receita']
    
    gasto_total = df_despesas_mes['Valor'].sum()
    receita_total = df_receitas_mes['Valor'].sum()
    
    top_5_categorias = df_despesas_mes.groupby('Categoria')['Valor'].sum().sort_values().head(5)
    gastos_por_pagador = df_despesas_mes.groupby('Pagador')['Valor'].sum().sort_values()

    nome_arquivo_pizza, nome_arquivo_pagador = None, None
    if not top_5_categorias.empty:
        nome_arquivo_pizza = f"relatorio_pizza_{ano}_{mes:02d}.png"
        plt.figure(figsize=(8, 5)); plt.pie(abs(top_5_categorias), labels=top_5_categorias.index, autopct='%1.1f%%', startangle=140); plt.title(f'Top 5 Categorias de Gasto - {data_relatorio.strftime("%B %Y")}'); plt.savefig(nome_arquivo_pizza, dpi=200, bbox_inches='tight'); plt.close()
    if not gastos_por_pagador.empty:
        nome_arquivo_pagador = f"relatorio_pagador_{ano}_{mes:02d}.png"
        plt.figure(figsize=(8, 5)); plt.bar(gastos_por_pagador.index, abs(gastos_por_pagador.values), color='mediumseagreen'); plt.ylabel('Total Gasto (R$)'); plt.title(f'Gastos por Pagador - {data_relatorio.strftime("%B %Y")}'); plt.savefig(nome_arquivo_pagador, dpi=200, bbox_inches='tight'); plt.close()
    
    load_dotenv(config.PROJECT_ROOT / ".env")
    
    # Carregar configuração do modelo
    modelo_atual = carregar_configuracao_modelo()
    
    llm = ChatOpenAI(model=modelo_atual, temperature=0.4)
    
    prompt_analise = f"""
    Você é um consultor financeiro escrevendo uma análise para o relatório do Provenzano.
    Analise os dados financeiros para {data_relatorio.strftime('%B de %Y')}. Seja objetivo e direto.
    Dados:
    - Receita Total: R$ {receita_total:.2f}
    - Gasto Total: R$ {abs(gasto_total):.2f}
    - Saldo do Mês: R$ {(receita_total + gasto_total):.2f}
    - Top 5 Categorias de Despesa: {abs(top_5_categorias).to_dict() if not top_5_categorias.empty else 'N/A'}
    - Gastos por Pagador: {abs(gastos_por_pagador).to_dict() if not gastos_por_pagador.empty else 'N/A'}
    Sua Tarefa:
    1. Análise Geral do mês (comparar receitas e despesas).
    2. Análise dos gastos por Pagador e Categoria.
    3. Dicas Práticas baseadas no saldo e nos principais gastos.
    """
    analise_ia = llm.invoke(prompt_analise).content
    meses_pt = {i+1: v for i, v in enumerate(['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])}
    periodo_formatado = f"{meses_pt[mes].capitalize()} de {ano}"
    pdf = PDF(periodo=periodo_formatado)
    pdf.add_font("DejaVu", style="", fname=str(config.PASTA_FONTES / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", style="B", fname=str(config.PASTA_FONTES / "DejaVuSans-Bold.ttf"))
    pdf.add_font("DejaVu", style="I", fname=str(config.PASTA_FONTES / "DejaVuSans-Oblique.ttf"))
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, 'Análise Financeira Detalhada', 0, 1, 'L')
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 7, analise_ia)
    pdf.ln(10)
    if nome_arquivo_pizza: pdf.image(nome_arquivo_pizza, x=10, w=pdf.w / 2 - 15)
    if nome_arquivo_pagador: pdf.image(nome_arquivo_pagador, x=pdf.w / 2 + 5, w=pdf.w / 2 - 15)
    config.PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
    nome_pdf = f'Relatório_{meses_pt[mes].capitalize()}_{ano}.pdf'
    caminho_completo_pdf = str(config.PASTA_RELATORIOS / nome_pdf)
    pdf.output(caminho_completo_pdf)
    if nome_arquivo_pizza and os.path.exists(nome_arquivo_pizza): os.remove(nome_arquivo_pizza)
    if nome_arquivo_pagador and os.path.exists(nome_arquivo_pagador): os.remove(nome_arquivo_pagador)
    return caminho_completo_pdf

def prever_gastos(df_historico: pd.DataFrame, meses_a_frente: int = 6):
    """
    Sistema avançado de previsão financeira com três cenários e detecção robusta de padrões.
    
    Args:
        df_historico: DataFrame com dados históricos
        meses_a_frente: Número de meses para prever
        
    Returns:
        dict: Dicionário com previsões e análises para três cenários
    """
    if df_historico.empty:
        return None
    
    df = df_historico[df_historico['Tipo'] == 'Despesa'].copy()
    
    if df.empty:
        return None

    # Preparar dados com tratamento robusto de outliers
    df['Data'] = pd.to_datetime(df['Data'])
    gastos_mensais = df.set_index('Data').resample('M')['Valor'].sum().abs().reset_index()
    gastos_mensais = gastos_mensais.rename(columns={'Data': 'Mes', 'Valor': 'Gasto_Total'})
    
    if len(gastos_mensais) < 4:
        print("Dados insuficientes para treinar o modelo (necessário no mínimo 4 meses).")
        return None
    
    # Verificar se há dados válidos após limpeza
    if len(gastos_mensais) == 0:
        print("Nenhum dado válido encontrado após processamento.")
        return None
    
    # Detecção e tratamento de outliers usando IQR
    Q1 = gastos_mensais['Gasto_Total'].quantile(0.25)
    Q3 = gastos_mensais['Gasto_Total'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Identificar outliers
    outliers = gastos_mensais[
        (gastos_mensais['Gasto_Total'] < lower_bound) | 
        (gastos_mensais['Gasto_Total'] > upper_bound)
    ]
    
    # Criar dados limpos (sem outliers para treinamento)
    dados_limpos = gastos_mensais[
        (gastos_mensais['Gasto_Total'] >= lower_bound) & 
        (gastos_mensais['Gasto_Total'] <= upper_bound)
    ].copy()
    
    # Verificar se ainda temos dados suficientes após remoção de outliers
    if len(dados_limpos) < 3:
        print("Dados insuficientes após remoção de outliers. Usando todos os dados.")
        dados_limpos = gastos_mensais.copy()
    
    # Engenharia de features avançada
    dados_limpos['ano'] = dados_limpos['Mes'].dt.year
    dados_limpos['mes_num'] = dados_limpos['Mes'].dt.month
    dados_limpos['trimestre'] = dados_limpos['Mes'].dt.quarter
    dados_limpos['tempo'] = np.arange(len(dados_limpos))
    
    # Features sazonais e cíclicas
    dados_limpos['seno_mes'] = np.sin(2 * np.pi * dados_limpos['mes_num'] / 12)
    dados_limpos['coseno_mes'] = np.cos(2 * np.pi * dados_limpos['mes_num'] / 12)
    dados_limpos['seno_trimestre'] = np.sin(2 * np.pi * dados_limpos['trimestre'] / 4)
    
    # Features de tendência e volatilidade
    dados_limpos['tendencia'] = dados_limpos['Gasto_Total'].rolling(window=3, min_periods=1).mean()
    dados_limpos['volatilidade'] = dados_limpos['Gasto_Total'].rolling(window=3, min_periods=1).std()
    
    # Features de crescimento
    dados_limpos['crescimento_mom'] = dados_limpos['Gasto_Total'].pct_change()
    dados_limpos['crescimento_ano'] = dados_limpos['Gasto_Total'].pct_change(periods=12)
    
    # Tratamento robusto de valores NaN
    # Para features de crescimento, preencher com 0 se for o primeiro valor
    dados_limpos['crescimento_mom'] = dados_limpos['crescimento_mom'].fillna(0)
    dados_limpos['crescimento_ano'] = dados_limpos['crescimento_ano'].fillna(0)
    
    # Para features de tendência e volatilidade, usar valores médios
    dados_limpos['tendencia'] = dados_limpos['tendencia'].fillna(dados_limpos['Gasto_Total'].mean())
    dados_limpos['volatilidade'] = dados_limpos['volatilidade'].fillna(dados_limpos['Gasto_Total'].std())
    
    # Verificar se ainda há NaN e remover linhas se necessário
    if dados_limpos.isnull().any().any():
        dados_limpos = dados_limpos.dropna()
        if len(dados_limpos) < 4:
            print("Dados insuficientes após limpeza de NaN (necessário no mínimo 4 meses).")
            return None
    
    # Features para o modelo
    features = [
        'ano', 'mes_num', 'trimestre', 'tempo', 
        'seno_mes', 'coseno_mes', 'seno_trimestre',
        'tendencia', 'volatilidade', 'crescimento_mom', 'crescimento_ano'
    ]
    target = 'Gasto_Total'
    
    X = dados_limpos[features]
    y = dados_limpos[target]
    
    # Verificação final de NaN antes do treinamento
    if X.isnull().any().any() or y.isnull().any():
        print("Erro: Ainda existem valores NaN nos dados após limpeza.")
        return None
    
    # Modelo ensemble robusto
    
    # Normalização robusta
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Múltiplos modelos para ensemble
    modelos = {
        'random_forest': RandomForestRegressor(
            n_estimators=200, 
            max_depth=10, 
            min_samples_split=5,
            min_samples_leaf=3,
            random_state=42
        ),
        'gradient_boosting': GradientBoostingRegressor(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ),
        'huber': HuberRegressor(epsilon=1.35, max_iter=1000)
    }
    
    # Treinar modelos
    previsoes_modelos = {}
    for nome, modelo in modelos.items():
        modelo.fit(X_scaled, y)
        previsoes_modelos[nome] = modelo
    
    # Preparar dados futuros
    ultimo_mes = dados_limpos['Mes'].max()
    ultimo_tempo = dados_limpos['tempo'].max()
    datas_futuras = pd.date_range(start=ultimo_mes, periods=meses_a_frente + 1, freq='M')[1:]
    
    df_futuro = pd.DataFrame({'Mes': datas_futuras})
    df_futuro['ano'] = df_futuro['Mes'].dt.year
    df_futuro['mes_num'] = df_futuro['Mes'].dt.month
    df_futuro['trimestre'] = df_futuro['Mes'].dt.quarter
    df_futuro['tempo'] = np.arange(ultimo_tempo + 1, ultimo_tempo + 1 + meses_a_frente)
    
    # Features futuras
    df_futuro['seno_mes'] = np.sin(2 * np.pi * df_futuro['mes_num'] / 12)
    df_futuro['coseno_mes'] = np.cos(2 * np.pi * df_futuro['mes_num'] / 12)
    df_futuro['seno_trimestre'] = np.sin(2 * np.pi * df_futuro['trimestre'] / 4)
    
    # Calcular tendência e volatilidade futuras
    ultima_tendencia = dados_limpos['tendencia'].iloc[-1]
    ultima_volatilidade = dados_limpos['volatilidade'].iloc[-1]
    ultimo_crescimento = dados_limpos['crescimento_mom'].iloc[-1]
    
    # Garantir que os valores não são NaN
    if pd.isna(ultima_tendencia):
        ultima_tendencia = dados_limpos['Gasto_Total'].mean()
    if pd.isna(ultima_volatilidade):
        ultima_volatilidade = dados_limpos['Gasto_Total'].std()
    if pd.isna(ultimo_crescimento):
        ultimo_crescimento = 0.0
    
    df_futuro['tendencia'] = ultima_tendencia
    df_futuro['volatilidade'] = ultima_volatilidade
    df_futuro['crescimento_mom'] = ultimo_crescimento
    df_futuro['crescimento_ano'] = ultimo_crescimento  # Simplificado
    
    X_futuro = df_futuro[features]
    
    # Verificação final de NaN nos dados futuros
    if X_futuro.isnull().any().any():
        print("Erro: Valores NaN detectados nos dados futuros.")
        return None
    
    X_futuro_scaled = scaler.transform(X_futuro)
    
    # Gerar previsões base
    previsoes_base = {}
    for nome, modelo in previsoes_modelos.items():
        previsoes_base[nome] = modelo.predict(X_futuro_scaled)
    
    # Calcular previsão média (cenário normal)
    previsao_normal = np.mean([previsoes_base[nome] for nome in previsoes_base.keys()], axis=0)
    
    # Calcular desvio padrão das previsões para cenários
    std_previsoes = np.std([previsoes_base[nome] for nome in previsoes_base.keys()], axis=0)
    
    # Criar três cenários
    previsao_otimista = previsao_normal - 0.5 * std_previsoes  # Menor gasto
    previsao_pessimista = previsao_normal + 0.5 * std_previsoes  # Maior gasto
    
    # Aplicar fatores de ajuste baseados na análise histórica
    tendencia_historica = dados_limpos['crescimento_mom'].mean()
    volatilidade_historica = dados_limpos['volatilidade'].mean()
    
    # Ajustar cenários baseado na tendência histórica
    if tendencia_historica > 0.05:  # Crescimento forte
        previsao_otimista *= 0.9
        previsao_pessimista *= 1.2
    elif tendencia_historica < -0.05:  # Redução forte
        previsao_otimista *= 0.8
        previsao_pessimista *= 1.1
    else:  # Estável
        previsao_otimista *= 0.95
        previsao_pessimista *= 1.05
    
    # Análise de padrões avançados
    padroes_avancados = analisar_padroes_avancados(df_historico)
    
    # Gerar explicações lógicas
    explicacoes = gerar_explicacoes_previsao(
        dados_limpos, outliers, tendencia_historica, 
        volatilidade_historica, len(outliers)
    )
    
    # Criar DataFrames de resultado
    df_resultado = pd.DataFrame({
        'Mes': datas_futuras.strftime('%Y-%m'),
        'Cenario_Otimista': previsao_otimista,
        'Cenario_Normal': previsao_normal,
        'Cenario_Pessimista': previsao_pessimista
    })
    
    return {
        'previsoes': df_resultado,
        'explicacoes': explicacoes,
        'outliers_detectados': len(outliers),
        'qualidade_dados': {
            'total_meses': len(gastos_mensais),
            'meses_limpos': len(dados_limpos),
            'tendencia_historica': tendencia_historica,
            'volatilidade_historica': volatilidade_historica
        },
        'padroes_avancados': padroes_avancados
    }

def gerar_explicacoes_previsao(dados_limpos, outliers, tendencia, volatilidade, num_outliers):
    """
    Gera explicações lógicas para as previsões baseadas nos padrões detectados.
    """
    explicacoes = {
        'otimista': [],
        'normal': [],
        'pessimista': []
    }
    
    # Análise de tendência
    if tendencia > 0.05:
        explicacoes['otimista'].append("Tendência de crescimento detectada - cenário otimista assume estabilização")
        explicacoes['normal'].append("Continuação da tendência de crescimento observada")
        explicacoes['pessimista'].append("Aceleração do crescimento baseada em padrões históricos")
    elif tendencia < -0.05:
        explicacoes['otimista'].append("Tendência de redução detectada - cenário otimista assume recuperação")
        explicacoes['normal'].append("Continuação da tendência de redução observada")
        explicacoes['pessimista'].append("Estabilização dos gastos em níveis mais altos")
    else:
        explicacoes['otimista'].append("Padrão estável - cenário otimista assume redução gradual")
        explicacoes['normal'].append("Manutenção da estabilidade observada")
        explicacoes['pessimista'].append("Aumento moderado baseado em sazonalidade")
    
    # Análise de volatilidade
    if volatilidade > dados_limpos['Gasto_Total'].std() * 0.5:
        explicacoes['otimista'].append("Alta volatilidade - cenário otimista assume redução da variabilidade")
        explicacoes['normal'].append("Manutenção da volatilidade observada")
        explicacoes['pessimista'].append("Aumento da volatilidade baseado em padrões históricos")
    else:
        explicacoes['otimista'].append("Baixa volatilidade - cenário otimista mantém estabilidade")
        explicacoes['normal'].append("Continuação da baixa volatilidade")
        explicacoes['pessimista'].append("Aumento moderado da volatilidade")
    
    # Análise de outliers
    if num_outliers > 0:
        explicacoes['otimista'].append(f"Detectados {num_outliers} outliers - cenário otimista exclui eventos excepcionais")
        explicacoes['normal'].append(f"Modelo treinado excluindo {num_outliers} outliers para maior robustez")
        explicacoes['pessimista'].append(f"Possibilidade de novos outliers baseada em {num_outliers} eventos anteriores")
    
    # Análise sazonal
    sazonalidade = dados_limpos.groupby('mes_num')['Gasto_Total'].mean()
    meses_altos = sazonalidade[sazonalidade > sazonalidade.mean()].index.tolist()
    if meses_altos:
        explicacoes['otimista'].append(f"Sazonalidade detectada nos meses {meses_altos} - cenário otimista considera redução")
        explicacoes['normal'].append(f"Padrão sazonal mantido nos meses {meses_altos}")
        explicacoes['pessimista'].append(f"Intensificação da sazonalidade nos meses {meses_altos}")
    
    return explicacoes

def analisar_padroes_avancados(df_historico: pd.DataFrame) -> dict:
    """
    Análise avançada de padrões financeiros para melhorar a qualidade das previsões.
    
    Args:
        df_historico: DataFrame com dados históricos
        
    Returns:
        dict: Dicionário com padrões detectados
    """
    if df_historico.empty:
        return {}
    
    df = df_historico[df_historico['Tipo'] == 'Despesa'].copy()
    
    if df.empty:
        return {}
    
    df['Data'] = pd.to_datetime(df['Data'])
    gastos_mensais = df.set_index('Data').resample('M')['Valor'].sum().abs().reset_index()
    
    # Padrões temporais
    padroes = {
        'sazonalidade': {},
        'tendencia': {},
        'volatilidade': {},
        'ciclos': {},
        'outliers': {},
        'categorias': {}
    }
    
    # Análise de sazonalidade
    gastos_mensais['mes'] = gastos_mensais['Data'].dt.month
    gastos_mensais['ano'] = gastos_mensais['Data'].dt.year
    
    # Média por mês
    media_por_mes = gastos_mensais.groupby('mes')['Valor'].mean()
    media_geral = gastos_mensais['Valor'].mean()
    
    meses_altos = media_por_mes[media_por_mes > media_geral * 1.1].index.tolist()
    meses_baixos = media_por_mes[media_por_mes < media_geral * 0.9].index.tolist()
    
    padroes['sazonalidade'] = {
        'meses_altos': meses_altos,
        'meses_baixos': meses_baixos,
        'intensidade_sazonal': (media_por_mes.max() - media_por_mes.min()) / media_geral
    }
    
    # Análise de tendência
    gastos_mensais['tendencia'] = gastos_mensais['Valor'].rolling(window=3, min_periods=1).mean()
    crescimento_medio = gastos_mensais['Valor'].pct_change().mean()
    
    # Tratar NaN na tendência
    if gastos_mensais['tendencia'].isnull().any():
        gastos_mensais['tendencia'] = gastos_mensais['tendencia'].fillna(gastos_mensais['Valor'].mean())
    
    # Tratar NaN no crescimento médio
    if pd.isna(crescimento_medio):
        crescimento_medio = 0.0
    
    padroes['tendencia'] = {
        'crescimento_medio': crescimento_medio,
        'direcao': 'crescimento' if crescimento_medio > 0.01 else 'reducao' if crescimento_medio < -0.01 else 'estavel',
        'intensidade': abs(crescimento_medio)
    }
    
    # Análise de volatilidade
    volatilidade = gastos_mensais['Valor'].std()
    volatilidade_relativa = volatilidade / media_geral
    
    padroes['volatilidade'] = {
        'valor_absoluto': volatilidade,
        'valor_relativo': volatilidade_relativa,
        'nivel': 'alta' if volatilidade_relativa > 0.3 else 'media' if volatilidade_relativa > 0.15 else 'baixa'
    }
    
    # Análise de ciclos
    if len(gastos_mensais) >= 12:
        # Autocorrelação para detectar ciclos
        autocorr = gastos_mensais['Valor'].autocorr()
        padroes['ciclos'] = {
            'autocorrelacao': autocorr,
            'padrao_ciclico': autocorr > 0.3
        }
    
    # Análise de outliers
    Q1 = gastos_mensais['Valor'].quantile(0.25)
    Q3 = gastos_mensais['Valor'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = gastos_mensais[
        (gastos_mensais['Valor'] < Q1 - 1.5 * IQR) | 
        (gastos_mensais['Valor'] > Q3 + 1.5 * IQR)
    ]
    
    padroes['outliers'] = {
        'quantidade': len(outliers),
        'percentual': len(outliers) / len(gastos_mensais) * 100,
        'valores': outliers['Valor'].tolist() if not outliers.empty else []
    }
    
    # Análise por categorias
    if 'Categoria' in df.columns:
        gastos_categoria = df.groupby('Categoria')['Valor'].sum().abs()
        categorias_principais = gastos_categoria.nlargest(5)
        
        padroes['categorias'] = {
            'principais': categorias_principais.to_dict(),
            'distribuicao': (categorias_principais / categorias_principais.sum()).to_dict()
        }
    
    return padroes

def assistente_pagamento():
    return "Assistente de pagamento ainda não implementado."

# --- Enhanced Data Processing System ---
@dataclass
class DataValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    processed_rows: int
    invalid_rows: int

class DataValidator:
    """Advanced data validation system."""
    
    def __init__(self):
        self.required_columns = ['Data', 'Estabelecimento', 'Valor', 'Tipo']
        self.valid_types = ['Despesa', 'Receita']
        self.max_value = 1000000  # R$ 1M
        self.min_date = datetime(2020, 1, 1)
        self.max_date = datetime.now() + timedelta(days=30)
    
    def validate_dataframe(self, df: pd.DataFrame, source: str) -> DataValidationResult:
        """Comprehensive dataframe validation."""
        errors = []
        warnings = []
        processed_rows = len(df)
        invalid_rows = 0
        
        # Check if dataframe is empty
        if df.empty:
            errors.append("DataFrame is empty")
            return DataValidationResult(False, errors, warnings, 0, 0)
        
        # Check required columns
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        # Validate data types
        if 'Data' in df.columns:
            invalid_dates = df['Data'].isna().sum()
            if invalid_dates > 0:
                warnings.append(f"{invalid_dates} invalid dates found")
                invalid_rows += invalid_dates
        
        if 'Valor' in df.columns:
            invalid_values = df['Valor'].isna().sum()
            if invalid_values > 0:
                warnings.append(f"{invalid_values} invalid values found")
                invalid_rows += invalid_values
            
            # Check for extreme values
            extreme_values = df[df['Valor'].abs() > self.max_value]
            if not extreme_values.empty:
                warnings.append(f"{len(extreme_values)} extreme values found (>R$ {self.max_value:,.0f})")
        
        if 'Tipo' in df.columns:
            invalid_types = df[~df['Tipo'].isin(self.valid_types)]
            if not invalid_types.empty:
                errors.append(f"Invalid types found: {invalid_types['Tipo'].unique().tolist()}")
        
        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            warnings.append(f"{duplicates} duplicate rows found")
        
        # Check for suspicious patterns
        suspicious_patterns = self._detect_suspicious_patterns(df)
        if suspicious_patterns:
            warnings.extend(suspicious_patterns)
        
        return DataValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            processed_rows=processed_rows,
            invalid_rows=invalid_rows
        )
    
    def _detect_suspicious_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect suspicious patterns in data."""
        patterns = []
        
        # Check for too many identical values
        for col in ['Estabelecimento', 'Valor']:
            if col in df.columns:
                value_counts = df[col].value_counts()
                if len(value_counts) > 0:
                    most_common_pct = (value_counts.iloc[0] / len(df)) * 100
                    if most_common_pct > 50:
                        patterns.append(f"High concentration of identical {col} values ({most_common_pct:.1f}%)")
        
        # Check for unusual date patterns
        if 'Data' in df.columns:
            date_range = df['Data'].max() - df['Data'].min()
            if date_range.days > 365 * 5:  # More than 5 years
                patterns.append("Unusual date range detected (>5 years)")
        
        return patterns

class AdvancedCategorizer:
    """Advanced categorization system with machine learning capabilities."""
    
    def __init__(self):
        self.categorization_rules = {
            'Alimentação': {
                'keywords': [
                    'restaurante', 'lanche', 'pizza', 'hamburger', 'cafe', 'bar', 'padaria',
                    'supermercado', 'mercado', 'ifood', 'uber eats', 'rappi', 'delivery',
                    'fast food', 'sorveteria', 'doceria', 'confeitaria', 'açougue', 'hortifruti',
                    'bakery', 'food', 'restaurant', 'snack', 'burger', 'coffee', 'pub',
                    'grocery', 'market', 'delivery', 'fastfood', 'ice cream', 'candy',
                    'butcher', 'vegetables', 'fruits', 'bread', 'meat', 'fish'
                ],
                'patterns': [
                    r'\b(restaurante|lanche|pizza|hamburger|cafe|bar|padaria)\b',
                    r'\b(supermercado|mercado|ifood|uber eats|rappi|delivery)\b',
                    r'\b(fast food|sorveteria|doceria|confeitaria|açougue|hortifruti)\b'
                ],
                'confidence_threshold': 0.6
            },
            'Transporte': {
                'keywords': [
                    'uber', '99', 'taxi', 'onibus', 'metro', 'trem', 'posto', 'combustivel',
                    'gasolina', 'etanol', 'diesel', 'estacionamento', 'pedagio', 'uber*',
                    'lyft', 'cabify', 'estacionamento', 'parking', 'whoosh', 'ec',
                    'bus', 'subway', 'train', 'gas station', 'fuel', 'parking', 'toll'
                ],
                'patterns': [
                    r'\b(uber|99|taxi|onibus|metro|trem|posto|combustivel)\b',
                    r'\b(gasolina|etanol|diesel|estacionamento|pedagio)\b',
                    r'\b(lyft|cabify|parking|whoosh|ec)\b'
                ],
                'confidence_threshold': 0.7
            },
            'Saúde': {
                'keywords': [
                    'farmacia', 'drogaria', 'hospital', 'clinica', 'medico', 'dentista',
                    'laboratorio', 'exame', 'consulta', 'remedio', 'panvel', 'raia',
                    'drogasil', 'drogaraia', 'ultrafarma', 'pharmacy', 'drugstore',
                    'hospital', 'clinic', 'doctor', 'dentist', 'laboratory', 'exam',
                    'consultation', 'medicine', 'drug'
                ],
                'patterns': [
                    r'\b(farmacia|drogaria|hospital|clinica|medico|dentista)\b',
                    r'\b(laboratorio|exame|consulta|remedio)\b',
                    r'\b(panvel|raia|drogasil|drogaraia|ultrafarma)\b'
                ],
                'confidence_threshold': 0.8
            },
            'Educação': {
                'keywords': [
                    'universidade', 'faculdade', 'escola', 'curso', 'livraria', 'papelaria',
                    'material escolar', 'mensalidade', 'matricula', 'saraiva', 'cultura',
                    'livraria', 'estante virtual', 'university', 'college', 'school',
                    'course', 'bookstore', 'stationery', 'tuition', 'enrollment'
                ],
                'patterns': [
                    r'\b(universidade|faculdade|escola|curso|livraria|papelaria)\b',
                    r'\b(material escolar|mensalidade|matricula)\b',
                    r'\b(saraiva|cultura|estante virtual)\b'
                ],
                'confidence_threshold': 0.8
            },
            'Lazer': {
                'keywords': [
                    'cinema', 'teatro', 'show', 'concerto', 'museu', 'parque', 'jogos',
                    'steam', 'netflix', 'spotify', 'youtube', 'disney', 'hbo', 'amazon',
                    'shopping', 'mall', 'loja', 'renner', 'riachuelo', 'c&a',
                    'movie', 'theater', 'concert', 'museum', 'park', 'games',
                    'store', 'shop', 'retail'
                ],
                'patterns': [
                    r'\b(cinema|teatro|show|concerto|museu|parque|jogos)\b',
                    r'\b(steam|netflix|spotify|youtube|disney|hbo|amazon)\b',
                    r'\b(shopping|mall|loja|renner|riachuelo|c&a)\b'
                ],
                'confidence_threshold': 0.6
            },
            'Moradia': {
                'keywords': [
                    'aluguel', 'condominio', 'iptu', 'agua', 'luz', 'gas', 'internet',
                    'energia', 'sabesp', 'enel', 'energisa', 'oi', 'vivo', 'claro',
                    'tim', 'net', 'claro', 'sky', 'directv', 'rent', 'condominium',
                    'property tax', 'water', 'electricity', 'gas', 'internet', 'energy'
                ],
                'patterns': [
                    r'\b(aluguel|condominio|iptu|agua|luz|gas|internet)\b',
                    r'\b(energia|sabesp|enel|energisa)\b',
                    r'\b(oi|vivo|claro|tim|net|sky|directv)\b'
                ],
                'confidence_threshold': 0.8
            },
            'Assinatura': {
                'keywords': [
                    'netflix', 'spotify', 'youtube', 'disney', 'hbo', 'amazon prime',
                    'apple', 'google', 'microsoft', 'adobe', 'canva', 'notion',
                    'ifood club', 'uber pass', '99 pass', 'subscription', 'membership'
                ],
                'patterns': [
                    r'\b(netflix|spotify|youtube|disney|hbo|amazon prime)\b',
                    r'\b(apple|google|microsoft|adobe|canva|notion)\b',
                    r'\b(ifood club|uber pass|99 pass)\b'
                ],
                'confidence_threshold': 0.9
            },
            'Investimento': {
                'keywords': [
                    'nubank', 'inter', 'itau', 'bradesco', 'santander', 'bb',
                    'rico', 'xp', 'clear', 'easynvest', 'btg', 'modalmais',
                    'investment', 'broker', 'bank', 'financial'
                ],
                'patterns': [
                    r'\b(nubank|inter|itau|bradesco|santander|bb)\b',
                    r'\b(rico|xp|clear|easynvest|btg|modalmais)\b'
                ],
                'confidence_threshold': 0.9
            }
        }
    
    def categorize_establishment(self, establishment: str) -> Tuple[str, float]:
        """Categorize establishment with confidence score."""
        if not establishment or pd.isna(establishment):
            return "Outros", 0.0
        
        establishment_lower = establishment.lower().strip()
        best_category = "Outros"
        best_confidence = 0.0
        
        for category, rules in self.categorization_rules.items():
            confidence = self._calculate_category_confidence(establishment_lower, rules)
            if confidence > best_confidence and confidence >= rules['confidence_threshold']:
                best_confidence = confidence
                best_category = category
        
        return best_category, best_confidence
    
    def _calculate_category_confidence(self, text: str, rules: Dict) -> float:
        """Calculate confidence score for a category."""
        confidence = 0.0
        
        # Keyword matching
        for keyword in rules['keywords']:
            if keyword in text:
                confidence += 0.3
        
        # Pattern matching
        for pattern in rules['patterns']:
            if re.search(pattern, text):
                confidence += 0.4
        
        # Exact match bonus
        if text in rules['keywords']:
            confidence += 0.2
        
        # Length-based penalty for very short texts
        if len(text) < 3:
            confidence *= 0.5
        
        return min(confidence, 1.0)
    
    def get_category_suggestions(self, establishment: str) -> List[Tuple[str, float]]:
        """Get category suggestions with confidence scores."""
        suggestions = []
        
        for category, rules in self.categorization_rules.items():
            confidence = self._calculate_category_confidence(establishment.lower(), rules)
            if confidence > 0.1:  # Only include if some confidence
                suggestions.append((category, confidence))
        
        return sorted(suggestions, key=lambda x: x[1], reverse=True)

class DataProcessor:
    """Advanced data processing pipeline."""
    
    def __init__(self):
        self.validator = DataValidator()
        self.categorizer = AdvancedCategorizer()
        self.cache = DataCache()
    
    def process_file(self, file_path: str, file_type: str) -> Tuple[pd.DataFrame, DataValidationResult]:
        """Process a single file with comprehensive validation."""
        try:
            # Security validation
            if not SecurityConfig.validate_file_path(file_path):
                raise ValueError("Invalid file path")
            
            # File size check
            file_size = os.path.getsize(file_path)
            if file_size > config.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {file_size} bytes")
            
            # Load data based on file type
            if file_type == 'credito':
                df = self._load_credit_file(file_path)
            elif file_type == 'debito':
                df = self._load_debit_file(file_path)
            else:
                raise ValueError(f"Unknown file type: {file_type}")
            
            # Validate data
            validation_result = self.validator.validate_dataframe(df, file_type)
            
            if not validation_result.is_valid:
                logger.error(f"Validation failed for {file_path}: {validation_result.errors}")
                return pd.DataFrame(), validation_result
            
            # Apply categorization
            df = self._apply_categorization(df)
            
            # Log warnings
            if validation_result.warnings:
                logger.warning(f"Warnings for {file_path}: {validation_result.warnings}")
            
            return df, validation_result
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return pd.DataFrame(), DataValidationResult(False, [str(e)], [], 0, 0)
    
    def _load_credit_file(self, file_path: str) -> pd.DataFrame:
        """Load and process credit file."""
        df = pd.read_csv(file_path, sep=';', encoding='utf-8', dayfirst=True, skipinitialspace=True)
        df = df.rename(columns=lambda col: col.strip())
        
        # Column mapping
        mapping = {
            'Data movimento': 'Data',
            'Nome do fornecedor/cliente': 'Estabelecimento',
            'Valor (R$)': 'Valor'
        }
        df = df.rename(columns=mapping)
        
        # Process values
        if 'Valor' in df.columns:
            df['Valor'] = self._clean_currency_values(df['Valor'])
            df['Valor'] = -abs(df['Valor'])  # Credit transactions are expenses
        
        df['Tipo'] = 'Despesa'
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce', dayfirst=True)
        
        return df[['Data', 'Estabelecimento', 'Valor', 'Tipo']]
    
    def _load_debit_file(self, file_path: str) -> pd.DataFrame:
        """Load and process debit file."""
        df = pd.read_csv(file_path, sep=';', encoding='utf-8', dayfirst=True, skipinitialspace=True)
        df = df.rename(columns=lambda col: col.strip())
        
        # Column mapping
        mapping = {
            'Data': 'Data',
            'Descricao': 'Estabelecimento',
            'Valor': 'Valor'
        }
        df = df.rename(columns=mapping)
        
        # Process dates
        if 'Data' in df.columns:
            df['Data'] = df['Data'].astype(str).str.split(' às').str[0]
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce', dayfirst=True)
        
        # Process values
        if 'Valor' in df.columns:
            df['Valor'] = self._clean_currency_values(df['Valor'])
        
        # Determine transaction type
        df['Tipo'] = np.where(df['Valor'] >= 0, 'Receita', 'Despesa')
        
        return df[['Data', 'Estabelecimento', 'Valor', 'Tipo']].dropna()
    
    def _clean_currency_values(self, series: pd.Series) -> pd.Series:
        """Clean currency values with better error handling."""
        try:
            cleaned = (series.astype(str)
                       .str.replace('R$', '', regex=False)
                       .str.replace('.', '', regex=False)
                       .str.strip()
                       .str.replace(',', '.', regex=False))
            
            # Convert to numeric with coerce
            numeric_values = pd.to_numeric(cleaned, errors='coerce')
            
            # Log conversion issues
            invalid_count = numeric_values.isna().sum()
            if invalid_count > 0:
                logger.warning(f"Could not convert {invalid_count} currency values")
            
            return numeric_values
            
        except Exception as e:
            logger.error(f"Error cleaning currency values: {e}")
            return pd.Series([np.nan] * len(series))
    
    def _apply_categorization(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply intelligent categorization to dataframe."""
        if 'Estabelecimento' not in df.columns:
            return df
        
        # Apply categorization with confidence tracking
        categorizations = []
        confidences = []
        
        for establishment in df['Estabelecimento']:
            category, confidence = self.categorizer.categorize_establishment(establishment)
            categorizations.append(category)
            confidences.append(confidence)
        
        df['Categoria'] = categorizations
        df['Confianca_Categoria'] = confidences
        
        # Log low confidence categorizations
        low_confidence = df[df['Confianca_Categoria'] < 0.3]
        if not low_confidence.empty:
            logger.info(f"{len(low_confidence)} establishments categorized with low confidence")
        
        return df
    
    def process_all_files(self) -> Tuple[pd.DataFrame, List[DataValidationResult]]:
        """Process all files in the data directories."""
        all_dataframes = []
        validation_results = []
        
        # Process credit files
        config.PASTA_CREDITO.mkdir(parents=True, exist_ok=True)
        for file_path in glob.glob(str(config.PASTA_CREDITO / "*.csv")):
            df, validation = self.process_file(file_path, 'credito')
            if not df.empty:
                all_dataframes.append(df)
            validation_results.append(validation)
        
        # Process debit files
        config.PASTA_DEBITO.mkdir(parents=True, exist_ok=True)
        for file_path in glob.glob(str(config.PASTA_DEBITO / "*.csv")):
            df, validation = self.process_file(file_path, 'debito')
            if not df.empty:
                all_dataframes.append(df)
            validation_results.append(validation)
        
        if not all_dataframes:
            logger.warning("No valid data files found")
            return pd.DataFrame(), validation_results
        
        # Combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Final cleaning and validation
        combined_df = self._final_cleaning(combined_df)
        
        return combined_df, validation_results
    
    def _final_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final cleaning and validation of combined data."""
        # Remove rows with missing critical data
        df = df.dropna(subset=['Data', 'Valor'])
        
        # Remove known problematic establishments
        problematic_establishments = [
            'pagamento de fatura', 'pagamentos validos normais',
            'transferencia', 'transfer', 'pix', 'ted', 'doc'
        ]
        
        if 'Estabelecimento' in df.columns:
            df['Estabelecimento'] = df['Estabelecimento'].astype(str)
            mask = df['Estabelecimento'].str.strip().str.lower().isin(problematic_establishments)
            df = df[~mask]
        
        # Sort by date
        df = df.sort_values(by='Data', ascending=False).reset_index(drop=True)
        
        return df

# Global data processor instance
data_processor = DataProcessor()

# --- Data Quality Monitoring System ---
class DataQualityMonitor:
    """Advanced data quality monitoring system."""
    
    def __init__(self):
        self.quality_thresholds = {
            'min_success_rate': 90.0,
            'min_categorization_quality': 70.0,
            'max_duplicate_rate': 5.0,
            'max_missing_rate': 2.0,
            'max_extreme_value_rate': 1.0
        }
        self.alert_history = []
    
    def analyze_data_quality(self, df: pd.DataFrame, validation_results: List[DataValidationResult]) -> Dict:
        """Comprehensive data quality analysis."""
        quality_report = {
            'overall_score': 0.0,
            'metrics': {},
            'alerts': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if df.empty:
            quality_report['alerts'].append("No data available for analysis")
            return quality_report
        
        # Calculate quality metrics
        metrics = self._calculate_quality_metrics(df, validation_results)
        quality_report['metrics'] = metrics
        
        # Generate alerts
        alerts = self._generate_alerts(metrics)
        quality_report['alerts'] = alerts
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, alerts)
        quality_report['recommendations'] = recommendations
        
        # Calculate overall score
        quality_report['overall_score'] = self._calculate_overall_score(metrics)
        
        # Store alert history
        self.alert_history.append({
            'timestamp': datetime.now(),
            'score': quality_report['overall_score'],
            'alerts': alerts
        })
        
        return quality_report
    
    def _calculate_quality_metrics(self, df: pd.DataFrame, validation_results: List[DataValidationResult]) -> Dict:
        """Calculate detailed quality metrics."""
        metrics = {}
        
        # Basic metrics
        total_rows = len(df)
        metrics['total_rows'] = total_rows
        
        # Missing data analysis
        missing_data = {}
        for col in ['Data', 'Estabelecimento', 'Valor', 'Tipo', 'Categoria']:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                missing_rate = (missing_count / total_rows) * 100 if total_rows > 0 else 0
                missing_data[col] = {
                    'count': missing_count,
                    'rate': missing_rate
                }
        metrics['missing_data'] = missing_data
        
        # Duplicate analysis
        duplicates = df.duplicated().sum()
        duplicate_rate = (duplicates / total_rows) * 100 if total_rows > 0 else 0
        metrics['duplicates'] = {
            'count': duplicates,
            'rate': duplicate_rate
        }
        
        # Value distribution analysis
        if 'Valor' in df.columns:
            extreme_values = df[df['Valor'].abs() > 1000000].shape[0]  # > R$ 1M
            extreme_rate = (extreme_values / total_rows) * 100 if total_rows > 0 else 0
            metrics['extreme_values'] = {
                'count': extreme_values,
                'rate': extreme_rate
            }
            
            # Value range
            metrics['value_range'] = {
                'min': df['Valor'].min(),
                'max': df['Valor'].max(),
                'mean': df['Valor'].mean(),
                'median': df['Valor'].median()
            }
        
        # Date range analysis
        if 'Data' in df.columns:
            date_range = df['Data'].max() - df['Data'].min()
            metrics['date_range'] = {
                'start': df['Data'].min().isoformat(),
                'end': df['Data'].max().isoformat(),
                'days': date_range.days
            }
        
        # Categorization quality
        if 'Confianca_Categoria' in df.columns:
            high_confidence = df[df['Confianca_Categoria'] >= 0.7].shape[0]
            medium_confidence = df[(df['Confianca_Categoria'] >= 0.3) & (df['Confianca_Categoria'] < 0.7)].shape[0]
            low_confidence = df[df['Confianca_Categoria'] < 0.3].shape[0]
            
            metrics['categorization'] = {
                'high_confidence': high_confidence,
                'medium_confidence': medium_confidence,
                'low_confidence': low_confidence,
                'quality_score': (high_confidence / total_rows) * 100 if total_rows > 0 else 0
            }
        
        # Category distribution
        if 'Categoria' in df.columns:
            category_counts = df['Categoria'].value_counts()
            metrics['category_distribution'] = {
                'unique_categories': len(category_counts),
                'most_common': category_counts.index[0] if len(category_counts) > 0 else None,
                'most_common_count': category_counts.iloc[0] if len(category_counts) > 0 else 0
            }
        
        # Validation results summary
        if validation_results:
            total_processed = sum(v.processed_rows for v in validation_results)
            total_invalid = sum(v.invalid_rows for v in validation_results)
            total_errors = sum(len(v.errors) for v in validation_results)
            total_warnings = sum(len(v.warnings) for v in validation_results)
            
            metrics['validation'] = {
                'total_processed': total_processed,
                'total_invalid': total_invalid,
                'total_errors': total_errors,
                'total_warnings': total_warnings,
                'success_rate': ((total_processed - total_invalid) / total_processed) * 100 if total_processed > 0 else 0
            }
        
        return metrics
    
    def _generate_alerts(self, metrics: Dict) -> List[str]:
        """Generate alerts based on quality metrics."""
        alerts = []
        
        # Check success rate
        if 'validation' in metrics:
            success_rate = metrics['validation']['success_rate']
            if success_rate < self.quality_thresholds['min_success_rate']:
                alerts.append(f"⚠️ Taxa de sucesso baixa: {success_rate:.1f}% (mínimo: {self.quality_thresholds['min_success_rate']}%)")
        
        # Check categorization quality
        if 'categorization' in metrics:
            quality_score = metrics['categorization']['quality_score']
            if quality_score < self.quality_thresholds['min_categorization_quality']:
                alerts.append(f"⚠️ Qualidade de categorização baixa: {quality_score:.1f}% (mínimo: {self.quality_thresholds['min_categorization_quality']}%)")
        
        # Check duplicate rate
        if 'duplicates' in metrics:
            duplicate_rate = metrics['duplicates']['rate']
            if duplicate_rate > self.quality_thresholds['max_duplicate_rate']:
                alerts.append(f"⚠️ Taxa de duplicatas alta: {duplicate_rate:.1f}% (máximo: {self.quality_thresholds['max_duplicate_rate']}%)")
        
        # Check missing data
        if 'missing_data' in metrics:
            for col, data in metrics['missing_data'].items():
                if data['rate'] > self.quality_thresholds['max_missing_rate']:
                    alerts.append(f"⚠️ Dados faltantes na coluna '{col}': {data['rate']:.1f}% (máximo: {self.quality_thresholds['max_missing_rate']}%)")
        
        # Check extreme values
        if 'extreme_values' in metrics:
            extreme_rate = metrics['extreme_values']['rate']
            if extreme_rate > self.quality_thresholds['max_extreme_value_rate']:
                alerts.append(f"⚠️ Taxa de valores extremos alta: {extreme_rate:.1f}% (máximo: {self.quality_thresholds['max_extreme_value_rate']}%)")
        
        # Check data freshness
        if 'date_range' in metrics:
            days_old = (datetime.now() - datetime.fromisoformat(metrics['date_range']['end'])).days
            if days_old > 30:
                alerts.append(f"⚠️ Dados desatualizados: {days_old} dias desde a última transação")
        
        return alerts
    
    def _generate_recommendations(self, metrics: Dict, alerts: List[str]) -> List[str]:
        """Generate recommendations based on quality issues."""
        recommendations = []
        
        # Recommendations based on alerts
        if any("Taxa de sucesso baixa" in alert for alert in alerts):
            recommendations.append("🔧 Revise os arquivos de entrada para identificar problemas de formato")
            recommendations.append("🔧 Verifique se todos os arquivos CSV estão no formato esperado")
        
        if any("Qualidade de categorização baixa" in alert for alert in alerts):
            recommendations.append("🔧 Adicione mais palavras-chave às regras de categorização")
            recommendations.append("🔧 Revise estabelecimentos com baixa confiança e ajuste as regras")
        
        if any("Taxa de duplicatas alta" in alert for alert in alerts):
            recommendations.append("🔧 Implemente verificação de duplicatas no processamento")
            recommendations.append("🔧 Revise se há arquivos duplicados nas pastas de dados")
        
        if any("Dados faltantes" in alert for alert in alerts):
            recommendations.append("🔧 Implemente validação mais rigorosa dos dados de entrada")
            recommendations.append("🔧 Verifique se todos os campos obrigatórios estão presentes")
        
        if any("Valores extremos" in alert for alert in alerts):
            recommendations.append("🔧 Implemente filtros para valores extremos")
            recommendations.append("🔧 Revise transações com valores muito altos")
        
        if any("Dados desatualizados" in alert for alert in alerts):
            recommendations.append("🔧 Atualize regularmente os dados financeiros")
            recommendations.append("🔧 Configure alertas para dados desatualizados")
        
        # General recommendations
        if not alerts:
            recommendations.append("✅ Qualidade de dados excelente! Continue mantendo os padrões")
        
        return recommendations
    
    def _calculate_overall_score(self, metrics: Dict) -> float:
        """Calculate overall data quality score."""
        score = 100.0
        
        # Penalize based on various factors
        if 'validation' in metrics:
            success_rate = metrics['validation']['success_rate']
            score -= (100 - success_rate) * 0.3
        
        if 'categorization' in metrics:
            quality_score = metrics['categorization']['quality_score']
            score -= (100 - quality_score) * 0.2
        
        if 'duplicates' in metrics:
            duplicate_rate = metrics['duplicates']['rate']
            score -= duplicate_rate * 0.5
        
        if 'missing_data' in metrics:
            for col, data in metrics['missing_data'].items():
                score -= data['rate'] * 0.3
        
        if 'extreme_values' in metrics:
            extreme_rate = metrics['extreme_values']['rate']
            score -= extreme_rate * 0.5
        
        return max(0.0, min(100.0, score))
    
    def get_quality_trend(self, days: int = 30) -> List[Dict]:
        """Get quality trend over time."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_alerts = [
            alert for alert in self.alert_history 
            if alert['timestamp'] >= cutoff_date
        ]
        return recent_alerts

# Global quality monitor instance
quality_monitor = DataQualityMonitor()

def debug_dados_previsao(df_historico: pd.DataFrame) -> dict:
    """
    Função de debug para verificar a qualidade dos dados antes da previsão.
    """
    debug_info = {
        'total_registros': len(df_historico),
        'registros_despesa': len(df_historico[df_historico['Tipo'] == 'Despesa']),
        'colunas': list(df_historico.columns),
        'tipos_dados': df_historico.dtypes.to_dict(),
        'valores_unicos_tipo': df_historico['Tipo'].unique().tolist() if 'Tipo' in df_historico.columns else [],
        'valores_nulos': df_historico.isnull().sum().to_dict(),
        'datas_min_max': None,
        'gastos_mensais_info': None
    }
    
    if not df_historico.empty and 'Data' in df_historico.columns:
        df_historico['Data'] = pd.to_datetime(df_historico['Data'])
        debug_info['datas_min_max'] = {
            'min': df_historico['Data'].min().strftime('%Y-%m-%d'),
            'max': df_historico['Data'].max().strftime('%Y-%m-%d')
        }
        
        # Verificar gastos mensais
        df_despesas = df_historico[df_historico['Tipo'] == 'Despesa'].copy()
        if not df_despesas.empty:
            gastos_mensais = df_despesas.set_index('Data').resample('M')['Valor'].sum().abs().reset_index()
            debug_info['gastos_mensais_info'] = {
                'total_meses': len(gastos_mensais),
                'meses_com_dados': len(gastos_mensais[gastos_mensais['Valor'] > 0]),
                'valor_medio': gastos_mensais['Valor'].mean(),
                'valor_min': gastos_mensais['Valor'].min(),
                'valor_max': gastos_mensais['Valor'].max()
            }
    
    return debug_info

def salvar_configuracao_modelo(modelo_selecionado: str):
    """
    Salva a configuração do modelo selecionado.
    """
    try:
        config.OPENAI_MODEL = modelo_selecionado
        # Salvar em arquivo de configuração
        config_path = config.PASTA_PROCESSADOS / "configuracoes.json"
        config_data = {
            "openai_model": modelo_selecionado,
            "openai_temperature": config.OPENAI_TEMPERATURE,
            "max_tokens": config.MAX_TOKENS,
            "allow_dangerous_code": config.ALLOW_DANGEROUS_CODE
        }
        
        config.PASTA_PROCESSADOS.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuração do modelo salva: {modelo_selecionado}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar configuração do modelo: {e}")
        return False

def carregar_configuracao_modelo():
    """
    Carrega a configuração do modelo salva.
    Retorna GPT-4.1 Nano como padrão se não houver configuração.
    """
    try:
        config_path = config.PASTA_PROCESSADOS / "configuracoes.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Atualizar configurações
            if 'openai_model' in config_data:
                config.OPENAI_MODEL = config_data['openai_model']
            if 'openai_temperature' in config_data:
                config.OPENAI_TEMPERATURE = config_data['openai_temperature']
            if 'max_tokens' in config_data:
                config.MAX_TOKENS = config_data['max_tokens']
            if 'allow_dangerous_code' in config_data:
                config.ALLOW_DANGEROUS_CODE = config_data['allow_dangerous_code']
            
            logger.info(f"Configuração carregada: {config.OPENAI_MODEL}")
            return config.OPENAI_MODEL
        else:
            # Se não há configuração salva, usar GPT-4.1 Nano como padrão
            logger.info("Nenhuma configuração encontrada. Usando GPT-4.1 Nano como padrão.")
            return "gpt-4.1-nano"
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        # Em caso de erro, usar GPT-4.1 Nano como padrão
        return "gpt-4.1-nano"