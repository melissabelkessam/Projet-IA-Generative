"""
AISCA - Module OpenAI avec Cache Automatique
Génération du Plan de Progression et Bio Professionnelle
VERSION OpenAI v1.0+ - SANS FALLBACK
Respect strict des consignes : Cache + 1 appel/plan + 1 appel/bio
"""

from openai import OpenAI  # ✅ NOUVELLE SYNTAXE
import json
import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

# Charger la clé API depuis .env
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY manquante ! Créez un fichier .env avec votre clé.")

# ✅ CONFIGURER CLIENT OPENAI (NOUVELLE SYNTAXE)
client = OpenAI(api_key=OPENAI_API_KEY)

# Chemin du fichier cache
CACHE_FILE = 'data/openai_cache.json'

# Modèle OpenAI à utiliser
OPENAI_MODEL = 'gpt-4o-mini'  # Plus économique et rapide


def load_cache() -> Dict:
    """Charger le cache depuis le fichier JSON"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur lecture cache : {e}")
            return {}
    return {}


def save_cache(cache: Dict):
    """Sauvegarder le cache dans le fichier JSON"""
    try:
        os.makedirs('data', exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde cache : {e}")


def generate_cache_key(request_type: str, profile_data: Dict) -> str:
    """
    Générer une clé unique pour le cache
    
    Args:
        request_type: 'progression' ou 'bio'
        profile_data: Données du profil utilisateur
        
    Returns:
        Clé unique basée sur les scores et métier
    """
    try:
        # Créer une signature unique du profil
        scores = profile_data.get('block_scores', {})
        jobs = profile_data.get('recommended_jobs', [])
        job = jobs[0].get('job_title', 'unknown') if jobs else 'unknown'
        
        # Arrondir les scores pour regrouper les profils similaires
        signature = f"{request_type}_"
        for bloc in ['bloc1', 'bloc2', 'bloc3', 'bloc4', 'bloc5']:
            score = scores.get(bloc, {}).get('score', 0)
            # Arrondir à 0.1 près pour créer des groupes
            rounded = round(score * 10) / 10
            signature += f"{bloc}_{rounded}_"
        
        signature += job.replace(' ', '_')
        
        return signature
    except Exception as e:
        print(f"⚠️ Erreur génération clé cache : {e}")
        return f"{request_type}_default"


def generate_progression_plan(analysis_results: Dict) -> str:
    """
    Générer un plan de progression personnalisé avec CACHE
    UN SEUL APPEL API par profil unique
    SANS FALLBACK - Erreur visible si OpenAI échoue
    
    Args:
        analysis_results: Résultats de l'analyse SBERT
        
    Returns:
        Plan de progression (str)
    """
    print("\n🔍 Génération du Plan de Progression avec OpenAI...")
    
    # Charger le cache
    cache = load_cache()
    
    # Générer la clé de cache
    cache_key = generate_cache_key('progression', analysis_results)
    
    # Vérifier si déjà en cache
    if cache_key in cache:
        print("✅ Plan trouvé dans le cache ! (Aucun appel API)")
        return cache[cache_key]['response']
    
    print(f"🌐 Appel API OpenAI ({OPENAI_MODEL}) - nouveau profil...")
    
    # Identifier les blocs FAIBLES (score < 0.5)
    weak_blocks = []
    block_scores = analysis_results.get('block_scores', {})
    
    for bloc_key, bloc_data in block_scores.items():
        score = bloc_data.get('score', 0)
        if score < 0.5:
            weak_blocks.append({
                'bloc': bloc_key,
                'score': score,
                'sbert_score': bloc_data.get('sbert_score', 0),
                'likert_score': bloc_data.get('likert_score', 0)
            })
    
    # Trier par score croissant (les plus faibles en premier)
    weak_blocks = sorted(weak_blocks, key=lambda x: x['score'])[:3]
    
    # Construire le prompt
    bloc_names = {
        'bloc1': 'Data Analysis & Visualization',
        'bloc2': 'Machine Learning Supervisé',
        'bloc3': 'Machine Learning Non Supervisé',
        'bloc4': 'NLP (Natural Language Processing)',
        'bloc5': 'Statistiques & Mathématiques'
    }
    
    prompt = "Tu es un expert en formation Data Science et IA.\n\n"
    prompt += "Analyse ce profil de compétences et crée un plan de progression personnalisé.\n\n"
    prompt += "**Blocs de compétences à améliorer (scores faibles) :**\n"
    
    for weak in weak_blocks:
        bloc_name = bloc_names.get(weak['bloc'], weak['bloc'])
        prompt += f"- **{bloc_name}** : Score actuel {weak['score']:.1%}\n"
    
    recommended_jobs = analysis_results.get('recommended_jobs', [])
    job_title = recommended_jobs[0].get('job_title', 'Data Analyst') if recommended_jobs else 'Data Analyst'
    
    prompt += f"\n**Métier visé :** {job_title}\n\n"
    prompt += "**Consignes :**\n"
    prompt += "1. Identifie les 2-3 compétences clés à développer en priorité\n"
    prompt += "2. Propose un plan d'apprentissage en 3 étapes concrètes\n"
    prompt += "3. Suggère des ressources spécifiques (cours, projets, outils)\n"
    prompt += "4. Durée estimée : 3-6 mois\n"
    prompt += "5. Format : concis, actionnable, professionnel\n\n"
    prompt += "Réponds en français, style professionnel."
    
    # ✅ APPEL API OPENAI (NOUVELLE SYNTAXE)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Tu es un expert en formation Data Science et IA."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    plan = response.choices[0].message.content
    
    # Sauvegarder dans le cache
    cache[cache_key] = {
        'query': prompt,
        'response': plan,
        'timestamp': datetime.now().isoformat(),
        'model_used': OPENAI_MODEL,
        'profile_summary': {
            'weak_blocks': [w['bloc'] for w in weak_blocks],
            'target_job': job_title
        }
    }
    save_cache(cache)
    
    print(f"✅ Plan généré avec {OPENAI_MODEL} et sauvegardé dans le cache")
    
    return plan


def generate_professional_bio(analysis_results: Dict) -> str:
    """
    Générer une bio professionnelle style Executive Summary avec CACHE
    UN SEUL APPEL API par profil unique
    SANS FALLBACK - Erreur visible si OpenAI échoue
    
    Args:
        analysis_results: Résultats de l'analyse SBERT
        
    Returns:
        Bio professionnelle (str)
    """
    print("\n📝 Génération de la Bio Professionnelle avec OpenAI...")
    
    # Charger le cache
    cache = load_cache()
    
    # Générer la clé de cache
    cache_key = generate_cache_key('bio', analysis_results)
    
    # Vérifier si déjà en cache
    if cache_key in cache:
        print("✅ Bio trouvée dans le cache ! (Aucun appel API)")
        return cache[cache_key]['response']
    
    print(f"🌐 Appel API OpenAI ({OPENAI_MODEL}) - nouveau profil...")
    
    # Identifier les blocs FORTS (score >= 0.6)
    strong_blocks = []
    block_scores = analysis_results.get('block_scores', {})
    
    for bloc_key, bloc_data in block_scores.items():
        score = bloc_data.get('score', 0)
        if score >= 0.6:
            strong_blocks.append({
                'bloc': bloc_key,
                'score': score
            })
    
    # Trier par score décroissant
    strong_blocks = sorted(strong_blocks, key=lambda x: x['score'], reverse=True)
    
    # Construire le prompt
    bloc_names = {
        'bloc1': 'Data Analysis & Visualization',
        'bloc2': 'Machine Learning Supervisé',
        'bloc3': 'Machine Learning Non Supervisé',
        'bloc4': 'NLP (Natural Language Processing)',
        'bloc5': 'Statistiques & Mathématiques'
    }
    
    prompt = "Tu es un expert en rédaction de profils professionnels.\n\n"
    prompt += "Crée une bio professionnelle courte et percutante (Executive Summary style).\n\n"
    prompt += "**Points forts détectés :**\n"
    
    for strong in strong_blocks[:3]:
        bloc_name = bloc_names.get(strong['bloc'], strong['bloc'])
        prompt += f"- {bloc_name} ({strong['score']:.0%})\n"
    
    recommended_jobs = analysis_results.get('recommended_jobs', [])
    if recommended_jobs:
        job_title = recommended_jobs[0].get('job_title', 'Data Analyst')
        match_score = recommended_jobs[0].get('match_score', 0)
    else:
        job_title = 'Data Analyst'
        match_score = 0
    
    prompt += f"\n**Profil métier recommandé :** {job_title}\n"
    prompt += f"**Score de compatibilité :** {match_score:.1f}%\n\n"
    prompt += "**Consignes :**\n"
    prompt += "1. Longueur : 2 paragraphes (6-8 phrases au total)\n"
    prompt += "2. Paragraphe 1 : Présentation du profil et compétences techniques maîtrisées\n"
    prompt += "3. Paragraphe 2 : Expérience, projets réalisés et objectifs professionnels\n"
    prompt += "4. Style : Professionnel, impactant, orienté résultats\n"
    prompt += "5. Mettre en avant les points forts détectés\n"
    prompt += "6. Positionner clairement pour le métier recommandé\n"
    prompt += "7. Terminer par une ouverture vers les opportunités futures\n\n"
    prompt += "Réponds en français, sans titre, 2 paragraphes bien structurés."
    
    # ✅ APPEL API OPENAI (CORRECTION ICI)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Tu es un expert en rédaction de profils professionnels."},
            {"role": "user", "content": prompt}  # ✅ SANS GUILLEMETS sur prompt
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    bio = response.choices[0].message.content
    
    # Sauvegarder dans le cache
    cache[cache_key] = {
        'query': prompt,
        'response': bio,
        'timestamp': datetime.now().isoformat(),
        'model_used': OPENAI_MODEL,
        'profile_summary': {
            'strong_blocks': [s['bloc'] for s in strong_blocks],
            'target_job': job_title
        }
    }
    save_cache(cache)
    
    print(f"✅ Bio générée avec {OPENAI_MODEL} et sauvegardée dans le cache")
    
    return bio