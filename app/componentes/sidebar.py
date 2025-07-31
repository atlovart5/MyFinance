# finbot_project/app/componentes/sidebar.py

import streamlit as st
import os
import pandas as pd
from datetime import datetime
from app.backend import (
    salvar_json, gerar_relatorio_pdf, ARQUIVO_CONTEXTO, ARQUIVO_ORCAMENTO
)

def render_sidebar():
    """Renderiza todos os componentes da barra lateral."""
    with st.sidebar:
        st.header("Controles")
        _gerenciar_orcamentos()
        st.markdown("---")
        _gerar_relatorio_mensal()
        st.markdown("---")
        _gerenciar_regras_fixas()

def _gerenciar_orcamentos():
    with st.expander("💰 Gerenciar Orçamentos", expanded=False):
        st.write("**Definir/Atualizar Orçamento:**")
        categorias_disponiveis = [""] + sorted(st.session_state.df_completo['Categoria'].unique().tolist())
        with st.form("form_orcamento", clear_on_submit=True):
            cat_orc_input = st.selectbox("Categoria", options=categorias_disponiveis)
            val_orc_input = st.number_input("Valor do Orçamento (R$)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Salvar Orçamento") and cat_orc_input and val_orc_input > 0:
                novo_orcamento = st.session_state.orcamento.copy()
                novo_orcamento[cat_orc_input] = val_orc_input
                salvar_json(ARQUIVO_ORCAMENTO, novo_orcamento)
                st.session_state.orcamento = novo_orcamento
                st.toast("Orçamento salvo!", icon="✅")
        
        st.write("**Remover Orçamento:**")
        if st.session_state.orcamento:
            cat_para_remover = st.selectbox("Selecione para remover", options=[""] + list(st.session_state.orcamento.keys()), key="remover_orc")
            if st.button("Remover", type="secondary") and cat_para_remover:
                novo_orcamento = st.session_state.orcamento.copy()
                del novo_orcamento[cat_para_remover]
                salvar_json(ARQUIVO_ORCAMENTO, novo_orcamento)
                st.session_state.orcamento = novo_orcamento
                st.rerun()
        else:
            st.caption("Nenhum orçamento definido.")

def _gerar_relatorio_mensal():
    st.subheader("Gerar Relatório Mensal")
    mes_map_inv = {i+1: v for i, v in enumerate(['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])}
    ano_selecionado = st.number_input("Ano", min_value=2020, max_value=2030, value=datetime.now().year)
    default_month_index = datetime.now().month - 1
    mes_selecionado = st.selectbox("Mês", options=list(mes_map_inv.keys()), format_func=lambda x: mes_map_inv[x], index=default_month_index)
    
    if st.button("Gerar Relatório em PDF"):
        with st.spinner(f"Gerando relatório para {mes_map_inv[mes_selecionado]}/{ano_selecionado}..."):
            caminho_pdf = gerar_relatorio_pdf(st.session_state.df_completo, ano_selecionado, mes_selecionado)
            if caminho_pdf:
                st.session_state.ultimo_relatorio_gerado = caminho_pdf
                st.success(f"Relatório '{os.path.basename(caminho_pdf)}' gerado com sucesso!")
            else:
                st.warning("Não há dados para o período selecionado.")
                st.session_state.ultimo_relatorio_gerado = None
                
    if st.session_state.get('ultimo_relatorio_gerado'):
        with open(st.session_state.ultimo_relatorio_gerado, "rb") as pdf_file:
            st.download_button(
                label="Baixar Relatório PDF",
                data=pdf_file,
                file_name=os.path.basename(st.session_state.ultimo_relatorio_gerado),
                mime='application/octet-stream'
            )

def _gerenciar_regras_fixas():
    with st.expander("Gerenciar Regras Fixas", expanded=False):
        st.write("**Regras Atuais:**")
        if not st.session_state.contexto:
            st.caption("Nenhuma regra definida.")
        else:
            regras_df = pd.DataFrame([
                {"Estabelecimento": k, "Categoria": v.get("categoria", "N/A"), "Pagador Fixo": v.get("pagador", "N/A")}
                for k, v in st.session_state.contexto.items()
            ])
            st.dataframe(regras_df, use_container_width=True, hide_index=True)
            
        st.write("**Adicionar/Editar Regra:**")
        with st.form("form_regra", clear_on_submit=True):
            est_input = st.text_input("Estabelecimento (Palavra-chave)")
            cat_input = st.text_input("Categoria")
            pag_input = st.selectbox("Pagador Fixo (opcional)", ["", "Arthur", "Pai", "EPR"])
            if st.form_submit_button("Salvar Regra"):
                if est_input and cat_input:
                    novo_contexto = st.session_state.contexto.copy()
                    novo_contexto[est_input] = {"categoria": cat_input, "pagador": pag_input if pag_input else None}
                    salvar_json(ARQUIVO_CONTEXTO, novo_contexto)
                    st.session_state.contexto = novo_contexto
                    st.success(f"Regra para '{est_input}' salva! Recarregue a página para aplicar as mudanças em novos dados.")
                else:
                    st.warning("Preencha pelo menos 'Estabelecimento' e 'Categoria'.")