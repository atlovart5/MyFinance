# finbot_project/app/layout.py

import streamlit as st
from datetime import datetime
import os

def configurar_pagina():
    """
    Configura as propriedades da página do Streamlit.
    """
    st.set_page_config(
        page_title="FinBot - Seu Assistente Financeiro",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def exibir_sidebar():
    """
    Cria e exibe a barra lateral de navegação e funcionalidades.
    """
    with st.sidebar:
        st.title("FinBot 🤖")
        st.markdown("---")

        # Adicionadas as novas páginas à lista de navegação.
        pagina_selecionada = st.radio(
            "Navegação",
            ["Dashboard", "Analytics", "Metas Financeiras", "Orçamento", "Processamento", "Configurações", "Relatórios", "Previsão de Gastos", "Assistente de Pagamento", "Converse com seus Dados"],
            key="navigation_radio"
        )
        
        st.markdown("---")

    return pagina_selecionada

def exibir_pagina_principal(titulo: str, layout_func):
    """
    Renderiza o conteúdo da página principal selecionada.

    Args:
        titulo (str): O título da página a ser exibido.
        layout_func (function): A função que renderiza o layout da página.
    """
    st.title(titulo)
    st.markdown("---")
    
    # Chama a função de layout específica da página
    layout_func()
