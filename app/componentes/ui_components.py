# finbot_project/app/componentes/ui_components.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

# Custom CSS for enhanced styling
CUSTOM_CSS = """
<style>
/* Main container styling */
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}

/* Card styling */
.custom-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
}

/* Success/Error/Warning cards */
.success-card {
    background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
    color: white;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}

.warning-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}

.error-card {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}

/* Progress bars */
.custom-progress {
    background: #f0f2f6;
    border-radius: 10px;
    height: 20px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}

/* Interactive buttons */
.interactive-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 0.75rem 1.5rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.interactive-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

/* Responsive design */
@media (max-width: 768px) {
    .metric-card {
        margin-bottom: 1rem;
    }
    
    .custom-card {
        padding: 1rem;
    }
}

/* Animation classes */
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Chart containers */
.chart-container {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
}

/* Data table styling */
.data-table {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Loading spinner */
.loading-spinner {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

/* Tooltip styling */
.tooltip {
    position: relative;
    display: inline-block;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 200px;
    background-color: #555;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}
</style>
"""

def apply_custom_css():
    """Apply custom CSS to the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def create_header(title: str, subtitle: str = "", icon: str = "🤖"):
    """Create a beautiful header with gradient background."""
    st.markdown(f"""
    <div class="main-header fade-in">
        <h1>{icon} {title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title: str, value: str, change: str = "", change_type: str = "neutral"):
    """Create a beautiful metric card with hover effects."""
    change_color = {
        "positive": "#56ab2f",
        "negative": "#ff6b6b", 
        "neutral": "#667eea"
    }.get(change_type, "#667eea")
    
    st.markdown(f"""
    <div class="metric-card fade-in">
        <h3>{title}</h3>
        <h2>{value}</h2>
        {f'<p style="color: {change_color};">{change}</p>' if change else ''}
    </div>
    """, unsafe_allow_html=True)

