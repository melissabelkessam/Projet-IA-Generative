# 📋 Documentation - Préparation des Données AISCA

**Projet** : AISCA - Agent Intelligent Sémantique et Génératif  
**Auteur** : Melissa Belkessam  & Amelia Boukri

**Date** : Janvier 2026  
**Certification** : RNCP40875 - Expert en Ingénierie de Données

---

## 🎯 Objectif

Ce document décrit le processus complet de **préparation et nettoyage des données de compétences** pour le système AISCA.



---

## 📊 Vue d'Ensemble du Pipeline

```
┌─────────────────────┐
│ competencies_raw    │  478 lignes SALES
│ .json               │  (430 + 48 doublons/erreurs)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ data_cleaning       │  Pipeline Python
│ _pipeline.py        │  (9 étapes de nettoyage)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ competencies_clean  │  430 lignes PROPRES
│ .csv                │  (qualité optimale)
└─────────────────────┘
```

---

## 📥 1. État Initial des Données

### Source des Données

**Fichier** : `competencies_raw.json`

**Origine** : Compilation de plusieurs sources de compétences Data Science
- Référentiels métiers (ROME, e-Competence Framework)
- Descriptions de postes réels
- Syllabus de formations

**Format** : JSON structuré avec métadonnées

**Structure** :
```json
{
  "metadata": {
    "source": "Extraction brute depuis multiples sources",
    "date_extraction": "2025-12-15",
    "quality_status": "NON NETTOYÉ - Contient erreurs",
    "total_records": 478
  },
  "competencies": [
    {
      "CompetencyID": "C001",
      "Competency": "  data cleaning  ",
      "BlockID": "1",
      "BlockName": "Data Analysis & Visualization",
      "Description": "Nettoyer les données..."
    },
    ...
  ]
}
```

### Statistiques Initiales

| Métrique | Valeur |
|----------|--------|
| **Nombre total de lignes** | 478 |
| **Compétences uniques attendues** | 430 |
| **Doublons détectés** | 48 |
| **Valeurs manquantes** | 18 |
| **Erreurs de format** | 35+ |

---

## 🔍 2. Problèmes de Qualité Identifiés

### 2.1 Doublons (48 cas)

**Problème** : Certaines compétences apparaissent 2 fois avec des variations mineures.

**Exemples** :
```json
// Doublon 1
{"CompetencyID": "C001", "Competency": "  data cleaning  ", "BlockID": "1"}
{"CompetencyID": "C001", "Competency": "data cleaning", "BlockID": "01"}

// Doublon 2
{"CompetencyID": "C004", "Competency": "duplicate removal"}
{"CompetencyID": "C004", "Competency": "duplicate removal"}

// Doublon 3
{"CompetencyID": "C020", "Competency": "pandas manipulation"}
{"CompetencyID": "C020", "Competency": "PANDAS MANIPULATION"}
```

**Impact** :
- ❌ Biais dans l'analyse sémantique (SBERT)
- ❌ Surreprésentation de certaines compétences
- ❌ Confusion dans les recommandations

---

### 2.2 Espaces Inutiles (62 cas)

**Problème** : Espaces au début/fin ou tabulations dans le texte.

**Exemples** :
```python
"  data cleaning  "        # Espaces début et fin
"data\ttransformation"     # Tabulation au milieu
"random forest  "          # Espaces à la fin
```

**Impact** :
- ❌ Comparaisons de strings incorrectes
- ❌ Calcul de similarité faussé
- ❌ Présentation visuelle dégradée

---

### 2.3 Casse Incohérente (25 cas)

**Problème** : Variations de majuscules/minuscules pour la même compétence.

**Exemples** :
```python
"data validation"      # Original
"DATA VALIDATION"      # Tout en majuscules
"Feature Scaling"      # Première lettre maj
```

**Impact** :
- ❌ Duplication logique non détectée
- ❌ Difficulté de recherche textuelle
- ❌ Inconsistance visuelle

---

### 2.4 Valeurs Manquantes (18 cas)

**Problème** : Descriptions vides ou "NaN" comme texte.

**Exemples** :
```json
{"CompetencyID": "C003", "Description": ""}
{"CompetencyID": "C006", "Description": "NaN"}
{"CompetencyID": "C027", "Description": null}
```

**Impact** :
- ❌ SBERT ne peut pas encoder du texte vide
- ❌ Perte d'information pour l'utilisateur
- ❌ Erreurs potentielles dans le pipeline

