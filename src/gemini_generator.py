"""
Générateur de contenu IA avec Google Gemini
Étape 6 : Plan de progression et biographie professionnelle
Avec système de cache automatique
"""

import google.generativeai as genai
import json
import os
import hashlib

# =========================
# Configuration
# =========================
CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gemini_cache.json")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAnKGUyBFQt9_uNd_tony1bClJsLwOScMg")

# Configuration de l'API Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# =========================
# Noms des blocs de compétences
# =========================
BLOCK_NAMES = {
    1: "Data Analysis",
    2: "Machine Learning",
    3: "NLP (Traitement du langage naturel)",
    4: "Statistics & Mathematics",
    5: "Cloud & Big Data",
    6: "Business & Data Communication",
    7: "Data Governance & Ethics",
    8: "SQL & Databases",
    9: "MLOps"
}

# =========================
# Système de Cache
# =========================
def load_cache():
    """Charge le cache depuis le fichier JSON."""
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Sauvegarde le cache dans le fichier JSON."""
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def generate_cache_key(prompt_type, data):
    """Génère une clé de cache unique."""
    data_str = f"{prompt_type}_{json.dumps(data, sort_keys=True)}"
    return hashlib.md5(data_str.encode()).hexdigest()

def get_from_cache(prompt_type, data):
    """Récupère une réponse du cache si elle existe."""
    cache = load_cache()
    cache_key = generate_cache_key(prompt_type, data)
    return cache.get(cache_key)

def save_to_cache(prompt_type, data, response):
    """Sauvegarde une réponse dans le cache."""
    cache = load_cache()
    cache_key = generate_cache_key(prompt_type, data)
    cache[cache_key] = {
        'response': response,
        'prompt_type': prompt_type,
        'timestamp': str(json.dumps(data))
    }
    save_cache(cache)

# =========================
# Fonction 1 : Analyser les forces et faiblesses
# =========================
def analyze_strengths_weaknesses(block_scores):
    """Identifie les 3 blocs les plus forts et les 3 plus faibles."""
    sorted_blocks = sorted(block_scores.items(), key=lambda x: x[1], reverse=True)
    
    strengths = [(block_id, score) for block_id, score in sorted_blocks[:3]]
    weaknesses = [(block_id, score) for block_id, score in sorted_blocks[-3:]]
    
    return strengths, weaknesses

# =========================
# Fonction 2 : Générer le plan de progression
# =========================
def generate_career_plan(recommended_jobs, block_scores, coverage_score):
    """Génère un plan de progression personnalisé."""
    
    target_job = recommended_jobs[0]
    strengths, weaknesses = analyze_strengths_weaknesses(block_scores)
    
    # Données pour le cache
    cache_data = {
        'job_title': target_job['title'],
        'job_score': target_job['score'],
        'coverage': coverage_score,
        'strengths': [(BLOCK_NAMES[bid], score) for bid, score in strengths],
        'weaknesses': [(BLOCK_NAMES[bid], score) for bid, score in weaknesses]
    }
    
    # Vérifier le cache
    print("📦 Vérification du cache...")
    cached_response = get_from_cache('career_plan', cache_data)
    
    if cached_response:
        print("✅ Réponse trouvée en cache")
        return cached_response['response']
    
    # Pas en cache, appeler l'API
    print("🌐 Appel API Gemini...")
    
    strengths_text = "\n".join([f"- {BLOCK_NAMES[bid]} : {score*100:.1f}%" for bid, score in strengths])
    weaknesses_text = "\n".join([f"- {BLOCK_NAMES[bid]} : {score*100:.1f}%" for bid, score in weaknesses])
    
    prompt = f"""Tu es un conseiller en orientation professionnelle spécialisé en Data Science.

Un candidat vise le métier de {target_job['title']} avec un score de compatibilité de {target_job['score']*100:.1f}%.

Points forts :
{strengths_text}

Points à renforcer :
{weaknesses_text}

Génère un plan de progression en 5 étapes concrètes.
Format : Markdown, en français, professionnel.
Maximum 800 mots."""
    
    try:
        response = model.generate_content(prompt)
        plan_text = response.text
        save_to_cache('career_plan', cache_data, plan_text)
        print("💾 Réponse sauvegardée")
        return plan_text
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        
        fallback_plan = f"""# 📋 Plan de Progression Personnalisé

## 🎯 Votre Objectif
**Métier visé :** {target_job['title']}  
**Compatibilité actuelle :** {target_job['score']*100:.1f}%  
**Score de couverture global :** {coverage_score*100:.1f}%

---

## 💪 Vos Points Forts

{chr(10).join([f"**{i}. {BLOCK_NAMES[bid]}** : {score*100:.1f}%" for i, (bid, score) in enumerate(strengths, 1)])}