def create_info_card(title: str, content: str, card_type: str = "info"):
    """Create an info card with different styles."""
    card_class = {
        "success": "success-card",
        "warning": "warning-card", 
        "error": "error-card",
        "info": "custom-card"
    }.get(card_type, "custom-card")
    
    st.markdown(f"""
    <div class="{card_class} fade-in">
        <h4>{title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_progress_bar(label: str, value: float, max_value: float = 100, color: str = "#667eea"):
    """Create a custom progress bar."""
    percentage = (value / max_value) * 100
    
    st.markdown(f"""
    <div class="custom-progress">
        <div class="progress-fill" style="width: {percentage}%; background: {color};"></div>
    </div>
    <p style="text-align: center; margin-top: 0.5rem; font-weight: bold;">
        {label}: {value:.1f}/{max_value:.1f} ({percentage:.1f}%)
    </p>
    """, unsafe_allow_html=True)

def create_interactive_button(text: str, key: str = None):
    """Create an interactive button with hover effects."""
    if st.button(text, key=key):
        return True
    return False

def create_animated_chart(fig, title: str = ""):
    """Create an animated chart container."""
    st.markdown(f"""
    <div class="chart-container fade-in">
        <h4 style="text-align: center; margin-bottom: 1rem;">{title}</h4>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

def create_gauge_chart(value: float, max_value: float, title: str, color: str = "blue"):
    """Create a beautiful gauge chart."""
    percentage = (value / max_value) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': max_value * 0.8},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, max_value * 0.5], 'color': "lightgray"},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_waterfall_chart(data: Dict[str, float], title: str = "Waterfall Chart"):
    """Create a waterfall chart for financial analysis."""
    categories = list(data.keys())
    values = list(data.values())
    
    # Calculate cumulative values for waterfall
    cumulative = np.cumsum([0] + values[:-1])
    
    fig = go.Figure(go.Waterfall(
        name="20 20",
        orientation="h",
        measure=["relative"] * len(values),
        x=values,
        textposition="outside",
        text=values,
        y=categories,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title=title,
        showlegend=True,
        height=400,
        waterfallgap=0.2,
    )
    
    return fig

def create_sunburst_chart(data: pd.DataFrame, path_cols: List[str], value_col: str, title: str = "Sunburst Chart"):
    """Create a sunburst chart for hierarchical data."""
    fig = px.sunburst(
        data,
        path=path_cols,
        values=value_col,
        title=title
    )
    
    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_timeline_chart(data: pd.DataFrame, date_col: str, value_col: str, category_col: str = None, title: str = "Timeline"):
    """Create an interactive timeline chart."""
    if category_col:
        fig = px.line(
            data,
            x=date_col,
            y=value_col,
            color=category_col,
            title=title,
            markers=True
        )
    else:
        fig = px.line(
            data,
            x=date_col,
            y=value_col,
            title=title,
            markers=True
        )
    
    fig.update_layout(
        height=400,
        xaxis_title="Data",
        yaxis_title="Valor",
        hovermode='x unified'
    )
    
    return fig

def create_heatmap_chart(data: pd.DataFrame, x_col: str, y_col: str, value_col: str, title: str = "Heatmap"):
    """Create a heatmap chart."""
    pivot_data = data.pivot_table(values=value_col, index=y_col, columns=x_col, aggfunc='sum')
    
    fig = px.imshow(
        pivot_data,
        title=title,
        aspect="auto",
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        height=400,
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig

def create_donut_chart(data: pd.DataFrame, category_col: str, value_col: str, title: str = "Donut Chart"):
    """Create a beautiful donut chart."""
    fig = px.pie(
        data,
        values=value_col,
        names=category_col,
        title=title,
        hole=0.4
    )
    
    fig.update_layout(
        height=400,
        showlegend=True
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_3d_scatter(data: pd.DataFrame, x_col: str, y_col: str, z_col: str, color_col: str = None, title: str = "3D Scatter"):
    """Create a 3D scatter plot."""
    if color_col:
        fig = px.scatter_3d(
            data,
            x=x_col,
            y=y_col,
            z=z_col,
            color=color_col,
            title=title
        )
    else:
        fig = px.scatter_3d(
            data,
            x=x_col,
            y=y_col,
            z=z_col,
            title=title
        )
    
    fig.update_layout(
        height=500,
        scene=dict(
            xaxis_title=x_col,
            yaxis_title=y_col,
            zaxis_title=z_col
        )
    )
    
    return fig

def create_interactive_table(df: pd.DataFrame, title: str = "Interactive Table"):
    """Create an interactive table with sorting and filtering."""
    st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
    
    # Add search functionality
    search_term = st.text_input("🔍 Buscar na tabela:", key=f"search_{title}")
    
    if search_term:
        # Filter dataframe based on search term
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        df_filtered = df[mask]
    else:
        df_filtered = df
    
    # Display with pagination
    page_size = st.selectbox("Linhas por página:", [10, 25, 50, 100], key=f"page_size_{title}")
    
    total_pages = len(df_filtered) // page_size + (1 if len(df_filtered) % page_size > 0 else 0)
    
    if total_pages > 1:
        page = st.selectbox("Página:", range(1, total_pages + 1), key=f"page_{title}")
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_display = df_filtered.iloc[start_idx:end_idx]
    else:
        df_display = df_filtered
    
    st.dataframe(df_display, use_container_width=True)
    
    # Show summary
    st.info(f"Mostrando {len(df_display)} de {len(df_filtered)} registros")

def create_loading_spinner(text: str = "Carregando..."):
    """Create a custom loading spinner."""
    st.markdown(f"""
    <div class="loading-spinner">
        <div style="text-align: center;">
            <div style="border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
            <p style="margin-top: 1rem; color: #667eea; font-weight: bold;">{text}</p>
        </div>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def create_tooltip(text: str, tooltip_text: str):
    """Create a tooltip component."""
    st.markdown(f"""
    <div class="tooltip">
        {text}
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    """, unsafe_allow_html=True)

def create_expandable_section(title: str, content: str, expanded: bool = False):
    """Create an expandable section."""
    with st.expander(title, expanded=expanded):
        st.markdown(content)

def create_metric_row(metrics: List[Tuple[str, str, str, str]]):
    """Create a row of metric cards."""
    cols = st.columns(len(metrics))
    
    for i, (title, value, change, change_type) in enumerate(metrics):
        with cols[i]:
            create_metric_card(title, value, change, change_type)

def create_status_indicator(status: str, text: str):
    """Create a status indicator."""
    status_colors = {
        "success": "🟢",
        "warning": "🟡", 
        "error": "🔴",
        "info": "🔵"
    }
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin: 0.5rem 0;">
        <span style="font-size: 1.5rem; margin-right: 0.5rem;">{status_colors.get(status, '⚪')}</span>
        <span>{text}</span>
    </div>
    """, unsafe_allow_html=True)

def create_animated_counter(target_value: float, duration: int = 2000):
    """Create an animated counter component."""
    st.markdown(f"""
    <div id="counter" style="font-size: 2rem; font-weight: bold; color: #667eea; text-align: center;">
        0
    </div>
    <script>
        function animateCounter(target, duration) {{
            let start = 0;
            const increment = target / (duration / 16);
            
            function updateCounter() {{
                start += increment;
                if (start < target) {{
                    document.getElementById('counter').textContent = Math.floor(start);
                    requestAnimationFrame(updateCounter);
                }} else {{
                    document.getElementById('counter').textContent = target;
                }}
            }}
            updateCounter();
        }}
        
        animateCounter({target_value}, {duration});
    </script>
    """, unsafe_allow_html=True)