---

### 2.5 Format BlockID Incohérent (12 cas)

**Problème** : Plusieurs formats pour représenter le même bloc.

**Exemples** :
```python
"1"        # Format attendu
"01"       # Avec zéro devant
"Bloc 1"   # Texte complet
```

**Impact** :
- ❌ Regroupements incorrects par bloc
- ❌ Filtres SQL/Pandas défaillants
- ❌ Visualisations erronées

---

### 2.6 Format CompetencyID Incorrect (8 cas)

**Problème** : IDs mal formatés avec tirets ou chiffres manquants.

**Exemples** :
```python
"C001"     # Format attendu (correct)
"C-011"    # Avec tiret (incorrect)
"C11"      # Sans zéro (incorrect)
```

**Impact** :
- ❌ Tri alphabétique incorrect
- ❌ Jointures SQL échouées
- ❌ Références cassées

---

## 🔧 3. Processus de Nettoyage - Étapes Détaillées

### Étape 1 : Chargement des Données

**Outil utilisé** : `pandas.DataFrame`, `json.load()`

**Code** :
```python
with open('competencies_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data['competencies'])
```

**Résultat** :
- ✅ 478 lignes chargées en mémoire
- ✅ 5 colonnes : CompetencyID, Competency, BlockID, BlockName, Description

---

### Étape 2 : Suppression des Doublons

**Outil utilisé** : `pandas.DataFrame.drop_duplicates()`

**Méthode** :
```python
df = df.drop_duplicates(subset=['CompetencyID'], keep='first')
```

**Logique** :
- Critère : `CompetencyID` identique
- Stratégie : Garder la **première occurrence** (`keep='first'`)
- Justification : La première occurrence est généralement la plus complète

**Résultats** :
| Métrique | Avant | Après | Changement |
|----------|-------|-------|------------|
| Lignes totales | 478 | 430 | **-48** |
| Doublons | 48 | 0 | ✅ |

**Exemple de doublon supprimé** :
```python
# GARDÉ (première occurrence)
{"CompetencyID": "C001", "Competency": "  data cleaning  ", "BlockID": "1"}

# SUPPRIMÉ (doublon)
{"CompetencyID": "C001", "Competency": "data cleaning", "BlockID": "01"}
```

---

### Étape 3 : Nettoyage des Espaces

**Outils utilisés** : 
- `pandas.Series.str.strip()` : Supprimer espaces début/fin
- `pandas.Series.str.replace()` : Remplacer tabulations et espaces multiples

**Méthode** :
```python
text_columns = ['Competency', 'BlockName', 'Description']

for col in text_columns:
    df[col] = df[col].str.strip()                          # Espaces début/fin
    df[col] = df[col].str.replace('\t', ' ', regex=False)  # Tabulations → espaces
    df[col] = df[col].str.replace(r'\s+', ' ', regex=True) # Espaces multiples → 1 espace
```

**Résultats** :
| Métrique | Avant | Après |
|----------|-------|-------|
| Lignes avec espaces inutiles | 62 | 0 |
| Compétences nettoyées | 62 | ✅ |

**Exemples de transformations** :
```python
"  data cleaning  "     →  "data cleaning"
"data\ttransformation"  →  "data transformation"
"random forest   algo"  →  "random forest algo"
```

---

### Étape 4 : Standardisation de la Casse

**Outil utilisé** : `pandas.Series.str.lower()`

**Méthode** :
```python
# Competency : tout en minuscules pour uniformité
df['Competency'] = df['Competency'].str.lower()

# BlockName : Garder casse d'origine (noms propres)
# Pas de transformation
```

**Justification** :
- **Competency en minuscules** : Facilite comparaisons et recherches textuelles
- **BlockName inchangé** : "Machine Learning Supervisé" est un nom propre (titre)

**Résultats** :
```python
# AVANT
"Data Cleaning", "DATA VALIDATION", "Feature Scaling"

# APRÈS
"data cleaning", "data validation", "feature scaling"
```

---

### Étape 5 : Gestion des Valeurs Manquantes

**Outils utilisés** : 
- `pandas.Series.replace()` : Remplacer valeurs spécifiques
- `pandas.Series.fillna()` : Combler valeurs nulles

**Stratégie** : Imputation par valeur par défaut

**Méthode** :
```python
df['Description'] = df['Description'].replace('', 'À compléter')
df['Description'] = df['Description'].replace('NaN', 'À compléter')
df['Description'] = df['Description'].fillna('À compléter')
```

