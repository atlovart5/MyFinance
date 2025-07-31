# finbot_project/app/componentes/responsive_layout.py

import streamlit as st
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px

# Mobile-friendly CSS
MOBILE_CSS = """
<style>
/* Mobile-first responsive design */
@media (max-width: 768px) {
    /* Adjust container padding */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Make columns stack on mobile */
    .row-widget.stHorizontal {
        flex-direction: column !important;
    }
    
    /* Adjust metric cards for mobile */
    .metric-card {
        margin-bottom: 1rem !important;
        padding: 1rem !important;
    }
    
    /* Make charts responsive */
    .js-plotly-plot {
        width: 100% !important;
        height: auto !important;
    }
    
    /* Adjust sidebar for mobile */
    .css-1d391kg {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Make tables scrollable on mobile */
    .dataframe {
        font-size: 0.8rem !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }
    
    /* Adjust buttons for mobile */
    .stButton > button {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Make text more readable on mobile */
    h1, h2, h3, h4, h5, h6 {
        font-size: 1.2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Adjust spacing for mobile */
    .element-container {
        margin-bottom: 1rem !important;
    }
    
    /* Make tabs more touch-friendly */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
    }
    
    /* Adjust form elements for mobile */
    .stSelectbox, .stTextInput, .stNumberInput {
        width: 100% !important;
    }
    
    /* Make progress bars more visible on mobile */
    .stProgress > div > div > div {
        height: 1rem !important;
    }
}

/* Tablet adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
    .main .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    .metric-card {
        padding: 1.25rem !important;
    }
}

/* Desktop optimizations */
@media (min-width: 1025px) {
    .main .block-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .metric-card {
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
    }
    
    .custom-card {
        background: #2c3e50 !important;
        color: white !important;
    }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
    .metric-card {
        transition: none !important;
    }
    
    .fade-in {
        animation: none !important;
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .metric-card {
        border: 2px solid #000 !important;
    }
    
    .custom-card {
        border: 2px solid #000 !important;
    }
}
</style>
"""

def apply_mobile_css():
    """Apply mobile-friendly CSS."""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

def create_mobile_friendly_metrics(metrics: List[Dict[str, Any]]):
    """Create mobile-friendly metric cards."""
    # Determine number of columns based on screen size
    if len(metrics) <= 2:
        cols = st.columns(len(metrics))
    else:
        cols = st.columns(2)  # Always 2 columns on mobile
    
    for i, metric in enumerate(metrics):
        col_idx = i % 2
        with cols[col_idx]:
            st.metric(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta', None)
            )

def create_responsive_chart(fig, title: str = "", height: int = 400):
    """Create a responsive chart that adapts to screen size."""
    # Adjust chart height for mobile
    if st.session_state.get('is_mobile', False):
        height = 300
    
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=10 if st.session_state.get('is_mobile', False) else 12)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def create_mobile_friendly_table(df, title: str = ""):
    """Create a mobile-friendly table."""
    if title:
        st.subheader(title)
    
    # Limit columns on mobile
    if st.session_state.get('is_mobile', False) and len(df.columns) > 4:
        # Show only most important columns on mobile
        important_cols = df.columns[:4].tolist()
        df_mobile = df[important_cols]
        
        st.dataframe(df_mobile, use_container_width=True)
        
        # Show column selector for mobile
        with st.expander("Ver todas as colunas"):
            st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

def create_touch_friendly_buttons(buttons: List[Dict[str, str]]):
    """Create touch-friendly buttons for mobile."""
    # Use full width on mobile
    if st.session_state.get('is_mobile', False):
        for button in buttons:
            if st.button(button['text'], key=button['key']):
                return button['key']
    else:
        # Use columns on desktop
        cols = st.columns(len(buttons))
        for i, button in enumerate(buttons):
            with cols[i]:
                if st.button(button['text'], key=button['key']):
                    return button['key']
    
    return None

def create_mobile_optimized_form(form_config: Dict[str, Any]):
    """Create a mobile-optimized form."""
    with st.form(form_config['key']):
        # Stack form elements vertically on mobile
        for field in form_config['fields']:
            if field['type'] == 'text':
                st.text_input(field['label'], key=field['key'])
            elif field['type'] == 'number':
                st.number_input(field['label'], key=field['key'])
            elif field['type'] == 'select':
                st.selectbox(field['label'], field['options'], key=field['key'])
            elif field['type'] == 'checkbox':
                st.checkbox(field['label'], key=field['key'])
            elif field['type'] == 'slider':
                st.slider(field['label'], field['min'], field['max'], key=field['key'])
        
        # Submit button
        submitted = st.form_submit_button(form_config['submit_text'])
        return submitted

def create_responsive_sidebar():
    """Create a responsive sidebar that adapts to screen size."""
    with st.sidebar:
        st.title("FinBot 🤖")
        
        # Collapsible sections on mobile
        if st.session_state.get('is_mobile', False):
            with st.expander("Navegação", expanded=True):
                # Navigation options
                pass
        else:
            # Regular sidebar on desktop
            pass

def detect_mobile():
    """Detect if user is on mobile device."""
    # This is a simplified detection - in a real app you'd use JavaScript
    # For now, we'll use a session state flag
    if 'is_mobile' not in st.session_state:
        st.session_state.is_mobile = False
    
    return st.session_state.is_mobile

def create_mobile_friendly_layout():
    """Create a mobile-friendly layout wrapper."""
    # Apply mobile CSS
    apply_mobile_css()
    
    # Detect mobile
    is_mobile = detect_mobile()
    
    # Set page config for mobile
    if is_mobile:
        st.set_page_config(
            page_title="FinBot Mobile",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
    
    return is_mobile

def create_responsive_grid(items: List[Any], cols_desktop: int = 3, cols_mobile: int = 1):
    """Create a responsive grid layout."""
    is_mobile = st.session_state.get('is_mobile', False)
    cols = cols_mobile if is_mobile else cols_desktop
    
    if cols == 1:
        # Stack vertically on mobile
        for item in items:
            st.write(item)
    else:
        # Use columns on desktop
        columns = st.columns(cols)
        for i, item in enumerate(items):
            with columns[i % cols]:
                st.write(item)

def create_mobile_friendly_chart_container(chart_func, title: str = ""):
    """Create a mobile-friendly chart container."""
    with st.container():
        if title:
            st.subheader(title)
        
        # Add loading state
        with st.spinner("Carregando gráfico..."):
            fig = chart_func()
            
            if fig:
                create_responsive_chart(fig, title)
            else:
                st.info("Nenhum dado disponível para este gráfico.")

def create_touch_friendly_navigation(pages: List[str], current_page: str):
    """Create touch-friendly navigation."""
    # Use tabs on mobile, radio buttons on desktop
    if st.session_state.get('is_mobile', False):
        selected = st.tabs(pages)
        return selected
    else:
        selected = st.radio("Navegação", pages, key="nav_radio")
        return selected

def create_mobile_optimized_dashboard():
    """Create a mobile-optimized dashboard layout."""
    is_mobile = create_mobile_friendly_layout()
    
    # Mobile-specific optimizations
    if is_mobile:
        # Use smaller fonts and spacing
        st.markdown("""
        <style>
        .main .block-container {
            padding: 1rem;
        }
        .stMetric {
            font-size: 0.9rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    return is_mobile 