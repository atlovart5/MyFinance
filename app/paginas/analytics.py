# finbot_project/app/paginas/analytics.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
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

def carregar_dados_analytics():
    """Carrega dados para análise avançada."""
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
        st.error(f"Erro ao carregar dados para analytics: {e}")
        return pd.DataFrame()


def calcular_metricas_financeiras(df):
    """Calcula métricas financeiras avançadas."""
    if df.empty:
        return {}
    
    # Separar receitas e despesas
    receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
    despesas = abs(df[df['Tipo'] == 'Despesa']['Valor'].sum())
    
    # Métricas básicas
    saldo_total = receitas - despesas
    taxa_poupanca = (saldo_total / receitas * 100) if receitas > 0 else 0
    
    # Análise por categoria
    gastos_por_categoria = df[df['Tipo'] == 'Despesa'].groupby('Categoria')['Valor'].sum().abs()
    
    # Análise temporal
    df['Mes'] = df['Data'].dt.to_period('M')
    gastos_mensais = df[df['Tipo'] == 'Despesa'].groupby('Mes')['Valor'].sum().abs()
    
    # Tendências
    if len(gastos_mensais) > 1:
        tendencia = np.polyfit(range(len(gastos_mensais)), gastos_mensais.values, 1)[0]
        tendencia_texto = "Crescimento" if tendencia > 0 else "Redução" if tendencia < 0 else "Estável"
    else:
        tendencia_texto = "Insuficiente"
    
    # Anomalias (outliers)
    gastos_por_estabelecimento = df[df['Tipo'] == 'Despesa'].groupby('Estabelecimento')['Valor'].sum().abs()
    q1 = gastos_por_estabelecimento.quantile(0.25)
    q3 = gastos_por_estabelecimento.quantile(0.75)
    iqr = q3 - q1
    outliers = gastos_por_estabelecimento[(gastos_por_estabelecimento < (q1 - 1.5 * iqr)) | 
                                          (gastos_por_estabelecimento > (q3 + 1.5 * iqr))]
    
    return {
        'receitas_total': receitas,
        'despesas_total': despesas,
        'saldo_total': saldo_total,
        'taxa_poupanca': taxa_poupanca,
        'gastos_por_categoria': gastos_por_categoria,
        'gastos_mensais': gastos_mensais,
        'tendencia': tendencia_texto,
        'outliers': outliers,
        'total_transacoes': len(df),
        'periodo_analise': f"{df['Data'].min().strftime('%d/%m/%Y')} - {df['Data'].max().strftime('%d/%m/%Y')}"
    }

