"""
AISCA - Application Principale
Agent Intelligent Sémantique et Génératif pour la Cartographie des Compétences
Navigation et orchestration complète du système
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Imports des modules
from app.semantic_analysis import SemanticAnalyzer
import pandas as pd
from datetime import datetime
import json

# Configuration de la page
st.set_page_config(
    page_title="AISCA - Système d'Analyse de Compétences",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS GLOBAL ULTRA MODERNE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Sidebar elements */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Navigation buttons in sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        width: 100%;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateX(5px);
    }
    
    /* Main content background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
    }
    
    /* Welcome screen */
    .welcome-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        padding: 4rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        margin: 2rem 0;
        animation: fadeIn 1s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .welcome-hero h1 {
        color: white !important;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .welcome-hero p {
        color: #e0e7ff !important;
        font-size: 1.4rem;
        font-weight: 300;
        line-height: 1.8;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 5px solid #667eea;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .feature-card h3 {
        color: #1a202c !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        color: #4a5568 !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 5px solid #667eea;
    }
    
    .info-box p {
        color: #1a202c !important;
        margin: 0;
        font-weight: 500;
    }
    
    /* Progress indicator */
    .progress-step {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .progress-step.active {
        background: rgba(255, 255, 255, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    .progress-step.completed {
        background: rgba(132, 250, 176, 0.3);
        border: 2px solid rgba(132, 250, 176, 0.5);
    }
    
    /* Stats card */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .stats-number {
        font-size: 3rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .stats-label {
        font-size: 1.1rem;
        font-weight: 300;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .welcome-hero h1 {
            font-size: 2.5rem;
        }
        .welcome-hero p {
            font-size: 1.1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialiser les variables de session"""
    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'
    if 'responses' not in st.session_state:
        st.session_state.responses = {
            'bloc1': {},
            'bloc2': {},
            'bloc3': {},
            'bloc4': {},
            'bloc5': {}
        }
    if 'current_block' not in st.session_state:
        st.session_state.current_block = 1
    if 'questionnaire_completed' not in st.session_state:
        st.session_state.questionnaire_completed = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None


