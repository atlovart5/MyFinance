import streamlit as st
from dotenv import load_dotenv
import sys
import os

# Carrega as variáveis de ambiente. O Streamlit é inteligente o suficiente
# para encontrar o arquivo .env na pasta raiz do projeto.
load_dotenv()

# Adiciona o diretório 'app' ao path para garantir que os imports funcionem
# independentemente de como o script é executado.
# Isso torna a estrutura de imports mais robusta.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Como o Streamlit executa o script a partir da pasta 'app',
# importamos os módulos diretamente, sem o prefixo 'app.'.
from backend import (
    processar_faturas,
    criar_graficos,
    gerar_relatorio_pdf,
    prever_gastos,
    chatbot_financeiro,
    assistente_pagamento
)
# Assumindo que existe um arquivo layout.py
from layout import (
    configurar_pagina,
    exibir_sidebar,
    exibir_pagina_principal
)
from paginas.chat import layout as layout_chat
from paginas.relatorios import layout as layout_relatorios
from paginas.assistente_pagador import layout as layout_assistente
from paginas.previsao import layout as layout_previsao
from paginas.metas_financeiras import layout as layout_metas
from paginas.analytics import layout as layout_analytics
from paginas.orcamento import layout as layout_orcamento
from paginas.processamento import layout as layout_processamento
from paginas.dashboard_enhanced import layout as layout_dashboard_enhanced
from paginas.configuracoes import layout as layout_configuracoes


def main():
    """
    Função principal que executa a aplicação FinBot.
    """
    configurar_pagina()

    # O processamento de faturas pode ser pesado, então o ideal é usar o cache do Streamlit
    # para não reprocessar a cada interação na UI.
    @st.cache_data
    def carregar_dados():
        df = processar_faturas()
        return df

    @st.cache_data
    def carregar_graficos(df):
        fig_col, fig_lin = criar_graficos(df)
        return fig_col, fig_lin

    df_consolidado = carregar_dados()
    
    # Só cria os gráficos se o dataframe não estiver vazio
    if df_consolidado is not None and not df_consolidado.empty:
        fig_coluna, fig_linha = carregar_graficos(df_consolidado)
    else:
        fig_coluna, fig_linha = None, None

    pagina_selecionada = exibir_sidebar()

    # Dicionário que mapeia o nome da página para a função que a renderiza
    paginas = {
        "Dashboard": layout_dashboard_enhanced,
        "Analytics": layout_analytics,
        "Metas Financeiras": layout_metas,
        "Orçamento": layout_orcamento,
        "Processamento": layout_processamento,
        "Configurações": layout_configuracoes,
        "Relatórios": layout_relatorios,
        "Previsão de Gastos": layout_previsao,
        "Assistente de Pagamento": layout_assistente,
        "Converse com seus Dados": layout_chat
    }

    if pagina_selecionada in paginas:
        # Chama a função correspondente à página selecionada
        paginas[pagina_selecionada]()
    else:
        st.error("Página não encontrada!")
        # Exibe o dashboard enhanced como padrão em caso de erro
        layout_dashboard_enhanced()


if __name__ == "__main__":
    main()
