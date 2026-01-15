"""
AISCA - Moteur d'Analyse Sémantique CORRIGÉ
VERSION FIXÉE : Score des outils calculé par bloc pertinent
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

def convert_numpy_types(obj):
    """
    Convertir récursivement les types NumPy en types Python natifs
    pour la sérialisation JSON
    """
    import numpy as np
    
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

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
        
        # Mapping domaines → BlockID
        self.domain_to_block = {
            "Data Analysis & Visualization": 1,
            "Machine Learning Supervisé": 2,
            "Machine Learning Non Supervisé": 3,
            "NLP (Natural Language Processing)": 4,
            "Statistiques & Mathématiques": 5
        }
        
        # Mapping inverse BlockID → Domaine
        self.block_to_domain = {
            1: "Data Analysis & Visualization",
            2: "Machine Learning Supervisé",
            3: "Machine Learning Non Supervisé",
            4: "NLP (Natural Language Processing)",
            5: "Statistiques & Mathématiques"
        }
        
        # ✅ NOUVEAU : MAPPING OUTILS → BLOCS PERTINENTS
        self.tools_to_blocks = {
            # Bloc 1 - Data Analysis & Visualization
            "Python (Pandas, NumPy)": [1, 2, 3, 5],  # Utilisé dans plusieurs blocs
            "SQL": [1],
            "Excel": [1],
            "Matplotlib / Seaborn": [1],
            "Plotly": [1],
            "Tableau": [1],
            "Power BI": [1],
            
            # Bloc 2 - Machine Learning Supervisé
            "Scikit-learn": [2, 3],  # Utilisé aussi en non-supervisé
            "XGBoost": [2],
            "LightGBM": [2],
            "TensorFlow / Keras": [2, 4],  # Peut être utilisé en NLP
            "PyTorch": [2, 4],
            
            # Bloc 3 - Machine Learning Non Supervisé
            "Scikit-learn (KMeans, PCA)": [3],
            "UMAP": [3],
            "t-SNE": [3],
            
            # Bloc 4 - NLP
            "NLTK": [4],
            "spaCy": [4],
            "Transformers (Hugging Face)": [4],
            "BERT / GPT": [4],
            "Sentence-Transformers (SBERT)": [4],
            
            # Bloc 5 - Statistiques & Mathématiques
            "NumPy": [1, 2, 3, 5],  # Utilisé partout
            "SciPy": [5],
            "Statsmodels": [5],
            "R / RStudio": [5]
        }
        
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
        NOUVELLE VERSION POUR 5 QUESTIONS ADAPTATIVES
        
        Args:
            responses: Dictionnaire des réponses
                {
                    'q1_parcours': str,
                    'q2_domaines': List[str],
                    'q3_niveaux': Dict[str, int],
                    'q4_outils': List[str],
                    'q5_experiences': Dict[str, str]
                }
        """
        print("\n🔍 ANALYSE DES RÉPONSES UTILISATEUR")
        print("=" * 60)
        
        self.user_responses = responses
        
        # Extraire les données des 5 questions
        q1_parcours = responses.get('q1_parcours', '')
        q2_domaines = responses.get('q2_domaines', [])
        q3_niveaux = responses.get('q3_niveaux', {})
        q4_outils = responses.get('q4_outils', [])
        q5_experiences = responses.get('q5_experiences', {})
        
        print(f"\n📝 Q1 - Parcours : {len(q1_parcours)} caractères")
        print(f"📊 Q2 - Domaines sélectionnés : {len(q2_domaines)}")
        print(f"📈 Q3 - Niveaux évalués : {len(q3_niveaux)}")
        print(f"🔧 Q4 - Outils maîtrisés : {len(q4_outils)}")
        print(f"💼 Q5 - Expériences par domaine : {len(q5_experiences)} domaine(s)")
        
        # Afficher détails Q5
        for domain, exp_text in q5_experiences.items():
            word_count = len(exp_text.split())
            print(f"    • {domain} : {word_count} mots")
        
        # Analyser le texte libre avec SBERT (Q1)
        print(f"\n{'='*60}")
        print("🧠 ANALYSE SÉMANTIQUE DU TEXTE LIBRE (Q1)")
        print(f"{'='*60}")
        
        all_similarities = self._analyze_text_sbert(q1_parcours)
        
        # Calculer les scores par bloc
        for bloc_id in range(1, 6):
            print(f"\n📊 Calcul du score Bloc {bloc_id}...")
            self._calculate_bloc_score(
                bloc_id, 
                all_similarities,
                q2_domaines,
                q3_niveaux,
                q4_outils,
                q5_experiences,
                q1_parcours  # ✅ NOUVEAU : Passer le texte Q1 pour détecter outils
            )
        
        # Calculer le coverage score global
        self._calculate_global_coverage_score()
        
        # Recommander les métiers
        self._recommend_jobs()
        
        print("\n✅ Analyse terminée !")
        print("=" * 60)
    
    
    def _analyze_text_sbert(self, user_text: str) -> List[Dict]:
        """
        Analyser le texte libre avec SBERT
        Compare le texte aux 430 compétences
        
        Args:
            user_text: Texte libre du parcours utilisateur (Q1)
            
        Returns:
            Liste des similarités pour chaque compétence
        """
        if not user_text or len(user_text.strip()) == 0:
            print("⚠️ Texte libre vide, scores SBERT = 0")
            return []
        
        # Encoder le texte utilisateur
        user_embedding = self.model.encode(user_text, convert_to_tensor=True)
        
        # Calculer similarités avec TOUTES les 430 compétences
        all_similarities = []
        
        for idx, comp_id in enumerate(self.competency_ids):
            comp_embedding = self.competency_embeddings[idx]
            
            # Similarité cosinus
            similarity = util.cos_sim(user_embedding, comp_embedding).item()
            
            # Récupérer les infos de la compétence
            comp_row = self.competencies_df[
                self.competencies_df['CompetencyID'] == comp_id
            ].iloc[0]
            
            all_similarities.append({
                'competency_id': comp_id,
                'competency_name': comp_row['Competency'],
                'block_id': comp_row['BlockID'],
                'similarity': similarity
            })
        
        # Filtrer les compétences avec similarité > 0.3
        detected = [s for s in all_similarities if s['similarity'] > 0.3]
        
        print(f"✅ {len(detected)} compétences détectées (seuil > 0.3)")
        
        return all_similarities
    
    
    def _calculate_tools_score_for_block(
        self,
        bloc_id: int,
        q4_outils: List[str],
        q1_parcours: str
    ) -> Tuple[float, int, int]:
        """
        ✅ NOUVELLE FONCTION : Calculer le score outils POUR UN BLOC SPÉCIFIQUE
        
        Args:
            bloc_id: ID du bloc (1-5)
            q4_outils: Outils sélectionnés en Q4
            q1_parcours: Texte libre Q1 pour détecter outils mentionnés
            
        Returns:
            (score, nb_outils_pertinents, nb_outils_dans_texte)
        """
        # 1. Compter outils pertinents dans Q4
        outils_pertinents_q4 = []
        for outil in q4_outils:
            blocs_outil = self.tools_to_blocks.get(outil, [])
            if bloc_id in blocs_outil:
                outils_pertinents_q4.append(outil)
        
        # 2. Détecter outils mentionnés dans le texte Q1
        outils_dans_texte = []
        texte_lower = q1_parcours.lower()
        
        # Mapping outil → mots-clés à chercher
        tool_keywords = {
            "Python (Pandas, NumPy)": ["pandas", "numpy", "python"],
            "SQL": ["sql", "mysql", "postgresql"],
            "Excel": ["excel", "sheets"],
            "Matplotlib / Seaborn": ["matplotlib", "seaborn"],
            "Plotly": ["plotly"],
            "Tableau": ["tableau"],
            "Power BI": ["power bi", "powerbi"],
            "Scikit-learn": ["scikit", "sklearn"],
            "XGBoost": ["xgboost", "xgb"],
            "LightGBM": ["lightgbm", "lgbm"],
            "TensorFlow / Keras": ["tensorflow", "keras"],
            "PyTorch": ["pytorch", "torch"],
            "Scikit-learn (KMeans, PCA)": ["kmeans", "pca", "clustering"],
            "UMAP": ["umap"],
            "t-SNE": ["tsne", "t-sne"],
            "NLTK": ["nltk"],
            "spaCy": ["spacy"],
            "Transformers (Hugging Face)": ["transformer", "hugging face", "bert", "gpt"],
            "BERT / GPT": ["bert", "gpt"],
            "Sentence-Transformers (SBERT)": ["sbert", "sentence transformer"],
            "NumPy": ["numpy", "np"],
            "SciPy": ["scipy"],
            "Statsmodels": ["statsmodels"],
            "R / RStudio": ["rstudio", " r "]
        }
        
        for outil, keywords in tool_keywords.items():
            blocs_outil = self.tools_to_blocks.get(outil, [])
            if bloc_id in blocs_outil:
                for keyword in keywords:
                    if keyword in texte_lower:
                        outils_dans_texte.append(outil)
                        break
        
        # 3. Combiner Q4 + Q1 (sans doublons)
        tous_outils_pertinents = list(set(outils_pertinents_q4 + outils_dans_texte))
        
        # 4. Définir le nombre max d'outils attendus par bloc
        max_outils_par_bloc = {
            1: 7,  # Data Viz : 7 outils possibles
            2: 5,  # ML Supervisé : 5 outils
            3: 3,  # ML Non Supervisé : 3 outils
            4: 5,  # NLP : 5 outils
            5: 4   # Stats : 4 outils
        }
        
        max_outils = max_outils_par_bloc.get(bloc_id, 5)
        
        # 5. Calculer le score (score = nb_outils / max_outils, plafonné à 1.0)
        score = min(len(tous_outils_pertinents) / max_outils, 1.0)
        
        return score, len(outils_pertinents_q4), len(outils_dans_texte)
    
    
    def _calculate_bloc_score(
        self, 
        bloc_id: int,
        all_similarities: List[Dict],
        q2_domaines: List[str],
        q3_niveaux: Dict[str, int],
        q4_outils: List[str],
        q5_experiences: Dict[str, str],
        q1_parcours: str  # ✅ NOUVEAU
    ):
        """
        Calculer le score d'un bloc spécifique
        
        Args:
            bloc_id: ID du bloc (1-5)
            all_similarities: Toutes les similarités SBERT
            q2_domaines: Domaines cochés en Q2
            q3_niveaux: Niveaux déclarés en Q3
            q4_outils: Outils sélectionnés en Q4
            q5_experiences: Expériences par domaine en Q5 (DICT)
            q1_parcours: Texte libre Q1 (pour détecter outils)
        """
        bloc_name = self.competencies_df[
            self.competencies_df['BlockID'] == bloc_id
        ]['BlockName'].iloc[0]
        
        print(f"\n  📦 Bloc {bloc_id} : {bloc_name}")
        
        # ===================================
        # 1. SCORE SBERT (40%)
        # ===================================
        bloc_similarities = [
            s for s in all_similarities 
            if s['block_id'] == bloc_id
        ]
        
        detected_comps = [s for s in bloc_similarities if s['similarity'] > 0.3]
        
        if detected_comps:
            top_sims = sorted([s['similarity'] for s in detected_comps], reverse=True)[:10]
            sbert_score = np.mean(top_sims)
        else:
            sbert_score = 0.0
        
        print(f"    🧠 Score SBERT : {sbert_score:.3f} ({len(detected_comps)} compétences)")
        
        # ===================================
        # 2. SCORE LIKERT (30%)
        # ===================================
        likert_score = 0.0
        for domaine, niveau in q3_niveaux.items():
            if self.domain_to_block.get(domaine) == bloc_id:
                likert_score = niveau / 5.0
                print(f"    📊 Score Likert : {likert_score:.3f} (niveau {niveau}/5)")
                break        
        if likert_score == 0.0:
            print(f"    📊 Score Likert : 0.000 (domaine non sélectionné)")
        
        # ===================================
        # 3. SCORE OUTILS (20%) - ✅ CORRIGÉ
        # ===================================
        tools_score, nb_q4, nb_q1 = self._calculate_tools_score_for_block(
            bloc_id, 
            q4_outils, 
            q1_parcours
        )
        
        print(f"    🔧 Score Outils : {tools_score:.3f}")
        print(f"       • Outils sélectionnés Q4 pertinents : {nb_q4}")
        print(f"       • Outils détectés dans texte Q1 : {nb_q1}")
        
        # ===================================
        # 4. BONUS EXPÉRIENCE PAR DOMAINE (10%)
        # ===================================
        experience_score = 0.0
        domain_name = self.block_to_domain.get(bloc_id)
        
        if domain_name and domain_name in q5_experiences:
            experience_text = q5_experiences[domain_name]
            word_count = len(experience_text.split())
            
            if word_count < 20:
                # Texte trop court
                experience_score = 0.0
                print(f"    💼 Score Expérience : 0.000 (texte trop court - {word_count} mots)")
            else:
                # ✅ ANALYSE SÉMANTIQUE DU TEXTE D'EXPÉRIENCE
                # Encoder le texte d'expérience
                exp_embedding = self.model.encode(experience_text, convert_to_tensor=True)
                
                # Calculer similarités avec les compétences de CE BLOC UNIQUEMENT
                bloc_similarities = []
                for idx, comp_id in enumerate(self.competency_ids):
                    comp_row = self.competencies_df[
                        self.competencies_df['CompetencyID'] == comp_id
                    ].iloc[0]
                    
                    # Filtrer uniquement les compétences du bloc actuel
                    if comp_row['BlockID'] == bloc_id:
                        comp_embedding = self.competency_embeddings[idx]
                        similarity = util.cos_sim(exp_embedding, comp_embedding).item()
                        bloc_similarities.append(similarity)
                
                # Score de qualité sémantique (moyenne des top 5 similarités)
                if bloc_similarities:
                    top_sims = sorted(bloc_similarities, reverse=True)[:5]
                    semantic_quality = np.mean(top_sims)
                else:
                    semantic_quality = 0.0
                
                # Score de longueur (max à 50 mots)
                length_score = min(word_count / 50.0, 1.0)
                
                # Score final = 70% qualité sémantique + 30% longueur
                experience_score = (0.7 * semantic_quality) + (0.3 * length_score)
                
                print(f"    💼 Score Expérience : {experience_score:.3f}")
                print(f"       • Qualité sémantique : {semantic_quality:.3f}")
                print(f"       • Longueur : {length_score:.3f} ({word_count} mots)")
        else:
            experience_score = 0.0
            print(f"    💼 Score Expérience : 0.000 (pas d'expérience déclarée)")
        
        # ===================================
        # CALCUL FINAL PONDÉRÉ
        # ===================================
        weights = {
            'sbert': 0.40,
            'likert': 0.30,
            'tools': 0.20,
            'experience': 0.10
        }
        
        bloc_score = (
            weights['sbert'] * sbert_score +
            weights['likert'] * likert_score +
            weights['tools'] * tools_score +
            weights['experience'] * experience_score
        )
        
        print(f"    ⭐ SCORE FINAL BLOC {bloc_id} : {bloc_score:.3f}")
        
        # Stocker les résultats
        self.block_scores[f'bloc{bloc_id}'] = {
            'score': bloc_score,
            'sbert_score': sbert_score,
            'likert_score': likert_score,
            'tools_score': tools_score,
            'experience_score': experience_score,
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
        
        weights = {
            'bloc1': 1.0,
            'bloc2': 1.0,
            'bloc3': 1.0,
            'bloc4': 1.0,
            'bloc5': 1.0
        }
        
        numerator = sum(
            weights[bloc_key] * self.block_scores[bloc_key]['score']
            for bloc_key in self.block_scores
        )
        denominator = sum(weights.values())
        
        self.coverage_score = numerator / denominator
        
        print(f"\n✨ COVERAGE SCORE GLOBAL : {self.coverage_score:.3f}")
        print("=" * 60)
        
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
            
            match_score = self._calculate_job_match(required_comps)
            
            job_scores.append({
                'job_id': job_id,
                'job_title': job_title,
                'match_score': match_score,
                'required_competencies': required_comps
            })
        
        job_scores.sort(key=lambda x: x['match_score'], reverse=True)
        
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
            
            comp_row = self.competencies_df[
                self.competencies_df['CompetencyID'] == comp_id
            ]
            
            if comp_row.empty:
                continue
            
            bloc_id = comp_row.iloc[0]['BlockID']
            bloc_key = f'bloc{bloc_id}'
            
            if bloc_key in self.block_scores:
                bloc_score = self.block_scores[bloc_key]['score']
                
                detected_comps = self.detected_competencies.get(bloc_key, [])
                detected_ids = [c['competency_id'] for c in detected_comps]
                
                if comp_id in detected_ids:
                    comp_score = min(bloc_score * 1.2, 1.0)
                else:
                    comp_score = bloc_score
                
                total_score += comp_score
        
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
        
        os.makedirs('responses', exist_ok=True)
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"responses/results_{timestamp}.json"
        
        results = self.get_results_summary()
        results = convert_numpy_types(results)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Résultats sauvegardés dans {filepath}")


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 TEST DU MOTEUR D'ANALYSE SÉMANTIQUE")
    print("=" * 60)
    
    analyzer = SemanticAnalyzer()
    
    example_responses = {
        'q1_parcours': "J'ai 3 ans d'expérience en Data Science. Je maîtrise Python, Pandas, et NumPy pour l'analyse de données. J'ai créé des dashboards avec Plotly et Matplotlib. En machine learning, j'utilise Scikit-learn, Random Forest, et XGBoost pour des modèles prédictifs. J'ai aussi travaillé sur du NLP avec SBERT et des transformers pour l'analyse de sentiments. Je connais les tests statistiques comme le t-test et ANOVA.",
        'q2_domaines': [
            "Data Analysis & Visualization",
            "Machine Learning Supervisé",
            "NLP (Natural Language Processing)"
        ],
        'q3_niveaux': {
            "Data Analysis & Visualization": 4,
            "Machine Learning Supervisé": 3,
            "NLP (Natural Language Processing)": 4
        },
        'q4_outils': [
            "Python (Pandas, NumPy)",
            "Matplotlib / Seaborn",
            "Plotly",
            "Scikit-learn",
            "XGBoost",
            "Transformers (Hugging Face)",
            "Sentence-Transformers (SBERT)"
        ],
        'q5_experiences': {
            "Data Analysis & Visualization": "J'ai développé plusieurs dashboards interactifs avec Plotly pour visualiser les KPIs de vente. J'ai également automatisé le nettoyage de données avec Pandas pour traiter 50k+ lignes par jour. Mes projets incluent l'analyse des tendances client et la création de rapports automatisés.",
            "Machine Learning Supervisé": "J'ai construit des modèles de prédiction de churn avec Random Forest atteignant 87% de précision. J'ai optimisé les hyperparamètres avec GridSearch et déployé les modèles en production avec Flask.",
            "NLP (Natural Language Processing)": "J'ai développé un système d'analyse de sentiments pour 10k+ avis clients utilisant SBERT et transformers. Le modèle a permis d'identifier automatiquement les thèmes récurrents et d'améliorer la satisfaction client de 15%."
        }
    }
    
    analyzer.analyze_user_responses(example_responses)
    
    results = analyzer.get_results_summary()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES RÉSULTATS")
    print("=" * 60)
    print(f"Coverage Score Global : {results['coverage_score']:.3f}")
    print(f"Métiers recommandés : {len(results['recommended_jobs'])}")
    
    analyzer.save_results()
    
    print("\n✅ Test terminé!")