def sidebar_navigation():
    """Barre latérale de navigation"""
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logo et titre
        st.markdown("""
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h1 style='color: white; font-size: 2rem; margin-bottom: 0.5rem;'>🎓 AISCA</h1>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem;'>Agent Intelligent Sémantique</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Progress steps
        st.markdown("### 📋 Progression")
        
        steps = [
            ('welcome', '🏠 Accueil', st.session_state.page == 'welcome'),
            ('questionnaire', '📝 Questionnaire', st.session_state.questionnaire_completed),
            ('analysis', '🔍 Analyse', st.session_state.analysis_results is not None),
            ('results', '📊 Résultats', st.session_state.analysis_results is not None)
        ]
        
        for step_id, step_name, completed in steps:
            if completed:
                icon = "✅"
                class_name = "completed"
            elif st.session_state.page == step_id:
                icon = "▶️"
                class_name = "active"
            else:
                icon = "⭕"
                class_name = ""
            
            st.markdown(f"""
                <div class='progress-step {class_name}'>
                    <span>{icon}</span>
                    <span>{step_name}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.page = 'welcome'
            st.rerun()
        
        if st.button("📝 Questionnaire", use_container_width=True):
            st.session_state.page = 'questionnaire'
            st.rerun()
        
        if st.session_state.analysis_results:
            if st.button("📊 Résultats", use_container_width=True):
                st.session_state.page = 'results'
                st.rerun()
        
        st.markdown("---")
        
        # Info
        st.markdown("### ℹ️ Informations")
        st.markdown("""
            <div style='color: white; font-size: 0.9rem; line-height: 1.6;'>
                <p><strong>Projet Master</strong><br>Expert en Ingénierie de Données</p>
                <p><strong>EFREI</strong><br>2025-2026</p>
            </div>
        """, unsafe_allow_html=True)


def welcome_page():
    """Page d'accueil"""
    st.markdown("""
        <div class="welcome-hero">
            <h1>🎓 Bienvenue sur AISCA</h1>
            <p>Agent Intelligent Sémantique et Génératif<br>pour la Cartographie des Compétences</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Description du projet
    st.markdown("""
        <div class="info-box">
            <p>
                <strong>🎯 Objectif :</strong> Évaluer vos compétences en Data Science à travers un questionnaire 
                hybride et recommander les métiers les plus adaptés à votre profil grâce à l'analyse sémantique 
                avec SBERT (Sentence-BERT).
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features en colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>📝 Questionnaire Hybride</h3>
                <p>5 blocs de compétences avec questions Likert, texte libre, choix multiples et cases à cocher</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>🧠 Analyse Sémantique</h3>
                <p>Utilisation de SBERT pour analyser vos réponses et détecter automatiquement vos compétences</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <h3>🎯 Recommandation</h3>
                <p>TOP 3 métiers recommandés parmi 15 profils data avec scores de compatibilité</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Stats en colonnes
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stats-card">
                <div class="stats-number">430</div>
                <div class="stats-label">Compétences</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stats-card">
                <div class="stats-number">5</div>
                <div class="stats-label">Blocs</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stats-card">
                <div class="stats-number">15</div>
                <div class="stats-label">Métiers</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="stats-card">
                <div class="stats-number">20</div>
                <div class="stats-label">Questions</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Commencer l'Évaluation", use_container_width=True, type="primary"):
            st.session_state.page = 'questionnaire'
            st.rerun()
    
    # Details expandables
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    with st.expander("📚 En savoir plus sur la méthodologie"):
        st.markdown("""
            ### Méthodologie AISCA
            
            **1. Collecte des Réponses**
            - Questionnaire hybride avec 5 types de questions
            - 4 questions par bloc de compétences
            - Collecte de données quantitatives ET qualitatives
            
            **2. Analyse Sémantique (SBERT)**
            - Conversion des réponses textuelles en embeddings
            - Calcul de similarité cosinus avec 430 compétences
            - Détection automatique des compétences maîtrisées
            
            **3. Calcul du Score**
            - Formule pondérée : 40% SBERT + 25% Likert + 20% Checkboxes + 15% Outils
            - Score par bloc (0-1)
            - Coverage Score global
            
            **4. Recommandation de Métiers**
            - Matching avec 15 profils métiers data
            - Calcul du score de compatibilité
            - Sélection des TOP 3 métiers les plus adaptés
            
            **5. Visualisation**
            - Radar chart du profil de compétences
            - Bar chart des scores par bloc
            - Gauge du coverage score
            - Heatmap des compétences détectées
        """)
    
    with st.expander("🎓 Les 5 Blocs de Compétences"):
        st.markdown("""
            ### Blocs Évalués
            
            **🔵 Bloc 1 : Data Analysis & Visualization**
            - Nettoyage et préparation des données
            - Manipulation avec Pandas/NumPy
            - SQL et bases de données
            - Visualisation (Matplotlib, Seaborn, Plotly)
            - Dashboards et storytelling
            
            **🟢 Bloc 2 : Machine Learning Supervisé**
            - Régression et classification
            - Algorithmes (Random Forest, XGBoost, SVM...)
            - Optimisation d'hyperparamètres
            - Évaluation de modèles
            - Feature engineering
            
            **🟡 Bloc 3 : Machine Learning Non Supervisé**
            - Clustering (K-means, DBSCAN...)
            - Réduction de dimensionnalité (PCA, t-SNE)
            - Détection d'anomalies
            - Segmentation
            
            **🔴 Bloc 4 : NLP (Natural Language Processing)**
            - Prétraitement de texte
            - Embeddings (Word2Vec, BERT, SBERT)
            - Transformers
            - Classification de texte
            - Analyse de sentiments
            - Chatbots
            
            **🟣 Bloc 5 : Statistiques & Mathématiques**
            - Tests d'hypothèses
            - Distributions de probabilités
            - Algèbre linéaire
            - Optimisation
            - Séries temporelles
        """)
    
    with st.expander("💼 Les 15 Métiers Data"):
        st.markdown("""
            ### Profils Métiers
            
            1. **Data Analyst** - Analyse et visualisation de données
            2. **Data Scientist** - Modélisation prédictive complète
            3. **Machine Learning Engineer** - Déploiement ML en production
            4. **NLP Engineer** - Solutions de traitement du langage
            5. **Data Engineer** - Pipelines et infrastructure data
            6. **Business Intelligence Analyst** - Dashboards et reporting
            7. **AI Research Scientist** - Recherche en IA
            8. **Deep Learning Engineer** - Réseaux de neurones profonds
            9. **Computer Vision Engineer** - Traitement d'images
            10. **MLOps Engineer** - Industrialisation ML
            11. **Data Architect** - Architecture de données
            12. **Statistician** - Analyse statistique avancée
            13. **Quantitative Analyst** - Modèles quantitatifs finance
            14. **Applied Scientist** - Recherche appliquée
            15. **Analytics Engineer** - Pipelines analytiques
        """)


def questionnaire_page():
    """Page du questionnaire"""
    # Si pas encore terminé, afficher le questionnaire
    if not st.session_state.questionnaire_completed:
        # Importer et lancer le questionnaire
        import sys
        import importlib
        
        # Recharger le module questionnaire pour éviter les caches
        if 'app.questionnaire' in sys.modules:
            importlib.reload(sys.modules['app.questionnaire'])
        
        from app import questionnaire
        questionnaire.main()
    else:
        # Questionnaire terminé, afficher le bouton pour l'analyse
        st.success("✅ Questionnaire terminé !")
        
        st.markdown("""
            <div class="info-box">
                <p>
                    🎉 <strong>Félicitations !</strong> Vous avez complété le questionnaire. 
                    Lancez maintenant l'analyse sémantique pour découvrir vos résultats.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔍 Lancer l'Analyse Sémantique", use_container_width=True, type="primary"):
                st.session_state.page = 'analysis'
                st.rerun()
        
        with col1:
            if st.button("🔄 Recommencer", use_container_width=True):
                # Reset
                st.session_state.responses = {
                    'bloc1': {},
                    'bloc2': {},
                    'bloc3': {},
                    'bloc4': {},
                    'bloc5': {}
                }
                st.session_state.current_block = 1
                st.session_state.questionnaire_completed = False
                st.session_state.analysis_results = None
                st.rerun()

def analysis_page():
    """Page d'analyse"""
    st.markdown("""
        <div class="welcome-hero">
            <h1>🔍 Analyse Sémantique en Cours</h1>
            <p>SBERT analyse vos réponses et calcule votre profil de compétences</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Étape 1 : Initialisation
        status_text.text("📥 Initialisation du moteur SBERT...")
        progress_bar.progress(10)
        
        if st.session_state.analyzer is None:
            st.session_state.analyzer = SemanticAnalyzer(
                competencies_path='data/competencies.csv',
                jobs_path='data/jobs.csv'
            )
        
        analyzer = st.session_state.analyzer
        
        # Étape 2 : Analyse des réponses
        status_text.text("🧠 Analyse sémantique des textes libres...")
        progress_bar.progress(30)
        
        analyzer.analyze_user_responses(st.session_state.responses)
        
        # Étape 3 : Calcul des scores
        status_text.text("📊 Calcul des scores par bloc...")
        progress_bar.progress(50)
        
        # Récupérer les résultats
        results = analyzer.get_results_summary()
        
        # Étape 4 : Génération du Plan de Progression (OPENAI)
        status_text.text("🤖 Génération du plan de progression avec OpenAI...")
        progress_bar.progress(70)
        
        from app import openai_helper
        progression_plan = openai_helper.generate_progression_plan(results)
        results['progression_plan'] = progression_plan
        
        # Étape 5 : Génération de la Bio (OPENAI)
        status_text.text("📝 Génération de la bio professionnelle avec OpenAI...")
        progress_bar.progress(85)
        
        professional_bio = openai_helper.generate_professional_bio(results)
        results['professional_bio'] = professional_bio
        
        # Étape 6 : Finalisation
        status_text.text("✅ Analyse terminée !")
        progress_bar.progress(100)
        
        # Sauvegarder les résultats
        st.session_state.analysis_results = results
        
        # Sauvegarder dans fichier JSON (dans responses/)
        analyzer.save_results()
        
        st.success("✅ Analyse terminée ! Résultats sauvegardés dans `responses/`")
        
        # Afficher un aperçu
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Coverage Score Global",
                f"{results['coverage_score']:.1%}",
                help="Score global de vos compétences"
            )
        
        with col2:
            top_job = results['recommended_jobs'][0]
            st.metric(
                "Métier Recommandé #1",
                top_job['job_title'],
                f"{top_job['match_score']:.1f}%"
            )
        
        with col3:
            # Compter les compétences détectées
            total_comps = sum(
                len(results['detected_competencies'].get(f'bloc{i}', []))
                for i in range(1, 6)
            )
            st.metric(
                "Compétences Détectées",
                total_comps,
                help="Nombre de compétences identifiées par SBERT"
            )
        
        # Afficher un aperçu du plan de progression
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎯 Aperçu du Plan de Progression")
        with st.expander("Voir le plan complet", expanded=False):
            st.markdown(progression_plan)
        
        # Afficher un aperçu de la bio
        st.markdown("### 📝 Votre Bio Professionnelle")
        st.info(professional_bio)
        
        # Bouton pour voir les résultats
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("📊 Voir les Résultats Complets", use_container_width=True, type="primary"):
                st.session_state.page = 'results'
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
        st.exception(e)
        
        if st.button("🔙 Retour au questionnaire"):
            st.session_state.page = 'questionnaire'
            st.rerun()

def results_page():
    """Page de résultats"""
    if st.session_state.analysis_results is None:
        st.warning("⚠️ Aucun résultat disponible. Veuillez d'abord compléter le questionnaire.")
        if st.button("📝 Aller au questionnaire"):
            st.session_state.page = 'questionnaire'
            st.rerun()
        return
    
    # Import du module results
    from app import results as results_module
    
    # Charger les données
    jobs_df = pd.read_csv('data/jobs.csv')
    competencies_df = pd.read_csv('data/competencies.csv')
    
    # Afficher les résultats
    results_module.display_results(
        st.session_state.analysis_results,
        jobs_df,
        competencies_df
    )


def main():
    """Fonction principale"""
    # Initialiser
    init_session_state()
    
    # Sidebar
    sidebar_navigation()
    
    # Router
    if st.session_state.page == 'welcome':
        welcome_page()
    elif st.session_state.page == 'questionnaire':
        questionnaire_page()
    elif st.session_state.page == 'analysis':
        analysis_page()
    elif st.session_state.page == 'results':
        results_page()
    else:
        st.error(f"Page inconnue : {st.session_state.page}")


if __name__ == "__main__":
    main()