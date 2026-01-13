# src/gemini_generator.py
"""
Étape 6 : Intégration IA Générative (Gemini)
- Plan de progression personnalisé (Markdown)
- Biographie professionnelle (LinkedIn/CV)

⚠️ IMPORTANT :
- Ne mets JAMAIS ta clé API dans le code.
- Utilise une variable d'environnement : GEMINI_API_KEY
"""

import os
import time
from typing import Any, Dict, List, Optional, Tuple

from google import genai


# === Config ===
API_KEY_ENV = "GEMINI_API_KEY"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")

BLOCK_NAMES_FR = {
    1: "Analyse de données",
    2: "Machine Learning",
    3: "NLP (Traitement du langage)",
    4: "Statistiques & Mathématiques",
    5: "Cloud & Big Data",
    6: "Communication Business & Data",
    7: "Gouvernance & Éthique des données",
    8: "SQL & Bases de données",
    9: "MLOps",
}


# === Utils ===
def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _normalize_scores(block_scores: Dict[Any, Any]) -> Dict[int, float]:
    """
    Accepte des scores en:
      - float [0,1]
      - int/float [0,100]
      - clés int 1..9 ou str ('1', 'bloc1', etc.)
    Retourne un dict complet 1..9 -> score [0,1]
    """
    out: Dict[int, float] = {}
    for k, v in (block_scores or {}).items():
        key_int: Optional[int] = None

        if isinstance(k, int):
            key_int = k
        elif isinstance(k, str):
            ks = k.strip().lower()
            if ks.isdigit():
                key_int = int(ks)
            elif ks.startswith("bloc") and ks[4:].isdigit():
                key_int = int(ks[4:])

        if key_int is None or key_int not in range(1, 10):
            continue

        s = _safe_float(v, 0.0)
        if s > 1.0:
            s = s / 100.0
        out[key_int] = max(0.0, min(1.0, s))

    for i in range(1, 10):
        out.setdefault(i, 0.0)
    return out


def _format_scores_md(bs: Dict[int, float]) -> str:
    return "\n".join([f"- **{BLOCK_NAMES_FR[i]}** : {bs[i]*100:.1f}%" for i in range(1, 10)])


