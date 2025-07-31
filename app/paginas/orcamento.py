# finbot_project/app/paginas/orcamento.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# --- CORREÇÃO INICIADA ---
# As importações foram separadas. Funções vêm do backend,
# e o objeto de configuração vem de config.py.
from backend import carregar_json, salvar_json
from config import config
# --- CORREÇÃO FINALIZADA ---

# File paths for budget
BUDGET_FILE = config.PASTA_PROCESSADOS / "orcamento_detalhado.json"
BUDGET_HISTORY_FILE = config.PASTA_PROCESSADOS / "historico_orcamento.json"

def carregar_orcamento():
    """Carrega orçamento detalhado."""
    return carregar_json(str(BUDGET_FILE))

def salvar_orcamento(orcamento):
    """Salva orçamento detalhado."""
    salvar_json(str(BUDGET_FILE), orcamento)

def carregar_historico_orcamento():
    """Carrega histórico de orçamentos."""
    return carregar_json(str(BUDGET_HISTORY_FILE))

def salvar_historico_orcamento(historico):
    """Salva histórico de orçamentos."""
    salvar_json(str(BUDGET_HISTORY_FILE), historico)

def calcular_gastos_reais(df, mes_atual=None):
    """Calcula gastos reais por categoria."""
    if df.empty:
        return pd.Series(dtype=float)
    
    if mes_atual:
        df_filtrado = df[
            (df['Data'].dt.to_period('M') == mes_atual) & 
            (df['Tipo'] == 'Despesa')
        ]
    else:
        df_filtrado = df[df['Tipo'] == 'Despesa']
    
    return df_filtrado.groupby('Categoria')['Valor'].sum().abs()

def calcular_progresso_orcamento(orcamento, gastos_reais):
    """Calcula progresso do orçamento."""
    progresso = {}
    
    for categoria, limite in orcamento.items():
        gasto_atual = gastos_reais.get(categoria, 0)
        percentual = (gasto_atual / limite * 100) if limite > 0 else 0
        status = "dentro" if percentual <= 100 else "excedido"
        
        progresso[categoria] = {
            'limite': limite,
            'gasto_atual': gasto_atual,
            'percentual': percentual,
            'status': status,
            'restante': max(0, limite - gasto_atual)
        }
    
    return progresso

def gerar_recomendacoes_ai(progresso, gastos_reais):
    """Gera recomendações baseadas nos dados de orçamento."""
    recomendacoes = []
    
    # Análise de categorias excedidas
    categorias_excedidas = [
        cat for cat, data in progresso.items() 
        if data['status'] == 'excedido'
    ]
    
    if categorias_excedidas:
        recomendacoes.append(f"⚠️ **Categorias excedidas:** {', '.join(categorias_excedidas)}")
        recomendacoes.append("💡 Considere reduzir gastos nessas categorias ou ajustar o orçamento.")
    
    # Análise de categorias com bom controle
    categorias_controladas = [
        cat for cat, data in progresso.items() 
        if data['percentual'] <= 80 and data['gasto_atual'] > 0
    ]
    
    if categorias_controladas:
        recomendacoes.append(f"✅ **Bom controle:** {', '.join(categorias_controladas)}")
        recomendacoes.append("Continue mantendo o controle nessas categorias!")
    
    # Análise de categorias não utilizadas
    categorias_nao_utilizadas = [
        cat for cat, data in progresso.items() 
        if data['gasto_atual'] == 0
    ]
    
    if categorias_nao_utilizadas:
        recomendacoes.append(f"📝 **Categorias não utilizadas:** {', '.join(categorias_nao_utilizadas)}")
        recomendacoes.append("Considere se essas categorias são realmente necessárias.")
    
    # Análise geral
    total_orcado = sum(data['limite'] for data in progresso.values())
    total_gasto = sum(data['gasto_atual'] for data in progresso.values())
    
    if total_gasto > total_orcado:
        recomendacoes.append("🚨 **Orçamento geral excedido!**")
        recomendacoes.append("Revise suas prioridades e considere reduzir gastos.")
    elif total_gasto < total_orcado * 0.7:
        recomendacoes.append("💰 **Gastos abaixo do orçado!**")
        recomendacoes.append("Você está controlando bem seus gastos. Continue assim!")
    
    return recomendacoes

