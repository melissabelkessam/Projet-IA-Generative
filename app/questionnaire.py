"""
AISCA - Questionnaire de Cartographie des Compétences
5 QUESTIONS ADAPTATIVES pour évaluer tous les blocs
Projet Master Expert en Ingénierie de Données
"""

import streamlit as st
import json
from datetime import datetime


# CSS MODERNE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
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
        font-size: 1.2rem;
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
    
    .adaptive-badge {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #1a202c;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.8rem;
    }
    
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
    
    .stTextArea textarea {
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        background-color: #ffffff !important;
        color: #1a202c !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stCheckbox > label {
        color: #2d3748 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    .stMultiSelect label {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    .stSlider label {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    .stRadio > label {
        color: #2d3748 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialiser les variables de session"""
    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'
    if 'responses' not in st.session_state:
        st.session_state.responses = {
            'q1_parcours': '',
            'q2_domaines': [],
            'q3_niveaux': {},
            'q4_outils': [],
            'q5_experience': ''
        }
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 1
    if 'questionnaire_completed' not in st.session_state:
        st.session_state.questionnaire_completed = False


def display_progress():
    """Afficher la progression"""
    progress = (st.session_state.current_question - 1) / 5
    
    st.markdown(f"""
        <div class="progress-container">
            <p class="progress-text">📊 Question {st.session_state.current_question} sur 5</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress)


def question_1():
    """Q1 - Texte libre général"""
    
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    
    st.markdown('<span class="question-label">Q1. Décrivez votre parcours et vos compétences en Data Science</span>', unsafe_allow_html=True)
    
    st.markdown('''<span class="question-subtitle">
        Parlez de votre expérience globale : projets réalisés, compétences acquises, domaines explorés 
        (analyse de données, machine learning, NLP, statistiques, cloud, etc.). Soyez précis et détaillé.
    </span>''', unsafe_allow_html=True)
    
    parcours = st.text_area(
        "",
        value=st.session_state.responses['q1_parcours'],
        height=250,
        key='q1_input',
        placeholder="""Exemple : J'ai 3 ans d'expérience en Data Science. J'ai travaillé sur plusieurs projets d'analyse de données avec Python et Pandas. 
J'ai développé des modèles de machine learning supervisé (classification, régression) avec Scikit-learn et XGBoost. 
J'ai également exploré le NLP avec BERT pour de l'analyse de sentiments. Je maîtrise SQL, la visualisation avec Plotly, 
et j'ai des bases solides en statistiques (tests d'hypothèses, régression)..."""
    )
    
    st.session_state.responses['q1_parcours'] = parcours
    
    st.markdown('</div>', unsafe_allow_html=True)


def question_2():
    """Q2 - Cases à cocher : Domaines connus"""
    
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    
    st.markdown('<span class="question-label">Q2. Sélectionnez les domaines Data Science que vous connaissez</span>', unsafe_allow_html=True)
    
    st.markdown('''<span class="question-subtitle">
        Cochez tous les domaines dans lesquels vous avez des connaissances ou de l'expérience.
    </span>''', unsafe_allow_html=True)
    
    domaines = [
        "Data Analysis & Visualization",
        "Machine Learning Supervisé",
        "Machine Learning Non Supervisé",
        "NLP (Natural Language Processing)",
        "Statistiques & Mathématiques"
    ]
    
    selected_domaines = []
    
    for domaine in domaines:
        if st.checkbox(
            domaine,
            value=domaine in st.session_state.responses['q2_domaines'],
            key=f'q2_{domaine}'
        ):
            selected_domaines.append(domaine)
    
    st.session_state.responses['q2_domaines'] = selected_domaines
    
    st.markdown('</div>', unsafe_allow_html=True)


def question_3():
    """Q3 - Likert ADAPTATIF : Niveau selon domaines cochés en Q2"""
    
    domaines_selectionnes = st.session_state.responses['q2_domaines']
    
    if not domaines_selectionnes:
        st.warning("⚠️ Veuillez d'abord sélectionner au moins un domaine à la question 2")
        return
    
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="adaptive-badge">🎯 Question Adaptative</span>', unsafe_allow_html=True)
    
    st.markdown('<span class="question-label">Q3. Évaluez votre niveau dans chaque domaine sélectionné</span>', unsafe_allow_html=True)
    
    st.markdown('''<span class="question-subtitle">
        Pour chaque domaine coché précédemment, indiquez votre niveau de maîtrise (0 = Aucune connaissance, 5 = Expert).
    </span>''', unsafe_allow_html=True)
    
    niveaux = {}
    
    for domaine in domaines_selectionnes:
        niveau = st.slider(
            f"**{domaine}**",
            min_value=0,
            max_value=5,
            value=st.session_state.responses['q3_niveaux'].get(domaine, 0),
            key=f'q3_{domaine}',
            help="0 = Aucune connaissance | 5 = Expert"
        )
        st.caption("0️⃣ Aucune — 1️⃣ Débutant — 2️⃣ Notions — 3️⃣ Intermédiaire — 4️⃣ Avancé — 5️⃣ Expert")
        niveaux[domaine] = niveau
    
    st.session_state.responses['q3_niveaux'] = niveaux
    
    st.markdown('</div>', unsafe_allow_html=True)


def question_4():
    """Q4 - Choix multiples ADAPTATIF : Outils selon domaines"""
    
    domaines_selectionnes = st.session_state.responses['q2_domaines']
    
    if not domaines_selectionnes:
        st.warning("⚠️ Veuillez d'abord sélectionner au moins un domaine à la question 2")
        return
    
    st.markdown('<div class="question-container">', unsafe_allow_html=True)
    st.markdown('<span class="adaptive-badge">🎯 Question Adaptative</span>', unsafe_allow_html=True)
    
    st.markdown('<span class="question-label">Q4. Quels outils et technologies utilisez-vous ?</span>', unsafe_allow_html=True)
    
    st.markdown('''<span class="question-subtitle">
        Sélectionnez tous les outils que vous maîtrisez dans vos domaines de compétence.
    </span>''', unsafe_allow_html=True)
    
    # Outils adaptés selon domaines sélectionnés
    outils_disponibles = []
    
    if "Data Analysis & Visualization" in domaines_selectionnes:
        outils_disponibles.extend([
            "Python (Pandas, NumPy)",
            "SQL",
            "Excel",
            "Matplotlib / Seaborn",
            "Plotly",
            "Tableau",
            "Power BI"
        ])
    
    if "Machine Learning Supervisé" in domaines_selectionnes:
        outils_disponibles.extend([
            "Scikit-learn",
            "XGBoost",
            "LightGBM",
            "TensorFlow / Keras",
            "PyTorch"
        ])
    
    if "Machine Learning Non Supervisé" in domaines_selectionnes:
        outils_disponibles.extend([
            "Scikit-learn (KMeans, PCA)",
            "UMAP",
            "t-SNE"
        ])
    
    if "NLP (Natural Language Processing)" in domaines_selectionnes:
        outils_disponibles.extend([
            "NLTK",
            "spaCy",
            "Transformers (Hugging Face)",
            "BERT / GPT",
            "Sentence-Transformers (SBERT)"
        ])
    
    if "Statistiques & Mathématiques" in domaines_selectionnes:
        outils_disponibles.extend([
            "NumPy",
            "SciPy",
            "Statsmodels",
            "R / RStudio"
        ])
    
    # Retirer les doublons
    outils_disponibles = list(set(outils_disponibles))
    outils_disponibles.sort()
    
    if outils_disponibles:
        outils = st.multiselect(
            "",
            options=outils_disponibles,
            default=st.session_state.responses['q4_outils'],
            key='q4_input'
        )
        st.session_state.responses['q4_outils'] = outils
    else:
        st.info("Aucun outil spécifique proposé. Sélectionnez d'abord des domaines en Q2.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def question_5():
    """
    Question 5 : Expérience professionnelle PAR DOMAINE
    Texte libre pour chaque domaine sélectionné en Q2
    """
    st.markdown("""
        <div class="question-container">
            <div class="question-number">Question 5/5</div>
            <h2 class="question-title">💼 Expérience Professionnelle par Domaine</h2>
            <p class="question-subtitle">
                Décrivez vos projets et expériences pour chaque domaine sélectionné précédemment.
                <br>Mentionnez les technologies utilisées, contexte, et résultats obtenus.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Récupérer les domaines sélectionnés en Q2
    selected_domains = st.session_state.responses.get('q2_domaines', [])
    
    if not selected_domains:
        st.warning("⚠️ Aucun domaine sélectionné en Question 2. Veuillez retourner à la Question 2.")
        return False
    
    st.markdown(f"""
        <div class="info-box">
            <p><strong>📋 Domaines à détailler :</strong> {len(selected_domains)} domaine(s)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialiser le dictionnaire si vide
    if 'q5_experiences' not in st.session_state.responses or not isinstance(st.session_state.responses['q5_experiences'], dict):
        st.session_state.responses['q5_experiences'] = {}
    
    # Pour chaque domaine, afficher un textarea
    all_filled = True
    
    for domain in selected_domains:
        st.markdown(f"""
            <div class="question-label">
                <span class="required">*</span> Expérience en <strong>{domain}</strong>
            </div>
        """, unsafe_allow_html=True)
        
        # Récupérer la valeur existante
        current_value = st.session_state.responses['q5_experiences'].get(domain, '')
        
        # Textarea pour ce domaine
        experience_text = st.text_area(
            f"Décrivez vos projets et expérience en {domain}",
            value=current_value,
            height=150,
            placeholder=f"Exemple : J'ai développé un système de recommandation avec Python et scikit-learn pour prédire les préférences clients. Le modèle a atteint 85% de précision...",
            key=f"q5_exp_{domain}",
            label_visibility="collapsed"
        )
        
        # Sauvegarder
        st.session_state.responses['q5_experiences'][domain] = experience_text
        
        # Vérifier si rempli (minimum 20 mots)
        word_count = len(experience_text.split())
        
        if word_count < 20:
            st.markdown(f"""
                <div class="warning-box">
                    ⚠️ Minimum 20 mots requis ({word_count}/20)
                </div>
            """, unsafe_allow_html=True)
            all_filled = False
        else:
            st.markdown(f"""
                <div class="success-box">
                    ✅ {word_count} mots
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    return all_filled



def validate_question(question_num):
    """
    Valider les réponses d'une question avant de passer à la suivante
    
    Args:
        question_num: Numéro de la question (1-5)
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if question_num == 1:
        # Vérifier que le texte a au moins 20 mots
        parcours = st.session_state.responses.get('q1_parcours', '')
        word_count = len(parcours.split())
        if word_count < 20:
            return False, f"Le texte doit contenir au moins 20 mots ({word_count}/20)."
        return True, None
    
    elif question_num == 2:
        # Vérifier qu'au moins un domaine est sélectionné
        domaines = st.session_state.responses.get('q2_domaines', [])
        if not domaines or len(domaines) == 0:
            return False, "Veuillez sélectionner au moins un domaine."
        return True, None
    
    elif question_num == 3:
        # Vérifier que tous les niveaux sont évalués
        niveaux = st.session_state.responses.get('q3_niveaux', {})
        domaines = st.session_state.responses.get('q2_domaines', [])
        
        if len(niveaux) != len(domaines):
            return False, "Veuillez évaluer votre niveau pour tous les domaines sélectionnés."
        
        return True, None
    
    elif question_num == 4:
        # Vérifier qu'au moins un outil est sélectionné
        outils = st.session_state.responses.get('q4_outils', [])
        if not outils or len(outils) == 0:
            return False, "Veuillez sélectionner au moins un outil ou technologie."
        return True, None
    
    elif question_num == 5:
        # ✅ CORRIGÉ - Vérifier que toutes les expériences sont remplies (minimum 20 mots)
        q5_experiences = st.session_state.responses.get('q5_experiences', {})
        
        if not q5_experiences:
            return False, "Veuillez décrire vos expériences pour chaque domaine."
        
        # Vérifier que chaque expérience a au moins 20 mots
        for domain, exp_text in q5_experiences.items():
            word_count = len(exp_text.split())
            if word_count < 20:
                return False, f"L'expérience en '{domain}' doit contenir au moins 20 mots ({word_count}/20)."
        
        return True, None
    
    return True, None








def save_responses():
    """Sauvegarder les réponses"""
    import os
    
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
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🎓 AISCA - Évaluation des Compétences Data</h1>
            <p>5 Questions Adaptatives pour Cartographier Votre Profil</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Si terminé
    if st.session_state.questionnaire_completed:
        st.markdown("""
            <div class="success-container">
                <h2>✅ Questionnaire Terminé !</h2>
                <p>Merci d'avoir complété l'évaluation.</p>
                <p>🚀 Passez à l'étape suivante : Analyse sémantique</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Recommencer", use_container_width=True):
            st.session_state.responses = {
                'q1_parcours': '',
                'q2_domaines': [],
                'q3_niveaux': {},
                'q4_outils': [],
                'q5_experiences': {}
            }
            st.session_state.current_question = 1
            st.session_state.questionnaire_completed = False
            st.rerun()
        
        return
    
    # Progress
    display_progress()
    
    # Info box
    st.markdown("""
        <div class="info-box">
            <p>💡 <strong>Questionnaire Adaptatif :</strong> Les questions s'adaptent automatiquement selon vos réponses 
            pour mieux évaluer votre profil Data Science.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Afficher la question actuelle
    current_q = st.session_state.current_question
    
    if current_q == 1:
        question_1()
    elif current_q == 2:
        question_2()
    elif current_q == 3:
        question_3()
    elif current_q == 4:
        question_4()
    elif current_q == 5:
        question_5()
    
    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_q > 1:
            if st.button("⬅️ Précédent", use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col3:
        if current_q < 5:
            if st.button("Suivant ➡️", use_container_width=True, type="primary"):
                is_valid, error_msg = validate_question(current_q)
                if is_valid:
                    st.session_state.current_question += 1
                    st.rerun()
                else:
                    st.error(error_msg)
        else:
            if st.button("✅ Terminer", use_container_width=True, type="primary"):
                is_valid, error_msg = validate_question(current_q)
                if is_valid:
                    filename = save_responses()
                    st.session_state.questionnaire_completed = True
                    st.success(f"✅ Réponses sauvegardées : {filename}")
                    st.rerun()
                else:
                    st.error(error_msg)
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #718096; font-size: 0.9rem;'>
            <p>AISCA - Projet Master Expert en Ingénierie de Données | EFREI 2025-2026</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()