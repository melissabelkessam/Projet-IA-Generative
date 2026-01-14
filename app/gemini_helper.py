"""
AISCA - Module Gemini avec Cache Automatique
Génération du Plan de Progression et Bio Professionnelle
VERSION ROBUSTE avec détection automatique des modèles
"""

import google.generativeai as genai
import json
import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Charger la clé API depuis .env
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY manquante ! Créez un fichier .env avec votre clé.")

# Configurer Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Chemin du fichier cache
CACHE_FILE = 'data/gemini_cache.json'

# Variable globale pour stocker le modèle détecté
DETECTED_MODEL = None


def detect_available_model():
    """
    Détecter automatiquement le premier modèle Gemini disponible
    
    Returns:
        str: Nom du modèle disponible
    """
    global DETECTED_MODEL
    
    if DETECTED_MODEL:
        return DETECTED_MODEL
    
    print("\n🔍 Détection des modèles Gemini disponibles...")
    
    try:
        # Liste des modèles à essayer dans l'ordre de préférence
        preferred_models = [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro',
            'gemini-1.5-pro-latest',
            'gemini-pro',
            'gemini-1.0-pro'
        ]
        
        # Lister tous les modèles disponibles
        available_models = []
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                available_models.append(model_name)
        
        print(f"📋 Modèles détectés : {available_models}")
        
        # Chercher le premier modèle préféré disponible
        for preferred in preferred_models:
            if preferred in available_models:
                DETECTED_MODEL = preferred
                print(f"✅ Modèle sélectionné : {DETECTED_MODEL}")
                return DETECTED_MODEL
        
        # Si aucun modèle préféré, prendre le premier disponible
        if available_models:
            DETECTED_MODEL = available_models[0]
            print(f"⚠️ Utilisation du modèle par défaut : {DETECTED_MODEL}")
            return DETECTED_MODEL
        
        # Aucun modèle disponible
        raise ValueError("❌ Aucun modèle Gemini disponible avec cette clé API")
    
    except Exception as e:
        print(f"❌ Erreur détection modèle : {e}")
        # Fallback : essayer gemini-pro en dernier recours
        DETECTED_MODEL = 'gemini-pro'
        print(f"🔄 Tentative avec modèle par défaut : {DETECTED_MODEL}")
        return DETECTED_MODEL


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
    
    Args:
        analysis_results: Résultats de l'analyse SBERT
        
    Returns:
        Plan de progression (str)
    """
    print("\n🔍 Génération du Plan de Progression...")
    
    # Charger le cache
    cache = load_cache()
    
    # Générer la clé de cache
    cache_key = generate_cache_key('progression', analysis_results)
    
    # Vérifier si déjà en cache
    if cache_key in cache:
        print("✅ Plan trouvé dans le cache ! (Aucun appel API)")
        return cache[cache_key]['response']
    
    print("🌐 Appel API Gemini (nouveau profil)...")
    
    try:
        # Détecter le modèle disponible
        model_name = detect_available_model()
        
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
        prompt = f"""Tu es un expert en formation Data Science et IA.

Analyse ce profil de compétences et crée un plan de progression personnalisé.

**Blocs de compétences à améliorer (scores faibles) :**
"""
        
        bloc_names = {
            'bloc1': 'Data Analysis & Visualization',
            'bloc2': 'Machine Learning Supervisé',
            'bloc3': 'Machine Learning Non Supervisé',
            'bloc4': 'NLP (Natural Language Processing)',
            'bloc5': 'Statistiques & Mathématiques'
        }
        
        for weak in weak_blocks:
            bloc_name = bloc_names.get(weak['bloc'], weak['bloc'])
            prompt += f"\n- **{bloc_name}** : Score actuel {weak['score']:.1%}"
        
        recommended_jobs = analysis_results.get('recommended_jobs', [])
        job_title = recommended_jobs[0].get('job_title', 'Data Analyst') if recommended_jobs else 'Data Analyst'
        
        prompt += f"""

**Métier visé :** {job_title}

**Consignes :**
1. Identifie les 2-3 compétences clés à développer en priorité
2. Propose un plan d'apprentissage en 3 étapes concrètes
3. Suggère des ressources spécifiques (cours, projets, outils)
4. Durée estimée : 3-6 mois
5. Format : concis, actionnable, professionnel

