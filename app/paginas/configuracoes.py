# finbot_project/app/paginas/configuracoes.py

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

# Presumindo que 'backend' e 'componentes' estão no caminho certo
# Se 'app.py' está na raiz de 'app', os imports precisam ser ajustados
# dependendo de como você executa o Streamlit.
# Por enquanto, vamos manter como está.
from backend import config, carregar_json, salvar_json, salvar_configuracao_modelo, carregar_configuracao_modelo
from componentes.ui_components import (
    apply_custom_css, create_header, create_info_card, create_metric_card,
    create_interactive_button, create_progress_bar, create_status_indicator,
    create_loading_spinner, create_expandable_section
)

# File paths for settings
SETTINGS_FILE = config.PASTA_PROCESSADOS / "configuracoes.json"
CATEGORIAS_FILE = config.PASTA_PROCESSADOS / "categorias_customizadas.json"

def carregar_configuracoes():
    """Carrega configurações salvas."""
    return carregar_json(str(SETTINGS_FILE))

def salvar_configuracoes(configuracoes):
    """Salva configurações."""
    salvar_json(str(SETTINGS_FILE), configuracoes)

def carregar_categorias_customizadas():
    """Carrega categorias customizadas."""
    return carregar_json(str(CATEGORIAS_FILE))

def salvar_categorias_customizadas(categorias):
    """Salva categorias customizadas."""
    salvar_json(str(CATEGORIAS_FILE), categorias)

def verificar_sistema():
    """Verifica o status do sistema."""
    status = {
        'api_key': False,
        'data_files': False,
        'processed_data': False,
        'cache': False,
        'directories': False
    }
    
    # Verificar API key
    api_key = os.getenv('OPENAI_API_KEY')
    status['api_key'] = bool(api_key and api_key.startswith('sk-'))
    
    # Verificar arquivos de dados
    credit_files = list(config.PASTA_CREDITO.glob("*.csv"))
    debit_files = list(config.PASTA_DEBITO.glob("*.csv"))
    status['data_files'] = len(credit_files) > 0 or len(debit_files) > 0
    
    # Verificar dados processados
    status['processed_data'] = config.ARQUIVO_CONSOLIDADO.exists()
    
    # Verificar cache
    status['cache'] = config.PASTA_CACHE.exists()
    
    # Verificar diretórios
    status['directories'] = all([
        config.PASTA_CREDITO.exists(),
        config.PASTA_DEBITO.exists(),
        config.PASTA_PROCESSADOS.exists(),
        config.PASTA_RELATORIOS.exists()
    ])
    
    return status

def calcular_estatisticas_sistema():
    """Calcula estatísticas do sistema."""
    stats = {
        'total_files': 0,
        'total_size': 0,
        'last_processed': None,
        'cache_size': 0,
        'reports_generated': 0
    }
    
    # Contar arquivos de dados
    credit_files = list(config.PASTA_CREDITO.glob("*.csv"))
    debit_files = list(config.PASTA_DEBITO.glob("*.csv"))
    stats['total_files'] = len(credit_files) + len(debit_files)
    
    # Calcular tamanho total
    for file in credit_files + debit_files:
        stats['total_size'] += file.stat().st_size
    
    # Verificar último processamento
    if config.ARQUIVO_CONSOLIDADO.exists():
        stats['last_processed'] = datetime.fromtimestamp(
            config.ARQUIVO_CONSOLIDADO.stat().st_mtime
        )
    
    # Calcular tamanho do cache
    if config.PASTA_CACHE.exists():
        for file in config.PASTA_CACHE.rglob("*"):
            if file.is_file():
                stats['cache_size'] += file.stat().st_size
    
    # Contar relatórios gerados
    if config.PASTA_RELATORIOS.exists():
        stats['reports_generated'] = len(list(config.PASTA_RELATORIOS.glob("*.pdf")))
    
    return stats

