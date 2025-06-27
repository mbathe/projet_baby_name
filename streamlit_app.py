import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Analyse des Prénoms en France (1900-2020)",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pour améliorer l'apparence
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge et nettoie les données des prénoms"""
    try:
        df = pd.read_csv("dpt2020.csv", sep=';')
        
        # Renommage et nettoyage
        df = df.rename(columns={
            'annais': 'year',
            'preusuel': 'name',
            'sexe': 'sex',
            'nombre': 'count',
            'dpt': 'dpt'
        })
        
        # Filtrage des données
        df = df.query("name != '_PRENOMS_RARES' and year != 'XXXX' and dpt != '97' and dpt != '98' and dpt != '99'")
        
        # Conversion des types
        df['year'] = df['year'].astype(int)
        df['count'] = df['count'].astype(int)
        df['name'] = df['name'].str.upper()
        
        # Mapping des sexes
        df['sex'] = df['sex'].map({1: 'Fille', 2: 'Garçon'})
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

@st.cache_data
def load_geo_data():
    """Charge les données géographiques des départements"""
    try:
        geo_df = gpd.read_file("departements-version-simplifiee.geojson")
        geo_df = geo_df.rename(columns={'code': 'dpt'})
        return geo_df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données géographiques: {e}")
        return None

def main():
    # En-tête principal
    st.markdown('<h1 class="main-header">👶 Analyse des Prénoms en France (1900-2020)</h1>', unsafe_allow_html=True)
    
    # Chargement des données
    df = load_data()
    geo_df = load_geo_data()
    
    if df is None:
        st.error("Impossible de charger les données. Vérifiez que le fichier 'dpt2020.csv' est présent.")
        return
    
    # Sidebar pour la navigation
    st.sidebar.title("🎛️ Navigation")
    page = st.sidebar.selectbox(
        "Choisissez une analyse:",
        ["🏠 Accueil", "📈 Évolution Temporelle", "🗺️ Analyse Géographique", "👫 Comparaison par Sexe", "🔍 Recherche de Prénom"]
    )
    
    if page == "🏠 Accueil":
        show_home(df)
    elif page == "📈 Évolution Temporelle":
        show_temporal_analysis(df)
    elif page == "🗺️ Analyse Géographique":
        show_geographic_analysis(df, geo_df)
    elif page == "👫 Comparaison par Sexe":
        show_gender_comparison(df)
    elif page == "🔍 Recherche de Prénom":
        show_name_search(df, geo_df)

def show_home(df):
    """Page d'accueil avec aperçu des données"""
    st.markdown('<h2 class="sub-header">📊 Vue d\'ensemble des données</h2>', unsafe_allow_html=True)
    
    # Métriques générales
    col1, col2, col3, col4 = st.columns(4)
    
    total_births = df['count'].sum()
    unique_names = df['name'].nunique()
    years_span = f"{df['year'].min()}-{df['year'].max()}"
    departments = df['dpt'].nunique()
    
    with col1:
        st.metric("Total naissances", f"{total_births:,}")
    with col2:
        st.metric("Prénoms uniques", f"{unique_names:,}")
    with col3:
        st.metric("Période", years_span)
    with col4:
        st.metric("Départements", departments)
    
    # Top 10 des prénoms
    st.markdown('<h3 class="sub-header">🏆 Top 10 des prénoms les plus populaires</h3>', unsafe_allow_html=True)
    
    top_names = df.groupby('name')['count'].sum().sort_values(ascending=False).head(10)
    
    fig = px.bar(
        x=top_names.values,
        y=top_names.index,
        orientation='h',
        title="Top 10 des prénoms (1900-2020)",
        labels={'x': 'Nombre de naissances', 'y': 'Prénom'},
        color=top_names.values,
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Évolution des naissances par année
    st.markdown('<h3 class="sub-header">📅 Évolution du nombre de naissances par année</h3>', unsafe_allow_html=True)
    
    yearly_births = df.groupby('year')['count'].sum().reset_index()
    
    fig = px.line(
        yearly_births,
        x='year',
        y='count',
        title="Nombre total de naissances par année",
        labels={'year': 'Année', 'count': 'Nombre de naissances'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_temporal_analysis(df):
    """Analyse temporelle des prénoms"""
    st.markdown('<h2 class="sub-header">📈 Analyse Temporelle des Prénoms</h2>', unsafe_allow_html=True)
    
    # Contrôles dans la sidebar
    st.sidebar.markdown("### Filtres")
    
    # Filtre par période
    year_range = st.sidebar.slider(
        "Période d'analyse",
        min_value=int(df['year'].min()),
        max_value=int(df['year'].max()),
        value=(1900, 2020),
        step=1
    )
    
    # Filtre par sexe
    sex_options = st.sidebar.multiselect(
        "Sexe",
        options=['Fille', 'Garçon'],
        default=['Fille', 'Garçon']
    )
    
    # Filtre par département
    dept_options = ['Tous'] + sorted(df['dpt'].unique().tolist())
    selected_dept = st.sidebar.selectbox("Département", dept_options)
    
    # Nombre de prénoms à afficher
    top_n = st.sidebar.slider("Nombre de prénoms à afficher", 3, 20, 10)
    
    # Filtrage des données
    filtered_df = df[
        (df['year'] >= year_range[0]) &
        (df['year'] <= year_range[1]) &
        (df['sex'].isin(sex_options))
    ]
    
    if selected_dept != 'Tous':
        filtered_df = filtered_df[filtered_df['dpt'] == selected_dept]
    
    if filtered_df.empty:
        st.warning("Aucune donnée disponible avec ces filtres.")
        return
    
    # Calcul des top prénoms
    top_names = (
        filtered_df.groupby('name')['count']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index.tolist()
    )
    
    # Données pour visualisation
    viz_df = filtered_df[filtered_df['name'].isin(top_names)]
    yearly_data = viz_df.groupby(['year', 'name'])['count'].sum().reset_index()
    
    # Graphique d'évolution
    fig = px.line(
        yearly_data,
        x='year',
        y='count',
        color='name',
        title=f"Évolution des {top_n} prénoms les plus populaires",
        labels={'year': 'Année', 'count': 'Nombre de naissances', 'name': 'Prénom'},
        markers=True
    )
    fig.update_layout(height=600, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total naissances", f"{filtered_df['count'].sum():,}")
    with col2:
        st.metric("Prénoms uniques", f"{filtered_df['name'].nunique():,}")
    with col3:
        if top_names:
            st.metric("Prénom le plus populaire", top_names[0])

def show_geographic_analysis(df, geo_df):
    """Analyse géographique des prénoms"""
    st.markdown('<h2 class="sub-header">🗺️ Analyse Géographique des Prénoms</h2>', unsafe_allow_html=True)
    
    if geo_df is None:
        st.error("Données géographiques non disponibles.")
        return
    
    # Contrôles
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.slider(
            "Année d'analyse",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=2000,
            step=10
        )
    
    with col2:
        sex_filter = st.radio("Sexe", ['Tous', 'Fille', 'Garçon'])
    
    # Filtrage des données
    map_data = df[df['year'] == selected_year].copy()
    
    if sex_filter != 'Tous':
        map_data = map_data[map_data['sex'] == sex_filter]
    
    if map_data.empty:
        st.warning("Aucune donnée pour cette année/sexe.")
        return
    
    # Calcul du prénom le plus populaire par département
    top_by_dept = (
        map_data.groupby(['dpt', 'name'])['count']
        .sum()
        .reset_index()
    )
    
    idx_max = top_by_dept.groupby('dpt')['count'].idxmax()
    top_by_dept = top_by_dept.loc[idx_max].reset_index(drop=True)
    
    # Affichage de la carte (version simplifiée avec un tableau)
    st.markdown(f"### Prénom le plus populaire par département en {selected_year}")
    
    # Tableau des résultats
    display_data = top_by_dept.copy()
    if not geo_df.empty:
        display_data = display_data.merge(geo_df[['dpt', 'nom']], on='dpt', how='left')
        display_data = display_data[['dpt', 'nom', 'name', 'count']].sort_values('count', ascending=False)
        display_data.columns = ['Code Dept.', 'Département', 'Prénom le + populaire', 'Nombre de naissances']
    
    st.dataframe(display_data, use_container_width=True)
    
    # Graphique des départements avec le plus de naissances
    top_depts = top_by_dept.nlargest(15, 'count')
    
    fig = px.bar(
        top_depts,
        x='count',
        y='dpt',
        orientation='h',
        title=f"Top 15 des départements par nombre de naissances en {selected_year}",
        labels={'count': 'Nombre de naissances', 'dpt': 'Département'},
        text='name'
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Sélecteur de département pour analyse détaillée
    st.markdown("### Analyse détaillée par département")
    selected_dept_code = st.selectbox(
        "Choisissez un département:",
        options=sorted(df['dpt'].unique()),
        format_func=lambda x: f"{x} - {geo_df[geo_df['dpt']==x]['nom'].iloc[0] if x in geo_df['dpt'].values else f'Département {x}'}"
    )
    
    if selected_dept_code:
        show_department_analysis(df, selected_dept_code, geo_df)

def show_department_analysis(df, dept_code, geo_df):
    """Affiche l'analyse détaillée d'un département"""
    dept_name = geo_df[geo_df['dpt'] == dept_code]['nom'].iloc[0] if dept_code in geo_df['dpt'].values else f"Département {dept_code}"
    
    dept_data = df[df['dpt'] == dept_code]
    
    if dept_data.empty:
        st.warning(f"Aucune donnée pour {dept_name}")
        return
    
    st.markdown(f"#### Analyse de {dept_name}")
    
    # Top 10 prénoms du département
    top_names_dept = (
        dept_data.groupby('name')['count']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            x=top_names_dept.values,
            y=top_names_dept.index,
            orientation='h',
            title=f"Top 10 des prénoms - {dept_name}",
            labels={'x': 'Nombre de naissances', 'y': 'Prénom'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Évolution temporelle des top 5
        top_5_names = top_names_dept.head(5).index.tolist()
        evolution_data = (
            dept_data[dept_data['name'].isin(top_5_names)]
            .groupby(['year', 'name'])['count']
            .sum()
            .reset_index()
        )
        
        fig = px.line(
            evolution_data,
            x='year',
            y='count',
            color='name',
            title=f"Évolution temporelle - {dept_name}",
            labels={'year': 'Année', 'count': 'Naissances', 'name': 'Prénom'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

def show_gender_comparison(df):
    """Comparaison par sexe"""
    st.markdown('<h2 class="sub-header">👫 Comparaison par Sexe</h2>', unsafe_allow_html=True)
    
    # Analyse par année avec animation
    st.markdown("### Animation temporelle par sexe")
    
    # Contrôles
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.slider(
            "Année",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=1950,
            step=5
        )
    
    with col2:
        top_n_gender = st.slider("Nombre de prénoms par sexe", 5, 15, 8)
    
    # Calcul des top prénoms par sexe
    top_names_by_sex = {}
    for sex in ['Fille', 'Garçon']:
        top_names_by_sex[sex] = (
            df[df['sex'] == sex]
            .groupby('name')['count']
            .sum()
            .sort_values(ascending=False)
            .head(top_n_gender)
            .index.tolist()
        )
    
    all_top_names = top_names_by_sex['Fille'] + top_names_by_sex['Garçon']
    
    # Données pour l'année sélectionnée
    year_data = df[
        (df['year'] == selected_year) &
        (df['name'].isin(all_top_names))
    ].groupby(['name', 'sex'])['count'].sum().reset_index()
    
    if not year_data.empty:
        fig = px.bar(
            year_data.sort_values('count'),
            x='count',
            y='name',
            color='sex',
            orientation='h',
            title=f"Prénoms les plus populaires en {selected_year}",
            labels={'count': 'Nombre de naissances', 'name': 'Prénom', 'sex': 'Sexe'},
            color_discrete_map={'Fille': '#FF69B4', 'Garçon': '#4169E1'}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        total_year = year_data['count'].sum()
        filles_total = year_data[year_data['sex'] == 'Fille']['count'].sum()
        garcons_total = year_data[year_data['sex'] == 'Garçon']['count'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total naissances", f"{total_year:,}")
        with col2:
            if total_year > 0:
                st.metric("Filles", f"{filles_total:,} ({filles_total/total_year*100:.1f}%)")
        with col3:
            if total_year > 0:
                st.metric("Garçons", f"{garcons_total:,} ({garcons_total/total_year*100:.1f}%)")
    
    # Comparaison globale par sexe
    st.markdown("### Comparaison globale (1900-2020)")
    
    sex_comparison = df.groupby(['name', 'sex'])['count'].sum().reset_index()
    top_global = sex_comparison.nlargest(20, 'count')
    
    fig = px.bar(
        top_global,
        x='name',
        y='count',
        color='sex',
        title="Top 20 des prénoms par sexe (1900-2020)",
        labels={'name': 'Prénom', 'count': 'Total naissances', 'sex': 'Sexe'},
        color_discrete_map={'Fille': '#FF69B4', 'Garçon': '#4169E1'}
    )
    fig.update_layout(height=500, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def show_name_search(df, geo_df):
    """Recherche de prénom spécifique"""
    st.markdown('<h2 class="sub-header">🔍 Recherche de Prénom</h2>', unsafe_allow_html=True)
    
    # Interface de recherche
    search_term = st.text_input(
        "Entrez un prénom à rechercher:",
        placeholder="Ex: Marie, Jean, Nicolas...",
        help="Vous pouvez entrer une partie du prénom"
    ).upper().strip()
    
    if not search_term:
        st.info("Entrez un prénom pour commencer la recherche.")
        return
    
    # Recherche
    name_data = df[df['name'].str.contains(search_term, na=False)]
    
    if name_data.empty:
        st.warning(f"Aucun prénom trouvé contenant '{search_term}'")
        return
    
    # Prénoms trouvés
    found_names = sorted(name_data['name'].unique())
    st.success(f"Prénoms trouvés: {', '.join(found_names)}")
    
    # Sélection du prénom spécifique si plusieurs trouvés
    if len(found_names) > 1:
        selected_name = st.selectbox("Choisissez un prénom spécifique:", found_names)
        name_data = name_data[name_data['name'] == selected_name]
        name_title = selected_name
    else:
        name_title = found_names[0]
    
    # Statistiques générales
    st.markdown(f"### Statistiques pour le prénom '{name_title}'")
    
    total_count = name_data['count'].sum()
    
    # Évolution temporelle
    evolution = (
        name_data.groupby(['year', 'sex'])['count']
        .sum()
        .reset_index()
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique d'évolution
        fig = px.line(
            evolution,
            x='year',
            y='count',
            color='sex',
            title=f"Évolution du prénom '{name_title}' (1900-2020)",
            labels={'year': 'Année', 'count': 'Nombre de naissances', 'sex': 'Sexe'},
            markers=True,
            color_discrete_map={'Fille': '#FF69B4', 'Garçon': '#4169E1'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition par sexe
        sex_data = name_data.groupby('sex')['count'].sum()
        
        if len(sex_data) > 1:
            fig = px.pie(
                values=sex_data.values,
                names=sex_data.index,
                title=f"Répartition par sexe - '{name_title}'",
                color_discrete_map={'Fille': '#FF69B4', 'Garçon': '#4169E1'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Le prénom '{name_title}' est exclusivement donné aux {sex_data.index[0].lower()}s")
    
    # Pic de popularité
    peak_data = evolution.loc[evolution['count'].idxmax()]
    peak_year = peak_data['year']
    peak_count = peak_data['count']
    
    # Métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total naissances", f"{total_count:,}")
    with col2:
        st.metric("Pic de popularité", f"{peak_year}")
    with col3:
        st.metric("Naissances au pic", f"{peak_count:,}")
    
    # Top départements
    st.markdown("### Répartition géographique")
    
    dept_data = name_data.groupby('dpt')['count'].sum().sort_values(ascending=False).head(10)
    
    if geo_df is not None:
        dept_names = []
        for dept in dept_data.index:
            if dept in geo_df['dpt'].values:
                dept_name = geo_df[geo_df['dpt'] == dept]['nom'].iloc[0]
                dept_names.append(f"{dept} - {dept_name}")
            else:
                dept_names.append(f"Département {dept}")
    else:
        dept_names = [f"Département {dept}" for dept in dept_data.index]
    
    fig = px.bar(
        x=dept_data.values,
        y=dept_names,
        orientation='h',
        title=f"Top 10 des départements pour le prénom '{name_title}'",
        labels={'x': 'Nombre de naissances', 'y': 'Département'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
