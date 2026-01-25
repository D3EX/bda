# pages/app_chef_departement.py - Version avec période 2025-2026
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import numpy as np
import io
from decimal import Decimal
import os
import toml
import time as time_module
from datetime import time
from datetime import time


# Configuration de la page
st.set_page_config(
    page_title="Vue Stratégique - Chef Département",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS PERSONNALISÉ PROFESSIONNEL
st.markdown("""
<style>
    /* Cache la navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* En-tête principal */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Cartes de métriques */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #3949ab;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #1a237e;
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-size: 13px;
        color: #666;
        font-weight: 500;
    }
    
    /* Badges de statut */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    .status-confirmed {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-cancelled {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Onglets améliorés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* Boutons améliorés */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Cartes d'examen */
    .examen-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #3949ab;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .examen-card:hover {
        border-color: #3949ab;
        box-shadow: 0 4px 12px rgba(57, 73, 171, 0.1);
    }
    
    /* En-têtes de section */
    .section-header {
        border-bottom: 2px solid #3949ab;
        padding-bottom: 0.8rem;
        margin-bottom: 1.5rem;
        color: #1a237e;
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    /* Barre de progression */
    .progress-container {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 8px;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Tags */
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .tag-info {
        background: #e3f2fd;
        color: #1565c0;
    }
    
    .tag-success {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .tag-warning {
        background: #fff8e1;
        color: #f57c00;
    }
    
    .tag-primary {
        background: #e8eaf6;
        color: #3949ab;
    }
    
    /* Tableaux */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Sidebar améliorée */
    .sidebar-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #3949ab 0%, #283593 100%);
        color: white;
        border-radius: 0 0 10px 10px;
        margin: -1rem -1rem 1rem -1rem;
    }
    
    .user-avatar {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        color: #3949ab;
        font-size: 1.8rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Pied de page */
    .footer {
        text-align: center;
        color: #666;
        font-size: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #e0e0e0;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    /* Filtres */
    .filter-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-bottom: 1.5rem;
    }
    
    /* Graphiques */
    .plotly-chart {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Animation de chargement */
    .loading-spinner {
        text-align: center;
        padding: 3rem;
    }
    
    /* Optimisation pour tableaux */
    .dataframe tbody tr:hover {
        background-color: #f5f5f5;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .metric-card {
            padding: 0.8rem;
        }
        .metric-value {
            font-size: 18px;
        }
    }
</style>
""", unsafe_allow_html=True)

# VÉRIFICATION DE CONNEXION
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/log.py")
    st.stop()

# VÉRIFICATION DU RÔLE
if st.session_state.role != 'chef_departement':
    st.error(f"⛔ Cette page est réservée aux chefs de département. Votre rôle: {st.session_state.role}")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

# L'ID de l'utilisateur connecté
CHEF_ID = st.session_state.user_id

# ============================================================================
# FONCTIONS UTILITAIRES OPTIMISÉES
# ============================================================================

def load_secrets():
    """Charger les secrets de configuration"""
    possible_paths = [
        r"C:\Users\FARES DH\.streamlit\secrets.toml",
        r"C:\Users\FARES DH\Desktop\pree\.streamlit\secrets.toml",
        ".streamlit/secrets.toml",
        "secrets.toml"
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                secrets = toml.load(path)
                return secrets.get("mysql", {})
        except:
            continue
    
    return {
        "host": "localhost",
        "database": "planning_examens",
        "user": "root",
        "password": ""
    }

@st.cache_resource(ttl=3600)  # Cache la connexion pour 1 heure
def init_connection():
    """Initialiser la connexion avec connection pooling"""
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            pool_name="mypool",
            pool_size=3,
            pool_reset_session=True,
            buffered=True
        )
        return conn
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

def run_query(query, params=None, fetch=True):
    """Exécuter une requête SQL de manière optimisée"""
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            # Charger les résultats par batch pour optimiser la mémoire
            batch_size = 500
            results = []
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                
                # Convertir les types pendant le chargement
                for row in batch:
                    for key, value in row.items():
                        if isinstance(value, timedelta):
                            total_seconds = value.total_seconds()
                            hours = int(total_seconds // 3600)
                            minutes = int((total_seconds % 3600) // 60)
                            seconds = int(total_seconds % 60)
                            row[key] = time(hours, minutes, seconds)
                        elif isinstance(value, Decimal):
                            row[key] = float(value)
                
                results.extend(batch)
            
            cursor.close()
            return results
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return None

@st.cache_data(ttl=300)  # Cache pour 5 minutes
def get_departement_chef(chef_id):
    """Récupérer le département dont l'utilisateur est responsable"""
    query = """
        SELECT id, nom 
        FROM departements 
        WHERE responsable_id = %s
        LIMIT 1
    """
    result = run_query(query, (chef_id,))
    return result[0] if result else None

# ============================================================================
# FONCTIONS SPÉCIFIQUES AU DÉPARTEMENT (OPTIMISÉES)
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_info_departement(dept_id, date_debut, date_fin):
    """Informations générales du département (optimisé)"""
    query = """
        SELECT 
            d.nom,
            (SELECT COUNT(*) FROM formations WHERE dept_id = %s) as nb_formations,
            (SELECT COUNT(*) FROM modules m 
             JOIN formations f ON m.formation_id = f.id 
             WHERE f.dept_id = %s) as nb_modules,
            (SELECT COUNT(*) FROM professeurs WHERE dept_id = %s) as nb_professeurs,
            (SELECT COUNT(DISTINCT et.id) FROM etudiants et 
             JOIN formations f ON et.formation_id = f.id 
             WHERE f.dept_id = %s) as nb_etudiants,
            (SELECT COUNT(DISTINCT e.id) FROM examens e 
             JOIN modules m ON e.module_id = m.id 
             JOIN formations f ON m.formation_id = f.id 
             WHERE f.dept_id = %s AND e.date_examen BETWEEN %s AND %s) as nb_examens_planifies
        FROM departements d
        WHERE d.id = %s
    """
    return run_query(query, (dept_id, dept_id, dept_id, dept_id, dept_id, date_debut, date_fin, dept_id))

@st.cache_data(ttl=300, show_spinner="Chargement des examens...")
def get_examens_departement_optimise(dept_id, date_debut, date_fin):
    """Tous les examens du département (version optimisée)"""
    query = """
        SELECT 
            e.id,
            e.date_examen,
            e.heure_debut,
            e.heure_fin,
            e.duree_minutes,
            e.statut,
            e.session,
            m.nom as module,
            f.nom as formation,
            CONCAT(p.nom, ' ', p.prenom) as professeur,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            (SELECT COUNT(*) FROM inscriptions i 
             WHERE i.module_id = m.id 
             AND i.annee_scolaire = YEAR(CURDATE())) as nb_etudiants
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        LEFT JOIN professeurs p ON e.professeur_id = p.id
        JOIN lieu_examen le ON e.salle_id = le.id
        WHERE f.dept_id = %s
        AND e.date_examen BETWEEN %s AND %s
        ORDER BY e.date_examen, e.heure_debut
    """
    return run_query(query, (dept_id, date_debut, date_fin))

@st.cache_data(ttl=300, show_spinner=False)
def get_statistiques_validation_departement(dept_id, date_debut, date_fin):
    """Statistiques de validation pour le département"""
    query = """
        SELECT 
            f.nom as formation,
            COUNT(DISTINCT e.id) as total_examens,
            SUM(CASE WHEN e.statut = 'planifié' THEN 1 ELSE 0 END) as en_attente,
            SUM(CASE WHEN e.statut = 'confirmé' THEN 1 ELSE 0 END) as confirmes,
            SUM(CASE WHEN e.statut = 'annulé' THEN 1 ELSE 0 END) as annules
        FROM formations f
        JOIN modules m ON f.id = m.formation_id
        JOIN examens e ON m.id = e.module_id
        WHERE f.dept_id = %s
        AND e.date_examen BETWEEN %s AND %s
        GROUP BY f.id
        HAVING total_examens > 0
        ORDER BY f.nom
    """
    result = run_query(query, (dept_id, date_debut, date_fin))
    
    # Calculer le taux de validation localement
    for row in result:
        total = float(row['total_examens'])
        confirmes = float(row['confirmes'])
        row['taux_validation'] = (confirmes / total * 100) if total > 0 else 0
    
    return result

@st.cache_data(ttl=300, show_spinner=False)
def get_professeurs_departement_simple(dept_id):
    """Liste simplifiée des professeurs du département"""
    query = """
        SELECT 
            p.id,
            CONCAT(p.nom, ' ', p.prenom) as nom_complet,
            p.specialite
        FROM professeurs p
        WHERE p.dept_id = %s
        ORDER BY p.nom, p.prenom
    """
    return run_query(query, (dept_id,))

@st.cache_data(ttl=300, show_spinner=False)
def get_formations_departement_simple(dept_id):
    """Liste simplifiée des formations du département"""
    query = """
        SELECT 
            f.id,
            f.nom
        FROM formations f
        WHERE f.dept_id = %s
        ORDER BY f.nom
    """
    return run_query(query, (dept_id,))

@st.cache_data(ttl=300, show_spinner=False)
def get_occupation_salles_departement_simple(dept_id, date_debut, date_fin):
    """Occupation simplifiée des salles pour le département"""
    query = """
        SELECT 
            le.type,
            le.nom as salle,
            le.capacite,
            COUNT(DISTINCT e.id) as nb_examens
        FROM lieu_examen le
        JOIN examens e ON le.id = e.salle_id 
            AND e.date_examen BETWEEN %s AND %s
            AND e.statut != 'annulé'
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        WHERE f.dept_id = %s
        GROUP BY le.id
        ORDER BY le.type, le.nom
    """
    return run_query(query, (date_debut, date_fin, dept_id))

# ============================================================================
# FONCTIONS DE MISE À JOUR (NON CACHÉES)
# ============================================================================

def valider_examen_departement(examen_id):
    """Valider un examen spécifique"""
    query = "UPDATE examens SET statut = 'confirmé' WHERE id = %s"
    result = run_query(query, (examen_id,), False)
    if result:
        st.cache_data.clear()  # Effacer le cache après modification
    return result

def valider_tous_examens_formation(formation_id, date_debut, date_fin):
    """Valider tous les examens d'une formation"""
    query = """
        UPDATE examens e
        JOIN modules m ON e.module_id = m.id
        SET e.statut = 'confirmé'
        WHERE m.formation_id = %s
        AND e.date_examen BETWEEN %s AND %s
        AND e.statut = 'planifié'
    """
    result = run_query(query, (formation_id, date_debut, date_fin), False)
    if result:
        st.cache_data.clear()  # Effacer le cache après modification
    return result

# ============================================================================
# PAGES AVEC CHARGEMENT PROGRESSIF
# ============================================================================

def render_tableau_de_bord():
    """Page: Tableau de Bord Département"""
    # En-tête principal
    col_title, col_stats = st.columns([3, 1])
    with col_title:
        st.title("📊 Tableau de Bord Département")
        st.markdown(f"**Département:** {departement_nom} | **Période:** {date_debut} au {date_fin}")
    
    with col_stats:
        with st.spinner("Calcul..."):
            examens = get_examens_departement_optimise(DEPARTEMENT_ID, date_debut, date_fin)
            if examens:
                df_examens = pd.DataFrame(examens)
                total_examens = len(df_examens)
                confirmes = len(df_examens[df_examens['statut'] == 'confirmé'])
                taux_validation = (confirmes/total_examens*100) if total_examens > 0 else 0
                st.markdown(f"""
                <div class="metric-card" style="text-align: center; background: rgba(255,255,255,0.1); border: none;">
                    <div class="metric-value" style="color: white;">{taux_validation:.1f}%</div>
                    <div class="metric-label" style="color: rgba(255,255,255,0.9);">Taux Validation</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Informations générales
    with st.spinner("Chargement des informations..."):
        info = get_info_departement(DEPARTEMENT_ID, date_debut, date_fin)
    
    if info:
        info_data = info[0]
        
        # Métriques principales
        st.markdown('<div class="section-header">📈 Aperçu du Département</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Formations", "🎓", int(info_data.get('nb_formations', 0)), "#3949ab"),
            ("Modules", "📚", int(info_data.get('nb_modules', 0)), "#2196F3"),
            ("Professeurs", "👨‍🏫", int(info_data.get('nb_professeurs', 0)), "#4CAF50"),
            ("Examens", "📅", int(info_data.get('nb_examens_planifies', 0)), "#FF9800")
        ]
        
        for i, (label, icon, value, color) in enumerate(metrics):
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div class="metric-value">{value}</div>
                        <div style="font-size: 24px; color: {color};">{icon}</div>
                    </div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Deuxième ligne de métriques
        with st.spinner("Chargement des données complémentaires..."):
            formations = get_formations_departement_simple(DEPARTEMENT_ID)
            occupation = get_occupation_salles_departement_simple(DEPARTEMENT_ID, date_debut, date_fin)
        
        col5, col6, col7, col8 = st.columns(4)
        
        metrics2 = [
            ("Étudiants", "👥", int(info_data.get('nb_etudiants', 0)), "#9C27B0"),
            ("Salles", "🏫", len(occupation) if occupation else 0, "#00BCD4"),
            ("Formations Actives", "🎯", len(formations) if formations else 0, "#FF5722"),
            ("Examens/Formation", "📊", f"{int(info_data.get('nb_examens_planifies', 0))/max(len(formations), 1):.1f}" if formations else "0", "#607D8B")
        ]
        
        for i, (label, icon, value, color) in enumerate(metrics2):
            with [col5, col6, col7, col8][i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div class="metric-value">{value}</div>
                        <div style="font-size: 24px; color: {color};">{icon}</div>
                    </div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Graphiques rapides
    st.markdown('<div class="section-header">📊 Visualisations Rapides</div>', unsafe_allow_html=True)
    
    if examens:
        df_examens = pd.DataFrame(examens)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📊 Examens par Formation</div>', unsafe_allow_html=True)
            if not df_examens.empty:
                exams_par_formation = df_examens.groupby('formation').size().reset_index(name='nb_examens')
                if not exams_par_formation.empty:
                    fig = px.pie(exams_par_formation.head(8), values='nb_examens', names='formation',
                                title="", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
                    fig.update_layout(showlegend=True, height=300, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📈 Statut des Examens</div>', unsafe_allow_html=True)
            if not df_examens.empty:
                statuts = df_examens['statut'].value_counts().reset_index()
                if not statuts.empty:
                    fig = px.bar(statuts, x='statut', y='count', 
                                color='statut',
                                color_discrete_map={'planifié': '#FFC107', 'confirmé': '#4CAF50', 'annulé': '#F44336'})
                    fig.update_layout(height=300, showlegend=False, xaxis_title="", yaxis_title="Nombre")
                    st.plotly_chart(fig, use_container_width=True)
    
    # Derniers examens
    st.markdown('<div class="section-header">📋 Derniers Examens Planifiés</div>', unsafe_allow_html=True)
    
    if examens and len(examens) > 0:
        df_recent = pd.DataFrame(examens)
        df_recent = df_recent.sort_values('date_examen', ascending=False).head(6)
        
        for _, row in df_recent.iterrows():
            with st.container():
                st.markdown('<div class="examen-card">', unsafe_allow_html=True)
                col_info, col_stat = st.columns([3, 1])
                
                with col_info:
                    # Status badge
                    if row['statut'] == 'confirmé':
                        status_class = "status-confirmed"
                        status_text = "✅ Validé"
                    elif row['statut'] == 'annulé':
                        status_class = "status-cancelled"
                        status_text = "❌ Annulé"
                    else:
                        status_class = "status-pending"
                        status_text = "⏳ En attente"
                    
                    occupation_rate = (float(row['nb_etudiants']) / float(row['capacite']) * 100) if row['capacite'] > 0 else 0
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <div style="font-weight: 600; font-size: 16px; color: #1a237e;">{row['module'][:40]}{'...' if len(row['module']) > 40 else ''}</div>
                        <span class="{status_class}">{status_text}</span>
                    </div>
                    <div style="color: #666; margin-bottom: 12px; font-size: 14px;">{row['formation']}</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
                        <span class="tag tag-primary">📅 {row['date_examen']}</span>
                        <span class="tag tag-warning">⏰ {row['heure_debut']}</span>
                        <span class="tag tag-info">🏫 {row['salle']}</span>
                    </div>
                    <div style="background: #f8f9fa; padding: 8px; border-radius: 6px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-size: 11px; color: #666;">Occupation: {occupation_rate:.1f}%</span>
                            <span style="font-size: 11px; color: #666;">{int(row['nb_etudiants'])}/{int(row['capacite'])} places</span>
                        </div>
                        <div style="height: 4px; background: #e0e0e0; border-radius: 2px; overflow: hidden;">
                            <div style="width: {min(occupation_rate, 100)}%; height: 100%; background: {'#4CAF50' if occupation_rate < 80 else '#FF9800' if occupation_rate < 95 else '#F44336'};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_stat:
                    st.write("")
                    if row['statut'] == 'planifié':
                        if st.button(f"✅", 
                                    key=f"val_{row['id']}", 
                                    help="Valider cet examen",
                                    use_container_width=True):
                            if valider_examen_departement(row['id']):
                                st.success(f"✓ Examen validé!")
                                st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("ℹ️ Aucun examen trouvé pour la période sélectionnée.")

def render_validation_edt():
    """Page: Validation des Emplois du Temps"""
    # En-tête principal
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("✅ Validation des Emplois du Temps")
    st.markdown(f"**Validez et gérez les examens planifiés pour le département {departement_nom}**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Validation Individuelle", "🎯 Validation par Formation"])
    
    with tab1:
        st.subheader("🔍 Filtres de Recherche")
        
        with st.spinner("Chargement des filtres..."):
            formations = get_formations_departement_simple(DEPARTEMENT_ID)
            examens = get_examens_departement_optimise(DEPARTEMENT_ID, date_debut, date_fin)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            statut_filter = st.selectbox(
                "Statut",
                options=['Tous', 'planifié', 'confirmé', 'annulé']
            )
        
        with col2:
            formation_options = ['Toutes'] + [f['nom'] for f in formations] if formations else ['Toutes']
            formation_filter = st.selectbox("Formation", formation_options)
        
        with col3:
            if examens:
                salles = pd.DataFrame(examen['salle'] for examen in examens if examen['salle'])
                salle_options = ['Toutes'] + sorted(salles[0].unique().tolist())
            else:
                salle_options = ['Toutes']
            salle_filter = st.selectbox("Salle", salle_options)
        
        # Récupérer les examens filtrés
        if examens:
            df_examens = pd.DataFrame(examens)
            
            # Appliquer les filtres
            if statut_filter != 'Tous':
                df_examens = df_examens[df_examens['statut'] == statut_filter]
            
            if formation_filter != 'Toutes':
                df_examens = df_examens[df_examens['formation'] == formation_filter]
            
            if salle_filter != 'Toutes':
                df_examens = df_examens[df_examens['salle'] == salle_filter]
            
            # Métriques de filtrage
            st.markdown('<div class="section-header">📊 Statistiques Filtrage</div>', unsafe_allow_html=True)
            
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            
            metrics_data = [
                ("Examens filtrés", len(df_examens), "#3949ab"),
                ("En attente", len(df_examens[df_examens['statut'] == 'planifié']), "#FF9800"),
                ("Validés", len(df_examens[df_examens['statut'] == 'confirmé']), "#4CAF50"),
                ("Annulés", len(df_examens[df_examens['statut'] == 'annulé']), "#F44336")
            ]
            
            for col, (label, value, color) in zip([col_met1, col_met2, col_met3, col_met4], metrics_data):
                with col:
                    st.markdown(f'''
                    <div class="metric-card" style="text-align: center; border-left-color: {color};">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Afficher les examens
            st.markdown('<div class="section-header">📝 Examens à Valider</div>', unsafe_allow_html=True)
            
            if len(df_examens) > 0:
                # Pagination
                items_per_page = 10
                total_pages = max(1, (len(df_examens) + items_per_page - 1) // items_per_page)
                page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
                
                start_idx = (page_number - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, len(df_examens))
                
                st.caption(f"Affichage des examens {start_idx + 1} à {end_idx} sur {len(df_examens)}")
                
                for idx in range(start_idx, end_idx):
                    row = df_examens.iloc[idx]
                    with st.container():
                        col_info, col_action = st.columns([4, 1])
                        
                        with col_info:
                            occupation_rate = (float(row['nb_etudiants']) / float(row['capacite']) * 100) if row['capacite'] > 0 else 0
                            
                            if row['statut'] == 'confirmé':
                                status_class = "status-confirmed"
                                status_icon = "✅"
                                status_text = "Validé"
                            elif row['statut'] == 'annulé':
                                status_class = "status-cancelled"
                                status_icon = "❌"
                                status_text = "Annulé"
                            else:
                                status_class = "status-pending"
                                status_icon = "⏳"
                                status_text = "En attente"
                            
                            st.markdown(f"""
                            <div style="display: flex; align-items: start; justify-content: space-between; margin-bottom: 12px;">
                                <div>
                                    <div style="font-weight: 600; font-size: 16px; color: #1a237e;">{row['module']}</div>
                                    <div style="color: #666; font-size: 14px;">{row['formation']}</div>
                                </div>
                                <span class="{status_class}">{status_icon} {status_text}</span>
                            </div>
                            
                            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
                                <span class="tag tag-primary">📅 {row['date_examen']}</span>
                                <span class="tag tag-warning">⏰ {row['heure_debut']}-{row['heure_fin']}</span>
                                <span class="tag tag-info">🏫 {row['salle']}</span>
                            </div>
                            
                            <div style="background: #f8f9fa; padding: 10px; border-radius: 6px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                    <span style="font-size: 12px; color: #666;">Occupation de la salle</span>
                                    <span style="font-size: 12px; font-weight: 600; color: #333;">{occupation_rate:.1f}%</span>
                                </div>
                                <div style="height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden;">
                                    <div style="width: {occupation_rate}%; height: 100%; background: {'#4CAF50' if occupation_rate < 80 else '#FF9800' if occupation_rate < 95 else '#F44336'};"></div>
                                </div>
                                <div style="font-size: 11px; color: #666; margin-top: 4px;">{int(row['nb_etudiants'])} étudiants sur {int(row['capacite'])} places</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_action:
                            st.write("")
                            if row['statut'] == 'planifié':
                                if st.button(f"Valider", 
                                            key=f"val_ex_{row['id']}", 
                                            use_container_width=True,
                                            type="primary"):
                                    if valider_examen_departement(row['id']):
                                        st.success(f"✓ Examen validé!")
                                        st.rerun()
                            elif row['statut'] == 'confirmé':
                                st.success("✅")
                            elif row['statut'] == 'annulé':
                                st.error("❌")
            else:
                st.info("ℹ️ Aucun examen ne correspond aux filtres sélectionnés.")
        else:
            st.info("ℹ️ Aucun examen trouvé pour la période sélectionnée.")
    
    with tab2:
        st.markdown('<div class="section-header">🎯 Validation Globale par Formation</div>', unsafe_allow_html=True)
        
        with st.spinner("Chargement des statistiques..."):
            stats = get_statistiques_validation_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if stats:
            df_stats = pd.DataFrame(stats)
            
            for _, formation in df_stats.iterrows():
                with st.container():
                    st.markdown('<div class="examen-card">', unsafe_allow_html=True)
                    col_stat, col_action = st.columns([3, 1])
                    
                    with col_stat:
                        confirmes_float = float(formation['confirmes'])
                        total_examens_float = float(formation['total_examens'])
                        progress = (confirmes_float / total_examens_float) if total_examens_float > 0 else 0
                        
                        st.markdown(f"""
                        <div style="font-weight: 600; font-size: 16px; color: #1a237e; margin-bottom: 12px;">🎓 {formation['formation']}</div>
                        
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-size: 12px; color: #666;">Progression de validation</span>
                                <span style="font-size: 12px; font-weight: 600; color: #1a237e;">{int(formation['confirmes'])}/{int(formation['total_examens'])}</span>
                            </div>
                            <div style="height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden;">
                                <div style="width: {progress*100}%; height: 100%; background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);"></div>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                            <div style="text-align: center; padding: 8px; background: #d4edda; border-radius: 6px;">
                                <div style="font-size: 18px; font-weight: 700; color: #2e7d32;">{int(formation['confirmes'])}</div>
                                <div style="font-size: 11px; color: #2e7d32;">Confirmés</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: #fff3cd; border-radius: 6px;">
                                <div style="font-size: 18px; font-weight: 700; color: #f57c00;">{int(formation['en_attente'])}</div>
                                <div style="font-size: 11px; color: #f57c00;">En attente</div>
                            </div>
                            <div style="text-align: center; padding: 8px; background: #f8d7da; border-radius: 6px;">
                                <div style="font-size: 18px; font-weight: 700; color: #c62828;">{int(formation['annules'])}</div>
                                <div style="font-size: 11px; color: #c62828;">Annulés</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_action:
                        st.write("")
                        if formation['en_attente'] > 0:
                            # Récupérer l'ID de la formation
                            formation_id_query = run_query(
                                "SELECT id FROM formations WHERE nom = %s AND dept_id = %s LIMIT 1", 
                                (formation['formation'], DEPARTEMENT_ID)
                            )
                            if formation_id_query:
                                formation_id = formation_id_query[0]['id']
                                if st.button(f"Tout Valider", 
                                           key=f"val_all_{formation_id}", 
                                           use_container_width=True,
                                           type="primary"):
                                    if valider_tous_examens_formation(formation_id, date_debut, date_fin):
                                        st.success(f"✓ Tous les examens validés!")
                                        st.rerun()
                        else:
                            st.markdown("""
                            <div style="text-align: center; padding: 10px; background: #d4edda; border-radius: 6px;">
                                <div style="font-weight: 600; color: #2e7d32;">✅</div>
                                <div style="font-size: 11px; color: #2e7d32;">Complètement validé</div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Graphique de synthèse
            st.markdown('<div class="section-header">📊 Synthèse de Validation</div>', unsafe_allow_html=True)
            
            if not df_stats.empty:
                fig = px.bar(df_stats, x='formation', y=['confirmes', 'en_attente', 'annules'],
                            title="",
                            labels={'value': "Nombre d'examens", 'formation': 'Formation', 'variable': 'Statut'},
                            barmode='stack',
                            color_discrete_sequence=['#4CAF50', '#FFC107', '#F44336'])
                
                fig.update_layout(
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#333'),
                    xaxis=dict(
                        tickangle=-45,
                        gridcolor='#f0f0f0'
                    ),
                    yaxis=dict(
                        gridcolor='#f0f0f0'
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)

def render_statistiques_departement():
    """Page: Statistiques du Département"""
    st.title("📊 Statistiques du Département")
    st.markdown(f"**Analyse détaillée des performances du département {departement_nom}**")
    
    tab1, tab2, tab3 = st.tabs(["📈 Vue Globale", "👨‍🏫 Ressources Humaines", "🏫 Ressources Matérielles"])
    
    with tab1:
        with st.spinner("Chargement des données..."):
            examens = get_examens_departement_optimise(DEPARTEMENT_ID, date_debut, date_fin)
        
        if examens:
            df_examens = pd.DataFrame(examens)
            
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            kpis = [
                ("Total Examens", len(df_examens), "📊", "#3949ab"),
                ("Formations", df_examens['formation'].nunique(), "🎓", "#2196F3"),
                ("Salles utilisées", df_examens['salle'].nunique(), "🏫", "#4CAF50"),
                ("Professeurs", df_examens['professeur'].nunique(), "👨‍🏫", "#FF9800")
            ]
            
            for i, (label, value, icon, color) in enumerate(kpis):
                with [col1, col2, col3, col4][i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div class="metric-value">{value}</div>
                            <div style="font-size: 24px; color: {color};">{icon}</div>
                        </div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Graphiques
            st.markdown('<div class="section-header">📈 Visualisations</div>', unsafe_allow_html=True)
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Répartition par statut
                statuts = df_examens['statut'].value_counts().reset_index()
                statuts.columns = ['statut', 'count']
                
                if not statuts.empty:
                    fig = px.pie(statuts, values='count', names='statut',
                                title="Répartition par Statut", hole=0.3,
                                color_discrete_map={'planifié': '#FFC107', 'confirmé': '#4CAF50', 'annulé': '#F44336'})
                    fig.update_layout(showlegend=True, height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                # Charge par jour
                df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
                charge_jour = df_examens.groupby('date_examen').size().reset_index(name='nb_examens')
                
                if not charge_jour.empty:
                    fig = px.line(charge_jour, x='date_examen', y='nb_examens',
                                 title="Charge Journalière", markers=True,
                                 color_discrete_sequence=['#3949ab'])
                    fig.update_layout(height=300, xaxis_title="Date", yaxis_title="Examens")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        with st.spinner("Chargement des données RH..."):
            professeurs = get_professeurs_departement_simple(DEPARTEMENT_ID)
        
        if professeurs:
            st.markdown('<div class="section-header">👨‍🏫 Liste des Professeurs</div>', unsafe_allow_html=True)
            
            df_profs = pd.DataFrame(professeurs)
            st.dataframe(
                df_profs,
                column_config={
                    "nom_complet": "Professeur",
                    "specialite": "Spécialité"
                },
                use_container_width=True
            )
    
    with tab3:
        with st.spinner("Chargement des données matérielles..."):
            occupation = get_occupation_salles_departement_simple(DEPARTEMENT_ID, date_debut, date_fin)
        
        if occupation:
            st.markdown('<div class="section-header">🏫 Occupation des Salles</div>', unsafe_allow_html=True)
            
            df_occupation = pd.DataFrame(occupation)
            st.dataframe(
                df_occupation,
                column_config={
                    "type": "Type",
                    "salle": "Salle",
                    "capacite": "Capacité",
                    "nb_examens": "Nb Examens"
                },
                use_container_width=True
            )

def render_gestion_professeurs():
    """Page: Gestion des Professeurs du Département"""
    st.title("👨‍🏫 Gestion des Professeurs du Département")
    st.markdown(f"**Gestion des ressources humaines pour le département {departement_nom}**")
    
    with st.spinner("Chargement des professeurs..."):
        professeurs = get_professeurs_departement_simple(DEPARTEMENT_ID)
    
    if professeurs:
        df_profs = pd.DataFrame(professeurs)
        
        # Statistiques globales
        st.markdown('<div class="section-header">📊 Vue d\'ensemble</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        stats_profs = [
            ("Nombre de professeurs", len(df_profs), "👨‍🏫", "#3949ab"),
            ("Spécialités uniques", df_profs['specialite'].nunique(), "🎯", "#4CAF50"),
            ("Données disponibles", "✅", "📊", "#FF9800")
        ]
        
        for i, (label, value, icon, color) in enumerate(stats_profs):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div class="metric-value">{value}</div>
                        <div style="font-size: 24px; color: {color};">{icon}</div>
                    </div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Recherche
        st.markdown('<div class="section-header">🔍 Recherche de Professeurs</div>', unsafe_allow_html=True)
        
        recherche_nom = st.text_input("Rechercher par nom")
        
        if recherche_nom:
            df_filtre = df_profs[df_profs['nom_complet'].str.contains(recherche_nom, case=False, na=False)]
        else:
            df_filtre = df_profs
        
        # Tableau des professeurs
        st.markdown('<div class="section-header">📋 Liste des Professeurs</div>', unsafe_allow_html=True)
        
        st.dataframe(
            df_filtre,
            column_config={
                "nom_complet": "Professeur",
                "specialite": "Spécialité"
            },
            use_container_width=True
        )
        
        # Export
        st.markdown('<div class="section-header">📤 Export des Données</div>', unsafe_allow_html=True)
        
        csv_data = df_profs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"professeurs_{departement_nom}.csv",
            mime="text/csv"
        )

def render_planning_departement():
    """Page: Planning Complet du Département"""
    st.title("📅 Planning Complet du Département")
    st.markdown(f"**Consultation du planning global pour le département {departement_nom}**")
    
    # Sélection de l'affichage
    display_mode = st.radio(
        "Mode d'affichage",
        ["📋 Vue Tableau", "📊 Vue Calendrier"],
        horizontal=True
    )
    
    with st.spinner("Chargement du planning..."):
        examens = get_examens_departement_optimise(DEPARTEMENT_ID, date_debut, date_fin)
    
    if examens:
        df_examens = pd.DataFrame(examens)
        
        if display_mode == "📋 Vue Tableau":
            # Filtres
            col1, col2, col3 = st.columns(3)
            
            with col1:
                formation_options = ['Toutes'] + sorted(df_examens['formation'].unique().tolist())
                formation_filter = st.selectbox("Formation", formation_options)
            
            with col2:
                statut_options = ['Tous'] + sorted(df_examens['statut'].unique().tolist())
                statut_filter = st.selectbox("Statut", statut_options)
            
            with col3:
                salle_options = ['Toutes'] + sorted(df_examens['salle'].unique().tolist())
                salle_filter = st.selectbox("Salle", salle_options)
            
            # Appliquer les filtres
            df_filtered = df_examens.copy()
            
            if formation_filter != 'Toutes':
                df_filtered = df_filtered[df_filtered['formation'] == formation_filter]
            
            if statut_filter != 'Tous':
                df_filtered = df_filtered[df_filtered['statut'] == statut_filter]
            
            if salle_filter != 'Toutes':
                df_filtered = df_filtered[df_filtered['salle'] == salle_filter]
            
            # Afficher le tableau
            st.dataframe(
                df_filtered[['date_examen', 'heure_debut', 'heure_fin', 'module', 'formation', 
                           'professeur', 'salle', 'nb_etudiants', 'statut']],
                column_config={
                    "date_examen": "Date",
                    "heure_debut": "Heure début",
                    "heure_fin": "Heure fin",
                    "module": "Module",
                    "formation": "Formation",
                    "professeur": "Professeur",
                    "salle": "Salle",
                    "nb_etudiants": "Étudiants",
                    "statut": "Statut"
                },
                use_container_width=True
            )
        
        elif display_mode == "📊 Vue Calendrier":
            # Grouper par date
            df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
            dates_uniques = sorted(df_examens['date_examen'].unique())
            
            for date in dates_uniques:  # Afficher toutes les dates
                df_date = df_examens[df_examens['date_examen'] == date]
                
                with st.expander(f"📅 {date.strftime('%A %d %B %Y')} ({len(df_date)} examens)"):
                    for _, exam in df_date.iterrows():
                        st.markdown('<div class="examen-card">', unsafe_allow_html=True)
                        col_ex1, col_ex2 = st.columns([3, 1])
                        
                        with col_ex1:
                            st.markdown(f"""
                            <div style="font-weight: 600; font-size: 16px; color: #1a237e;">{exam['module'][:50]}</div>
                            <div style="color: #666; margin-bottom: 8px;">{exam['formation']}</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                <span class="tag tag-warning">⏰ {exam['heure_debut']} - {exam['heure_fin']}</span>
                                <span class="tag tag-info">👨‍🏫 {exam['professeur'] or 'Non assigné'}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_ex2:
                            if exam['statut'] == 'confirmé':
                                status_class = "status-confirmed"
                            elif exam['statut'] == 'annulé':
                                status_class = "status-cancelled"
                            else:
                                status_class = "status-pending"
                            
                            st.markdown(f"""
                            <div style="text-align: right;">
                                <span class="{status_class}" style="display: block; margin-bottom: 8px;">{exam['statut']}</span>
                                <div style="font-size: 12px; color: #666;">🏫 {exam['salle']}</div>
                                <div style="font-size: 12px; color: #666;">👥 {int(exam['nb_etudiants'])}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        st.markdown('<div class="section-header">📤 Export du Planning</div>', unsafe_allow_html=True)
        
        csv_data = df_examens.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"planning_{departement_nom}_{date_debut}_{date_fin}.csv",
            mime="text/csv"
        )
    
    else:
        st.info("ℹ️ Aucun examen trouvé pour la période sélectionnée.")

# ============================================================================
# CONFIGURATION INITIALE
# ============================================================================

# Charger les secrets
secrets = load_secrets()

# Initialiser la connexion
with st.spinner("Connexion à la base de données..."):
    conn = init_connection()

if not conn:
    st.error("❌ Impossible de se connecter à la base de données.")
    st.stop()

# Récupérer le département
with st.spinner("Récupération des informations du département..."):
    departement_info = get_departement_chef(CHEF_ID)

if not departement_info:
    st.error("❌ Vous n'êtes pas responsable d'un département.")
    st.info("Veuillez contacter l'administrateur pour vous assigner un département.")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

DEPARTEMENT_ID = departement_info['id']
departement_nom = departement_info['nom']

# ============================================================================
# SIDEBAR AVEC PÉRIODE 2025-2026
# ============================================================================

with st.sidebar:
    # En-tête sidebar
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.markdown('<div class="user-avatar">👨‍💼</div>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="color: white; margin-bottom: 5px;">{st.session_state.nom_complet}</h3>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: white; margin: 0; font-size: 14px;">Chef de Département</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📋 Navigation</div>', unsafe_allow_html=True)
    
    menu = st.radio(
        "Menu",
        ["🏠 Tableau de Bord", 
         "✅ Validation EDT", 
         "📊 Statistiques Département",
         "👨‍🏫 Gestion Professeurs",
         "📅 Planning Département"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Période d'analyse limitée à 2025-2026
    st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">📅 Période d\'analyse (2025-2026)</div>', unsafe_allow_html=True)
    
    # Définir les dates limites
    min_date = datetime(2025, 1, 1).date()
    max_date = datetime(2026, 12, 31).date()
    
    date_debut = st.date_input(
        "Date début", 
        value=datetime(2025, 1, 1).date(),
        min_value=min_date,
        max_value=max_date
    )
    
    date_fin = st.date_input(
        "Date fin", 
        value=datetime(2026, 6, 30).date(),
        min_value=date_debut,
        max_value=max_date
    )
    
    # Afficher la durée
    delta = (date_fin - date_debut).days
    st.caption(f"**Durée:** {delta} jours")
    
    st.markdown("---")
    
    # Options de performance
    st.markdown('<div style="font-weight: 600; color: #1a237e; margin-bottom: 1rem;">⚡ Options</div>', unsafe_allow_html=True)
    
    if st.button("🗑️ Effacer le cache", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.success("Cache effacé!")
        st.rerun()
    
    if st.button("🔄 Actualiser", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    # Déconnexion
    if st.button("🚪 Déconnexion", use_container_width=True, type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/log.py")

# ============================================================================
# EN-TÊTE PRINCIPAL
# ============================================================================

# Titre principal
col_title, col_dept = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 1rem;">
        <div style="font-size: 32px;">👨‍💼</div>
        <div>
            <h1 style="margin: 0; color: #1a237e;">Tableau de Bord Chef de Département</h1>
            <p style="margin: 0; color: #666; font-size: 14px;">Gestion stratégique du département {departement_nom} - Année scolaire 2025-2026</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_dept:
    st.markdown(f"""
    <div class="metric-card" style="text-align: center;">
        <div class="metric-value" style="color: #3949ab;">{departement_nom}</div>
        <div class="metric-label">Département</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# ROUTAGE DES PAGES
# ============================================================================

# Afficher un indicateur de chargement pour les pages lourdes
if menu in ["✅ Validation EDT", "📊 Statistiques Département"]:

if menu == "🏠 Tableau de Bord":
    render_tableau_de_bord()
    
elif menu == "✅ Validation EDT":
    render_validation_edt()
    
elif menu == "📊 Statistiques Département":
    render_statistiques_departement()
    
elif menu == "👨‍🏫 Gestion Professeurs":
    render_gestion_professeurs()
    
elif menu == "📅 Planning Département":
    render_planning_departement()

# ============================================================================
# PIED DE PAGE
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="font-weight: 600; color: #1a237e; margin-bottom: 5px;">Tableau de Bord Chef de Département • {departement_nom}</div>
            <div style="color: #666; font-size: 11px;">Année Scolaire 2025-2026 • Version Complète</div>
        </div>
        <div style="text-align: right;">
            <div style="color: #666; font-size: 11px;">Période: {date_debut} au {date_fin}</div>
            <div style="color: #666; font-size: 11px;">Dernière mise à jour: {datetime.now().strftime('%H:%M')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
