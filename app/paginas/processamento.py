# finbot_project/app/paginas/processamento.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from pathlib import Path

# --- CORREÇÃO INICIADA ---
# As importações foram separadas. Funções vêm do backend,
# e o objeto de configuração vem de config.py.
from backend import (
    data_processor, carregar_json,
    DataValidationResult, quality_monitor
)
from config import config
# --- CORREÇÃO FINALIZADA ---

def carregar_dados_processados():
    """Carrega dados já processados."""
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

def simular_processamento():
    """Simula o processamento de dados para mostrar estatísticas."""
    # Process all files and get validation results
    df, validation_results = data_processor.process_all_files()
    
    # Calculate processing statistics
    stats = {
        'total_files': len(validation_results),
        'total_rows': sum(v.processed_rows for v in validation_results),
        'invalid_rows': sum(v.invalid_rows for v in validation_results),
        'total_errors': sum(len(v.errors) for v in validation_results),
        'total_warnings': sum(len(v.warnings) for v in validation_results),
        'success_rate': 0,
        'categorization_quality': 0
    }
    
    if stats['total_rows'] > 0:
        stats['success_rate'] = ((stats['total_rows'] - stats['invalid_rows']) / stats['total_rows']) * 100
    
    # Calculate categorization quality
    if not df.empty and 'Confianca_Categoria' in df.columns:
        high_confidence = df[df['Confianca_Categoria'] >= 0.7].shape[0]
        total_categorized = df.shape[0]
        if total_categorized > 0:
            stats['categorization_quality'] = (high_confidence / total_categorized) * 100
    
    return df, validation_results, stats

def criar_grafico_validacao(validation_results):
    """Cria gráfico de resultados de validação."""
    if not validation_results:
        return go.Figure()
    
    # Prepare data for visualization
    data = []
    for i, result in enumerate(validation_results):
        data.append({
            'File': f"File {i+1}",
            'Valid Rows': result.processed_rows - result.invalid_rows,
            'Invalid Rows': result.invalid_rows,
            'Errors': len(result.errors),
            'Warnings': len(result.warnings)
        })
    
    df_viz = pd.DataFrame(data)
    
    fig = go.Figure()
    
    # Add bars for valid and invalid rows
    fig.add_trace(go.Bar(
        x=df_viz['File'],
        y=df_viz['Valid Rows'],
        name='Valid Rows',
        marker_color='green'
    ))
    
    fig.add_trace(go.Bar(
        x=df_viz['File'],
        y=df_viz['Invalid Rows'],
        name='Invalid Rows',
        marker_color='red'
    ))
    
    fig.update_layout(
        title="Data Validation Results by File",
        xaxis_title="File",
        yaxis_title="Number of Rows",
        barmode='stack',
        height=400
    )
    
    return fig

def criar_grafico_categorizacao(df):
    """Cria gráfico de qualidade da categorização."""
    if df.empty or 'Confianca_Categoria' not in df.columns:
        return go.Figure()
    
    # Create confidence distribution
    fig = px.histogram(
        df, 
        x='Confianca_Categoria',
        nbins=20,
        title="Categorization Confidence Distribution",
        labels={'Confianca_Categoria': 'Confidence Score', 'count': 'Number of Transactions'}
    )
    
    fig.update_layout(
        xaxis_title="Confidence Score",
        yaxis_title="Number of Transactions",
        height=400
    )
    
    # Add vertical lines for thresholds
    fig.add_vline(x=0.3, line_dash="dash", line_color="orange", annotation_text="Low Confidence")
    fig.add_vline(x=0.7, line_dash="dash", line_color="green", annotation_text="High Confidence")
    
    return fig

def criar_grafico_categorias(df):
    """Cria gráfico de distribuição de categorias."""
    if df.empty or 'Categoria' not in df.columns:
        return go.Figure()
    
    # Count categories
    category_counts = df['Categoria'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Transaction Distribution by Category"
    )
    
    fig.update_layout(height=400)
    
    return fig

