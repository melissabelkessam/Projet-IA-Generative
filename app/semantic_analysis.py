"""
AISCA - Moteur d'Analyse Sémantique
Étapes 3 & 4 : Semantic Matching + Calcul de Score
Utilise SBERT pour analyse sémantique des compétences
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import json
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class SemanticAnalyzer:
    """
    Classe principale pour l'analyse sémantique des compétences
    Implémente SBERT pour le matching sémantique
    """
    
    def __init__(self, competencies_path='data/competencies.csv', jobs_path='data/jobs.csv'):
        """
        Initialiser l'analyseur sémantique
        
        Args:
            competencies_path: Chemin vers competencies.csv
            jobs_path: Chemin vers jobs.csv
        """
        print("🔄 Initialisation du moteur d'analyse sémantique...")
        
        # Charger le modèle SBERT multilingue
        print("📥 Chargement du modèle SBERT...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Charger les données
        print("📂 Chargement des compétences et métiers...")
        self.competencies_df = pd.read_csv(competencies_path)
        self.jobs_df = pd.read_csv(jobs_path)
        
        # Créer les embeddings des compétences (une seule fois)
        print("🧠 Création des embeddings des compétences...")
        self._create_competency_embeddings()
        
        # Variables pour stocker les résultats
        self.user_responses = None
        self.block_scores = {}
        self.detected_competencies = {}
        self.coverage_score = 0.0
        self.recommended_jobs = []
        
        print("✅ Initialisation terminée !\n")
    
    
    def _create_competency_embeddings(self):
        """
        ÉTAPE 3 : Créer les embeddings pour toutes les compétences
        Combine le nom court + description pour un meilleur matching
        """
        self.competency_texts = []
        self.competency_ids = []
        
        for _, row in self.competencies_df.iterrows():
            # Combiner nom de compétence + description pour contexte riche
            text = f"{row['Competency']} {row['Description']}"
            self.competency_texts.append(text)
            self.competency_ids.append(row['CompetencyID'])
        
        # Encoder toutes les compétences en une seule fois (efficace)
        self.competency_embeddings = self.model.encode(
            self.competency_texts,
            convert_to_tensor=True,
            show_progress_bar=True
        )
        
        print(f"✅ {len(self.competency_embeddings)} embeddings de compétences créés")
    
    
    def analyze_user_responses(self, responses: Dict):
        """
        Analyser les réponses du questionnaire utilisateur
        
        Args:
            responses: Dictionnaire des réponses par bloc
        """
        print("\n🔍 ANALYSE DES RÉPONSES UTILISATEUR")
        print("=" * 60)
        
        self.user_responses = responses
        
        # Analyser chaque bloc
        for bloc_id in range(1, 6):
            bloc_key = f'bloc{bloc_id}'
            if bloc_key in responses:
                print(f"\n📊 Analyse du Bloc {bloc_id}...")
                self._analyze_bloc(bloc_id, responses[bloc_key])
        
        # Calculer le coverage score global
        self._calculate_global_coverage_score()
        
        # Recommander les métiers
        self._recommend_jobs()
        
        print("\n✅ Analyse terminée !")
        print("=" * 60)
    
    
    def _analyze_bloc(self, bloc_id: int, bloc_responses: Dict):
        """
        ÉTAPE 3 & 4 : Analyser un bloc spécifique
        Calcule le score de similarité sémantique
        
        Args:
            bloc_id: Numéro du bloc (1-5)
            bloc_responses: Réponses pour ce bloc
        """
        # Récupérer toutes les compétences du bloc
        bloc_competencies = self.competencies_df[
            self.competencies_df['BlockID'] == bloc_id
        ]
        
        # ========================================
        # ÉTAPE 3.1 : ANALYSE SÉMANTIQUE TEXTE LIBRE
        # ========================================
        text_key = f'q{bloc_id*4-2}_text'  # Question texte libre
        user_text = bloc_responses.get(text_key, '')
        
        sbert_score = 0.0
        detected_comps = []
        
        if user_text and len(user_text.strip()) > 0:
            # Encoder le texte utilisateur
            user_embedding = self.model.encode(user_text, convert_to_tensor=True)
            
            # Calculer similarités avec toutes les compétences du bloc
            similarities = []
            for _, comp_row in bloc_competencies.iterrows():
                comp_idx = self.competency_ids.index(comp_row['CompetencyID'])
                comp_embedding = self.competency_embeddings[comp_idx]
                
                # Similarité cosinus
                similarity = util.cos_sim(user_embedding, comp_embedding).item()
                similarities.append({
                    'competency_id': comp_row['CompetencyID'],
                    'competency_name': comp_row['Competency'],
                    'similarity': similarity
                })
            
            # Filtrer les compétences avec similarité > 0.3 (seuil)
            detected_comps = [
                comp for comp in similarities 
                if comp['similarity'] > 0.3
            ]
            
            # Score SBERT = moyenne des top similarités
            if detected_comps:
                top_similarities = sorted(
                    [c['similarity'] for c in detected_comps],
                    reverse=True
                )[:10]  # Top 10 compétences
                sbert_score = np.mean(top_similarities)
            
            print(f"  📝 Texte libre analysé : {len(detected_comps)} compétences détectées")
            print(f"  🎯 Score SBERT : {sbert_score:.3f}")
        
        # ========================================
        # ANALYSE LIKERT (Auto-évaluation)
        # ========================================
        likert_key = f'q{bloc_id*4-3}_likert'
        likert_value = bloc_responses.get(likert_key, 0)
        likert_score = likert_value / 5.0  # Normaliser à [0, 1]
        
        print(f"  📊 Score Likert : {likert_score:.3f} (niveau {likert_value}/5)")
        
        # ========================================
        # ANALYSE CHOIX MULTIPLE (OUTILS)
        # ========================================
        tools_key = f'q{bloc_id*4-1}_tools'
        selected_tools = bloc_responses.get(tools_key, [])
        
        # Score tools = proportion sélectionnée (hors "Aucun")
        if selected_tools and "Aucun" not in selected_tools and "Aucune" not in selected_tools:
            tools_score = min(len(selected_tools) / 6.0, 1.0)  # Max 1.0
        else:
            tools_score = 0.0
        
        print(f"  🔧 Score Outils : {tools_score:.3f} ({len(selected_tools)} outils)")
        
        # ========================================
        # ANALYSE CASES COCHÉES (COMPÉTENCES)
        # ========================================
        checkbox_key = f'q{bloc_id*4}_competences'
        if bloc_id == 2:
            checkbox_key = f'q{bloc_id*4}_algorithmes'
        elif bloc_id == 3:
            checkbox_key = f'q{bloc_id*4}_techniques'
        elif bloc_id == 5:
            checkbox_key = f'q{bloc_id*4}_domaines'
        
        checked_items = bloc_responses.get(checkbox_key, [])
        
        if checked_items and "Aucun" not in checked_items and "Aucune" not in checked_items:
            checkbox_score = min(len(checked_items) / 10.0, 1.0)
        else:
            checkbox_score = 0.0
        
        print(f"  ☑️  Score Compétences : {checkbox_score:.3f} ({len(checked_items)} items)")
        
        # ========================================
        # ÉTAPE 4 : CALCUL DU SCORE PONDÉRÉ (4 COMPOSANTES)
        # ========================================
        weights = {
            'sbert': 0.40,      # 40% - Analyse sémantique
            'likert': 0.25,     # 25% - Auto-évaluation
            'checkbox': 0.20,   # 20% - Compétences cochées
            'tools': 0.15       # 15% - Outils sélectionnés
        }
        
        bloc_score = (
            weights['sbert'] * sbert_score +
            weights['likert'] * likert_score +
            weights['checkbox'] * checkbox_score +
            weights['tools'] * tools_score
        )
        
        print(f"  ⭐ SCORE FINAL BLOC {bloc_id} : {bloc_score:.3f}")
        
        # Stocker les résultats
        self.block_scores[f'bloc{bloc_id}'] = {
            'score': bloc_score,
            'sbert_score': sbert_score,
            'likert_score': likert_score,
            'checkbox_score': checkbox_score,
            'tools_score': tools_score,
            'detected_competencies': detected_comps
        }
        
        self.detected_competencies[f'bloc{bloc_id}'] = detected_comps
    
    
    def _calculate_global_coverage_score(self):
        """
        ÉTAPE 4 : Calculer le Coverage Score global
        Formule : moyenne pondérée des 5 blocs
        """
        print("\n" + "=" * 60)
        print("📊 CALCUL DU COVERAGE SCORE GLOBAL")
        print("=" * 60)
        
        # Poids par défaut = 1 pour tous les blocs (importance égale)
        weights = {
            'bloc1': 1.0,
            'bloc2': 1.0,
            'bloc3': 1.0,
            'bloc4': 1.0,
            'bloc5': 1.0
        }
        
        # Calcul avec formule du PDF
        numerator = sum(
            weights[bloc_key] * self.block_scores[bloc_key]['score']
            for bloc_key in self.block_scores
        )
        denominator = sum(weights.values())
        
        self.coverage_score = numerator / denominator
        
        print(f"\n✨ COVERAGE SCORE GLOBAL : {self.coverage_score:.3f}")
        print("=" * 60)
        
        # Afficher détails
        print("\n📋 Détail des scores par bloc :")
        for bloc_key in sorted(self.block_scores.keys()):
            score = self.block_scores[bloc_key]['score']
            print(f"  • {bloc_key.upper()} : {score:.3f}")
    
    
    def _recommend_jobs(self):
        """
        ÉTAPE 5 : Recommander les 3 meilleurs métiers
        Match le profil utilisateur avec les 15 métiers
        """
        print("\n" + "=" * 60)
        print("🎯 RECOMMANDATION DES MÉTIERS")
        print("=" * 60)
        
        job_scores = []
        
        for _, job_row in self.jobs_df.iterrows():
            job_id = job_row['JobID']
            job_title = job_row['JobTitle']
            required_comps = job_row['RequiredCompetencies'].split(';')
            
            # Calculer le score de match pour ce métier
            match_score = self._calculate_job_match(required_comps)
            
            job_scores.append({
                'job_id': job_id,
                'job_title': job_title,
                'match_score': match_score,
                'required_competencies': required_comps
            })
        
        # Trier par score décroissant
        job_scores.sort(key=lambda x: x['match_score'], reverse=True)
        
        # TOP 3
        self.recommended_jobs = job_scores[:3]
        
        print("\n🏆 TOP 3 MÉTIERS RECOMMANDÉS :")
        for i, job in enumerate(self.recommended_jobs, 1):
            print(f"  {i}. {job['job_title']} - Score : {job['match_score']:.1f}%")
        
        print("=" * 60)
    
    
    def _calculate_job_match(self, required_competencies: List[str]) -> float:
        """
        Calculer le score de match entre profil utilisateur et un métier
        
        Args:
            required_competencies: Liste des IDs de compétences requises
            
        Returns:
            Score de match en pourcentage (0-100)
        """
        if not required_competencies:
            return 0.0
        
        total_score = 0.0
        
        for comp_id in required_competencies:
            comp_id = comp_id.strip()
            
            # Trouver le bloc de cette compétence
            comp_row = self.competencies_df[
                self.competencies_df['CompetencyID'] == comp_id
            ]
            
            if comp_row.empty:
                continue
            
            bloc_id = comp_row.iloc[0]['BlockID']
            bloc_key = f'bloc{bloc_id}'
            
            # Score du bloc correspondant
            if bloc_key in self.block_scores:
                bloc_score = self.block_scores[bloc_key]['score']
                
                # Vérifier si compétence spécifiquement détectée
                detected_comps = self.detected_competencies.get(bloc_key, [])
                detected_ids = [c['competency_id'] for c in detected_comps]
                
                if comp_id in detected_ids:
                    # Boost si compétence spécifiquement détectée
                    comp_score = min(bloc_score * 1.2, 1.0)
                else:
                    comp_score = bloc_score
                
                total_score += comp_score
        
        # Score moyen en pourcentage
        match_percentage = (total_score / len(required_competencies)) * 100
        
        return match_percentage
    
    
    def get_results_summary(self) -> Dict:
        """
        Obtenir un résumé complet des résultats
        
        Returns:
            Dictionnaire avec tous les résultats
        """
        return {
            'coverage_score': self.coverage_score,
            'block_scores': self.block_scores,
            'detected_competencies': self.detected_competencies,
            'recommended_jobs': self.recommended_jobs
        }
    
    
    def save_results(self, filepath=None):
        """
        Sauvegarder les résultats dans un fichier JSON
        
        Args:
            filepath: Chemin du fichier de sortie (optionnel)
        """
        import os
        from datetime import datetime
        
        # Créer le dossier responses s'il n'existe pas
        os.makedirs('responses', exist_ok=True)
        
        # Nom de fichier par défaut avec timestamp
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"responses/results_{timestamp}.json"
        
        results = self.get_results_summary()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Résultats sauvegardés dans {filepath}")


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def load_responses_from_file(filepath: str) -> Dict:
    """
    Charger les réponses depuis un fichier JSON
    
    Args:
        filepath: Chemin vers le fichier de réponses
        
    Returns:
        Dictionnaire des réponses
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['responses']


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    # Test du moteur d'analyse
    print("\n" + "=" * 60)
    print("🧪 TEST DU MOTEUR D'ANALYSE SÉMANTIQUE")
    print("=" * 60)
    
    # Initialiser l'analyseur
    analyzer = SemanticAnalyzer()
    
    # Exemple de réponses (à remplacer par vraies réponses du questionnaire)
    example_responses = {
        'bloc1': {
            'q1_likert': 4,
            'q2_text': "J'ai une grande expérience en analyse de données avec Python et Pandas. J'ai créé des dashboards interactifs avec Plotly pour visualiser les KPIs de vente.",
            'q3_tools': ['Matplotlib', 'Seaborn', 'Plotly'],
            'q4_competences': ['Data cleaning (nettoyage de données)', 'Manipulation avec Pandas', 'Requêtes SQL']
        },
        'bloc2': {
            'q5_likert': 3,
            'q6_text': "J'ai développé des modèles de prédiction avec Random Forest et XGBoost. J'optimise les hyperparamètres avec GridSearch.",
            'q7_tools': ['Scikit-learn', 'XGBoost'],
            'q8_algorithmes': ['Random Forest', 'Gradient Boosting (XGBoost, LightGBM)']
        },
        'bloc3': {
            'q9_likert': 2,
            'q10_text': "J'ai utilisé K-means pour segmenter des clients et PCA pour visualiser.",
            'q11_tools': ['Scikit-learn (clustering, PCA)'],
            'q12_techniques': ['K-means clustering', 'PCA (Principal Component Analysis)']
        },
        'bloc4': {
            'q13_likert': 4,
            'q14_text': "J'ai développé un chatbot avec SBERT pour analyse sémantique. J'utilise des transformers pour la classification de texte et l'analyse de sentiments.",
            'q15_tools': ['Transformers (Hugging Face)', 'Sentence-Transformers (SBERT)'],
            'q16_competences': ['SBERT (Sentence-BERT)', 'BERT / Transformers', 'Sentiment analysis']
        },
        'bloc5': {
            'q17_likert': 3,
            'q18_text': "Je maîtrise les tests statistiques (t-test, ANOVA) et l'algèbre linéaire pour comprendre les algorithmes ML.",
            'q19_tools': ['NumPy', 'SciPy'],
            'q20_domaines': ['Tests d\'hypothèses (t-test, chi-carré, ANOVA)', 'Algèbre linéaire (matrices, vecteurs propres)']
        }
    }
    
    # Analyser les réponses
    analyzer.analyze_user_responses(example_responses)
    
    # Afficher les résultats
    results = analyzer.get_results_summary()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES RÉSULTATS")
    print("=" * 60)
    print(f"Coverage Score Global : {results['coverage_score']:.3f}")
    print(f"Métiers recommandés : {len(results['recommended_jobs'])}")
    
    print("\n✅ Test terminé !")