# finbot_project/app/paginas/dashboard_enhanced.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple

# --- CORREÇÃO INICIADA ---
# As importações foram separadas. Funções vêm do backend,
# e o objeto de configuração vem de config.py.
from backend import processar_faturas
from config import config
from componentes.ui_components import (
    apply_custom_css, create_header, create_metric_card, create_info_card,
    create_progress_bar, create_gauge_chart, create_waterfall_chart,
    create_sunburst_chart, create_timeline_chart, create_donut_chart,
    create_interactive_table, create_loading_spinner, create_metric_row,
    create_status_indicator, create_animated_chart
)
# --- CORREÇÃO FINALIZADA ---

@st.cache_data
def carregar_dados():
    """Carrega dados financeiros."""
    try:
        # --- CORREÇÃO INICIADA ---
        # Acessando a variável através do objeto 'config'
        if not config.ARQUIVO_CONSOLIDADO.exists():
            return pd.DataFrame()
        df = pd.read_csv(str(config.ARQUIVO_CONSOLIDADO), sep=';')
        # --- CORREÇÃO FINALIZADA ---
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def calcular_metricas_principais(df: pd.DataFrame) -> Dict:
    """Calcula métricas principais para o dashboard."""
    if df.empty:
        return {}
    
    # Separar receitas e despesas
    receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
    despesas = abs(df[df['Tipo'] == 'Despesa']['Valor'].sum())
    
    # Calcular saldo
    saldo = receitas - despesas
    
    # Calcular taxa de poupança
    taxa_poupanca = (saldo / receitas * 100) if receitas > 0 else 0
    
    # Calcular métricas por período
    df['Mes'] = df['Data'].dt.to_period('M')
    
    # Garantir que há pelo menos um mês
    if df['Mes'].nunique() == 0:
        return {
            'receitas': receitas, 'despesas': despesas, 'saldo': saldo,
            'taxa_poupanca': taxa_poupanca, 'receitas_ultimo': 0, 'despesas_ultimo': 0,
            'var_receitas': 0, 'var_despesas': 0, 'total_transacoes': len(df),
            'periodo_dias': 0
        }

    ultimo_mes = df['Mes'].max()
    penultimo_mes = df['Mes'].unique()[-2] if len(df['Mes'].unique()) > 1 else ultimo_mes
    
    # Dados do último mês
    df_ultimo_mes = df[df['Mes'] == ultimo_mes]
    receitas_ultimo = df_ultimo_mes[df_ultimo_mes['Tipo'] == 'Receita']['Valor'].sum()
    despesas_ultimo = abs(df_ultimo_mes[df_ultimo_mes['Tipo'] == 'Despesa']['Valor'].sum())
    
    # Dados do penúltimo mês
    df_penultimo_mes = df[df['Mes'] == penultimo_mes]
    receitas_penultimo = df_penultimo_mes[df_penultimo_mes['Tipo'] == 'Receita']['Valor'].sum()
    despesas_penultimo = abs(df_penultimo_mes[df_penultimo_mes['Tipo'] == 'Despesa']['Valor'].sum())
    
    # Calcular variações
    var_receitas = ((receitas_ultimo - receitas_penultimo) / receitas_penultimo * 100) if receitas_penultimo > 0 else 0
    var_despesas = ((despesas_ultimo - despesas_penultimo) / despesas_penultimo * 100) if despesas_penultimo > 0 else 0
    
    return {
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
        'taxa_poupanca': taxa_poupanca,
        'receitas_ultimo': receitas_ultimo,
        'despesas_ultimo': despesas_ultimo,
        'var_receitas': var_receitas,
        'var_despesas': var_despesas,
        'total_transacoes': len(df),
        'periodo_dias': (df['Data'].max() - df['Data'].min()).days
    }

