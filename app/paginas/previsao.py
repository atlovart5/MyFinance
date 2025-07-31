# finbot_project/app/paginas/previsao.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- CORREÇÃO INICIADA ---
# A importação foi dividida. A função vem do 'backend' e a
# configuração de arquivo vem do objeto 'config'.
from backend import prever_gastos, debug_dados_previsao
from config import config
# --- CORREÇÃO FINALIZADA ---

def layout():
    """
    Renderiza a página de previsão de gastos com três cenários.
    """
    st.header("🔮 Previsão de Gastos Futuros")
    st.info("Utilizamos Machine Learning avançado para analisar seu histórico e prever seus gastos em três cenários: Otimista, Normal e Pessimista.")

    try:
        # --- CORREÇÃO INICIADA ---
        # Acessando a variável através do objeto 'config'
        if not config.ARQUIVO_CONSOLIDADO.exists():
            st.error("Arquivo de dados consolidados não encontrado. Processe suas faturas primeiro na página 'Processamento'.")
            return
        df_historico = pd.read_csv(config.ARQUIVO_CONSOLIDADO, sep=';')
        # --- CORREÇÃO FINALIZADA ---
    except FileNotFoundError:
        st.error("Arquivo de dados consolidados não encontrado. Processe suas faturas primeiro.")
        return
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {e}")
        return
    
    meses_a_prever = st.slider(
        "Selecione quantos meses à frente você quer prever:",
        min_value=1,
        max_value=12,
        value=6,
        step=1
    )

    # Adicionar botão de debug
    if st.checkbox("Mostrar informações de debug"):
        debug_info = debug_dados_previsao(df_historico)
        st.subheader("🔍 Informações de Debug")
        st.json(debug_info)
    
    if st.button("Gerar Previsão Avançada", type="primary"):
        with st.spinner("Treinando modelos ensemble e gerando previsões em três cenários... Isso pode levar um momento."):
            resultado_previsao = prever_gastos(df_historico, meses_a_frente=meses_a_prever)
        
        if resultado_previsao is not None:
            df_previsao = resultado_previsao['previsoes']
            explicacoes = resultado_previsao['explicacoes']
            qualidade_dados = resultado_previsao['qualidade_dados']
            outliers_detectados = resultado_previsao['outliers_detectados']
            padroes_avancados = resultado_previsao.get('padroes_avancados', {})
            
            st.subheader("📊 Resultados da Previsão Avançada")
            
            # Criar gráfico com três cenários
            fig = go.Figure()
            
            # Adicionar linhas para cada cenário
            fig.add_trace(go.Scatter(
                x=df_previsao['Mes'],
                y=df_previsao['Cenario_Otimista'],
                mode='lines+markers',
                name='Cenário Otimista',
                line=dict(color='green', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_previsao['Mes'],
                y=df_previsao['Cenario_Normal'],
                mode='lines+markers',
                name='Cenário Normal',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_previsao['Mes'],
                y=df_previsao['Cenario_Pessimista'],
                mode='lines+markers',
                name='Cenário Pessimista',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=f'Previsão de Gastos para os Próximos {meses_a_prever} Meses',
                xaxis_title='Mês',
                yaxis_title='Gasto Previsto (R$)',
                hovermode='x unified',
                title_x=0.5
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Exibir métricas de qualidade dos dados
            st.subheader("📈 Qualidade dos Dados")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Meses", qualidade_dados['total_meses'])
            with col2:
                st.metric("Meses Limpos", qualidade_dados['meses_limpos'])
            with col3:
                st.metric("Outliers Detectados", outliers_detectados)
            with col4:
                tendencia_pct = qualidade_dados['tendencia_historica'] * 100
                st.metric("Tendência Histórica", f"{tendencia_pct:.1f}%")
            
            # Exibir explicações lógicas
            st.subheader("🧠 Análise Lógica dos Cenários")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🟢 Cenário Otimista")
                for explicacao in explicacoes['otimista']:
                    st.write(f"• {explicacao}")
            
            with col2:
                st.markdown("### 🔵 Cenário Normal")
                for explicacao in explicacoes['normal']:
                    st.write(f"• {explicacao}")
            
            with col3:
                st.markdown("### 🔴 Cenário Pessimista")
                for explicacao in explicacoes['pessimista']:
                    st.write(f"• {explicacao}")
            
            # Exibir dados tabulares
            st.subheader("📋 Dados Detalhados da Previsão")
            
            df_display = df_previsao.copy()
            df_display['Cenario_Otimista'] = df_display['Cenario_Otimista'].apply(lambda x: f'R$ {x:,.2f}')
            df_display['Cenario_Normal'] = df_display['Cenario_Normal'].apply(lambda x: f'R$ {x:,.2f}')
            df_display['Cenario_Pessimista'] = df_display['Cenario_Pessimista'].apply(lambda x: f'R$ {x:,.2f}')
            
            st.dataframe(df_display, use_container_width=True)
            
            # Análise de diferenças entre cenários
            st.subheader("📊 Análise Comparativa")
            
            df_analise = df_previsao.copy()
            df_analise['Diferenca_Ot_Norm'] = df_analise['Cenario_Normal'] - df_analise['Cenario_Otimista']
            df_analise['Diferenca_Pess_Norm'] = df_analise['Cenario_Pessimista'] - df_analise['Cenario_Normal']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Diferença entre Cenário Normal e Otimista:**")
                for idx, row in df_analise.iterrows():
                    diff = row['Diferenca_Ot_Norm']
                    st.write(f"{row['Mes']}: R$ {diff:,.2f}")
            
            with col2:
                st.markdown("**Diferença entre Cenário Pessimista e Normal:**")
                for idx, row in df_analise.iterrows():
                    diff = row['Diferenca_Pess_Norm']
                    st.write(f"{row['Mes']}: R$ {diff:,.2f}")
            
            # Análise de padrões avançados
            if padroes_avancados:
                st.subheader("🔍 Padrões Detectados")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📈 Sazonalidade")
                    if padroes_avancados.get('sazonalidade'):
                        saz = padroes_avancados['sazonalidade']
                        if saz.get('meses_altos'):
                            st.write(f"**Meses com gastos altos:** {saz['meses_altos']}")
                        if saz.get('meses_baixos'):
                            st.write(f"**Meses com gastos baixos:** {saz['meses_baixos']}")
                        st.write(f"**Intensidade sazonal:** {saz.get('intensidade_sazonal', 0):.2f}")
                    
                    st.markdown("### 📊 Tendência")
                    if padroes_avancados.get('tendencia'):
                        tend = padroes_avancados['tendencia']
                        st.write(f"**Direção:** {tend.get('direcao', 'N/A')}")
                        st.write(f"**Crescimento médio:** {tend.get('crescimento_medio', 0):.2%}")
                        st.write(f"**Intensidade:** {tend.get('intensidade', 0):.2f}")
                
                with col2:
                    st.markdown("### 📉 Volatilidade")
                    if padroes_avancados.get('volatilidade'):
                        vol = padroes_avancados['volatilidade']
                        st.write(f"**Nível:** {vol.get('nivel', 'N/A')}")
                        st.write(f"**Valor relativo:** {vol.get('valor_relativo', 0):.2f}")
                    
                    st.markdown("### 🔄 Ciclos")
                    if padroes_avancados.get('ciclos'):
                        cic = padroes_avancados['ciclos']
                        st.write(f"**Autocorrelação:** {cic.get('autocorrelacao', 0):.2f}")
                        st.write(f"**Padrão cíclico:** {'Sim' if cic.get('padrao_ciclico') else 'Não'}")
                
                # Análise de categorias
                if padroes_avancados.get('categorias'):
                    st.markdown("### 🏷️ Principais Categorias")
                    cat = padroes_avancados['categorias']
                    if cat.get('principais'):
                        for categoria, valor in cat['principais'].items():
                            percentual = cat['distribuicao'].get(categoria, 0) * 100
                            st.write(f"**{categoria}:** R$ {valor:,.2f} ({percentual:.1f}%)")
            
        else:
            st.error("❌ Erro na geração da previsão")
            st.warning("Possíveis causas:")
            st.write("• Dados insuficientes (mínimo 4 meses)")
            st.write("• Problemas na qualidade dos dados")
            st.write("• Valores ausentes ou inconsistentes")
            st.write("")
            st.info("💡 Dica: Ative o debug acima para verificar a qualidade dos seus dados.")

