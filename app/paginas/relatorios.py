# finbot_project/app/paginas/relatorios.py

import streamlit as st
import base64
import os
import pandas as pd
from datetime import datetime

# --- CORREÇÃO INICIADA ---
# A importação foi dividida. A função vem do 'backend' e as
# configurações de pastas vêm do objeto 'config'.
from backend import gerar_relatorio_pdf, obter_periodos_disponiveis
from config import config
# --- CORREÇÃO FINALIZADA ---

def _display_pdf(file_path):
    """Função auxiliar para exibir um PDF na tela."""
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo do relatório não encontrado em '{file_path}'. Tente gerá-lo novamente.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao tentar exibir o PDF: {e}")

def layout():
    """Renderiza o conteúdo da página de relatórios."""
    st.header("📄 Relatórios Mensais")
    st.markdown("Gere e visualize seus relatórios financeiros em formato PDF.")

    # --- Seção de Geração de Relatório ---
    st.subheader("Gerar Novo Relatório")
    
    # Obter períodos disponíveis nos dados
    periodos = obter_periodos_disponiveis()
    
    if not periodos["anos"]:
        st.warning("Não há dados processados disponíveis. Processe os dados para gerar relatórios.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        ano_selecionado = st.selectbox(
            "Selecione o Ano",
            options=periodos["anos"],
            index=len(periodos["anos"]) - 1  # Seleciona o ano mais recente por padrão
        )
    with col2:
        # Obter meses disponíveis para o ano selecionado
        meses_disponiveis = periodos["meses_por_ano"].get(ano_selecionado, [])
        if not meses_disponiveis:
            st.error(f"Não há dados para o ano {ano_selecionado}")
            return
            
        mes_selecionado = st.selectbox(
            "Selecione o Mês",
            options=meses_disponiveis,
            format_func=lambda mes: datetime(ano_selecionado, mes, 1).strftime("%B"),
            index=len(meses_disponiveis) - 1  # Seleciona o mês mais recente por padrão
        )

    if st.button("Gerar Relatório PDF", key="gerar_relatorio_btn"):
        with st.spinner(f"Gerando relatório para {mes_selecionado:02d}/{ano_selecionado}..."):
            try:
                # Carregar dados para o período selecionado
                if config.ARQUIVO_CONSOLIDADO.exists():
                    df = pd.read_csv(config.ARQUIVO_CONSOLIDADO, sep=';', parse_dates=['Data'])
                    # Filtrar dados para o período selecionado
                    df_periodo = df[
                        (df['Data'].dt.year == ano_selecionado) & 
                        (df['Data'].dt.month == mes_selecionado)
                    ]
                    
                    if not df_periodo.empty:
                        caminho_pdf = gerar_relatorio_pdf(df, ano_selecionado, mes_selecionado)
                        if caminho_pdf:
                            st.success(f"Relatório gerado com sucesso! '{os.path.basename(caminho_pdf)}'")
                            st.balloons()
                        else:
                            st.warning("Não foram encontrados dados para o período selecionado.")
                    else:
                        st.warning("Não há dados para o período selecionado.")
                else:
                    st.error("Arquivo de dados consolidados não encontrado.")
            except Exception as e:
                st.error(f"Falha ao gerar o relatório: {e}")

    st.markdown("---")

    # --- Seção de Visualização de Relatórios ---
    st.subheader("Visualizar Relatórios Gerados")
    
    try:
        # --- CORREÇÃO INICIADA ---
        # A variável agora é acessada através do objeto 'config'
        config.PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
        arquivos_pdf = [f for f in os.listdir(config.PASTA_RELATORIOS) if f.endswith('.pdf')]
        # --- CORREÇÃO FINALIZADA ---
        arquivos_pdf.sort(reverse=True) # Mostra os mais recentes primeiro
    except Exception as e:
        st.error(f"Não foi possível acessar a pasta de relatórios: {e}")
        arquivos_pdf = []

    if not arquivos_pdf:
        st.info("Nenhum relatório em PDF foi encontrado. Use a opção acima para gerar um novo.")
        return

    pdf_selecionado = st.selectbox(
        "Selecione um relatório para visualizar:",
        arquivos_pdf
    )

    if pdf_selecionado:
        # --- CORREÇÃO INICIADA ---
        # A variável agora é acessada através do objeto 'config'
        caminho_completo = os.path.join(config.PASTA_RELATORIOS, pdf_selecionado)
        # --- CORREÇÃO FINALIZADA ---
        _display_pdf(caminho_completo)

