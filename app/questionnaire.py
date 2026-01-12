import json
import os
from datetime import datetime
import streamlit as st

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

MULTI_CHOICE_OPTIONS = {
    "bloc1": ["Nettoyage", "EDA", "Visualisation", "Feature engineering", "Autre"],
    "bloc2": ["Régression", "Classification", "Clustering", "Recommandation", "Autre"],
    "bloc3": ["Tokenization", "Classification texte", "Embeddings", "RAG", "Autre"],
    "bloc4": ["Probabilités", "Tests", "Régression", "Optimisation", "Autre"],
    "bloc5": ["Spark", "Kafka", "Hadoop", "Databricks", "Autre"],
    "bloc6": ["Dashboard", "Storytelling", "KPI", "Présentation", "Autre"],
    "bloc7": ["RGPD", "Qualité", "Traçabilité", "Biais IA", "Autre"],
    "bloc8": ["JOIN/CTE", "Window functions", "Modélisation", "Optimisation", "Autre"],
    "bloc9": ["CI/CD", "Déploiement", "Monitoring", "MLflow", "Autre"],
}

CHECKBOX_OPTIONS = {
    "bloc1": ["Pandas", "NumPy", "Matplotlib", "Plotly"],
    "bloc2": ["scikit-learn", "XGBoost", "PyTorch", "TensorFlow"],
    "bloc3": ["spaCy", "NLTK", "Transformers", "SentenceTransformers"],
    "bloc4": ["Statsmodels", "SciPy", "SymPy", "R"],
    "bloc5": ["AWS", "GCP", "Azure", "Docker"],
    "bloc6": ["PowerBI", "Tableau", "Excel", "Slides"],
    "bloc7": ["Data Catalog", "RBAC", "Audit logs", "Anonymisation"],
    "bloc8": ["PostgreSQL", "MySQL", "SQLite", "MongoDB"],
    "bloc9": ["MLflow", "DVC", "Airflow", "FastAPI"],
}

# =========================
# CSS Styling
# =========================
# =========================
# CSS Styling
# =========================
st.markdown("""
<style>
    /* Arrière-plan général */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Titre principal - NOIR pour contraste */
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
    
    /* Bouton submit personnalisé */
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
    
    /* Fix pour les labels */
    label {
        color: #333 !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


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
# UI
# =========================
st.set_page_config(page_title="AISCA - Questionnaire", layout="wide", initial_sidebar_state="collapsed")

st.title("🎯 AISCA - Cartographie des Compétences")

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
        # 1) Likert
        likert_key = f"{code}_likert"
        responses[likert_key] = st.slider(
            f"📊 Niveau global en **{label}**",
            1, 5, 3, key=likert_key,
            help="1 = Débutant, 5 = Expert"
        )
        
        # 2) Texte libre (IMPORTANT)
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
        
        # 4) Choix multiple
        choice_key = f"{code}_choice"
        responses[choice_key] = st.selectbox(
            "🎯 Sélectionnez ce qui vous correspond le plus :",
            MULTI_CHOICE_OPTIONS[code],
            key=choice_key
        )
        
        # 5) Cases à cocher
        checks_key = f"{code}_checks"
        responses[checks_key] = st.multiselect(
            "🛠️ Outils et technologies maîtrisés :",
            CHECKBOX_OPTIONS[code],
            key=checks_key
        )
        
        if responses[text_key] == "":
            missing_text_blocks.append(label)
    
    st.markdown("---")

# Bouton de soumission
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Soumettre et sauvegarder", type="primary", use_container_width=True):
    if missing_text_blocks:
        st.error(
            f"❌ Veuillez remplir au moins **1 texte libre** pour chaque bloc.\n\n"
            f"**Blocs manquants :** {', '.join(missing_text_blocks)}"
        )
    else:
        payload = {
            "user_id": int(user_id),
            "user_name": user_name,
            "submitted_at": datetime.utcnow().isoformat() + "Z",
            "responses": responses,
        }
        append_to_json_array(SAVE_PATH, payload)
        st.success("✅ Réponses sauvegardées avec succès !")
        st.balloons()