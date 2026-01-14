"""
AISCA - Questionnaire de Cartographie des Compétences
Projet Master Expert en Ingénierie de Données
Interface moderne et professionnelle
"""

import streamlit as st
import json
from datetime import datetime



# CSS MODERNE ET PROFESSIONNEL - Lisible sur TOUS les fonds
st.markdown("""
    <style>
    /* Import de Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Style global */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Container principal */
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: #ffffff !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: #e0e7ff !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Progress bar container */
    .progress-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(245, 87, 108, 0.2);
    }
    
    .progress-text {
        color: #ffffff !important;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    /* Bloc de questions - Card style */
    .block-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.25);
    }
    
    .block-card h2 {
        color: #ffffff !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.15);
    }
    
    /* Questions container */
    .question-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .question-label {
        color: #1a202c !important;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: block;
    }
    
    .question-subtitle {
        color: #4a5568 !important;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0.3rem;
        font-style: italic;
    }
    
    /* Inputs styling */
    .stTextArea textarea {
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        background-color: #ffffff !important;
        color: #1a202c !important;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Radio buttons et checkboxes */
    .stRadio > label, .stCheckbox > label {
        color: #2d3748 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    .stRadio > div, .stCheckbox > div {
        background-color: #f7fafc;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    .stMultiSelect label {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* Slider Likert */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #f093fb 0%, #667eea 100%) !important;
    }
    
    .stSlider label {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    /* Boutons de navigation */
    .nav-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.8rem 2rem !important;
        border-radius: 10px !important;
        border: none !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Success message */
    .success-container {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(132, 250, 176, 0.3);
    }
    
    .success-container h2 {
        color: #ffffff !important;
        font-size: 2rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .success-container p {
        color: #ffffff !important;
        font-size: 1.2rem;
        margin-top: 1rem;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .info-box p {
        color: #2d3748 !important;
        margin: 0;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        .block-card h2 {
            font-size: 1.4rem;
        }
        .question-container {
            padding: 1.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialiser les variables de session"""
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


def display_progress():
    """Afficher la barre de progression"""
    progress = (st.session_state.current_block - 1) / 5
    
    st.markdown(f"""
        <div class="progress-container">
            <p class="progress-text">📊 Progression : Bloc {st.session_state.current_block} sur 5</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress)


def bloc1_data_analysis():
    """Bloc 1 : Data Analysis & Visualization"""
    
    st.markdown("""
        <div class="block-card">
            <h2>🔵 Bloc 1 : Data Analysis & Visualization</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Q1 - Likert
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q1. Évaluez votre niveau de maîtrise en analyse et préparation de données</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Nettoyage, transformation, gestion des valeurs manquantes, visualisation</span>', unsafe_allow_html=True)
    
    q1 = st.slider(
        "",
        min_value=0,
        max_value=5,
        value=st.session_state.responses['bloc1'].get('q1_likert', 0),
        key='bloc1_q1',
        help="0 = Aucune connaissance | 5 = Expert"
    )
    st.caption("0️⃣ Aucune connaissance — 1️⃣ Débutant — 2️⃣ Notions de base — 3️⃣ Intermédiaire — 4️⃣ Avancé — 5️⃣ Expert")
    st.session_state.responses['bloc1']['q1_likert'] = q1
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q2 - Texte libre
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q2. Décrivez vos compétences et expériences en Data Analysis</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Parlez de vos projets, méthodes utilisées, insights découverts, outils maîtrisés</span>', unsafe_allow_html=True)
    
    q2 = st.text_area(
        "",
        value=st.session_state.responses['bloc1'].get('q2_text', ''),
        height=150,
        key='bloc1_q2',
        placeholder="Exemple : J'ai réalisé une analyse exploratoire de données de ventes avec Python et Pandas. J'ai créé des dashboards interactifs avec Plotly pour visualiser les tendances..."
    )
    st.session_state.responses['bloc1']['q2_text'] = q2
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q3 - Choix multiple (outils)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q3. Quels outils et bibliothèques de visualisation maîtrisez-vous ?</span>', unsafe_allow_html=True)
    
    q3 = st.multiselect(
        "",
        options=[
            "Matplotlib",
            "Seaborn", 
            "Plotly",
            "Tableau",
            "Power BI",
            "D3.js",
            "Altair",
            "Bokeh",
            "Aucun"
        ],
        default=st.session_state.responses['bloc1'].get('q3_tools', []),
        key='bloc1_q3'
    )
    st.session_state.responses['bloc1']['q3_tools'] = q3
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q4 - Cases à cocher (compétences)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q4. Quelles compétences en Data Analysis possédez-vous ?</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Sélectionnez toutes celles que vous maîtrisez</span>', unsafe_allow_html=True)
    
    competences_data_analysis = [
        "Data cleaning (nettoyage de données)",
        "Gestion des valeurs manquantes",
        "Détection et traitement des outliers",
        "Transformation et normalisation de données",
        "Manipulation avec Pandas",
        "Requêtes SQL",
        "Jointures SQL complexes",
        "Exploratory Data Analysis (EDA)",
        "Création de dashboards interactifs",
        "Storytelling avec les données",
        "ETL (Extract, Transform, Load)",
        "Web scraping",
        "Aucune"
    ]
    
    q4_selected = []
    for comp in competences_data_analysis:
        if st.checkbox(
            comp,
            value=comp in st.session_state.responses['bloc1'].get('q4_competences', []),
            key=f'bloc1_q4_{comp}'
        ):
            q4_selected.append(comp)
    
    st.session_state.responses['bloc1']['q4_competences'] = q4_selected
    st.markdown('</div>', unsafe_allow_html=True)


def bloc2_ml_supervise():
    """Bloc 2 : Machine Learning Supervisé"""
    
    st.markdown("""
        <div class="block-card">
            <h2>🟢 Bloc 2 : Machine Learning Supervisé</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Q5 - Likert
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q5. Évaluez votre niveau de maîtrise en Machine Learning supervisé</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Régression, classification, évaluation de modèles, hyperparamètres</span>', unsafe_allow_html=True)
    
    q5 = st.slider(
        "",
        min_value=0,
        max_value=5,
        value=st.session_state.responses['bloc2'].get('q5_likert', 0),
        key='bloc2_q5',
        help="0 = Aucune connaissance | 5 = Expert"
    )
    st.caption("0️⃣ Aucune connaissance — 1️⃣ Débutant — 2️⃣ Notions de base — 3️⃣ Intermédiaire — 4️⃣ Avancé — 5️⃣ Expert")
    st.session_state.responses['bloc2']['q5_likert'] = q5
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q6 - Texte libre
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q6. Décrivez vos compétences et projets en Machine Learning supervisé</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Problème métier, algorithmes testés, évaluation des performances, résultats obtenus</span>', unsafe_allow_html=True)
    
    q6 = st.text_area(
        "",
        value=st.session_state.responses['bloc2'].get('q6_text', ''),
        height=150,
        key='bloc2_q6',
        placeholder="Exemple : J'ai développé un modèle de prédiction de churn avec Random Forest. J'ai optimisé les hyperparamètres avec GridSearch et obtenu un F1-score de 0.87..."
    )
    st.session_state.responses['bloc2']['q6_text'] = q6
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q7 - Choix multiple (outils/bibliothèques)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q7. Quelles bibliothèques et frameworks ML utilisez-vous ?</span>', unsafe_allow_html=True)
    
    q7 = st.multiselect(
        "",
        options=[
            "Scikit-learn",
            "XGBoost",
            "LightGBM",
            "CatBoost",
            "TensorFlow",
            "Keras",
            "PyTorch",
            "MLflow",
            "Aucune"
        ],
        default=st.session_state.responses['bloc2'].get('q7_tools', []),
        key='bloc2_q7'
    )
    st.session_state.responses['bloc2']['q7_tools'] = q7
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q8 - Cases à cocher (algorithmes)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q8. Quels algorithmes de ML supervisé avez-vous déjà implémentés ?</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Sélectionnez tous ceux que vous avez utilisés</span>', unsafe_allow_html=True)
    
    algorithmes_ml = [
        "Régression linéaire",
        "Régression logistique",
        "Arbres de décision",
        "Random Forest",
        "Gradient Boosting (XGBoost, LightGBM)",
        "SVM (Support Vector Machines)",
        "K-Nearest Neighbors (KNN)",
        "Naive Bayes",
        "Réseaux de neurones (MLP)",
        "Optimisation d'hyperparamètres (GridSearch, RandomSearch)",
        "Validation croisée (Cross-validation)",
        "Gestion du déséquilibre de classes (SMOTE)",
        "Feature engineering",
        "Déploiement de modèles",
        "Aucun"
    ]
    
    q8_selected = []
    for algo in algorithmes_ml:
        if st.checkbox(
            algo,
            value=algo in st.session_state.responses['bloc2'].get('q8_algorithmes', []),
            key=f'bloc2_q8_{algo}'
        ):
            q8_selected.append(algo)
    
    st.session_state.responses['bloc2']['q8_algorithmes'] = q8_selected
    st.markdown('</div>', unsafe_allow_html=True)


def bloc3_ml_non_supervise():
    """Bloc 3 : Machine Learning Non Supervisé"""
    
    st.markdown("""
        <div class="block-card">
            <h2>🟡 Bloc 3 : Machine Learning Non Supervisé</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Q9 - Likert
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q9. Évaluez votre niveau en Machine Learning non supervisé</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Clustering, réduction de dimensionnalité, détection d\'anomalies</span>', unsafe_allow_html=True)
    
    q9 = st.slider(
        "",
        min_value=0,
        max_value=5,
        value=st.session_state.responses['bloc3'].get('q9_likert', 0),
        key='bloc3_q9',
        help="0 = Aucune connaissance | 5 = Expert"
    )
    st.caption("0️⃣ Aucune connaissance — 1️⃣ Débutant — 2️⃣ Notions de base — 3️⃣ Intermédiaire — 4️⃣ Avancé — 5️⃣ Expert")
    st.session_state.responses['bloc3']['q9_likert'] = q9
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q10 - Texte libre
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q10. Décrivez vos expériences avec le ML non supervisé</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Clustering, PCA, détection d\'anomalies, segmentation - objectif, algorithmes, résultats</span>', unsafe_allow_html=True)
    
    q10 = st.text_area(
        "",
        value=st.session_state.responses['bloc3'].get('q10_text', ''),
        height=150,
        key='bloc3_q10',
        placeholder="Exemple : J'ai segmenté des clients en 5 groupes avec K-means. J'ai utilisé PCA pour visualiser les clusters et la méthode du coude pour choisir k optimal..."
    )
    st.session_state.responses['bloc3']['q10_text'] = q10
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q11 - Choix multiple (outils)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q11. Quels outils utilisez-vous pour le ML non supervisé ?</span>', unsafe_allow_html=True)
    
    q11 = st.multiselect(
        "",
        options=[
            "Scikit-learn (clustering, PCA)",
            "UMAP",
            "t-SNE",
            "HDBSCAN",
            "PyOD (détection d'anomalies)",
            "Isolation Forest",
            "Autoencodeurs (Keras/PyTorch)",
            "Aucun"
        ],
        default=st.session_state.responses['bloc3'].get('q11_tools', []),
        key='bloc3_q11'
    )
    st.session_state.responses['bloc3']['q11_tools'] = q11
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q12 - Cases à cocher (techniques)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q12. Quelles techniques de ML non supervisé connaissez-vous ?</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Sélectionnez toutes celles que vous maîtrisez</span>', unsafe_allow_html=True)
    
    techniques_unsupervised = [
        "K-means clustering",
        "Clustering hiérarchique",
        "DBSCAN",
        "Gaussian Mixture Models (GMM)",
        "PCA (Principal Component Analysis)",
        "t-SNE",
        "UMAP",
        "Détection d'anomalies (Isolation Forest, LOF)",
        "Autoencodeurs",
        "Méthode du coude (Elbow method)",
        "Silhouette score",
        "Segmentation de clients",
        "Topic modeling (LDA)",
        "Aucune"
    ]
    
    q12_selected = []
    for tech in techniques_unsupervised:
        if st.checkbox(
            tech,
            value=tech in st.session_state.responses['bloc3'].get('q12_techniques', []),
            key=f'bloc3_q12_{tech}'
        ):
            q12_selected.append(tech)
    
    st.session_state.responses['bloc3']['q12_techniques'] = q12_selected
    st.markdown('</div>', unsafe_allow_html=True)


def bloc4_nlp():
    """Bloc 4 : NLP"""
    
    st.markdown("""
        <div class="block-card">
            <h2>🔴 Bloc 4 : NLP (Natural Language Processing)</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Q13 - Likert
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q13. Évaluez votre niveau en NLP (Natural Language Processing)</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Traitement du langage naturel, embeddings, transformers, analyse de texte</span>', unsafe_allow_html=True)
    
    q13 = st.slider(
        "",
        min_value=0,
        max_value=5,
        value=st.session_state.responses['bloc4'].get('q13_likert', 0),
        key='bloc4_q13',
        help="0 = Aucune connaissance | 5 = Expert"
    )
    st.caption("0️⃣ Aucune connaissance — 1️⃣ Débutant — 2️⃣ Notions de base — 3️⃣ Intermédiaire — 4️⃣ Avancé — 5️⃣ Expert")
    st.session_state.responses['bloc4']['q13_likert'] = q13
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q14 - Texte libre
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q14. Décrivez vos compétences et projets en NLP</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Projets réalisés, techniques utilisées (tokenization, embeddings, transformers), cas d\'usage</span>', unsafe_allow_html=True)
    
    q14 = st.text_area(
        "",
        value=st.session_state.responses['bloc4'].get('q14_text', ''),
        height=150,
        key='bloc4_q14',
        placeholder="Exemple : J'ai développé un système de classification de sentiments avec BERT fine-tuné. J'ai utilisé SBERT pour calculer la similarité sémantique entre documents..."
    )
    st.session_state.responses['bloc4']['q14_text'] = q14
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q15 - Choix multiple (outils)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q15. Quels outils et bibliothèques NLP utilisez-vous ?</span>', unsafe_allow_html=True)
    
    q15 = st.multiselect(
        "",
        options=[
            "NLTK",
            "spaCy",
            "Transformers (Hugging Face)",
            "Gensim",
            "Stanford NLP",
            "TextBlob",
            "Sentence-Transformers (SBERT)",
            "fastText",
            "OpenAI API (GPT)",
            "LangChain",
            "Aucun"
        ],
        default=st.session_state.responses['bloc4'].get('q15_tools', []),
        key='bloc4_q15'
    )
    st.session_state.responses['bloc4']['q15_tools'] = q15
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q16 - Cases à cocher (compétences NLP)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q16. Quelles compétences NLP possédez-vous ?</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Sélectionnez toutes celles que vous maîtrisez</span>', unsafe_allow_html=True)
    
    competences_nlp = [
        "Tokenization",
        "Lemmatization / Stemming",
        "Stopwords removal",
        "Part-of-Speech tagging",
        "Named Entity Recognition (NER)",
        "TF-IDF",
        "Word embeddings (Word2Vec, GloVe)",
        "BERT / Transformers",
        "SBERT (Sentence-BERT)",
        "Similarité cosinus",
        "Sentiment analysis",
        "Text classification",
        "Question answering",
        "Text generation",
        "Chatbots / Systèmes conversationnels",
        "Résumé automatique de texte",
        "Traduction automatique",
        "Topic modeling",
        "Prompt engineering",
        "Aucune"
    ]
    
    q16_selected = []
    for comp in competences_nlp:
        if st.checkbox(
            comp,
            value=comp in st.session_state.responses['bloc4'].get('q16_competences', []),
            key=f'bloc4_q16_{comp}'
        ):
            q16_selected.append(comp)
    
    st.session_state.responses['bloc4']['q16_competences'] = q16_selected
    st.markdown('</div>', unsafe_allow_html=True)


def bloc5_stats_maths():
    """Bloc 5 : Statistiques & Mathématiques"""
    
    st.markdown("""
        <div class="block-card">
            <h2>🟣 Bloc 5 : Statistiques & Mathématiques</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Q17 - Likert
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q17. Évaluez votre niveau en statistiques et mathématiques</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Tests d\'hypothèses, probabilités, algèbre linéaire, optimisation</span>', unsafe_allow_html=True)
    
    q17 = st.slider(
        "",
        min_value=0,
        max_value=5,
        value=st.session_state.responses['bloc5'].get('q17_likert', 0),
        key='bloc5_q17',
        help="0 = Aucune connaissance | 5 = Expert"
    )
    st.caption("0️⃣ Aucune connaissance — 1️⃣ Débutant — 2️⃣ Notions de base — 3️⃣ Intermédiaire — 4️⃣ Avancé — 5️⃣ Expert")
    st.session_state.responses['bloc5']['q17_likert'] = q17
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q18 - Texte libre
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q18. Décrivez vos compétences en statistiques et mathématiques appliquées</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Tests d\'hypothèses, inférence, optimisation, algèbre linéaire - contexte d\'utilisation</span>', unsafe_allow_html=True)
    
    q18 = st.text_area(
        "",
        value=st.session_state.responses['bloc5'].get('q18_text', ''),
        height=150,
        key='bloc5_q18',
        placeholder="Exemple : J'ai appliqué des tests t-student et ANOVA pour valider des hypothèses business. J'utilise l'algèbre linéaire pour comprendre PCA et SVD..."
    )
    st.session_state.responses['bloc5']['q18_text'] = q18
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q19 - Choix multiple (outils)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q19. Quels outils statistiques et mathématiques utilisez-vous ?</span>', unsafe_allow_html=True)
    
    q19 = st.multiselect(
        "",
        options=[
            "NumPy",
            "SciPy",
            "Statsmodels",
            "R / RStudio",
            "MATLAB",
            "Jupyter Notebooks",
            "Excel (analyses statistiques)",
            "SPSS",
            "Aucun"
        ],
        default=st.session_state.responses['bloc5'].get('q19_tools', []),
        key='bloc5_q19'
    )
    st.session_state.responses['bloc5']['q19_tools'] = q19
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Q20 - Cases à cocher (domaines)
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="question-label">Q20. Quels domaines statistiques et mathématiques maîtrisez-vous ?</span>', unsafe_allow_html=True)
    st.markdown('<span class="question-subtitle">Sélectionnez tous ceux que vous connaissez</span>', unsafe_allow_html=True)
    
    domaines_stats = [
        "Statistiques descriptives (moyenne, médiane, écart-type)",
        "Distributions de probabilités (normale, binomiale, Poisson)",
        "Tests d'hypothèses (t-test, chi-carré, ANOVA)",
        "Corrélation et régression",
        "Intervalles de confiance",
        "Tests non-paramétriques",
        "Algèbre linéaire (matrices, vecteurs propres)",
        "Calcul différentiel et optimisation",
        "Gradient descent",
        "Séries temporelles (ARIMA, prévisions)",
        "Statistiques bayésiennes",
        "Théorème de Bayes",
        "Monte Carlo / Simulations",
        "Analyse multivariée",
        "Bootstrap / Resampling",
        "Aucun"
    ]
    
    q20_selected = []
    for dom in domaines_stats:
        if st.checkbox(
            dom,
            value=dom in st.session_state.responses['bloc5'].get('q20_domaines', []),
            key=f'bloc5_q20_{dom}'
        ):
            q20_selected.append(dom)
    
    st.session_state.responses['bloc5']['q20_domaines'] = q20_selected
    st.markdown('</div>', unsafe_allow_html=True)