def criar_grafico_evolucao_mensal(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de evolução mensal."""
    if df.empty:
        return go.Figure()
    
    df['Mes'] = df['Data'].dt.to_period('M').astype(str)
    df_mensal = df.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()
    
    # Separar receitas e despesas
    receitas = df_mensal[df_mensal['Tipo'] == 'Receita']
    despesas = df_mensal[df_mensal['Tipo'] == 'Despesa']
    
    fig = go.Figure()
    
    # Adicionar linha de receitas
    fig.add_trace(go.Scatter(
        x=receitas['Mes'],
        y=receitas['Valor'],
        mode='lines+markers',
        name='Receitas',
        line=dict(color='#56ab2f', width=3),
        marker=dict(size=8)
    ))
    
    # Adicionar linha de despesas
    fig.add_trace(go.Scatter(
        x=despesas['Mes'],
        y=abs(despesas['Valor']),
        mode='lines+markers',
        name='Despesas',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Evolução Mensal de Receitas e Despesas",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def criar_grafico_categorias_donut(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de pizza das categorias."""
    if df.empty or 'Categoria' not in df.columns:
        return go.Figure()
    
    # Filtrar apenas despesas
    df_despesas = df[df['Tipo'] == 'Despesa']
    
    if df_despesas.empty:
        return go.Figure()
    
    # Agrupar por categoria
    categorias = df_despesas.groupby('Categoria')['Valor'].sum().abs()
    
    # Criar donut chart
    fig = create_donut_chart(
        data=pd.DataFrame({
            'Categoria': categorias.index,
            'Valor': categorias.values
        }),
        category_col='Categoria',
        value_col='Valor',
        title="Distribuição de Gastos por Categoria"
    )
    
    return fig

def criar_grafico_top_estabelecimentos(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico dos top estabelecimentos."""
    if df.empty:
        return go.Figure()
    
    # Filtrar apenas despesas
    df_despesas = df[df['Tipo'] == 'Despesa']
    
    if df_despesas.empty:
        return go.Figure()
    
    # Top 10 estabelecimentos
    top_estabelecimentos = df_despesas.groupby('Estabelecimento')['Valor'].sum().abs().nlargest(10)
    
    fig = px.bar(
        x=top_estabelecimentos.values,
        y=top_estabelecimentos.index,
        orientation='h',
        title="Top 10 Estabelecimentos por Valor Gasto",
        labels={'x': 'Valor (R$)', 'y': 'Estabelecimento'}
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Valor (R$)",
        yaxis_title="Estabelecimento"
    )
    
    return fig

def criar_heatmap_diario(df: pd.DataFrame) -> go.Figure:
    """Cria heatmap de gastos por dia da semana."""
    if df.empty:
        return go.Figure()
    
    # Filtrar apenas despesas
    df_despesas = df[df['Tipo'] == 'Despesa'].copy()
    
    if df_despesas.empty:
        return go.Figure()
    
    # Adicionar colunas de dia da semana e mês
    df_despesas['DiaSemana'] = df_despesas['Data'].dt.day_name()
    df_despesas['Mes'] = df_despesas['Data'].dt.month_name()
    
    # Agrupar por dia da semana e mês
    heatmap_data = df_despesas.groupby(['DiaSemana', 'Mes'])['Valor'].sum().abs().reset_index()
    
    # Pivotar para formato de heatmap
    heatmap_pivot = heatmap_data.pivot(index='DiaSemana', columns='Mes', values='Valor')
    
    fig = px.imshow(
        heatmap_pivot,
        title="Heatmap de Gastos por Dia da Semana e Mês",
        color_continuous_scale="Reds",
        aspect="auto"
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Mês",
        yaxis_title="Dia da Semana"
    )
    
    return fig

def layout():
    """Renderiza o dashboard enhanced."""
    # Aplicar CSS customizado
    apply_custom_css()
    
    # Criar header
    create_header("Dashboard Financeiro", "Visão geral dos seus dados financeiros", "💰")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        df = carregar_dados()
    
    if df.empty:
        create_info_card(
            "Nenhum dado encontrado",
            "Adicione arquivos CSV nas pastas de dados para visualizar o dashboard.",
            "warning"
        )
        return
    
    # Calcular métricas
    metricas = calcular_metricas_principais(df)
    
    # Métricas principais
    st.subheader("📊 Métricas Principais")
    
    # Criar linha de métricas
    create_metric_row([
        ("Receitas Totais", f"R$ {metricas.get('receitas', 0):,.2f}", 
         f"{metricas.get('var_receitas', 0):+.1f}%", "positive" if metricas.get('var_receitas', 0) > 0 else "negative"),
        ("Despesas Totais", f"R$ {metricas.get('despesas', 0):,.2f}", 
         f"{metricas.get('var_despesas', 0):+.1f}%", "negative" if metricas.get('var_despesas', 0) > 0 else "positive"),
        ("Saldo", f"R$ {metricas.get('saldo', 0):,.2f}", "", "positive" if metricas.get('saldo', 0) > 0 else "negative"),
        ("Taxa de Poupança", f"{metricas.get('taxa_poupanca', 0):.1f}%", "", "positive" if metricas.get('taxa_poupanca', 0) > 0 else "negative")
    ])
    
    # Status indicators
    st.subheader("🎯 Status Financeiro")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if metricas.get('saldo', 0) > 0:
            create_status_indicator("success", "Saldo Positivo")
        else:
            create_status_indicator("error", "Saldo Negativo")
    
    with col2:
        if metricas.get('taxa_poupanca', 0) > 20:
            create_status_indicator("success", "Boa Poupança")
        elif metricas.get('taxa_poupanca', 0) > 10:
            create_status_indicator("warning", "Poupança Regular")
        else:
            create_status_indicator("error", "Poupança Baixa")
    
    with col3:
        if metricas.get('var_despesas', 0) < 0:
            create_status_indicator("success", "Despesas Reduzindo")
        else:
            create_status_indicator("warning", "Despesas Aumentando")
    
    # Gráficos principais
    st.subheader("📈 Análise Visual")
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Evolução Mensal", "🍩 Categorias", "🏪 Top Estabelecimentos", "🔥 Heatmap"])
    
    with tab1:
        fig_evolucao = criar_grafico_evolucao_mensal(df)
        create_animated_chart(fig_evolucao, "Evolução Mensal")
    
    with tab2:
        fig_categorias = criar_grafico_categorias_donut(df)
        create_animated_chart(fig_categorias, "Distribuição por Categoria")
    
    with tab3:
        fig_estabelecimentos = criar_grafico_top_estabelecimentos(df)
        create_animated_chart(fig_estabelecimentos, "Top Estabelecimentos")
    
    with tab4:
        fig_heatmap = criar_heatmap_diario(df)
        create_animated_chart(fig_heatmap, "Heatmap de Gastos")
    
    # Análise detalhada
    st.subheader("🔍 Análise Detalhada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge chart para taxa de poupança
        fig_gauge = create_gauge_chart(
            value=metricas.get('taxa_poupanca', 0),
            max_value=100,
            title="Taxa de Poupança (%)",
            color="green" if metricas.get('taxa_poupanca', 0) > 20 else "orange" if metricas.get('taxa_poupanca', 0) > 10 else "red"
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Waterfall chart para análise de fluxo
        waterfall_data = {
            'Receitas': metricas.get('receitas', 0),
            'Despesas': -metricas.get('despesas', 0),
            'Saldo': metricas.get('saldo', 0)
        }
        
        fig_waterfall = create_waterfall_chart(
            data=waterfall_data,
            title="Fluxo Financeiro"
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Tabela interativa
    st.subheader("📋 Dados Detalhados")
    
    # Preparar dados para tabela
    df_display = df.copy()
    df_display['Data'] = df_display['Data'].dt.strftime('%d/%m/%Y')
    df_display['Valor'] = df_display['Valor'].apply(lambda x: f"R$ {x:,.2f}")
    
    # Selecionar colunas para exibição
    colunas_exibicao = ['Data', 'Estabelecimento', 'Valor', 'Tipo']
    if 'Categoria' in df_display.columns:
        colunas_exibicao.append('Categoria')
    if 'Pagador' in df_display.columns:
        colunas_exibicao.append('Pagador')
    
    df_display = df_display[colunas_exibicao]
    
    create_interactive_table(df_display, "Transações Financeiras")
    
    # Informações adicionais
    st.subheader("ℹ️ Informações do Período")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_info_card(
            "Período Analisado",
            f"De {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')} ({metricas.get('periodo_dias', 0)} dias)",
            "info"
        )
    
    with col2:
        create_info_card(
            "Total de Transações",
            f"{metricas.get('total_transacoes', 0):,} transações processadas",
            "info"
        )
    
    with col3:
        if metricas.get('saldo', 0) > 0:
            create_info_card(
                "Situação Financeira",
                "✅ Sua situação financeira está positiva!",
                "success"
            )
        else:
            create_info_card(
                "Situação Financeira",
                "⚠️ Atenção: Saldo negativo detectado",
                "warning"
            )