Réponds en français, style professionnel."""
        
        # Appel API avec le modèle détecté
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        plan = response.text
        
        # Sauvegarder dans le cache
        cache[cache_key] = {
            'query': prompt,
            'response': plan,
            'timestamp': datetime.now().isoformat(),
            'model_used': model_name,
            'profile_summary': {
                'weak_blocks': [w['bloc'] for w in weak_blocks],
                'target_job': job_title
            }
        }
        save_cache(cache)
        
        print(f"✅ Plan généré avec {model_name} et sauvegardé dans le cache")
        
        return plan
    
    except Exception as e:
        print(f"❌ Erreur génération plan : {e}")
        # Retourner un plan par défaut
        return """## 📚 Plan de Progression Personnalisé

**Phase 1 : Renforcement des fondamentaux (Mois 1-2)**
- Réviser les bases de Python et analyse de données
- Pratiquer avec des datasets Kaggle
- Suivre des tutoriels sur Pandas et NumPy

**Phase 2 : Développement des compétences techniques (Mois 3-4)**
- Approfondir le Machine Learning supervisé
- Réaliser des projets pratiques
- Étudier les algorithmes avancés

**Phase 3 : Spécialisation et portfolio (Mois 5-6)**
- Se spécialiser dans le domaine ciblé
- Construire un portfolio de projets
- Participer à des compétitions Kaggle

💡 *Note: Plan généré automatiquement. Consultez un mentor pour personnalisation.*"""


def generate_professional_bio(analysis_results: Dict) -> str:
    """
    Générer une bio professionnelle style Executive Summary avec CACHE
    UN SEUL APPEL API par profil unique
    
    Args:
        analysis_results: Résultats de l'analyse SBERT
        
    Returns:
        Bio professionnelle (str)
    """
    print("\n📝 Génération de la Bio Professionnelle...")
    
    # Charger le cache
    cache = load_cache()
    
    # Générer la clé de cache
    cache_key = generate_cache_key('bio', analysis_results)
    
    # Vérifier si déjà en cache
    if cache_key in cache:
        print("✅ Bio trouvée dans le cache ! (Aucun appel API)")
        return cache[cache_key]['response']
    
    print("🌐 Appel API Gemini (nouveau profil)...")
    
    try:
        # Détecter le modèle disponible
        model_name = detect_available_model()
        
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
        
        prompt = f"""Tu es un expert en rédaction de profils professionnels.

Crée une bio professionnelle courte et percutante (Executive Summary style).

**Points forts détectés :**
"""
        
        for strong in strong_blocks[:3]:
            bloc_name = bloc_names.get(strong['bloc'], strong['bloc'])
            prompt += f"\n- {bloc_name} ({strong['score']:.0%})"
        
        recommended_jobs = analysis_results.get('recommended_jobs', [])
        if recommended_jobs:
            job_title = recommended_jobs[0].get('job_title', 'Data Analyst')
            match_score = recommended_jobs[0].get('match_score', 0)
        else:
            job_title = 'Data Analyst'
            match_score = 0
        
        prompt += f"""

**Profil métier recommandé :** {job_title}
**Score de compatibilité :** {match_score:.1f}%

**Consignes :**
1. Longueur : 2 paragraphes (6-8 phrases au total)
2. Paragraphe 1 : Présentation du profil et compétences techniques maîtrisées
3. Paragraphe 2 : Expérience, projets réalisés et objectifs professionnels
4. Style : Professionnel, impactant, orienté résultats
5. Mettre en avant les points forts détectés
6. Positionner clairement pour le métier recommandé
7. Terminer par une ouverture vers les opportunités futures

Réponds en français, sans titre, 2 paragraphes bien structurés."""
        
        # Appel API avec le modèle détecté
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        bio = response.text
        
        # Sauvegarder dans le cache
        cache[cache_key] = {
            'query': prompt,
            'response': bio,
            'timestamp': datetime.now().isoformat(),
            'model_used': model_name,
            'profile_summary': {
                'strong_blocks': [s['bloc'] for s in strong_blocks],
                'target_job': job_title
            }
        }
        save_cache(cache)
        
        print(f"✅ Bio générée avec {model_name} et sauvegardée dans le cache")
        
        return bio
    
    except Exception as e:
        print(f"❌ Erreur génération bio : {e}")
        # Retourner une bio par défaut
        coverage = analysis_results.get('coverage_score', 0)
        recommended_jobs = analysis_results.get('recommended_jobs', [])
        job_title = recommended_jobs[0].get('job_title', 'Data Analyst') if recommended_jobs else 'Data Analyst'
        
        return f"""Profil Data Science polyvalent avec un score de couverture de {coverage:.0%}. Compétences solides en analyse de données et modélisation. Orienté {job_title} avec une forte capacité d'adaptation et un potentiel de croissance élevé. Prêt à relever de nouveaux défis dans l'écosystème data."""