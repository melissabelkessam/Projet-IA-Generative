"""
Moteur d'analyse sémantique SBERT
Étape 3 : Correspondance sémantique (Semantic Matching)
Version améliorée : Utilise textes libres + tâches + outils
"""

import pandas as pd
import json
import os
from sentence_transformers import SentenceTransformer, util
import numpy as np

# =========================
# Configuration
# =========================
COMPETENCIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "competencies.csv")
USER_RESPONSES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_responses.json")
SBERT_MODEL = "all-MiniLM-L6-v2"

# =========================
# Fonction 1 : Charger et concaténer les compétences par bloc
# =========================
def load_and_concatenate_blocks():
    """
    Charge le référentiel de compétences et concatène toutes les compétences
    de chaque bloc en une seule grande chaîne de texte.
    
    Retourne un dictionnaire : {BlockID: texte_concaténé}
    """
    print("📂 Chargement du référentiel de compétences...")
    df = pd.read_csv(COMPETENCIES_PATH)
    
    blocks_text = {}
    
    # Regrouper par BlockID
    for block_id in sorted(df['BlockID'].unique()):
        # Prendre toutes les compétences du bloc
        competencies = df[df['BlockID'] == block_id]['Competency'].tolist()
        
        # Concaténer toutes les compétences en une seule phrase
        blocks_text[block_id] = ' '.join(competencies)
        
        block_name = df[df['BlockID'] == block_id]['BlockName'].iloc[0]
        print(f"   ✅ Bloc {block_id} ({block_name}) : {len(competencies)} compétences")
    
    return blocks_text

# =========================
# Fonction 2 : Charger les réponses utilisateur (VERSION AMÉLIORÉE)
# =========================
def load_user_responses():
    """
    Charge les réponses utilisateur depuis le JSON.
    Extrait :
    - Les textes libres (_text)
    - Les tâches maîtrisées (_tasks)
    - Les outils maîtrisés (_tools)
    
    Retourne un texte enrichi combinant toutes ces informations.
    """
    print("\n📂 Chargement des réponses utilisateur...")
    
    with open(USER_RESPONSES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prendre la dernière réponse soumise
    if isinstance(data, list):
        user_data = data[-1]  # Dernière soumission
    else:
        user_data = data
    
    responses = user_data.get('responses', {})
    
    # Listes pour stocker les différents types de réponses
    user_texts = []
    user_tasks = []
    user_tools = []
    
    # Parcourir toutes les réponses
    for key, value in responses.items():
        
        # 1. Textes libres
        if key.endswith('_text') and isinstance(value, str) and value.strip() != "":
            user_texts.append(value)
            print(f"   ✅ Texte trouvé : {value[:50]}...")
        
        # 2. Tâches (listes)
        elif key.endswith('_tasks') and isinstance(value, list):
            # Filtrer "Aucune de ces tâches"
            filtered_tasks = [task for task in value if task != "Aucune de ces tâches"]
            if filtered_tasks:
                user_tasks.extend(filtered_tasks)
                print(f"   🎯 Tâches : {', '.join(filtered_tasks)}")
        
        # 3. Outils (listes)
        elif key.endswith('_tools') and isinstance(value, list):
            if value:
                user_tools.extend(value)
                print(f"   🛠️ Outils : {', '.join(value)}")
    
    # Combiner tout en un seul texte enrichi
    combined_parts = []
    
    if user_texts:
        combined_parts.append(' '.join(user_texts))
    
    if user_tasks:
        combined_parts.append(' '.join(user_tasks))
    
    if user_tools:
        combined_parts.append(' '.join(user_tools))
    
    combined_user_text = ' '.join(combined_parts)
    
    print(f"\n📝 Texte enrichi total : {len(combined_user_text)} caractères")
    print(f"   - {len(user_texts)} textes libres")
    print(f"   - {len(user_tasks)} tâches")
    print(f"   - {len(user_tools)} outils")
    
    return combined_user_text

# =========================
# Fonction 3 : Calculer la similarité sémantique
# =========================
def calculate_semantic_similarity(user_text, blocks_text):
    """
    Encode le texte utilisateur et les textes des blocs avec SBERT.
    Calcule la similarité cosinus entre l'utilisateur et chaque bloc.
    
    Retourne un dictionnaire : {BlockID: score_similarité}
    """
    print("\n🤖 Chargement du modèle SBERT...")
    model = SentenceTransformer(SBERT_MODEL)
    
    print("🔄 Encodage du texte utilisateur enrichi...")
    user_embedding = model.encode(user_text, convert_to_tensor=True)
    
    print("🔄 Encodage des blocs de compétences...")
    block_scores = {}
    
    for block_id, block_text in blocks_text.items():
        # Encoder le bloc
        block_embedding = model.encode(block_text, convert_to_tensor=True)
        
        # Calculer la similarité cosinus
        similarity = util.cos_sim(user_embedding, block_embedding)
        score = float(similarity[0][0])
        
        block_scores[block_id] = round(score, 4)
        print(f"   📊 Bloc {block_id} : {score:.4f}")
    
    return block_scores

# =========================
# Fonction principale : Analyse complète
# =========================
def analyze_user_profile():
    """
    Fonction principale qui orchestre toute l'analyse sémantique.
    
    Retourne les scores de similarité pour chaque bloc.
    """
    print("=" * 60)
    print("🎯 ANALYSE SÉMANTIQUE AMÉLIORÉE - ÉTAPE 3")
    print("=" * 60)
    
    # 1. Charger et concaténer les compétences par bloc
    blocks_text = load_and_concatenate_blocks()
    
    # 2. Charger les réponses utilisateur (textes + tâches + outils)
    user_text = load_user_responses()
    
    if not user_text.strip():
        print("\n❌ ERREUR : Aucune information trouvée dans les réponses utilisateur !")
        return None
    
    # 3. Calculer la similarité sémantique
    block_scores = calculate_semantic_similarity(user_text, blocks_text)
    
    print("\n" + "=" * 60)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 60)
    
    return block_scores

# =========================
# Test du module
# =========================
if __name__ == "__main__":
    scores = analyze_user_profile()
    
    if scores:
        print("\n📊 RÉSULTATS FINAUX :")
        print("-" * 40)
        for block_id, score in scores.items():
            print(f"Bloc {block_id} : {score}")