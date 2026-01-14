"""
AISCA - Page de Résultats et Visualisations
Étape 5 : Recommandation de métiers + Data Viz
Interface ultra moderne avec Plotly
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List

# CSS ULTRA MODERNE - Glassmorphism + Gradients
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background avec gradient animé */
    .main {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        padding: 2rem;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hero Header avec effet glassmorphism */
    .hero-header {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
        animation: fadeInDown 0.8s ease;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-header h1 {
        color: #ffffff !important;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px;
    }
    
    .hero-header p {
        color: #f0f4ff !important;
        font-size: 1.3rem;
        margin-top: 1rem;
        font-weight: 300;
    }
    
    /* Coverage Score Card - Grande et imposante */
    .coverage-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        text-align: center;
        animation: fadeInUp 1s ease;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .coverage-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 3s ease infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .coverage-score {
        font-size: 6rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 3px 3px 15px rgba(0, 0, 0, 0.3);
        margin: 1rem 0;
        position: relative;
        z-index: 1;
    }
    
    .coverage-label {
        font-size: 1.5rem;
        color: #e0e7ff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
    }
    
    /* Job Recommendation Cards */
    .job-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        animation: fadeIn 0.6s ease;
        border-left: 5px solid transparent;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .job-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
    }
    
    .job-card.rank-1 {
        border-left-color: #ffd700;
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 255, 255, 0.95) 100%);
    }
    
    .job-card.rank-2 {
        border-left-color: #c0c0c0;
        background: linear-gradient(135deg, rgba(192, 192, 192, 0.1) 0%, rgba(255, 255, 255, 0.95) 100%);
    }
    
    .job-card.rank-3 {
        border-left-color: #cd7f32;
        background: linear-gradient(135deg, rgba(205, 127, 50, 0.1) 0%, rgba(255, 255, 255, 0.95) 100%);
    }
    
    .job-rank {
        display: inline-block;
        width: 50px;
        height: 50px;
        line-height: 50px;
        border-radius: 50%;
        text-align: center;
        font-weight: 800;
        font-size: 1.5rem;
        margin-right: 1rem;
        float: left;
    }
    
    .job-rank.rank-1 {
        background: linear-gradient(135deg, #ffd700, #ffed4e);
        color: #ffffff;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
    }
    
    .job-rank.rank-2 {
        background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
        color: #ffffff;
        box-shadow: 0 5px 15px rgba(192, 192, 192, 0.4);
    }
    
    .job-rank.rank-3 {
        background: linear-gradient(135deg, #cd7f32, #e89b5c);
        color: #ffffff;
        box-shadow: 0 5px 15px rgba(205, 127, 50, 0.4);
    }
    
    .job-title {
        color: #1a202c !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .job-match {
        color: #4a5568 !important;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .job-description {
        color: #718096 !important;
        font-size: 1rem;
        margin-top: 1rem;
        line-height: 1.6;
    }
    
    /* Section Headers */
    .section-header {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 2rem 0 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .section-header h2 {
        color: #ffffff !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
    }
    
    /* Graph Container */
    .graph-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        animation: fadeIn 0.8s ease;
    }
    
    /* Competencies List */
    .competencies-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    }
    
    .competency-item {
        background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .competency-item:hover {
        transform: translateX(10px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .competency-name {
        color: #1a202c !important;
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    .competency-score {
        color: #667eea !important;
        font-weight: 700;
        font-size: 1.1rem;
        float: right;
    }
    
    /* Action Button */
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2.5rem;
        border-radius: 50px;
        border: none;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .action-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.3rem;
    }
    
    .badge-excellent {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #ffffff;
    }
    
    .badge-good {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #1a202c;
    }
    
    .badge-average {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #1a202c;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-header h1 {
            font-size: 2rem;
        }
        .coverage-score {
            font-size: 4rem;
        }
        .job-title {
            font-size: 1.4rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


def create_radar_chart(block_scores: Dict) -> go.Figure:
    """
    Créer un Radar Chart pour visualiser le profil de compétences
    
    Args:
        block_scores: Dictionnaire des scores par bloc
        
    Returns:
        Figure Plotly
    """
    # Préparer les données
    categories = [
        'Data Analysis &<br>Visualization',
        'Machine Learning<br>Supervisé',
        'Machine Learning<br>Non Supervisé',
        'NLP',
        'Statistiques &<br>Mathématiques'
    ]
    
    values = [
        block_scores['bloc1']['score'],
        block_scores['bloc2']['score'],
        block_scores['bloc3']['score'],
        block_scores['bloc4']['score'],
        block_scores['bloc5']['score']
    ]
    
    # Fermer le polygone
    values.append(values[0])
    categories_closed = categories + [categories[0]]
    
    # Créer le radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#667eea'),
        name='Votre Profil',
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showline=False,
                gridcolor='rgba(0, 0, 0, 0.1)',
                tickfont=dict(size=12, color='#4a5568'),
            ),
            angularaxis=dict(
                gridcolor='rgba(0, 0, 0, 0.1)',
                linecolor='rgba(0, 0, 0, 0.2)',
            ),
            bgcolor='rgba(255, 255, 255, 0.5)'
        ),
        showlegend=False,
        title={
            'text': '📊 Profil de Compétences (Radar Chart)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#1a202c', 'family': 'Inter'}
        },
        font=dict(size=13, color='#1a202c', family='Inter'),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        height=600,
        margin=dict(t=100, b=50, l=80, r=80)
    )
    
    return fig


def create_bar_chart(block_scores: Dict) -> go.Figure:
    """
    Créer un Bar Chart horizontal pour les scores par bloc
    
    Args:
        block_scores: Dictionnaire des scores par bloc
        
    Returns:
        Figure Plotly
    """
    # Préparer les données
    blocs = [
        'Bloc 1: Data Analysis',
        'Bloc 2: ML Supervisé',
        'Bloc 3: ML Non Supervisé',
        'Bloc 4: NLP',
        'Bloc 5: Stats & Maths'
    ]
    
    scores = [
        block_scores['bloc1']['score'],
        block_scores['bloc2']['score'],
        block_scores['bloc3']['score'],
        block_scores['bloc4']['score'],
        block_scores['bloc5']['score']
    ]
    
    # Couleurs gradient
    colors = [
        '#4facfe',  # Bleu
        '#00f2fe',  # Cyan
        '#43e97b',  # Vert
        '#38f9d7',  # Turquoise
        '#667eea'   # Violet
    ]
    
    # Créer le bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=blocs,
        x=scores,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255, 255, 255, 0.3)', width=2)
        ),
        text=[f'{score:.1%}' for score in scores],
        textposition='outside',
        textfont=dict(size=16, color='#1a202c', family='Inter', weight=600),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '📊 Scores Détaillés par Bloc',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#1a202c', 'family': 'Inter'}
        },
        xaxis=dict(
            title=dict(
                text='Score',
                font=dict(size=14, color='#1a202c')
            ),
            range=[0, 1.1],
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.05)',
            zeroline=False,
            tickfont=dict(size=12, color='#4a5568')
        ),
        yaxis=dict(
            tickfont=dict(size=14, color='#1a202c', family='Inter', weight=600),
            automargin=True
        ),
        font=dict(size=13, color='#1a202c', family='Inter'),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0.5)',
        height=500,
        margin=dict(t=100, b=50, l=200, r=100),
        showlegend=False
    )
    
    return fig


def create_gauge_chart(coverage_score: float) -> go.Figure:
    """
    Créer un Gauge Chart pour le Coverage Score global
    
    Args:
        coverage_score: Score global (0-1)
        
    Returns:
        Figure Plotly
    """
    # Déterminer la couleur selon le score
    if coverage_score >= 0.7:
        color = '#84fab0'  # Vert
        level = 'Excellent'
    elif coverage_score >= 0.5:
        color = '#4facfe'  # Bleu
        level = 'Bon'
    else:
        color = '#fcb69f'  # Orange
        level = 'Moyen'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=coverage_score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"<b>Coverage Score Global</b><br><span style='font-size:0.8em;color:#718096'>Niveau: {level}</span>",
            'font': {'size': 24, 'color': '#1a202c', 'family': 'Inter'}
        },
        number={
            'suffix': '%',
            'font': {'size': 60, 'color': '#1a202c', 'family': 'Inter', 'weight': 800}
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 2,
                'tickcolor': '#4a5568',
                'tickfont': {'size': 14, 'color': '#4a5568'}
            },
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': 'rgba(0, 0, 0, 0.05)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': 'rgba(252, 182, 159, 0.3)'},
                {'range': [50, 70], 'color': 'rgba(79, 172, 254, 0.3)'},
                {'range': [70, 100], 'color': 'rgba(132, 250, 176, 0.3)'}
            ],
            'threshold': {
                'line': {'color': 'rgba(255, 255, 255, 0.8)', 'width': 4},
                'thickness': 0.85,
                'value': coverage_score * 100
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0)',
        font={'family': 'Inter'},
        height=400,
        margin=dict(t=100, b=50, l=50, r=50)
    )
    
    return fig


def create_competencies_heatmap(detected_competencies: Dict, competencies_df: pd.DataFrame) -> go.Figure:
    """
    Créer une Heatmap des compétences détectées
    
    Args:
        detected_competencies: Compétences détectées par bloc
        competencies_df: DataFrame des compétences
        
    Returns:
        Figure Plotly
    """
    # Préparer les données pour la heatmap
    all_comps = []
    
    for bloc_id in range(1, 6):
        bloc_key = f'bloc{bloc_id}'
        if bloc_key in detected_competencies:
            comps = detected_competencies[bloc_key]
            # Prendre les top 5 par bloc
            top_comps = sorted(comps, key=lambda x: x['similarity'], reverse=True)[:5]
            all_comps.extend(top_comps)
    
    # Trier par similarité
    all_comps = sorted(all_comps, key=lambda x: x['similarity'], reverse=True)[:20]
    
    if not all_comps:
        # Si aucune compétence détectée, retourner figure vide
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune compétence détectée avec confiance suffisante",
            showarrow=False,
            font=dict(size=16, color='#718096')
        )
        return fig
    
    # Créer les données
    comp_names = [comp['competency_name'] for comp in all_comps]
    similarities = [comp['similarity'] for comp in all_comps]
    
    # Créer la heatmap (en fait, un bar chart horizontal coloré)
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=comp_names,
        x=similarities,
        orientation='h',
        marker=dict(
            color=similarities,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title=dict(
                    text='Score',
                    side='right'
                ),
                tickmode='linear',
                tick0=0,
                dtick=0.2,
                tickfont=dict(size=12, color='#4a5568')
            ),
            line=dict(color='rgba(255, 255, 255, 0.3)', width=1)
        ),
        text=[f'{sim:.2f}' for sim in similarities],
        textposition='outside',
        textfont=dict(size=12, color='#1a202c', family='Inter', weight=600),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '🎯 Top 20 Compétences Détectées (Analyse Sémantique)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#1a202c', 'family': 'Inter'}
        },
        xaxis=dict(
            title=dict(
                text='Score de Similarité SBERT',
                font=dict(size=14, color='#1a202c')
            ),
            range=[0, 1],
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.05)',
            zeroline=False,
            tickfont=dict(size=12, color='#4a5568')
        ),
        yaxis=dict(
            tickfont=dict(size=11, color='#1a202c', family='Inter'),
            automargin=True
        ),
        font=dict(size=13, color='#1a202c', family='Inter'),
        paper_bgcolor='rgba(255, 255, 255, 0)',
        plot_bgcolor='rgba(255, 255, 255, 0.5)',
        height=700,
        margin=dict(t=100, b=50, l=300, r=100),
        showlegend=False
    )
    
    return fig


def display_results(results: Dict, jobs_df: pd.DataFrame, competencies_df: pd.DataFrame):
    """
    Afficher tous les résultats avec visualisations
    
    Args:
        results: Résultats de l'analyse sémantique
        jobs_df: DataFrame des métiers
        competencies_df: DataFrame des compétences
    """
    
    # Hero Header
    st.markdown("""
        <div class="hero-header">
            <h1>🎓 Résultats de Votre Évaluation AISCA</h1>
            <p>Analyse sémantique complète de vos compétences data</p>
        </div>
    """, unsafe_allow_html=True)
    
    # ========================================
    # COVERAGE SCORE GLOBAL
    # ========================================
    coverage_score = results['coverage_score']
    
    st.markdown(f"""
        <div class="coverage-card">
            <div class="coverage-label">Coverage Score Global</div>
            <div class="coverage-score">{coverage_score:.1%}</div>
            <div class="coverage-label">
                {"🏆 Excellent Profil !" if coverage_score >= 0.7 else "👍 Bon Profil" if coverage_score >= 0.5 else "📈 Profil en Développement"}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # ========================================
    # TOP 3 MÉTIERS RECOMMANDÉS
    # ========================================
    st.markdown("""
        <div class="section-header">
            <h2>🎯 Top 3 Métiers Recommandés</h2>
        </div>
    """, unsafe_allow_html=True)
    
    recommended_jobs = results['recommended_jobs']
    
    for i, job in enumerate(recommended_jobs[:3], 1):
        job_title = job['job_title']
        match_score = job['match_score']
        
        # Récupérer la description du métier
        job_info = jobs_df[jobs_df['JobTitle'] == job_title]
        description = job_info.iloc[0]['Description'] if not job_info.empty else "Description non disponible"
        
        st.markdown(f"""
            <div class="job-card rank-{i}">
                <div class="job-rank rank-{i}">{i}</div>
                <div>
                    <h3 class="job-title">{job_title}</h3>
                    <p class="job-match">💯 Score de compatibilité : {match_score:.1f}%</p>
                    <p class="job-description">{description}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ========================================
    # VISUALISATIONS
    # ========================================
    st.markdown("""
        <div class="section-header">
            <h2>📊 Visualisations de Votre Profil</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Gauge Chart
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    gauge_fig = create_gauge_chart(coverage_score)
    st.plotly_chart(gauge_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Layout 2 colonnes pour Radar + Bar
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        radar_fig = create_radar_chart(results['block_scores'])
        st.plotly_chart(radar_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        bar_fig = create_bar_chart(results['block_scores'])
        st.plotly_chart(bar_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Heatmap des compétences
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    heatmap_fig = create_competencies_heatmap(
        results['detected_competencies'],
        competencies_df
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================
    # DÉTAIL DES SCORES PAR BLOC
    # ========================================
    st.markdown("""
        <div class="section-header">
            <h2>🔍 Détail des Scores par Bloc</h2>
        </div>
    """, unsafe_allow_html=True)
    
    block_names = {
        'bloc1': '🔵 Data Analysis & Visualization',
        'bloc2': '🟢 Machine Learning Supervisé',
        'bloc3': '🟡 Machine Learning Non Supervisé',
        'bloc4': '🔴 NLP (Natural Language Processing)',
        'bloc5': '🟣 Statistiques & Mathématiques'
    }
    
    for bloc_key in ['bloc1', 'bloc2', 'bloc3', 'bloc4', 'bloc5']:
        bloc_data = results['block_scores'][bloc_key]
        
        with st.expander(f"{block_names[bloc_key]} - Score: {bloc_data['score']:.1%}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🧠 SBERT", f"{bloc_data.get('sbert_score', 0):.1%}", 
                         help="Score d'analyse sémantique du texte libre")
            with col2:
                st.metric("📊 Likert", f"{bloc_data.get('likert_score', 0):.1%}",
                         help="Score d'auto-évaluation")
            with col3:
                st.metric("🔧 Outils", f"{bloc_data.get('tools_score', 0):.1%}",
                         help="Score basé sur les outils sélectionnés")
            with col4:
                # ✅ CORRIGÉ ICI - experience_score au lieu de checkbox_score
                st.metric("💼 Expérience", f"{bloc_data.get('experience_score', 0):.1%}",
                         help="Score basé sur l'expérience déclarée")
            
            # Liste des compétences détectées
            detected_comps = bloc_data.get('detected_competencies', [])
            if detected_comps:
                st.markdown("**🎯 Compétences détectées par analyse sémantique:**")
                for comp in detected_comps[:10]:
                    st.markdown(f"- `{comp['competency_name']}` (score: {comp['similarity']:.3f})")
    
# ========================================
    # ACTIONS
    # ========================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # ✅ BOUTON 1 - Retour à la page analyse (Bio + Plan)
        if st.button("⬅️ Retour au Récapitulatif", use_container_width=True, type="primary"):
            st.session_state.page = 'analysis'
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ✅ BOUTON 2 - Recommencer vraiment (Reset tout)
        if st.button("🔄 Recommencer une Nouvelle Évaluation", use_container_width=True):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()