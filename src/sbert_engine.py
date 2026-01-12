"""
Moteur d'analyse sémantique SBERT
Étape 3 : Correspondance sémantique (Semantic Matching)
Étape 4 : Calcul du Coverage Score (Score de Couverture Global)
Étape 5 : Recommandation des 3 meilleurs métiers
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
JOBS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jobs.csv")
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
# Fonction 4 : Calculer le Coverage Score
# =========================
def calculate_coverage_score(block_scores, weights=None):
    """
    Calcule le Coverage Score global selon la formule de la prof.
    """
    
    # Si pas de poids fournis, tous les blocs ont un poids de 1
    if weights is None:
        weights = {block_id: 1.0 for block_id in block_scores.keys()}
    
    # Calcul du numérateur : somme des (poids × score)
    weighted_sum = sum(weights[block_id] * score for block_id, score in block_scores.items())
    
    # Calcul du dénominateur : somme des poids
    total_weight = sum(weights.values())
    
    # Coverage Score
    coverage_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    
    return round(coverage_score, 4)

# =========================
# Fonction 5 : Mapper les compétences aux blocs (NOUVEAU - ÉTAPE 5)
# =========================
def create_competency_to_block_mapping():
    """
    Crée un dictionnaire qui mappe chaque CompetencyID à son BlockID.
    
    Retourne : {CompetencyID: BlockID}
    Exemple : {'C001': 1, 'C002': 1, 'C101': 2, ...}
    """
    df = pd.read_csv(COMPETENCIES_PATH)
    
    mapping = {}
    for _, row in df.iterrows():
        mapping[row['CompetencyID']] = row['BlockID']
    
    return mapping

# =========================
# Fonction 6 : Calculer le score d'un métier (NOUVEAU - ÉTAPE 5)
# =========================
def calculate_job_score(required_competencies, block_scores, comp_to_block_mapping):
    """
    Calcule le score d'un métier basé sur ses compétences requises.
    
    Logique :
    - Pour chaque compétence requise, trouve son bloc
    - Prend le score du bloc correspondant
    - Fait la moyenne de tous les scores
    
    Args:
        required_competencies (list): Liste des CompetencyID requis (ex: ['C001', 'C002', 'C101'])
        block_scores (dict): Scores par bloc {BlockID: score}
        comp_to_block_mapping (dict): Mapping {CompetencyID: BlockID}
    
    Returns:
        float: Score du métier (moyenne des scores des blocs concernés)
    """
    
    scores = []
    
    for comp_id in required_competencies:
        # Trouver le bloc de cette compétence
        block_id = comp_to_block_mapping.get(comp_id)
        
        if block_id and block_id in block_scores:
            scores.append(block_scores[block_id])
    
    # Calculer la moyenne
    if scores:
        return round(sum(scores) / len(scores), 4)
    else:
        return 0.0

# =========================
# Fonction 7 : Recommander les métiers (NOUVEAU - ÉTAPE 5)
# =========================
def recommend_jobs(block_scores):
    """
    Recommande les 3 meilleurs métiers basés sur les scores de blocs.
    
    Args:
        block_scores (dict): Scores par bloc
    
    Returns:
        list: Top 3 métiers avec leurs scores
              Format : [{'job_id': 'J01', 'title': '...', 'score': 0.85, 'description': '...'}, ...]
    """
    print("\n" + "=" * 60)
    print("🎯 RECOMMANDATION DE MÉTIERS - ÉTAPE 5")
    print("=" * 60)
    
    # Charger les métiers
    print("\n📂 Chargement des métiers...")
    jobs_df = pd.read_csv(JOBS_PATH)
    
    # Créer le mapping compétence → bloc
    comp_to_block = create_competency_to_block_mapping()
    
    # Calculer le score de chaque métier
    job_scores = []
    
    for _, job in jobs_df.iterrows():
        # Extraire les compétences requises (format: "C001;C002;C011")
        required_comps = job['RequiredCompetencies'].split(';')
        
        # Calculer le score du métier
        job_score = calculate_job_score(required_comps, block_scores, comp_to_block)
        
        job_scores.append({
            'job_id': job['JobID'],
            'title': job['JobTitle'],
            'score': job_score,
            'description': job['Description']
        })
        
        print(f"   📊 {job['JobTitle']} : {job_score:.4f}")
    
    # Trier par score décroissant et prendre les 3 premiers
    top_3_jobs = sorted(job_scores, key=lambda x: x['score'], reverse=True)[:3]
    
    print("\n" + "=" * 60)
    print("✅ TOP 3 MÉTIERS RECOMMANDÉS :")
    print("=" * 60)
    for i, job in enumerate(top_3_jobs, 1):
        print(f"{i}. {job['title']} - Score: {job['score']:.4f} ({job['score']*100:.1f}%)")
    
    return top_3_jobs

# =========================
# Fonction principale : Analyse complète (MODIFIÉE)
# =========================
def analyze_user_profile():
    """
    Fonction principale qui orchestre toute l'analyse sémantique.
    
    Retourne un dictionnaire contenant :
    - 'block_scores': scores par bloc
    - 'coverage_score': score de couverture global
    - 'recommended_jobs': top 3 métiers recommandés
    """
    print("=" * 60)
    print("🎯 ANALYSE SÉMANTIQUE COMPLÈTE - ÉTAPES 3, 4 & 5")
    print("=" * 60)
    
    # 1. Charger et concaténer les compétences par bloc
    blocks_text = load_and_concatenate_blocks()
    
    # 2. Charger les réponses utilisateur (textes + tâches + outils)
    user_text = load_user_responses()
    
    if not user_text.strip():
        print("\n❌ ERREUR : Aucune information trouvée dans les réponses utilisateur !")
        return None
    
    # 3. Calculer la similarité sémantique (Étape 3)
    block_scores = calculate_semantic_similarity(user_text, blocks_text)
    
    # 4. Calculer le Coverage Score (Étape 4)
    coverage_score = calculate_coverage_score(block_scores)
    
    print("\n" + "=" * 60)
    print(f"🎯 COVERAGE SCORE GLOBAL : {coverage_score} ({coverage_score*100:.1f}%)")
    print("=" * 60)
    
    # 5. Recommander les métiers (Étape 5)
    recommended_jobs = recommend_jobs(block_scores)
    
    print("\n" + "=" * 60)
    print("✅ ANALYSE COMPLÈTE TERMINÉE")
    print("=" * 60)
    
    # Retourner les résultats
    return {
        'block_scores': block_scores,
        'coverage_score': coverage_score,
        'recommended_jobs': recommended_jobs
    }

# =========================
# Test du module
# =========================
if __name__ == "__main__":
    results = analyze_user_profile()
    
    if results:
        print("\n📊 RÉSULTATS FINAUX :")
        print("-" * 40)
        print(f"Coverage Score : {results['coverage_score']} ({results['coverage_score']*100:.1f}%)")
        print("-" * 40)
        print("\n🏆 TOP 3 MÉTIERS :")
        for i, job in enumerate(results['recommended_jobs'], 1):
            print(f"{i}. {job['title']} - {job['score']*100:.1f}%")