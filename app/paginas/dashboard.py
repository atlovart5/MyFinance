# finbot_project/app/paginas/dashboard.py

import streamlit as st
from datetime import datetime

# CORREÇÃO: Nome da função alterado para 'layout' e adicionado argumentos
def layout(df_completo, fig_coluna, fig_linha):
    """
    Renderiza o conteúdo da página do dashboard.

    Args:
        df_completo (pd.DataFrame): O DataFrame com todos os dados.
        fig_coluna (go.Figure): A figura do gráfico de colunas (gastos por categoria).
        fig_linha (go.Figure): A figura do gráfico de linhas (evolução dos gastos).
    """
    
    st.subheader("Visão Geral dos Gastos")
    
    if df_completo.empty:
        st.warning("Não há dados para exibir. Verifique se suas planilhas foram processadas.")
        return

    # Exibe os gráficos principais
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_coluna, use_container_width=True)
    with col2:
        st.plotly_chart(fig_linha, use_container_width=True)

    st.divider()

    # Exibe a tabela com as últimas transações
    st.subheader("Últimas Transações")
    st.dataframe(df_completo.head(10), use_container_width=True)