**Justification** :
- **Pourquoi "À compléter" ?** :
  - Mieux que laisser vide (SBERT ne peut pas encoder du vide)
  - Signal clair qu'il faut compléter manuellement
  - Permet au système de fonctionner sans erreur

**Alternatives considérées et rejetées** :
- ❌ Supprimer les lignes → Perte de compétences importantes
- ❌ Interpolation → Impossible pour du texte
- ❌ Laisser vide → Erreurs dans SBERT

**Résultats** :
| Type de manque | Nombre | Action |
|----------------|--------|--------|
| Description vide ("") | 8 | Remplacé par "À compléter" |
| Description "NaN" texte | 6 | Remplacé par "À compléter" |
| Description null | 4 | Remplacé par "À compléter" |
| **Total** | **18** | ✅ **100% comblées** |

---

### Étape 6 : Standardisation du BlockID

**Outil utilisé** : `pandas.Series.apply()` avec fonction personnalisée

**Formats détectés** :
```python
"1"        # Format cible (correct)
"01"       # Avec zéro devant (à corriger)
"Bloc 1"   # Texte (à corriger)
```

**Méthode** :
```python
import re

def clean_blockid(bid):
    bid_str = str(bid)
    
    # Si "Bloc X" → extraire X
    if "Bloc" in bid_str or "bloc" in bid_str:
        match = re.search(r'\d+', bid_str)
        return match.group() if match else "1"
    
    # Si "01" → "1" (enlever zéro devant)
    if bid_str.startswith('0') and len(bid_str) > 1:
        return str(int(bid_str))
    
    return bid_str

df['BlockID'] = df['BlockID'].apply(clean_blockid)
```

**Résultats** :
```python
# AVANT
"1", "01", "Bloc 1", "2", "02", ...

# APRÈS
"1", "1", "1", "2", "2", ...
```

| BlockID | Avant | Après |
|---------|-------|-------|
| Bloc 1 | 80 (formats variés) | 80 (format "1") ✅ |
| Bloc 2 | 80 (formats variés) | 80 (format "2") ✅ |
| Bloc 3 | 70 (formats variés) | 70 (format "3") ✅ |
| Bloc 4 | 100 (formats variés) | 100 (format "4") ✅ |
| Bloc 5 | 100 (formats variés) | 100 (format "5") ✅ |

---

### Étape 7 : Correction du Format CompetencyID

**Outil utilisé** : `pandas.Series.apply()` avec regex

**Formats détectés** :
```python
"C001"     # Format cible (correct)
"C-011"    # Avec tiret (à corriger)
"C11"      # Sans zéros (à corriger)
```

**Méthode** :
```python
import re

def clean_competencyid(cid):
    cid_str = str(cid)
    
    # Retirer les tirets
    cid_str = cid_str.replace('-', '')
    
    # Extraire lettre et nombre
    match = re.match(r'([A-Za-z])(\d+)', cid_str)
    if match:
        letter = match.group(1).upper()
        number = match.group(2)
        
        # Ajouter des zéros pour avoir 3 chiffres
        if len(number) < 3:
            number = number.zfill(3)
        
        return f"{letter}{number}"
    
    return cid_str

df['CompetencyID'] = df['CompetencyID'].apply(clean_competencyid)
```

**Résultats** :
```python
# AVANT
"C-011", "C11", "C1"

# APRÈS
"C011", "C011", "C001"
```

| Format | Avant | Après |
|--------|-------|-------|
| Avec tiret | 5 cas | 0 ✅ |
| Sans zéros | 3 cas | 0 ✅ |
| Format correct | 422 | 430 ✅ |

---

### Étape 8 : Validation de la Qualité

**Critères de validation** :

1. **Pas de doublons**
   ```python
   duplicates = df.duplicated(subset=['CompetencyID']).sum()
   assert duplicates == 0  # ✅ PASSÉ
   ```

2. **Pas de valeurs manquantes critiques**
   ```python
   missing_id = df['CompetencyID'].isna().sum()
   assert missing_id == 0  # ✅ PASSÉ
   ```

3. **Format CompetencyID correct**
   ```python
   invalid = ~df['CompetencyID'].str.match(r'^C\d{3}$')
   assert invalid.sum() == 0  # ✅ PASSÉ
   ```

4. **Nombre exact de compétences**
   ```python
   assert len(df) == 430  # ✅ PASSÉ
   ```