def criar_grafico_tendencia(gastos_mensais):
    """Cria gráfico de tendência de gastos."""
    if len(gastos_mensais) < 2:
        return go.Figure()
    
    fig = go.Figure()
    
    # Dados reais
    fig.add_trace(go.Scatter(
        x=gastos_mensais.index.astype(str),
        y=gastos_mensais.values,
        mode='lines+markers',
        name='Gastos Reais',
        line=dict(color='red', width=3)
    ))
    
    # Linha de tendência
    x_numeric = np.arange(len(gastos_mensais))
    z = np.polyfit(x_numeric, gastos_mensais.values, 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=gastos_mensais.index.astype(str),
        y=p(x_numeric),
        mode='lines',
        name='Tendência',
        line=dict(color='blue', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Tendência de Gastos Mensais",
        xaxis_title="Mês",
        yaxis_title="Gastos (R$)",
        height=400
    )
    
    return fig

def criar_grafico_categoria_tempo(df):
    """Cria gráfico de gastos por categoria ao longo do tempo."""
    if df.empty:
        return go.Figure()
    
    # Preparar dados
    df_temp = df[df['Tipo'] == 'Despesa'].copy()
    df_temp['Mes'] = df_temp['Data'].dt.to_period('M')
    
    gastos_categoria_tempo = df_temp.groupby(['Mes', 'Categoria'])['Valor'].sum().abs().reset_index()
    
    # Pivot para formato adequado ao gráfico
    pivot_data = gastos_categoria_tempo.pivot(index='Mes', columns='Categoria', values='Valor').fillna(0)
    
    fig = go.Figure()
    
    for categoria in pivot_data.columns:
        fig.add_trace(go.Scatter(
            x=pivot_data.index.astype(str),
            y=pivot_data[categoria],
            mode='lines+markers',
            name=categoria,
            stackgroup='one'
        ))
    
    fig.update_layout(
        title="Evolução dos Gastos por Categoria",
        xaxis_title="Mês",
        yaxis_title="Gastos (R$)",
        height=400
    )
    
    return fig

def gerar_insights_ai(metricas):
    """Gera insights baseados nas métricas calculadas."""
    insights = []
    
    # Análise de taxa de poupança
    if metricas['taxa_poupanca'] > 20:
        insights.append("🎉 Excelente! Sua taxa de poupança está acima de 20%. Continue assim!")
    elif metricas['taxa_poupanca'] > 10:
        insights.append("👍 Boa! Sua taxa de poupança está saudável. Considere aumentar para 20%.")
    elif metricas['taxa_poupanca'] > 0:
        insights.append("⚠️ Atenção! Sua taxa de poupança está baixa. Considere reduzir gastos.")
    else:
        insights.append("🚨 Crítico! Você está gastando mais do que ganha. Ação imediata necessária.")
    
    # Análise de tendência
    if metricas['tendencia'] == "Crescimento":
        insights.append("📈 Seus gastos estão aumentando. Revise suas categorias de maior crescimento.")
    elif metricas['tendencia'] == "Redução":
        insights.append("📉 Ótimo! Seus gastos estão diminuindo. Continue com essa disciplina!")
    
    # Análise de outliers
    if len(metricas['outliers']) > 0:
        insights.append(f"🔍 Encontramos {len(metricas['outliers'])} gastos anômalos. Revise-os!")
    
    # Análise de categorias
    if not metricas['gastos_por_categoria'].empty:
        maior_categoria = metricas['gastos_por_categoria'].idxmax()
        maior_valor = metricas['gastos_por_categoria'].max()
        percentual = (maior_valor / metricas['despesas_total']) * 100
        
        insights.append(f"💡 Sua maior categoria de gasto é '{maior_categoria}' ({percentual:.1f}% do total).")
    
    return insights

def layout():
    """Renderiza a página de analytics avançados."""
    st.header("📊 Analytics Avançados")
    st.info("Análise profunda dos seus dados financeiros com insights inteligentes.")
    
    # Carregar dados
    df = carregar_dados_analytics()
    
    if df.empty:
        st.warning("Nenhum dado encontrado. Processe os dados na página 'Processamento' primeiro.")
        return
    
    # Calcular métricas
    metricas = calcular_metricas_financeiras(df)
    
    # Tabs para diferentes análises
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "🎯 Insights", "📊 Gráficos", "🔍 Detalhes"])
    
    with tab1:
        st.subheader("Métricas Financeiras")
        
        # Cards de métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Receitas Totais",
                f"R$ {metricas['receitas_total']:,.2f}",
                help="Total de receitas no período"
            )
        
        with col2:
            st.metric(
                "Despesas Totais",
                f"R$ {metricas['despesas_total']:,.2f}",
                help="Total de despesas no período"
            )
        
        with col3:
            st.metric(
                "Saldo",
                f"R$ {metricas['saldo_total']:,.2f}",
                delta=f"{metricas['saldo_total']:,.2f}",
                delta_color="normal" if metricas['saldo_total'] >= 0 else "inverse"
            )
        
        with col4:
            st.metric(
                "Taxa de Poupança",
                f"{metricas['taxa_poupanca']:.1f}%",
                help="(Receitas - Despesas) / Receitas"
            )
        
        # Informações adicionais
        st.subheader("Informações do Período")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Período:** {metricas['periodo_analise']}")
        
        with col2:
            st.info(f"**Total de Transações:** {metricas['total_transacoes']}")
        
        with col3:
            st.info(f"**Tendência:** {metricas['tendencia']}")
    
    with tab2:
        st.subheader("Insights Inteligentes")
        
        # Gerar insights
        insights = gerar_insights_ai(metricas)
        
        for i, insight in enumerate(insights):
            st.write(f"{i+1}. {insight}")
        
        # Análise de categorias
        if not metricas['gastos_por_categoria'].empty:
            st.subheader("Top 5 Categorias de Gasto")
            
            top_categorias = metricas['gastos_por_categoria'].head(5)
            
            for categoria, valor in top_categorias.items():
                percentual = (valor / metricas['despesas_total']) * 100
                st.write(f"• **{categoria}:** R$ {valor:,.2f} ({percentual:.1f}%)")
    
    with tab3:
        st.subheader("Gráficos Avançados")
        
        # Gráfico de tendência
        if len(metricas['gastos_mensais']) > 1:
            fig_tendencia = criar_grafico_tendencia(metricas['gastos_mensais'])
            st.plotly_chart(fig_tendencia, use_container_width=True)
        
        # Gráfico de categoria ao longo do tempo
        fig_categoria_tempo = criar_grafico_categoria_tempo(df)
        st.plotly_chart(fig_categoria_tempo, use_container_width=True)
        
        # Gráfico de pizza das categorias
        if not metricas['gastos_por_categoria'].empty:
            fig_pizza = px.pie(
                values=metricas['gastos_por_categoria'].values,
                names=metricas['gastos_por_categoria'].index,
                title="Distribuição de Gastos por Categoria"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
    
    with tab4:
        st.subheader("Análise Detalhada")
        
        # Análise de outliers
        if len(metricas['outliers']) > 0:
            st.warning(f"**Gastos Anômalos Detectados ({len(metricas['outliers'])}):**")
            for estabelecimento, valor in metricas['outliers'].items():
                st.write(f"• **{estabelecimento}:** R$ {valor:,.2f}")
        
        # Análise temporal detalhada
        if len(metricas['gastos_mensais']) > 1:
            st.subheader("Análise Mensal")
            
            df_mensal = pd.DataFrame({
                'Mês': metricas['gastos_mensais'].index.astype(str),
                'Gastos': metricas['gastos_mensais'].values
            })
            
            # Calcular variação percentual
            df_mensal['Variação (%)'] = df_mensal['Gastos'].pct_change() * 100
            
            st.dataframe(df_mensal, use_container_width=True)
        
        # Estatísticas por pagador
        if 'Pagador' in df.columns:
            st.subheader("Análise por Pagador")
            
            gastos_por_pagador = df[df['Tipo'] == 'Despesa'].groupby('Pagador')['Valor'].sum().abs()
            
            if not gastos_por_pagador.empty:
                fig_pagador = px.bar(
                    x=gastos_por_pagador.index,
                    y=gastos_por_pagador.values,
                    title="Gastos por Pagador"
                )
                st.plotly_chart(fig_pagador, use_container_width=True)
