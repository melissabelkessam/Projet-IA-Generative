import json
import os
from datetime import datetime
import streamlit as st
import sys
import pandas as pd

# Import du moteur SBERT
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.sbert_engine import analyze_user_profile

# =========================
# Config
# =========================
SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_responses.json")

BLOCKS = [
    ("bloc1", "📊 Data Analysis", "#1f77b4"),
    ("bloc2", "🤖 Machine Learning", "#ff7f0e"),
    ("bloc3", "💬 NLP", "#2ca02c"),
    ("bloc4", "📈 Statistics & Mathematics", "#d62728"),
    ("bloc5", "☁️ Cloud & Big Data", "#9467bd"),
    ("bloc6", "💼 Business & Data Communication", "#8c564b"),
    ("bloc7", "🛡️ Data Governance & Ethics", "#e377c2"),
    ("bloc8", "🗄️ SQL & Databases", "#7f7f7f"),
    ("bloc9", "⚙️ MLOps", "#bcbd22"),
]

# Tâches par bloc (choix multiples)
TASKS_OPTIONS = {
    "bloc1": ["Aucune de ces tâches", "Nettoyage de données", "Analyse exploratoire (EDA)", "Visualisation", "Feature engineering", "Autre"],
    "bloc2": ["Aucune de ces tâches", "Régression", "Classification", "Clustering", "Systèmes de recommandation", "Autre"],
    "bloc3": ["Aucune de ces tâches", "Tokenization", "Classification de texte", "Embeddings", "RAG (Retrieval-Augmented Generation)", "Autre"],
    "bloc4": ["Aucune de ces tâches", "Probabilités", "Tests statistiques", "Régression statistique", "Optimisation mathématique", "Autre"],
    "bloc5": ["Aucune de ces tâches", "Apache Spark", "Kafka", "Hadoop", "Databricks", "Autre"],
    "bloc6": ["Aucune de ces tâches", "Création de dashboards", "Data storytelling", "Définition de KPIs", "Présentations business", "Autre"],
    "bloc7": ["Aucune de ces tâches", "RGPD / Conformité", "Qualité des données", "Traçabilité", "Détection de biais IA", "Autre"],
    "bloc8": ["Aucune de ces tâches", "Requêtes complexes (JOIN, CTE)", "Window functions", "Modélisation de bases de données", "Optimisation de requêtes", "Autre"],
    "bloc9": ["Aucune de ces tâches", "CI/CD pour ML", "Déploiement de modèles", "Monitoring de modèles", "MLflow / DVC", "Autre"],
}

# Outils par bloc (cases à cocher)
TOOLS_OPTIONS = {
    "bloc1": ["Pandas", "NumPy", "Matplotlib", "Plotly"],
    "bloc2": ["scikit-learn", "XGBoost", "PyTorch", "TensorFlow"],
    "bloc3": ["spaCy", "NLTK", "Transformers", "SentenceTransformers"],
    "bloc4": ["Statsmodels", "SciPy", "SymPy", "R"],
    "bloc5": ["AWS", "GCP", "Azure", "Docker"],
    "bloc6": ["PowerBI", "Tableau", "Excel", "Google Slides"],
    "bloc7": ["Data Catalog", "RBAC", "Audit logs", "Outils d'anonymisation"],
    "bloc8": ["PostgreSQL", "MySQL", "SQLite", "MongoDB"],
    "bloc9": ["MLflow", "DVC", "Airflow", "FastAPI"],
}