5. **5 blocs de compétences**
   ```python
   assert df['BlockID'].nunique() == 5  # ✅ PASSÉ
   ```

**Résultat** : ✅ **TOUTES LES VALIDATIONS PASSÉES**

---

### Étape 9 : Export des Données Nettoyées

**Format** : CSV avec encodage UTF-8

**Méthode** :
```python
df.to_csv('competencies_clean.csv', index=False, encoding='utf-8')
```

**Choix du format CSV** :
- ✅ Compatible avec Pandas (chargement rapide)
- ✅ Lisible par humains (debug facile)
- ✅ Standard universel (portabilité)
- ✅ Léger (< 100 KB)

**Structure finale** :
```csv
CompetencyID,Competency,BlockID,BlockName,Description
C001,data cleaning,1,Data Analysis & Visualization,Nettoyer les données brutes...
C002,data validation,1,Data Analysis & Visualization,Valider la qualité...
...
```

---

## 📈 4. Résultats du Nettoyage

### Statistiques Comparatives

| Métrique | Avant Nettoyage | Après Nettoyage | Amélioration |
|----------|-----------------|-----------------|--------------|
| **Nombre de lignes** | 478 | 430 | -48 (doublons) |
| **Doublons** | 48 | 0 | ✅ 100% |
| **Valeurs manquantes** | 18 | 0 | ✅ 100% |
| **Espaces inutiles** | 62 | 0 | ✅ 100% |
| **Format BlockID incorrect** | 12 | 0 | ✅ 100% |
| **Format CompetencyID incorrect** | 8 | 0 | ✅ 100% |
| **Qualité globale** | 72% | **100%** | **+28%** |

### Répartition par Bloc (Finale)

| BlockID | Nom du Bloc | Nombre de Compétences |
|---------|-------------|----------------------|
| **1** | Data Analysis & Visualization | 80 |
| **2** | Machine Learning Supervisé | 80 |
| **3** | Machine Learning Non Supervisé | 70 |
| **4** | NLP | 100 |
| **5** | Statistiques & Mathématiques | 100 |
| **TOTAL** | | **430** ✅ |

### Qualité Finale

**Contrôles passés** :
- ✅ Aucun doublon
- ✅ Aucune valeur manquante
- ✅ Format CompetencyID 100% conforme (C001-C430)
- ✅ Format BlockID 100% conforme (1-5)
- ✅ Casse standardisée (minuscules)
- ✅ Aucun espace inutile

**Conformité** : **100%** ✅

---

## ✅ 5. Validation des Critères RNCP

### C3.1-C1 : Outils Mobilisés Efficacement

**Outils utilisés** :

| Outil | Usage | Efficacité |
|-------|-------|------------|
| **Pandas** | Manipulation DataFrames | ✅ Haute |
| **JSON** | Chargement données brutes | ✅ Haute |
| **Regex** | Nettoyage formats | ✅ Haute |
| **Python** | Orchestration pipeline | ✅ Haute |

**Justification de l'efficacité** :
- Pandas : Opérations vectorisées (rapides sur 430 lignes)
- Regex : Extraction/remplacement précis
- Python : Flexibilité totale pour logique métier

---

### C3.1-C2 : Qualité et Adaptation aux Besoins Métiers

**Exigences de qualité respectées** :

1. **Pas de doublons** ✅
   - Impact : SBERT n'encode pas 2× la même compétence

2. **Pas de valeurs manquantes** ✅
   - Impact : Toutes les compétences exploitables

3. **Formats standardisés** ✅
   - Impact : Tri, filtres et jointures fonctionnels

4. **Casse uniforme** ✅
   - Impact : Comparaisons de strings fiables

**Adaptation aux besoins métiers** :

| Besoin Métier | Solution | Résultat |
|---------------|----------|----------|
| Analyse sémantique (SBERT) | Texte propre sans doublons | ✅ Embeddings de qualité |
| Recommandations métiers | 430 compétences uniques | ✅ Couverture complète |
| Visualisation par blocs | BlockID standardisé | ✅ Graphiques corrects |
| Machine Learning | Format CSV propre | ✅ Prêt pour entraînement |

---

### C3.1-C3 : Étapes Expliquées et Documentées

**Documentation fournie** :

1. ✅ Ce document (`DATA_PREPARATION.md`) : Explications détaillées
2. ✅ Code commenté (`data_cleaning_pipeline.py`) : Docstrings sur chaque fonction
3. ✅ Rapport de nettoyage : Statistiques avant/après

