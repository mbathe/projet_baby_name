# Application Streamlit - Analyse des Prénoms en France

## Installation et lancement

1. **Installation des dépendances :**
```bash
pip install -r requirements.txt
```

2. **Lancement de l'application :**
```bash
streamlit run streamlit_app.py
```

3. **Accès à l'application :**
L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

## Fonctionnalités

### 🏠 Accueil
- Vue d'ensemble des données
- Métriques générales
- Top 10 des prénoms les plus populaires
- Évolution du nombre de naissances par année

### 📈 Évolution Temporelle
- Filtres interactifs par période, sexe et département
- Graphiques d'évolution des prénoms les plus populaires
- Statistiques dynamiques

### 🗺️ Analyse Géographique
- Carte des prénoms par département et année
- Analyse détaillée par département
- Top des départements par nombre de naissances

### 👫 Comparaison par Sexe
- Animation temporelle par sexe
- Comparaison globale filles/garçons
- Statistiques par année

### 🔍 Recherche de Prénom
- Recherche de prénoms spécifiques
- Évolution temporelle du prénom
- Répartition géographique
- Statistiques détaillées

## Avantages de Streamlit

- **Interface web intuitive** : Navigation facile avec sidebar et onglets
- **Interactivité fluide** : Widgets réactifs (sliders, selectbox, etc.)
- **Visualisations modernes** : Graphiques Plotly interactifs
- **Performance optimisée** : Cache automatique des données
- **Responsive design** : Interface adaptée à tous les écrans
