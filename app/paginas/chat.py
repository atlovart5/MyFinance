# finbot_project/app/paginas/chat.py

import streamlit as st
import pandas as pd
import re
import logging

# --- CORREÇÃO INICIADA ---
# A importação foi dividida. 'chatbot_financeiro' vem do backend,
# mas as configurações como 'ARQUIVO_CONSOLIDADO' vêm do objeto 'config'.
from backend import chatbot_financeiro
from config import config
# --- CORREÇÃO FINALIZADA ---

logger = logging.getLogger(__name__)

def layout():
    """
    Renderiza a página de chat com o assistente financeiro.
    """
    st.header("💬 Converse com Seus Dados")
    st.info("Faça perguntas em linguagem natural sobre suas finanças. Ex: 'Qual foi meu maior gasto em julho?' ou 'Crie um gráfico de pizza dos meus gastos por categoria'.")

    # Inicializa o histórico do chat na sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe as mensagens do histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "chart" in message:
                try:
                    st.image(message["chart"])
                except Exception as e:
                    st.error(f"Erro ao exibir gráfico: {e}")

    # Prepara os dataframes para o agente de IA
    try:
        # --- CORREÇÃO INICIADA ---
        # A variável agora é acessada através do objeto 'config'
        if not config.ARQUIVO_CONSOLIDADO.exists():
             st.error("O arquivo de dados consolidados (dados_consolidados.csv) não foi encontrado. Por favor, processe as faturas primeiro na página 'Processamento'.")
             return
        
        df1 = pd.read_csv(config.ARQUIVO_CONSOLIDADO, sep=';')
        # --- CORREÇÃO FINALIZADA ---
        
        # Validação de dados
        if df1.empty:
            st.error("O arquivo de dados consolidados está vazio. Por favor, processe as faturas primeiro.")
            return
        
        required_columns = ['Data', 'Estabelecimento', 'Valor', 'Tipo']
        missing_columns = [col for col in required_columns if col not in df1.columns]
        if missing_columns:
            st.error(f"Colunas obrigatórias ausentes no arquivo de dados: {missing_columns}")
            return
        
        # Garante que a coluna 'Data' esteja no formato datetime antes de passar para o agente.
        df1['Data'] = pd.to_datetime(df1['Data'], errors='coerce')
        
        # Remove linhas com datas inválidas
        invalid_dates = df1['Data'].isna().sum()
        if invalid_dates > 0:
            st.warning(f"Encontradas {invalid_dates} linhas com datas inválidas. Estas serão ignoradas.")
            df1 = df1.dropna(subset=['Data'])
        
        # Valida valores numéricos
        df1['Valor'] = pd.to_numeric(df1['Valor'], errors='coerce')
        invalid_values = df1['Valor'].isna().sum()
        if invalid_values > 0:
            st.warning(f"Encontrados {invalid_values} valores inválidos na coluna 'Valor'. Estes serão ignorados.")
            df1 = df1.dropna(subset=['Valor'])
        
        if df1.empty:
            st.error("Após a limpeza, não restaram dados válidos para análise.")
            return

        df2 = df1.groupby('Estabelecimento')['Valor'].sum().reset_index()
        df_temp_mes = df1.copy()
        df_temp_mes['Mes'] = df_temp_mes['Data'].dt.to_period('M').astype(str)
        df3 = df_temp_mes.groupby(['Mes', 'Categoria', 'Pagador'])['Valor'].sum().reset_index()
        
        dfs_para_agente = [df1, df2, df3]

    except FileNotFoundError:
        st.error("O arquivo de dados consolidados (dados_consolidados.csv) não foi encontrado. Por favor, processe as faturas primeiro.")
        return
    except pd.errors.EmptyDataError:
        st.error("O arquivo de dados consolidados está vazio. Por favor, processe as faturas primeiro.")
        return
    except pd.errors.ParserError as e:
        st.error(f"Erro ao ler o arquivo de dados: {e}. Verifique se o formato está correto.")
        return
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar dados: {e}")
        st.error(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
        return

    # Input do usuário
    if prompt := st.chat_input("Sua pergunta..."):
        # Validação do input
        if not prompt.strip():
            st.warning("Por favor, digite uma pergunta.")
            return
        
        if len(prompt.strip()) < 3:
            st.warning("A pergunta deve ter pelo menos 3 caracteres.")
            return
        
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gera e exibe a resposta do assistente
        with st.chat_message("assistant"):
            with st.spinner("FinBot está pensando..."):
                try:
                    response_text = chatbot_financeiro(dfs_para_agente, prompt)
                    
                    if not response_text or response_text.strip() == "":
                        st.error("O assistente não retornou uma resposta válida.")
                        return
                    
                    # Verifica se a resposta contém um caminho de gráfico
                    chart_match = re.search(r'\[chart_path:(.*?)\]', response_text)
                    
                    if chart_match:
                        chart_path = chart_match.group(1).strip()
                        # Remove a tag do texto da resposta
                        response_text_clean = re.sub(r'\[chart_path:.*?\]', '', response_text).strip()
                        
                        st.markdown(response_text_clean)
                        try:
                            st.image(chart_path)
                            # Adiciona a resposta e o gráfico ao histórico
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": response_text_clean,
                                "chart": chart_path
                            })
                        except FileNotFoundError:
                            st.error(f"Arquivo de gráfico não encontrado: {chart_path}")
                            st.session_state.messages.append({"role": "assistant", "content": response_text_clean})
                        except Exception as e:
                            st.error(f"Não foi possível exibir o gráfico em '{chart_path}'. Erro: {e}")
                            st.session_state.messages.append({"role": "assistant", "content": response_text_clean})

                    else:
                        st.markdown(response_text)
                        # Adiciona apenas a resposta de texto ao histórico
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                except Exception as e:
                    logger.error(f"Erro no chatbot: {e}")
                    error_message = f"Ocorreu um erro ao processar sua pergunta: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

    # Adiciona botão para limpar histórico
    if st.session_state.messages:
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.messages = []
            st.rerun()