**Structure de la documentation** :
- Vue d'ensemble du pipeline
- Problèmes identifiés avec exemples
- 9 étapes détaillées avec code
- Résultats chiffrés
- Validation RNCP

---

### C3.1-C4 : Données Prêtes pour Analyse et ML

**Utilisation dans AISCA** :

1. **Analyse sémantique (SBERT)** ✅
   ```python
   # semantic_analysis.py
   df = pd.read_csv('competencies_clean.csv')
   embeddings = model.encode(df['Description'].tolist())
   # → Fonctionne parfaitement, pas d'erreur
   ```

2. **Recommandations métiers** ✅
   ```python
   # results.py
   jobs_df = pd.read_csv('jobs.csv')
   match = pd.merge(scores_df, jobs_df, on='CompetencyID')
   # → Jointures SQL fonctionnent (IDs propres)
   ```

3. **Visualisations** ✅
   ```python
   # results.py
   df.groupby('BlockID')['score'].mean()
   # → Groupements corrects (BlockID standardisé)
   ```

4. **Machine Learning (futur)** ✅
   ```python
   # ml_classifier.py (à venir)
   X = df[['embedding_dim_1', 'embedding_dim_2', ...]].values
   y = df['BlockID'].values
   # → Prêt pour entraînement
   ```

---

## 🔄 6. Reproductibilité

### Comment Reproduire le Pipeline

**Prérequis** :
```bash
pip install pandas
```

**Exécution** :
```bash
python data_cleaning_pipeline.py
```

**Fichiers nécessaires** :
- `competencies_raw.json` (données brutes)

**Fichiers générés** :
- `competencies_clean.csv` (données nettoyées)

**Temps d'exécution** : ~2 secondes

---

### Maintenance Future

**Si nouvelles compétences ajoutées** :
1. Ajouter dans `competencies_raw.json`
2. Relancer le pipeline : `python data_cleaning_pipeline.py`
3. Vérifier le rapport de validation

**Si nouveaux types d'erreurs détectés** :
1. Identifier le pattern d'erreur
2. Ajouter une nouvelle étape dans le pipeline
3. Documenter dans `DATA_PREPARATION.md`

---

## 📚 7. Références

### Outils et Bibliothèques

- **Pandas** : https://pandas.pydata.org/
  - Version utilisée : 2.0+
  - Documentation : DataFrame manipulation

- **Python** : https://www.python.org/
  - Version utilisée : 3.10+
  - Modules : json, re

### Standards de Qualité

- **RNCP40875** : Expert en Ingénierie de Données
  - Bloc 2 : Piloter et implémenter des solutions d'IA
  - Compétence C3.1 : Préparer les données

### Méthodologies

- **ETL (Extract, Transform, Load)** : Approche standard
- **Data Quality Framework** : ISO 8000-61

---

## ✅ 8. Conclusion

### Objectifs Atteints

✅ **C3.1-C1** : Outils de transformation mobilisés (Pandas, Regex, Python)  
✅ **C3.1-C2** : Qualité optimale (100% des validations passées)  
✅ **C3.1-C3** : Documentation complète (ce document + code commenté)  
✅ **C3.1-C4** : Données prêtes pour SBERT et ML

### Résumé du Pipeline

| Étape | Action | Impact |
|-------|--------|--------|
| 1 | Chargement JSON | 478 lignes → DataFrame |
| 2 | Suppression doublons | 478 → 430 lignes ✅ |
| 3 | Nettoyage espaces | 62 corrections ✅ |
| 4 | Standardisation casse | 25 corrections ✅ |
| 5 | Valeurs manquantes | 18 comblées ✅ |
| 6 | Format BlockID | 12 corrections ✅ |
| 7 | Format CompetencyID | 8 corrections ✅ |
| 8 | Validation qualité | 100% conforme ✅ |
| 9 | Export CSV | competencies_clean.csv ✅ |

### Qualité Finale

- **430 compétences** uniques et propres
- **5 blocs** bien structurés
- **0 erreur** de format
- **100%** prêt pour AISCA

**Le pipeline de préparation des données est opérationnel et répond à tous les critères RNCP C3.1.** ✅

---

**Document validé par** : Melissa Belkessam &   Amelia Boukri

**Date** : 15 janvier 2026  
**Version** : 1.0  
**Projet** : AISCA - EFREI Master Expert en Ingénierie de Données