def layout():
    """Renderiza a página de processamento de dados."""
    st.header("🔧 Processamento de Dados")
    st.info("Monitore a qualidade do processamento de dados e validação.")
    
    # Process data
    with st.spinner("Processando dados..."):
        df, validation_results, stats = simular_processamento()
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Arquivos Processados", stats['total_files'])
    
    with col2:
        st.metric("Linhas Processadas", f"{stats['total_rows']:,}")
    
    with col3:
        st.metric("Taxa de Sucesso", f"{stats['success_rate']:.1f}%")
    
    with col4:
        st.metric("Qualidade Categorização", f"{stats['categorization_quality']:.1f}%")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Validação", "🏷️ Categorização", "📈 Estatísticas", "🔍 Detalhes", "🎯 Qualidade"])
    
    with tab1:
        st.subheader("Resultados de Validação")
        
        if validation_results:
            # Validation summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Erros Encontrados", stats['total_errors'])
                st.metric("Avisos", stats['total_warnings'])
            
            with col2:
                st.metric("Linhas Inválidas", stats['invalid_rows'])
                st.metric("Linhas Válidas", stats['total_rows'] - stats['invalid_rows'])
            
            # Validation chart
            fig_validacao = criar_grafico_validacao(validation_results)
            st.plotly_chart(fig_validacao, use_container_width=True)
            
            # Detailed validation results
            st.subheader("Detalhes de Validação por Arquivo")
            
            for i, result in enumerate(validation_results):
                with st.expander(f"Arquivo {i+1} - {result.processed_rows} linhas"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Estatísticas:**")
                        st.write(f"- Linhas processadas: {result.processed_rows}")
                        st.write(f"- Linhas inválidas: {result.invalid_rows}")
                        if result.processed_rows > 0:
                            st.write(f"- Taxa de sucesso: {((result.processed_rows - result.invalid_rows) / result.processed_rows * 100):.1f}%")
                    
                    with col2:
                        st.write("**Status:**")
                        if result.is_valid:
                            st.success("✅ Válido")
                        else:
                            st.error("❌ Inválido")
                    
                    if result.errors:
                        st.error("**Erros:**")
                        for error in result.errors:
                            st.write(f"- {error}")
                    
                    if result.warnings:
                        st.warning("**Avisos:**")
                        for warning in result.warnings:
                            st.write(f"- {warning}")
        else:
            st.warning("Nenhum arquivo encontrado para processamento.")
    
    with tab2:
        st.subheader("Qualidade da Categorização")
        
        if not df.empty:
            # Categorization quality metrics
            col1, col2, col3 = st.columns(3)
            
            if 'Confianca_Categoria' in df.columns:
                high_conf = df[df['Confianca_Categoria'] >= 0.7].shape[0]
                medium_conf = df[(df['Confianca_Categoria'] >= 0.3) & (df['Confianca_Categoria'] < 0.7)].shape[0]
                low_conf = df[df['Confianca_Categoria'] < 0.3].shape[0]
                
                with col1:
                    st.metric("Alta Confiança (≥70%)", high_conf)
                
                with col2:
                    st.metric("Média Confiança (30-70%)", medium_conf)
                
                with col3:
                    st.metric("Baixa Confiança (<30%)", low_conf)
            
            # Categorization chart
            fig_cat = criar_grafico_categorizacao(df)
            st.plotly_chart(fig_cat, use_container_width=True)
            
            # Category distribution
            fig_categorias = criar_grafico_categorias(df)
            st.plotly_chart(fig_categorias, use_container_width=True)
            
            # Low confidence establishments
            if 'Confianca_Categoria' in df.columns:
                low_confidence = df[df['Confianca_Categoria'] < 0.3]
                if not low_confidence.empty:
                    st.subheader("Estabelecimentos com Baixa Confiança")
                    st.dataframe(
                        low_confidence[['Estabelecimento', 'Categoria', 'Confianca_Categoria']].head(10),
                        use_container_width=True
                    )
        else:
            st.warning("Nenhum dado processado encontrado.")
    
    with tab3:
        st.subheader("Estatísticas Gerais")
        
        if not df.empty:
            # Data quality metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Qualidade dos Dados:**")
                st.write(f"- Total de transações: {len(df):,}")
                st.write(f"- Período: {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
                st.write(f"- Categorias únicas: {df['Categoria'].nunique()}")
                st.write(f"- Estabelecimentos únicos: {df['Estabelecimento'].nunique()}")
            
            with col2:
                st.write("**Distribuição por Tipo:**")
                tipo_counts = df['Tipo'].value_counts()
                for tipo, count in tipo_counts.items():
                    st.write(f"- {tipo}: {count:,}")
            
            # Monthly transaction volume
            df['Mes'] = df['Data'].dt.to_period('M')
            monthly_volume = df.groupby('Mes').size().reset_index(name='Transacoes')
            monthly_volume['Mes'] = monthly_volume['Mes'].astype(str)
            
            fig_monthly = px.line(
                monthly_volume, 
                x='Mes', 
                y='Transacoes',
                title="Volume de Transações por Mês"
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Value distribution
            fig_values = px.histogram(
                df, 
                x='Valor',
                nbins=30,
                title="Distribuição de Valores",
                labels={'Valor': 'Valor (R$)', 'count': 'Número de Transações'}
            )
            st.plotly_chart(fig_values, use_container_width=True)
        else:
            st.warning("Nenhum dado processado encontrado.")
    
    with tab4:
        st.subheader("Detalhes do Processamento")
        
        # Processing configuration
        st.write("**Configuração do Processamento:**")
        st.write(f"- Diretório de crédito: {config.PASTA_CREDITO}")
        st.write(f"- Diretório de débito: {config.PASTA_DEBITO}")
        st.write(f"- Tamanho máximo de arquivo: {config.MAX_FILE_SIZE:,} bytes")
        st.write(f"- Cache habilitado: {config.CACHE_ENABLED}")
        
        # Recent processing logs
        st.write("**Logs de Processamento:**")
        st.info("Os logs detalhados estão disponíveis no console da aplicação.")
        
        # Data quality recommendations
        if validation_results:
            st.write("**Recomendações de Qualidade:**")
            
            total_errors = sum(len(v.errors) for v in validation_results)
            total_warnings = sum(len(v.warnings) for v in validation_results)
            
            if total_errors > 0:
                st.error(f"⚠️ {total_errors} erros encontrados. Revise os arquivos de entrada.")
            
            if total_warnings > 0:
                st.warning(f"⚠️ {total_warnings} avisos encontrados. Considere revisar os dados.")
            
            if stats['categorization_quality'] < 70:
                st.warning("⚠️ Qualidade de categorização baixa. Considere ajustar as regras.")
            
            if stats['success_rate'] < 90:
                st.warning("⚠️ Taxa de sucesso baixa. Verifique a qualidade dos dados de entrada.")
            
            if total_errors == 0 and total_warnings == 0 and stats['categorization_quality'] >= 70:
                st.success("✅ Qualidade de dados excelente!")
    
    with tab5:
        st.subheader("Monitoramento de Qualidade")
        
        # Analyze data quality
        quality_report = quality_monitor.analyze_data_quality(df, validation_results)
        
        # Overall quality score
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pontuação Geral", f"{quality_report['overall_score']:.1f}/100")
        
        with col2:
            if quality_report['overall_score'] >= 80:
                st.success("✅ Excelente")
            elif quality_report['overall_score'] >= 60:
                st.warning("⚠️ Boa")
            else:
                st.error("❌ Precisa Melhorar")
        
        with col3:
            st.metric("Alertas", len(quality_report['alerts']))
        
        # Quality alerts
        if quality_report['alerts']:
            st.subheader("Alertas de Qualidade")
            for alert in quality_report['alerts']:
                st.warning(alert)
        else:
            st.success("✅ Nenhum alerta de qualidade encontrado!")
        
        # Recommendations
        if quality_report['recommendations']:
            st.subheader("Recomendações")
            for recommendation in quality_report['recommendations']:
                st.info(recommendation)
        
        # Detailed metrics
        if 'metrics' in quality_report:
            st.subheader("Métricas Detalhadas")
            
            metrics = quality_report['metrics']
            
            # Missing data
            if 'missing_data' in metrics:
                st.write("**Dados Faltantes:**")
                for col, data in metrics['missing_data'].items():
                    if data['count'] > 0:
                        st.write(f"- {col}: {data['count']} ({data['rate']:.1f}%)")
            
            # Duplicates
            if 'duplicates' in metrics:
                st.write("**Duplicatas:**")
                st.write(f"- Total: {metrics['duplicates']['count']} ({metrics['duplicates']['rate']:.1f}%)")
            
            # Value range
            if 'value_range' in metrics:
                st.write("**Distribuição de Valores:**")
                st.write(f"- Mínimo: R$ {metrics['value_range']['min']:,.2f}")
                st.write(f"- Máximo: R$ {metrics['value_range']['max']:,.2f}")
                st.write(f"- Média: R$ {metrics['value_range']['mean']:,.2f}")
                st.write(f"- Mediana: R$ {metrics['value_range']['median']:,.2f}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reprocessar Dados"):
            st.rerun()
    
    with col2:
        if st.button("📊 Exportar Relatório"):
            st.info("Funcionalidade de exportação será implementada em breve.")
    
    with col3:
        if st.button("⚙️ Configurar Regras"):
            st.info("Configuração de regras será implementada em breve.")