def _get_target_job(recommended_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not recommended_jobs:
        return {"title": "Métier cible", "score": 0.0}

    job0 = recommended_jobs[0] or {}
    title = job0.get("title") or job0.get("name") or job0.get("job") or "Métier cible"
    score = _safe_float(job0.get("score", 0.0), 0.0)
    if score > 1.0:
        score = score / 100.0
    score = max(0.0, min(1.0, score))
    return {"title": title, "score": score}


def _get_top_blocks(bs: Dict[int, float], top_n: int = 3) -> List[Tuple[int, float]]:
    return sorted(bs.items(), key=lambda x: x[1], reverse=True)[:top_n]


# === Gemini client (singleton) ===
_CLIENT: Optional[genai.Client] = None


def _client() -> genai.Client:
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    api_key = os.getenv(API_KEY_ENV, "").strip()
    if not api_key:
        raise RuntimeError(
            f"Clé manquante : définis la variable d'environnement {API_KEY_ENV} "
            f"(ex: $env:{API_KEY_ENV}='...')"
        )

    _CLIENT = genai.Client(api_key=api_key)
    return _CLIENT


def _is_quota_error(err: Exception) -> bool:
    msg = str(err).lower()
    return ("429" in msg) or ("resource_exhausted" in msg) or ("quota" in msg) or ("rate" in msg)


def _generate(prompt: str, model: str = DEFAULT_MODEL, retries: int = 3) -> str:
    """
    Génère du texte avec Gemini + retry basique si quota/rate-limit.
    """
    c = _client()

    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            resp = c.models.generate_content(model=model, contents=prompt)
            return (resp.text or "").strip()
        except Exception as e:
            last_err = e
            if _is_quota_error(e) and attempt < retries:
                # backoff simple
                sleep_s = 2 * (attempt + 1)
                time.sleep(sleep_s)
                continue
            break

    # si on arrive ici => échec final
    if last_err is None:
        return "⚠️ Erreur inconnue lors de la génération."
    if _is_quota_error(last_err):
        return (
            "⚠️ Erreur Gemini : quota/rate-limit (429 RESOURCE_EXHAUSTED).\n"
            "➡️ Solutions : attendre un peu, réduire le nombre d'appels, vérifier le quota/billing du projet Google."
        )
    return f"⚠️ Erreur Gemini : {last_err}"


# === Étape 6 : fonctions demandées ===
def generate_career_plan(
    recommended_jobs: List[Dict[str, Any]],
    block_scores: Dict[Any, Any],
    coverage_score: float,
) -> str:
    bs = _normalize_scores(block_scores)

    cov = _safe_float(coverage_score, 0.0)
    if cov > 1.0:
        cov = cov / 100.0
    cov = max(0.0, min(1.0, cov))

    target = _get_target_job(recommended_jobs)
    top_blocks = _get_top_blocks(bs, 3)
    top_blocks_txt = ", ".join([BLOCK_NAMES_FR[i] for i, _ in top_blocks]) if top_blocks else "N/A"

    prompt = f"""
Tu es un conseiller en orientation professionnelle spécialisé en Data/IA.

Contexte candidat :
- Métier cible : {target['title']}
- Compatibilité actuelle : {target['score']*100:.1f}%
- Coverage score global : {cov*100:.1f}%
- Points forts (top 3 blocs) : {top_blocks_txt}

Scores par bloc :
{_format_scores_md(bs)}

Mission :
Génère un plan de progression personnalisé en 5 étapes, en Markdown.
Pour chaque étape, donne :
1) Objectif (compétence à renforcer)
2) Actions concrètes (mini-projets, exercices)
3) Ressources (cours, certifications, livres — sans liens obligatoires)
4) Durée estimée

Termine par une section : "✅ Prochains pas cette semaine" avec 3 actions ultra concrètes.
Ton : professionnel, clair, motivant. En français.
""".strip()

    return _generate(prompt)


def generate_professional_bio(
    recommended_jobs: List[Dict[str, Any]],
    block_scores: Dict[Any, Any],
    user_responses: Optional[Dict[str, Any]] = None,
) -> str:
    bs = _normalize_scores(block_scores)
    target = _get_target_job(recommended_jobs)

    # Top blocs
    top_blocks = _get_top_blocks(bs, 3)
    strengths = ", ".join([BLOCK_NAMES_FR[i] for i, _ in top_blocks]) if top_blocks else "N/A"

    # Résumé du texte user (si dispo)
    texts = []
    if isinstance(user_responses, dict):
        for i in range(1, 10):
            t = user_responses.get(f"bloc{i}_text", "")
            if isinstance(t, str) and t.strip():
                texts.append(f"- {BLOCK_NAMES_FR[i]} : {t.strip()}")
    user_texts = "\n".join(texts) if texts else "Aucune réponse texte fournie."

    prompt = f"""
Tu es un expert en rédaction de profils LinkedIn/CV.

Métier visé : {target['title']}
Forces détectées : {strengths}

Contexte (extraits des réponses utilisateur) :
{user_texts}

Contraintes :
- 1 seul paragraphe
- 3 à 5 phrases
- à la première personne ("Je")
- style LinkedIn : clair, pro, orienté impact
- mots-clés du métier visé
- ne pas inventer d'entreprises, diplômes ou expériences non mentionnés
""".strip()

    return _generate(prompt)


def generate_ai_insights(results: Dict[str, Any]) -> Dict[str, str]:
    """
    Orchestration : renvoie {'career_plan': ..., 'professional_bio': ...}
    """
    block_scores = results.get("block_scores", {})
    coverage_score = results.get("coverage_score", 0.0)
    recommended_jobs = results.get("recommended_jobs", [])
    user_responses = results.get("user_responses")

    return {
        "career_plan": generate_career_plan(recommended_jobs, block_scores, coverage_score),
        "professional_bio": generate_professional_bio(recommended_jobs, block_scores, user_responses),
    }


# === Test local ===
if __name__ == "__main__":
    test_results = {
        "block_scores": {1: 0.85, 2: 0.78, 3: 0.65, 4: 0.72, 5: 0.68, 6: 0.55, 7: 0.45, 8: 0.70, 9: 0.50},
        "coverage_score": 0.65,
        "recommended_jobs": [{"title": "Data Scientist", "score": 0.82}],
        "user_responses": {"bloc1_text": "J’ai nettoyé et analysé des données avec pandas."},
    }

    out = generate_ai_insights(test_results)
    print("\n--- PLAN ---\n")
    print(out["career_plan"])
    print("\n--- BIO ---\n")
    print(out["professional_bio"])