# =========================
# CSS Styling
# =========================
st.markdown("""
<style>
    /* Arrière-plan général */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Titre principal */
    h1 {
        color: #1a1a1a !important;
        background-color: rgba(255, 255, 255, 0.95);
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Sous-titres des blocs */
    h2 {
        color: white !important;
        padding: 15px;
        border-radius: 10px;
        margin-top: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: bold;
    }
    
    /* Conteneur des questions */
    .stTextArea, .stSlider, .stRadio, .stSelectbox, .stMultiSelect {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Bouton submit */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 15px 40px;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Divider */
    hr {
        border: 1px solid rgba(255,255,255,0.3);
        margin: 30px 0;
    }
    
    /* Labels */
    label {
        color: #333 !important;
        font-weight: 500;
    }
    
    /* Bloc résultats */
    .results-container {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin: 20px 0;
    }
    
    .medal-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# =========================
# Helpers
# =========================
def ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def append_to_json_array(path: str, row: dict):
    ensure_file(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]
    data.append(row)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================
# UI PRINCIPALE
# =========================
st.set_page_config(page_title="AISCA - Questionnaire", layout="wide", initial_sidebar_state="collapsed")

st.title("🎯 AISCA - Cartographie des Compétences")

# Si les résultats doivent être affichés
if st.session_state.show_results and st.session_state.analysis_results:
    
    block_names = {
        1: "📊 Data Analysis",
        2: "🤖 Machine Learning",
        3: "💬 NLP",
        4: "📈 Statistics & Mathematics",
        5: "☁️ Cloud & Big Data",
        6: "💼 Business & Data Communication",
        7: "🛡️ Data Governance & Ethics",
        8: "🗄️ SQL & Databases",
        9: "⚙️ MLOps"
    }
    
    block_scores = st.session_state.analysis_results
    
    # Titre des résultats
    st.markdown("""
    <div class='results-container'>
        <h1 style='text-align: center; color: #667eea; margin-bottom: 30px;'>
            🎯 VOS RÉSULTATS D'ANALYSE SÉMANTIQUE
        </h1>
    """, unsafe_allow_html=True)
    
    # TOP 3
    st.markdown("<h2 style='color: #333; text-align: center;'>🏆 Vos 3 Domaines d'Excellence</h2>", unsafe_allow_html=True)
    
    top_3 = sorted(block_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    medals = ["🥇", "🥈", "🥉"]
    
    cols = st.columns(3)
    for i, (block_id, score) in enumerate(top_3):
        with cols[i]:
            st.markdown(f"""
            <div class='medal-card'>
                <div style='font-size: 60px;'>{medals[i]}</div>
                <h3 style='color: white; margin: 10px 0;'>{block_names[block_id]}</h3>
                <div style='font-size: 40px; font-weight: bold; margin: 15px 0;'>{score*100:.1f}%</div>
                <p style='font-size: 14px; opacity: 0.9;'>Similarité : {score:.4f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tous les scores
    st.markdown("<h2 style='color: #333; text-align: center;'>📊 Tous vos Scores par Bloc</h2>", unsafe_allow_html=True)
    
    scores_data = []
    for block_id, score in sorted(block_scores.items(), key=lambda x: x[1], reverse=True):
        scores_data.append({
            "Bloc": block_names[block_id],
            "Score": score,
            "Pourcentage": f"{score * 100:.1f}%"
        })
    
    df_scores = pd.DataFrame(scores_data)
    
    # Graphique
    st.bar_chart(df_scores.set_index("Bloc")["Score"], height=400)
    
    # Tableau
    st.dataframe(df_scores, use_container_width=True, hide_index=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton pour recommencer
    if st.button("🔄 Faire un nouveau questionnaire", type="primary", use_container_width=True):
        st.session_state.show_results = False
        st.session_state.analysis_results = None
        st.rerun()
    
    st.stop()  # Arrête l'exécution pour ne pas afficher le questionnaire

# Description du questionnaire
st.markdown("""
<div style='background-color: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
    <h3 style='color: #667eea; margin-top: 0;'>📋 Objectif du questionnaire</h3>
    <p style='color: #333; font-size: 16px;'>
        Ce questionnaire analyse vos compétences pour vous recommander les <strong>3 métiers les plus adaptés</strong> à votre profil.
    </p>
    <p style='color: #d62728; font-size: 14px;'>
        ⚠️ <strong>Important :</strong> Remplissez au moins les <strong>questions de texte libre</strong> pour une analyse sémantique précise.
    </p>
</div>
""", unsafe_allow_html=True)

user_id = 1
user_name = ""

with st.expander("👤 Informations utilisateur (optionnel)"):
    user_id = st.number_input("ID utilisateur", min_value=1, value=1, step=1)
    user_name = st.text_input("Nom / Pseudo", "")

st.markdown("---")

responses = {}
missing_text_blocks = []

for code, label, color in BLOCKS:
    st.markdown(f"<h2 style='background-color: {color};'>{label}</h2>", unsafe_allow_html=True)
    
    with st.container():
        # 1) Likert - 0 à 5
        likert_key = f"{code}_likert"
        responses[likert_key] = st.slider(
            f"📊 Niveau global en **{label}**",
            0, 5, 2, key=likert_key,
            help="0 = Aucune compétence, 1 = Débutant, 5 = Expert"
        )
        
        # 2) Texte libre (OBLIGATOIRE)
        text_key = f"{code}_text"
        responses[text_key] = st.text_area(
            f"✍️ Décrivez un projet ou une expérience liée à **{label}**",
            placeholder="Ex: J'ai travaillé sur un projet de... J'ai utilisé les outils... Le résultat était...",
            key=text_key,
            height=100
        ).strip()
        
        # 3) Oui / Non
        yesno_key = f"{code}_yesno"
        responses[yesno_key] = st.radio(
            "✅ Avez-vous déjà réalisé un projet concret dans ce domaine ?",
            ["Oui", "Non"],
            horizontal=True,
            key=yesno_key
        )
        
        # 4) Tâches - CHOIX MULTIPLES (NOUVEAU)
        tasks_key = f"{code}_tasks"
        responses[tasks_key] = st.multiselect(
            "🎯 Cochez toutes les tâches que vous maîtrisez :",
            TASKS_OPTIONS[code],
            key=tasks_key
        )
        
        # 5) Outils - Cases à cocher
        tools_key = f"{code}_tools"
        responses[tools_key] = st.multiselect(
            "🛠️ Outils et technologies maîtrisés :",
            TOOLS_OPTIONS[code],
            key=tools_key
        )
        
        if responses[text_key] == "":
            missing_text_blocks.append(label)
    
    st.markdown("---")

# Bouton de soumission
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Soumettre et Analyser", type="primary", use_container_width=True):
    if missing_text_blocks:
        st.error(
            f"❌ Veuillez remplir au moins **1 texte libre** pour chaque bloc.\n\n"
            f"**Blocs manquants :** {', '.join(missing_text_blocks)}"
        )
    else:
        # Sauvegarde
        payload = {
            "user_id": int(user_id),
            "user_name": user_name,
            "submitted_at": datetime.utcnow().isoformat() + "Z",
            "responses": responses,
        }
        append_to_json_array(SAVE_PATH, payload)
        st.success("✅ Réponses sauvegardées !")
        st.balloons()
        
        # Analyse SBERT
        with st.spinner("🤖 Analyse sémantique SBERT en cours..."):
            try:
                block_scores = analyze_user_profile()
                
                if block_scores:
                    # Stocker les résultats
                    st.session_state.analysis_results = block_scores
                    st.session_state.show_results = True
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'analyse")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
                st.exception(e)