def layout():
    """Renderiza a página de configurações."""
    # Aplicar CSS customizado
    apply_custom_css()
    
    # Criar header
    create_header("Configurações", "Gerencie as configurações do FinBot", "⚙️")
    
    # Verificar status do sistema
    status = verificar_sistema()
    stats = calcular_estatisticas_sistema()
    
    # Carregar configurações
    configuracoes = carregar_configuracoes()
    categorias_customizadas = carregar_categorias_customizadas()
    
    # Tabs para diferentes seções
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Status do Sistema", "⚙️ Configurações", "🏷️ Categorias", "📊 Estatísticas", "🛠️ Manutenção"
    ])
    
    with tab1:
        st.subheader("Status do Sistema")
        
        # Status indicators
        col1, col2 = st.columns(2)
        
        with col1:
            if status['api_key']:
                create_status_indicator("success", "API Key Configurada")
            else:
                create_status_indicator("error", "API Key Não Configurada")
            
            if status['data_files']:
                create_status_indicator("success", "Arquivos de Dados Encontrados")
            else:
                create_status_indicator("warning", "Nenhum Arquivo de Dados")
            
            if status['processed_data']:
                create_status_indicator("success", "Dados Processados")
            else:
                create_status_indicator("warning", "Dados Não Processados")
        
        with col2:
            if status['cache']:
                create_status_indicator("success", "Cache Ativo")
            else:
                create_status_indicator("info", "Cache Não Configurado")
            
            if status['directories']:
                create_status_indicator("success", "Diretórios OK")
            else:
                create_status_indicator("error", "Problema nos Diretórios")
        
        # Progresso geral do sistema
        total_checks = len(status)
        passed_checks = sum(status.values())
        progress_percentage = (passed_checks / total_checks) * 100
        
        st.subheader("Progresso de Configuração")
        create_progress_bar(
            "Configuração do Sistema",
            progress_percentage,
            100,
            "green" if progress_percentage >= 80 else "orange" if progress_percentage >= 60 else "red"
        )
        
        # Recomendações baseadas no status
        st.subheader("Recomendações")
        
        if not status['api_key']:
            create_info_card(
                "Configurar API Key",
                "Adicione sua chave da OpenAI no arquivo .env para usar o chatbot.",
                "warning"
            )
        
        if not status['data_files']:
            create_info_card(
                "Adicionar Dados",
                "Adicione arquivos CSV nas pastas data/raw/credito e data/raw/debito.",
                "warning"
            )
        
        if not status['processed_data'] and status['data_files']:
            create_info_card(
                "Processar Dados",
                "Execute o processamento de dados para gerar análises.",
                "info"
            )
    
    with tab2:
        st.subheader("Configurações Gerais")
        
        # Configurações de IA
        st.write("**Configurações de IA:**")
        
        # Carregar modelo atual
        modelo_atual = carregar_configuracao_modelo()
        
        # Se não há modelo configurado, usar GPT-4.1 Nano como padrão
        if not modelo_atual or modelo_atual not in config.AVAILABLE_MODELS:
            modelo_atual = "gpt-4.1-nano"
        
        # Informações sobre modelos disponíveis
        with st.expander("ℹ️ Informações sobre os Modelos"):
            st.markdown("""
            **Modelos Disponíveis:**
            
            🚀 **GPT-4.1 Nano** - Modelo mais rápido e econômico
            - Ideal para análises rápidas e respostas simples
            - Menor custo por token
            - Boa performance para tarefas básicas
            
            ⚡ **GPT-4o Mini** - Boa relação custo-benefício
            - Equilibrio entre velocidade e qualidade
            - Ideal para análises moderadamente complexas
            - Custo intermediário
            
            🧠 **GPT-4o** - Modelo mais avançado e preciso
            - Máxima precisão para análises complexas
            - Melhor compreensão de contexto
            - Maior custo por token
            
            💡 **GPT-3.5 Turbo** - Modelo estável e confiável
            - Performance consistente
            - Boa para tarefas gerais
            - Custo moderado
            """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            modelo_ia = st.selectbox(
                "Modelo de IA",
                config.AVAILABLE_MODELS,
                index=config.AVAILABLE_MODELS.index(modelo_atual) if modelo_atual in config.AVAILABLE_MODELS else 0,
                key="modelo_ia",
                help="Selecione o modelo OpenAI que será usado para análises e chatbot"
            )
            
            temperatura = st.slider(
                "Temperatura",
                min_value=0.0,
                max_value=2.0,
                value=config.OPENAI_TEMPERATURE,
                step=0.1,
                key="temperatura",
                help="Controla a criatividade das respostas (0 = mais determinístico, 2 = mais criativo)"
            )
        
        with col2:
            max_tokens = st.number_input(
                "Máximo de Tokens",
                min_value=100,
                max_value=4000,
                value=config.MAX_TOKENS,
                step=100,
                key="max_tokens",
                help="Número máximo de tokens por resposta"
            )
            
            allow_dangerous_code = st.checkbox(
                "Permitir Execução de Código (Chatbot)",
                value=config.ALLOW_DANGEROUS_CODE,
                key="allow_dangerous_code",
                help="Necessário para o funcionamento do chatbot"
            )
        
        # Configurações de processamento
        st.write("**Configurações de Processamento:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_file_size = st.number_input(
                "Tamanho Máximo de Arquivo (MB)",
                min_value=1,
                max_value=100,
                value=50,
                key="max_file_size"
            )
            
            validate_paths = st.checkbox(
                "Validar Caminhos de Arquivo",
                value=True,
                key="validate_paths"
            )
        
        with col2:
            log_level = st.selectbox(
                "Nível de Log",
                ["DEBUG", "INFO", "WARNING", "ERROR"],
                index=1,
                key="log_level"
            )
            
            rate_limit = st.number_input(
                "Limite de Taxa (chamadas/min)",
                min_value=1,
                max_value=100,
                value=10,
                key="rate_limit"
            )
        
        # Salvar configurações
        if st.button("💾 Salvar Configurações", key="salvar_config"):
            # Salvar configuração do modelo
            if salvar_configuracao_modelo(modelo_ia):
                st.success(f"✅ Modelo alterado para: {modelo_ia}")
            else:
                st.error("❌ Erro ao salvar configuração do modelo")
            
            # Atualizar outras configurações
            novas_configuracoes = {
                'ai_model': modelo_ia,
                'temperature': temperatura,
                'max_tokens': max_tokens,
                'allow_dangerous_code': allow_dangerous_code,
                'max_file_size': max_file_size * 1024 * 1024,  # Converter para bytes
                'validate_paths': validate_paths,
                'log_level': log_level,
                'rate_limit': rate_limit,
                'last_updated': datetime.now().isoformat()
            }
            
            salvar_configuracoes(novas_configuracoes)
            st.success("✅ Configurações salvas com sucesso!")
            
            # Mostrar informações sobre o modelo selecionado
            if modelo_ia == "gpt-4.1-nano":
                st.info("🚀 GPT-4.1 Nano selecionado - Modelo mais rápido e econômico!")
            elif modelo_ia == "gpt-4o":
                st.info("🧠 GPT-4o selecionado - Modelo mais avançado e preciso!")
            elif modelo_ia == "gpt-4o-mini":
                st.info("⚡ GPT-4o Mini selecionado - Boa relação custo-benefício!")
            elif modelo_ia == "gpt-3.5-turbo":
                st.info("💡 GPT-3.5 Turbo selecionado - Modelo estável e confiável!")
    
    with tab3:
        st.subheader("Gerenciamento de Categorias")
        
        # Categorias padrão
        categorias_padrao = [
            "Alimentação", "Transporte", "Saúde", "Educação", "Lazer", 
            "Moradia", "Assinatura", "Investimento", "Outros"
        ]
        
        st.write("**Categorias Padrão:**")
        for categoria in categorias_padrao:
            st.write(f"• {categoria}")
        
        # Adicionar nova categoria
        st.write("**Adicionar Nova Categoria:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nova_categoria = st.text_input("Nome da Categoria", key="nova_categoria")
        
        with col2:
            palavras_chave = st.text_input("Palavras-chave (separadas por vírgula)", key="palavras_chave")
        
        if st.button("➕ Adicionar Categoria", key="adicionar_categoria"):
            if nova_categoria and palavras_chave:
                if 'categorias' not in categorias_customizadas:
                    categorias_customizadas['categorias'] = {}
                
                categorias_customizadas['categorias'][nova_categoria] = {
                    'keywords': [kw.strip() for kw in palavras_chave.split(',')],
                    'created': datetime.now().isoformat()
                }
                
                salvar_categorias_customizadas(categorias_customizadas)
                st.success(f"Categoria '{nova_categoria}' adicionada com sucesso!")
        
        # Listar categorias customizadas
        if 'categorias' in categorias_customizadas and categorias_customizadas['categorias']:
            st.write("**Categorias Customizadas:**")
            
            for categoria, info in categorias_customizadas['categorias'].items():
                with st.expander(f"📁 {categoria}"):
                    st.write(f"**Palavras-chave:** {', '.join(info['keywords'])}")
                    st.write(f"**Criada em:** {info['created'][:10]}")
                    
                    if st.button(f"🗑️ Remover {categoria}", key=f"remover_{categoria}"):
                        del categorias_customizadas['categorias'][categoria]
                        salvar_categorias_customizadas(categorias_customizadas)
                        st.success(f"Categoria '{categoria}' removida!")
                        st.rerun()
    
    with tab4:
        st.subheader("Estatísticas do Sistema")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Arquivos de Dados",
                f"{stats['total_files']}",
                "arquivos encontrados"
            )
        
        with col2:
            create_metric_card(
                "Tamanho Total",
                f"{stats['total_size'] / (1024*1024):.1f} MB",
                "dados armazenados"
            )
        
        with col3:
            create_metric_card(
                "Relatórios",
                f"{stats['reports_generated']}",
                "relatórios gerados"
            )
        
        with col4:
            create_metric_card(
                "Cache",
                f"{stats['cache_size'] / (1024*1024):.1f} MB",
                "cache utilizado"
            )
        
        # Informações detalhadas
        st.subheader("Informações Detalhadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if stats['last_processed']:
                create_info_card(
                    "Último Processamento",
                    f"Data: {stats['last_processed'].strftime('%d/%m/%Y %H:%M')}",
                    "info"
                )
            else:
                create_info_card(
                    "Último Processamento",
                    "Nenhum processamento realizado",
                    "warning"
                )
        
        with col2:
            create_info_card(
                "Diretórios do Sistema",
                f"• Crédito: {len(list(config.PASTA_CREDITO.glob('*.csv')))} arquivos\n"
                f"• Débito: {len(list(config.PASTA_DEBITO.glob('*.csv')))} arquivos\n"
                f"• Processados: {len(list(config.PASTA_PROCESSADOS.glob('*')))} arquivos\n"
                f"• Relatórios: {len(list(config.PASTA_RELATORIOS.glob('*.pdf')))} arquivos",
                "info"
            )
    
    with tab5:
        st.subheader("Ferramentas de Manutenção")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Limpeza de Dados:**")
            
            if st.button("🧹 Limpar Cache", key="limpar_cache"):
                if config.PASTA_CACHE.exists():
                    for file in config.PASTA_CACHE.rglob("*"):
                        if file.is_file():
                            file.unlink()
                    st.success("Cache limpo com sucesso!")
                else:
                    st.info("Cache já está vazio.")
            
            if st.button("🗑️ Limpar Relatórios Antigos", key="limpar_relatorios"):
                if config.PASTA_RELATORIOS.exists():
                    for file in config.PASTA_RELATORIOS.glob("*.pdf"):
                        if (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days > 30:
                            file.unlink()
                    st.success("Relatórios antigos removidos!")
                else:
                    st.info("Nenhum relatório encontrado.")
        
        with col2:
            st.write("**Verificação de Integridade:**")
            
            if st.button("🔍 Verificar Arquivos", key="verificar_arquivos"):
                with st.spinner("Verificando arquivos..."):
                    # Verificar integridade dos arquivos
                    credit_files = list(config.PASTA_CREDITO.glob("*.csv"))
                    debit_files = list(config.PASTA_DEBITO.glob("*.csv"))
                    
                    total_files = len(credit_files) + len(debit_files)
                    valid_files = 0
                    
                    for file in credit_files + debit_files:
                        try:
                            pd.read_csv(file, sep=';', nrows=1)
                            valid_files += 1
                        except:
                            pass
                    
                    if valid_files == total_files:
                        st.success(f"✅ Todos os {total_files} arquivos são válidos!")
                    else:
                        st.warning(f"⚠️ {total_files - valid_files} arquivos com problemas encontrados.")
            
            if st.button("📊 Recalcular Estatísticas", key="recalcular_stats"):
                st.success("Estatísticas recalculadas!")
                st.rerun()
        
        # Backup e Restauração
        st.subheader("Backup e Restauração")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Criar Backup", key="criar_backup"):
                # Implementar backup
                st.info("Funcionalidade de backup será implementada em breve.")
        
        with col2:
            if st.button("📥 Restaurar Backup", key="restaurar_backup"):
                # Implementar restauração
                st.info("Funcionalidade de restauração será implementada em breve.")
        
        # Logs do sistema
        st.subheader("Logs do Sistema")
        
        create_expandable_section(
            "📋 Ver Logs Recentes",
            "Os logs detalhados estão disponíveis no console da aplicação.",
            expanded=False
        )