---

## 📈 Axes d'Amélioration

{chr(10).join([f"**{i}. {BLOCK_NAMES[bid]}** : {score*100:.1f}%" for i, (bid, score) in enumerate(weaknesses, 1)])}

---

## 🗓️ Plan d'Action en 5 Étapes

### Étape 1 : Renforcer {BLOCK_NAMES[weaknesses[0][0]]}
Suivre des formations ciblées, réaliser des projets pratiques.
Durée : 2-3 mois

### Étape 2 : Renforcer {BLOCK_NAMES[weaknesses[1][0]]}
Formation spécialisée, projets hands-on.
Durée : 2-3 mois

### Étape 3 : Renforcer {BLOCK_NAMES[weaknesses[2][0]]}
Cours avancés, contribution open-source.
Durée : 2-3 mois

### Étape 4 : Portfolio
Créer un portfolio GitHub avec 5 projets.
Durée : 3-4 mois

### Étape 5 : Networking
Optimiser LinkedIn, participer à des meetups.
Durée : En continu

**Bonne chance ! 💪**
"""
        
        save_to_cache('career_plan', cache_data, fallback_plan)
        return fallback_plan

# =========================
# Fonction 3 : Générer la biographie
# =========================
def generate_professional_bio(recommended_jobs, block_scores):
    """Génère une biographie professionnelle."""
    
    target_job = recommended_jobs[0]
    strengths, _ = analyze_strengths_weaknesses(block_scores)
    
    cache_data = {
        'job_title': target_job['title'],
        'strengths': [(BLOCK_NAMES[bid], score) for bid, score in strengths]
    }
    
    print("📦 Vérification du cache...")
    cached_response = get_from_cache('professional_bio', cache_data)
    
    if cached_response:
        print("✅ Réponse trouvée en cache")
        return cached_response['response']
    
    print("🌐 Appel API Gemini...")
    
    strengths_text = ", ".join([BLOCK_NAMES[bid].lower() for bid, _ in strengths])
    
    prompt = f"""Rédige une biographie LinkedIn pour un profil {target_job['title']}.
Points forts : {strengths_text}

Consignes : 3-4 phrases, première personne, professionnel, en français.
60-80 mots."""
    
    try:
        response = model.generate_content(prompt)
        bio_text = response.text.strip()
        save_to_cache('professional_bio', cache_data, bio_text)
        print("💾 Réponse sauvegardée")
        return bio_text
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        
        strong_areas = [BLOCK_NAMES[bid].lower() for bid, _ in strengths]
        fallback_bio = f"Passionné(e) par la data science, je me spécialise dans {target_job['title'].lower()} avec une forte expertise en {strong_areas[0]}, {strong_areas[1]} et {strong_areas[2]}. Mon approche combine compétences techniques et vision business pour créer de la valeur."
        
        save_to_cache('professional_bio', cache_data, fallback_bio)
        return fallback_bio

# =========================
# Fonction principale
# =========================
def generate_ai_insights(results):
    """Fonction principale qui génère tous les contenus IA."""
    
    print("\n" + "="*60)
    print("🤖 GÉNÉRATION IA - ÉTAPE 6")
    print("="*60)
    
    block_scores = results['block_scores']
    coverage_score = results['coverage_score']
    recommended_jobs = results['recommended_jobs']
    
    print("\n📋 Génération du plan...")
    career_plan = generate_career_plan(recommended_jobs, block_scores, coverage_score)
    print("✅ Plan généré !")
    
    print("\n✍️ Génération de la bio...")
    professional_bio = generate_professional_bio(recommended_jobs, block_scores)
    print("✅ Bio générée !")
    
    print("\n" + "="*60)
    print("✅ GÉNÉRATION TERMINÉE")
    print("="*60)
    
    return {
        'career_plan': career_plan,
        'professional_bio': professional_bio
    }

# =========================
# Test du module
# =========================
if __name__ == "__main__":
    test_results = {
        'block_scores': {1: 0.85, 2: 0.78, 3: 0.40, 4: 0.72, 5: 0.68, 6: 0.55, 7: 0.45, 8: 0.70, 9: 0.50},
        'coverage_score': 0.63,
        'recommended_jobs': [
            {'title': 'Data Scientist', 'score': 0.82, 'description': 'Expert'},
            {'title': 'ML Engineer', 'score': 0.75, 'description': 'Ingénieur'},
            {'title': 'Data Analyst', 'score': 0.73, 'description': 'Analyste'}
        ]
    }
    
    insights = generate_ai_insights(test_results)
    
    print("\n📋 PLAN :")
    print(insights['career_plan'])
    
    print("\n✍️ BIO :")
    print(insights['professional_bio'])