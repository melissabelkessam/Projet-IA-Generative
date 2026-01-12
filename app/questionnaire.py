import json
import os
from datetime import datetime
import streamlit as st

# =========================
# Config
# =========================
SAVE_PATH = "data/user_responses.json"

BLOCKS = [
    ("bloc1", "Data Analysis"),
    ("bloc2", "Machine Learning"),
    ("bloc3", "NLP"),
    ("bloc4", "Statistics & Mathematics"),
    ("bloc5", "Cloud & Big Data"),
    ("bloc6", "Business & Data Communication"),
    ("bloc7", "Data Governance & Ethics"),
    ("bloc8", "SQL & Databases"),
    ("bloc9", "MLOps"),
]

# Options (tu peux modifier)
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
st.set_page_config(page_title="AISCA - Questionnaire", layout="wide")
st.title("📋 Questionnaire Streamlit (Étape 2)")

st.markdown(
    """
**Objectif :** Collecter des réponses *numériques + textuelles* pour l’analyse sémantique (SBERT).  
⚠️ Les **questions ouvertes (texte libre)** sont **essentielles**.
"""
)

# ✅ Correction: pas de "else" après un "with"
user_id = 1
user_name = ""

with st.expander("Infos utilisateur (optionnel)"):
    user_id = st.number_input("user_id", min_value=1, value=1, step=1)
    user_name = st.text_input("Nom / pseudo", "")

st.divider()

responses = {}

# Pour vérifier qu'il y a bien un texte libre par bloc
missing_text_blocks = []

for code, label in BLOCKS:
    st.subheader(f"=== {label} ===")

    # 1) Likert
    likert_key = f"{code}_likert"
    responses[likert_key] = st.slider(
        f"1) (Likert 1–5) Évalue ton niveau global en **{label}**",
        1, 5, 3, key=likert_key
    )

    # 2) Texte libre (IMPORTANT)
    text_key = f"{code}_text"
    responses[text_key] = st.text_area(
        f"2) (Texte libre) Décris un projet / expérience lié(e) à **{label}** (contexte, outils, résultats)",
        placeholder="Ex: J’ai travaillé sur ... j’ai utilisé ... le résultat était ...",
        key=text_key
    ).strip()

    # 3) Oui / Non
    yesno_key = f"{code}_yesno"
    responses[yesno_key] = st.radio(
        "3) (Oui/Non) As-tu déjà fait un projet concret dans ce domaine ?",
        ["Oui", "Non"],
        horizontal=True,
        key=yesno_key
    )

    # 4) Choix multiple (single)
    choice_key = f"{code}_choice"
    responses[choice_key] = st.selectbox(
        "4) (Choix multiple) Sélectionne ce qui te correspond le plus :",
        MULTI_CHOICE_OPTIONS[code],
        key=choice_key
    )

    # 5) Cases à cocher (multi-select)
    checks_key = f"{code}_checks"
    responses[checks_key] = st.multiselect(
        "5) (Cases à cocher) Coche les outils / notions que tu maîtrises :",
        CHECKBOX_OPTIONS[code],
        key=checks_key
    )

    if responses[text_key] == "":
        missing_text_blocks.append(label)

    st.divider()

st.subheader("💾 Sauvegarde des réponses")

col1, col2 = st.columns([1, 1])

with col1:
    st.caption("Format enregistré dans `data/user_responses.json`")

with col2:
    if st.button("✅ Soumettre et sauvegarder"):
        if missing_text_blocks:
            st.error(
                "Tu dois remplir au moins **1 texte libre** pour chaque bloc. Manquants : "
                + ", ".join(missing_text_blocks)
            )
        else:
            payload = {
                "user_id": int(user_id),
                "user_name": user_name,
                "submitted_at": datetime.utcnow().isoformat() + "Z",
                "responses": responses,
            }
            append_to_json_array(SAVE_PATH, payload)
            st.success("Sauvegardé ✅ (data/user_responses.json)")

# st.caption("Aperçu (debug) :")
# st.json({"user_id": user_id, "user_name": user_name, "responses": responses})

