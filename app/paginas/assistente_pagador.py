# finbot_project/app/paginas/assistente_pagador.py

import streamlit as st
import pandas as pd
from datetime import datetime

# --- CORREÇÃO INICIADA ---
# As importações foram separadas. Funções vêm do backend,
# e variáveis de configuração vêm do objeto 'config'.
from backend import (
    carregar_dados_brutos, aplicar_regras_contexto,
    carregar_json, atualizar_contexto_pagador
)
from config import config
# --- CORREÇÃO FINALIZADA ---

DATA_CORTE_PAGADOR = "2025-06-01"

def layout():
    """Renderiza a página do assistente de atribuição de pagador/recebedor."""
    st.header("✨ Assistente de Atribuição")
    st.info("Detectamos transações que precisam de uma atribuição. Por favor, classifique cada uma delas.")

    if 'df_em_processo' not in st.session_state or st.session_state.df_em_processo is None:
        try:
            df_bruto = carregar_dados_brutos()
            if df_bruto is None or df_bruto.empty:
                st.error("Nenhum arquivo .csv encontrado nas pastas 'data/raw/credito' ou 'data/raw/debito'.")
                return # Usar return em vez de st.stop()

            # --- CORREÇÃO INICIADA ---
            # Acessando a variável através do objeto 'config'
            contexto = carregar_json(str(config.ARQUIVO_CONTEXTO))
            # --- CORREÇÃO FINALIZADA ---
            st.session_state.df_em_processo = aplicar_regras_contexto(df_bruto, contexto)
        except ValueError as e:
            st.error(e)
            return # Usar return em vez de st.stop()

    df_para_processar = st.session_state.df_em_processo
    data_corte = pd.to_datetime(DATA_CORTE_PAGADOR)
    
    # O filtro agora procura por transações (despesas ou receitas) que não têm um 'Pagador' atribuído.
    filtro_necessario = (df_para_processar['Data'] >= data_corte) & (df_para_processar['Pagador'].isnull())
    transacoes_a_categorizar = df_para_processar[filtro_necessario]

    if transacoes_a_categorizar.empty:
        st.success("Nenhuma transação nova precisa de atribuição!")
        if st.button("Concluir e Ir para o Dashboard"):
            df_final = st.session_state.df_em_processo.copy()
            df_final['Pagador'].fillna('Não Aplicável', inplace=True)
            # --- CORREÇÃO INICIADA ---
            # Acessando a variável através do objeto 'config'
            df_final.to_csv(config.ARQUIVO_CONSOLIDADO, index=False, sep=';', encoding='utf-8')
            # --- CORREÇÃO FINALIZADA ---
            st.session_state.categorizacao_concluida = True
            st.rerun()
        return

    indice_atual = st.session_state.get('indice_transacao_atual', 0)
    total_transacoes = len(transacoes_a_categorizar)

    if indice_atual < total_transacoes:
        transacao = transacoes_a_categorizar.iloc[indice_atual]
        st.progress((indice_atual + 1) / total_transacoes)
        st.write(f"**Transação {indice_atual + 1} de {total_transacoes}**")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Data", f"{transacao['Data'].strftime('%d/%m/%Y')}")
        col2.metric("Estabelecimento", f"{transacao['Estabelecimento']}")
        
        # Adapta a cor e o texto do valor com base no tipo da transação
        if transacao['Tipo'] == 'Receita':
            cor_valor = "green"
            texto_valor = f"R$ {transacao['Valor']:.2f}"
            label_radio = "Quem foi o recebedor?"
            opcoes_radio = ["Arthur"] # Para receitas, só pode ser você
        else: # Despesa
            cor_valor = "red"
            texto_valor = f"R$ {abs(transacao['Valor']):.2f}"
            label_radio = "Quem foi o pagador?"
            opcoes_radio = ["Arthur", "Pai", "EPR"]

        col3.markdown(f"""
        <div style="margin-top: 20px;">
            <p style="font-size: 1rem; color: #808495; margin-bottom: -5px;">Valor</p>
            <p style="font-size: 1.75rem; color: {cor_valor};">{texto_valor}</p>
        </div>
        """, unsafe_allow_html=True)
        
        atribuicao = st.radio(label_radio, opcoes_radio, key=f"pagador_{transacao.name}", horizontal=True)
        
        st.divider()
        col_btn1, col_btn2 = st.columns([3, 1])

        with col_btn1:
            lembrar_escolha = st.checkbox(
                "Lembrar desta atribuição para este estabelecimento", 
                key=f"lembrar_{transacao.name}"
            )
        
        with col_btn2:
            if st.button("Confirmar e Próxima", key=f"btn_{transacao.name}", use_container_width=True):
                st.session_state.df_em_processo.loc[transacao.name, 'Pagador'] = atribuicao
                
                if lembrar_escolha:
                    nome_estabelecimento = transacao['Estabelecimento']
                    atualizar_contexto_pagador(nome_estabelecimento, atribuicao)
                    st.toast(f"Regra salva: '{nome_estabelecimento}' será sempre de '{atribuicao}'.", icon="💾")

                st.session_state.indice_transacao_atual = indice_atual + 1
                st.rerun()
    else:
        st.success("Todas as transações foram atribuídas! Clique abaixo para salvar.")
        if st.button("Concluir e Salvar Dados", type="primary"):
            with st.spinner("Salvando dados consolidados..."):
                df_final = st.session_state.df_em_processo.copy()
                df_final['Pagador'].fillna('Não Aplicável', inplace=True)
                # --- CORREÇÃO INICIADA ---
                # Acessando a variável através do objeto 'config'
                df_final.to_csv(config.ARQUIVO_CONSOLIDADO, index=False, sep=';', encoding='utf-8')
                # --- CORREÇÃO FINALIZADA ---
                st.session_state.categorizacao_concluida = True
                st.rerun()