def validate_block_responses(block_num):
    """Valider les réponses d'un bloc avant de passer au suivant"""
    block_key = f'bloc{block_num}'
    responses = st.session_state.responses[block_key]
    
    # Vérifier que les questions obligatoires sont remplies
    if f'q{block_num*4-3}_likert' not in responses:
        return False, "Veuillez répondre à la question d'évaluation (Likert)"
    
    text_key = f'q{block_num*4-2}_text'
    if text_key not in responses or not responses[text_key].strip():
        return False, "Veuillez décrire vos compétences dans la zone de texte libre"
    
    if len(responses[text_key].strip().split()) < 10:
        return False, "Votre description doit contenir au moins 10 mots pour une analyse sémantique pertinente"
    
    return True, ""


def save_responses_to_file():
    """Sauvegarder les réponses dans un fichier JSON"""
    import os
    
    # Créer le dossier responses s'il n'existe pas
    os.makedirs('responses', exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"responses/responses_{timestamp}.json"
    
    data = {
        'timestamp': timestamp,
        'responses': st.session_state.responses
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename


def main():
    """Fonction principale"""
    
    init_session_state()
    
    # Header principal
    st.markdown("""
        <div class="main-header">
            <h1>🎓 AISCA - Évaluation des Compétences Data</h1>
            <p>Agent Intelligent Sémantique et Génératif pour la Cartographie des Compétences</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Si questionnaire terminé
    if st.session_state.questionnaire_completed:
        st.markdown("""
            <div class="success-container">
                <h2>✅ Questionnaire Terminé !</h2>
                <p>Merci d'avoir complété l'évaluation de vos compétences.</p>
                <p>🚀 Passez à l'étape suivante : Analyse sémantique et recommandation de métiers</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Recommencer le questionnaire"):
            st.session_state.responses = {
                'bloc1': {},
                'bloc2': {},
                'bloc3': {},
                'bloc4': {},
                'bloc5': {}
            }
            st.session_state.current_block = 1
            st.session_state.questionnaire_completed = False
            st.rerun()
        
        return
    
    # Afficher la progression
    display_progress()
    
    # Info box
    st.markdown("""
        <div class="info-box">
            <p>💡 <strong>Conseil :</strong> Soyez précis dans vos réponses textuelles. Plus vous détaillez vos expériences et projets, 
            plus l'analyse sémantique sera pertinente pour recommander les métiers qui vous correspondent.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Afficher le bloc actuel
    current_block = st.session_state.current_block
    
    if current_block == 1:
        bloc1_data_analysis()
    elif current_block == 2:
        bloc2_ml_supervise()
    elif current_block == 3:
        bloc3_ml_non_supervise()
    elif current_block == 4:
        bloc4_nlp()
    elif current_block == 5:
        bloc5_stats_maths()
    
    # Boutons de navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_block > 1:
            if st.button("⬅️ Bloc Précédent", use_container_width=True):
                st.session_state.current_block -= 1
                st.rerun()
    
    with col3:
        if current_block < 5:
            if st.button("Bloc Suivant ➡️", use_container_width=True, type="primary"):
                # Valider les réponses
                is_valid, error_msg = validate_block_responses(current_block)
                if is_valid:
                    st.session_state.current_block += 1
                    st.rerun()
                else:
                    st.error(f"❌ {error_msg}")
        else:
            if st.button("✅ Terminer le Questionnaire", use_container_width=True, type="primary"):
                # Valider le dernier bloc
                is_valid, error_msg = validate_block_responses(current_block)
                if is_valid:
                    # Sauvegarder les réponses
                    filename = save_responses_to_file()
                    st.session_state.questionnaire_completed = True
                    st.success(f"✅ Réponses sauvegardées dans {filename}")
                    st.rerun()
                else:
                    st.error(f"❌ {error_msg}")
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #718096; font-size: 0.9rem;'>
            <p>AISCA - Projet Master Expert en Ingénierie de Données | EFREI 2025-2026</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()