def criar_grafico_orcamento(progresso):
    """Cria gráfico de progresso do orçamento."""
    if not progresso:
        return go.Figure()
    
    categorias = list(progresso.keys())
    limites = [progresso[cat]['limite'] for cat in categorias]
    gastos = [progresso[cat]['gasto_atual'] for cat in categorias]
    cores = ['red' if progresso[cat]['status'] == 'excedido' else 'green' for cat in categorias]
    
    fig = go.Figure()
    
    # Barras de limite
    fig.add_trace(go.Bar(
        x=categorias,
        y=limites,
        name='Limite Orçado',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    # Barras de gastos
    fig.add_trace(go.Bar(
        x=categorias,
        y=gastos,
        name='Gastos Reais',
        marker_color=cores,
        opacity=0.9
    ))
    
    fig.update_layout(
        title="Progresso do Orçamento por Categoria",
        xaxis_title="Categoria",
        yaxis_title="Valor (R$)",
        barmode='group',
        height=500
    )
    
    return fig

def layout():
    """Renderiza a página de orçamento."""
    st.header("💰 Gestão de Orçamento")
    st.info("Defina limites de gastos por categoria e acompanhe seu progresso em tempo real.")
    
    # Carregar dados
    orcamento = carregar_orcamento()
    historico = carregar_historico_orcamento()
    
    # Carregar dados financeiros
    try:
        # --- CORREÇÃO INICIADA ---
        # Acessando a variável através do objeto 'config'
        if not config.ARQUIVO_CONSOLIDADO.exists():
            df = pd.DataFrame()
        else:
            df = pd.read_csv(str(config.ARQUIVO_CONSOLIDADO), sep=';')
            df['Data'] = pd.to_datetime(df['Data'])
        # --- CORREÇÃO FINALIZADA ---
    except FileNotFoundError:
        df = pd.DataFrame()
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "⚙️ Configurar", "📈 Histórico", "🤖 Recomendações"])
    
    with tab1:
        st.subheader("Dashboard do Orçamento")
        
        if not orcamento:
            st.warning("Nenhum orçamento configurado. Configure seu orçamento na aba 'Configurar'.")
        else:
            # Seletor de período
            col1, col2 = st.columns(2)
            with col1:
                periodo = st.selectbox(
                    "Período de Análise",
                    ["Mês Atual", "Últimos 3 Meses", "Últimos 6 Meses", "Ano Todo"],
                    index=0
                )
            
            # Definir o período de análise
            mes_atual = None
            if periodo == "Mês Atual":
                mes_atual = pd.Timestamp.now().to_period('M')
            
            # Calcular gastos reais
            gastos_reais = calcular_gastos_reais(df, mes_atual)
            
            # Calcular progresso
            progresso = calcular_progresso_orcamento(orcamento, gastos_reais)
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            total_orcado = sum(data['limite'] for data in progresso.values())
            total_gasto = sum(data['gasto_atual'] for data in progresso.values())
            percentual_geral = (total_gasto / total_orcado * 100) if total_orcado > 0 else 0
            
            with col1:
                st.metric("Total Orçado", f"R$ {total_orcado:,.2f}")
            
            with col2:
                st.metric("Total Gasto", f"R$ {total_gasto:,.2f}")
            
            with col3:
                st.metric("Restante", f"R$ {max(0, total_orcado - total_gasto):,.2f}")
            
            with col4:
                st.metric("Progresso Geral", f"{percentual_geral:.1f}%")
            
            # Gráfico de progresso
            fig_orcamento = criar_grafico_orcamento(progresso)
            st.plotly_chart(fig_orcamento, use_container_width=True)
            
            # Tabela detalhada
            st.subheader("Detalhes por Categoria")
            
            dados_tabela = []
            for categoria, data in progresso.items():
                dados_tabela.append({
                    'Categoria': categoria,
                    'Limite': f"R$ {data['limite']:,.2f}",
                    'Gasto Atual': f"R$ {data['gasto_atual']:,.2f}",
                    'Restante': f"R$ {data['restante']:,.2f}",
                    'Progresso': f"{data['percentual']:.1f}%",
                    'Status': "✅ Dentro" if data['status'] == 'dentro' else "⚠️ Excedido"
                })
            
            df_tabela = pd.DataFrame(dados_tabela)
            st.dataframe(df_tabela, use_container_width=True)
    
    with tab2:
        st.subheader("Configurar Orçamento")
        
        # Categorias padrão
        categorias_padrao = [
            "Alimentação", "Transporte", "Saúde", "Educação", "Lazer", 
            "Moradia", "Assinatura", "Investimento", "Outros"
        ]
        
        with st.form("configurar_orcamento"):
            st.write("**Defina limites mensais por categoria:**")
            
            orcamento_novo = {}
            col1, col2 = st.columns(2)
            
            for i, categoria in enumerate(categorias_padrao):
                with col1 if i % 2 == 0 else col2:
                    valor = st.number_input(
                        f"{categoria} (R$)",
                        min_value=0.0,
                        value=orcamento.get(categoria, 0.0),
                        step=100.0,
                        key=f"orcamento_{categoria}"
                    )
                    orcamento_novo[categoria] = valor
            
            submitted = st.form_submit_button("Salvar Orçamento")
            
            if submitted:
                salvar_orcamento(orcamento_novo)
                
                # Salvar no histórico
                if 'historico' not in historico:
                    historico['historico'] = []
                
                historico['historico'].append({
                    'data': datetime.now().isoformat(),
                    'orcamento': orcamento_novo.copy()
                })
                
                salvar_historico_orcamento(historico)
                st.success("Orçamento salvo com sucesso!")
                st.rerun()
    
    with tab3:
        st.subheader("Histórico de Orçamentos")
        
        if 'historico' in historico and historico['historico']:
            # Mostrar histórico
            for i, entrada in enumerate(reversed(historico['historico'][-10:])):  # Últimas 10 entradas
                with st.expander(f"Orçamento de {entrada['data'][:10]}"):
                    for categoria, valor in entrada['orcamento'].items():
                        if valor > 0:
                            st.write(f"**{categoria}:** R$ {valor:,.2f}")
        else:
            st.info("Nenhum histórico de orçamento encontrado.")
    
    with tab4:
        st.subheader("Recomendações Inteligentes")
        
        if not orcamento:
            st.warning("Configure um orçamento primeiro para receber recomendações.")
        else:
            # Calcular dados para recomendações
            gastos_reais = calcular_gastos_reais(df)
            progresso = calcular_progresso_orcamento(orcamento, gastos_reais)
            
            # Gerar recomendações
            recomendacoes = gerar_recomendacoes_ai(progresso, gastos_reais)
            
            for recomendacao in recomendacoes:
                st.write(recomendacao)
            
            # Análise adicional
            if progresso:
                st.subheader("Análise Detalhada")
                
                # Categorias que precisam de atenção
                categorias_atencao = [
                    cat for cat, data in progresso.items() 
                    if data['percentual'] > 90
                ]
                
                if categorias_atencao:
                    st.warning(f"**Categorias que precisam de atenção:** {', '.join(categorias_atencao)}")
                
                # Categorias bem controladas
                categorias_boas = [
                    cat for cat, data in progresso.items() 
                    if data['percentual'] <= 70 and data['gasto_atual'] > 0
                ]
                
                if categorias_boas:
                    st.success(f"**Categorias bem controladas:** {', '.join(categorias_boas)}")
