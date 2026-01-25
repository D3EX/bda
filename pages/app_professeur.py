import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, time, timedelta
import numpy as np
import io
import os
import toml
import plotly.express as px
import plotly.graph_objects as go
import time

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord Professeur | Planification Examens",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLE PERSONNALISÉ ===
st.markdown("""
<style>
    /* Style global */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Cards styling */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        text-align: center;
        border-left: 5px solid #3498db;
    }
    
    /* Exam cards */
    .exam-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border-left: 5px solid;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    
    .exam-card.responsable {
        border-left-color: #3498db;
        background: linear-gradient(90deg, rgba(52, 152, 219, 0.1) 0%, rgba(255, 255, 255, 1) 50%);
    }
    
    .exam-card.surveillant {
        border-left-color: #2ecc71;
        background: linear-gradient(90deg, rgba(46, 204, 113, 0.1) 0%, rgba(255, 255, 255, 1) 50%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #d3d3d3 100%);
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .badge-primary {
        background: #3498db;
        color: white;
    }
    
    .badge-success {
        background: #2ecc71;
        color: white;
    }
    
    .badge-warning {
        background: #f39c12;
        color: white;
    }
    
    /* Progress bar */
    .progress-container {
        background: #ecf0f1;
        border-radius: 10px;
        height: 10px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #3498db 0%, #2ecc71 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom tabs */
    .custom-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    
    .custom-tab {
        flex: 1;
        text-align: center;
        padding: 0.8rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .custom-tab.active {
        background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
        color: white;
        box-shadow: 0 3px 10px rgba(52, 152, 219, 0.2);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        border: none !important;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
    }
    
    /* Calendar style */
    .calendar-day {
        text-align: center;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.1rem;
        font-weight: bold;
    }
    
    .calendar-day.has-exam {
        background: #3498db;
        color: white;
    }
    
    /* Loading indicator */
    .loading-spinner {
        text-align: center;
        padding: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# HIDE THE PAGE NAVIGATION
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# === VÉRIFICATION DE SESSION ===
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/log.py")
    st.stop()

if 'role' not in st.session_state or st.session_state.role != 'professeur':
    st.error(f"⛔ Cette page est réservée aux professeurs.")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

PROFESSEUR_ID = st.session_state.user_id

# === FONCTIONS AUXILIAIRES OPTIMISÉES ===
def load_secrets():
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

secrets = load_secrets()

@st.cache_resource(ttl=3600)
def init_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            pool_name="profpool",
            pool_size=3,
            pool_reset_session=True,
            buffered=True
        )
        return conn
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

conn = init_connection()

def run_query(query, params=None, fetch=True):
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            # Charger par batch pour optimisation
            batch_size = 500
            results = []
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
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

@st.cache_data(ttl=300, show_spinner="Chargement des informations...")
def get_professeur_info(prof_id):
    """Récupérer les informations du professeur"""
    return run_query("""
        SELECT p.nom, p.prenom, p.specialite, p.heures_service, d.nom as departement
        FROM professeurs p
        LEFT JOIN departements d ON p.dept_id = d.id
        WHERE p.id = %s
    """, (prof_id,))

@st.cache_data(ttl=300, show_spinner="Chargement des examens...")
def get_examens_professeur_optimise(prof_id, date_debut, date_fin, role=None):
    """Récupérer les examens du professeur (optimisé)"""
    query = """
        SELECT 
            e.id,
            e.date_examen,
            e.heure_debut,
            e.heure_fin,
            e.duree_minutes,
            e.statut,
            e.session,
            e.salle_id,
            m.nom as module,
            f.nom as formation,
            CASE WHEN e.professeur_id = %s THEN 'Responsable' ELSE 'Surveillant' END as role
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        WHERE (e.professeur_id = %s OR e.surveillant_id = %s)
        AND e.date_examen BETWEEN %s AND %s
    """
    
    params = [prof_id, prof_id, prof_id, date_debut, date_fin]
    
    if role == "Responsable":
        query += " AND e.professeur_id = %s"
        params.append(prof_id)
    elif role == "Surveillant":
        query += " AND e.surveillant_id = %s"
        params.append(prof_id)
    
    query += " ORDER BY e.date_examen, e.heure_debut"
    
    return run_query(query, params)

@st.cache_data(ttl=300, show_spinner=False)
def get_statistiques_professeur(prof_id, date_debut, date_fin):
    """Statistiques du professeur"""
    result = run_query("""
        SELECT 
            COUNT(*) as total_examens,
            SUM(CASE WHEN e.professeur_id = %s THEN 1 ELSE 0 END) as responsable,
            SUM(CASE WHEN e.surveillant_id = %s THEN 1 ELSE 0 END) as surveillant,
            SUM(e.duree_minutes) as total_minutes
        FROM examens e
        WHERE (e.professeur_id = %s OR e.surveillant_id = %s)
        AND e.date_examen BETWEEN %s AND %s
        AND e.statut = 'confirmé'
    """, (prof_id, prof_id, prof_id, prof_id, date_debut, date_fin))
    
    return result[0] if result else {}

# === HEADER PRINCIPAL ===
professeur_info = get_professeur_info(PROFESSEUR_ID)
if professeur_info:
    prof = professeur_info[0]
else:
    st.error("Professeur non trouvé")
    st.stop()

st.markdown("""
<div class="header-container">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem; display: flex; align-items: center; gap: 10px;">
                👨‍🏫 Tableau de Bord Professeur
            </h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 1rem;">
                Gestion intelligente de votre planning d'examens
            </p>
        </div>
        <div style="text-align: right;">
            <div style="background: rgba(255, 255, 255, 0.1); padding: 8px 15px; border-radius: 8px;">
                <div style="font-size: 0.9rem; opacity: 0.8;">Connecté en tant que</div>
                <div style="font-weight: bold; font-size: 1.1rem;">{}</div>
            </div>
        </div>
    </div>
</div>
""".format(st.session_state.nom_complet), unsafe_allow_html=True)

# === SIDEBAR REDESIGNÉE ===
with st.sidebar:
    # Photo de profil
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #ffffff 0%, #bdc3c7 100%); 
                     border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                     margin: 0 auto 10px; font-size: 2rem;">
                👨‍🏫
            </div>
            <div style="font-weight: bold; font-size: 1.1rem;">{}</div>
            <div style="color: rgba(0, 0, 0, 0.8); font-size: 0.9rem;">Professeur</div>
        </div>
        """.format(f"{prof['prenom']} {prof['nom'][0]}."), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📍 Navigation")
    menu_options = {
        "📊 Tableau de Bord": "dashboard",
        "📅 Mes Examens": "examens",
        "📈 Statistiques": "statistiques",
        "📤 Export": "export",
        "⚙️ Paramètres": "parametres"
    }
    
    selected_menu = st.radio(
        "",
        list(menu_options.keys()),
        label_visibility="collapsed",
        key="nav_menu"
    )
    
    st.markdown("---")
    
    # Période 2025-2026
    st.markdown("### 📅 Période d'analyse (2025-2026)")
    
    # Définir les dates limites
    min_date = datetime(2025, 1, 1).date()
    max_date = datetime(2026, 12, 31).date()
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_debut = st.date_input(
            "Début", 
            value=datetime(2025, 1, 1).date(),
            min_value=min_date,
            max_value=max_date,
            key="date_debut", 
            label_visibility="collapsed"
        )
    with col_d2:
        date_fin = st.date_input(
            "Fin", 
            value=datetime(2026, 6, 30).date(),
            min_value=date_debut,
            max_value=max_date,
            key="date_fin", 
            label_visibility="collapsed"
        )
    
    # Actions
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_act2:
        if st.button("🚪 Déconnexion", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")

# === CONTENU PRINCIPAL ===
if selected_menu == "📊 Tableau de Bord":
    # Charger les statistiques
    with st.spinner("Calcul des statistiques..."):
        stats = get_statistiques_professeur(PROFESSEUR_ID, date_debut, date_fin)
        examens = get_examens_professeur_optimise(PROFESSEUR_ID, date_debut, date_fin)
    
    # Métriques rapides
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_heures = (stats.get('total_minutes', 0) / 60) if stats else 0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">📊</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{total_heures:.1f}h</div>
            <div style="color: #7f8c8d;">Heures cette période</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_examens = stats.get('total_examens', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">👥</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{total_examens}</div>
            <div style="color: #7f8c8d;">Examens totaux</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        responsable_examens = stats.get('responsable', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">📚</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{responsable_examens}</div>
            <div style="color: #7f8c8d;">En tant que responsable</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        surveillant_examens = stats.get('surveillant', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">🎯</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{surveillant_examens}</div>
            <div style="color: #7f8c8d;">En tant que surveillant</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Section principale en deux colonnes
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Calendrier des examens à venir
        st.markdown("### 📅 Prochains examens")
        
        if examens:
            for exam in examens[:5]:  # Limiter à 5 pour l'affichage
                role_class = "responsable" if exam['role'] == 'Responsable' else "surveillant"
                badge_color = "badge-primary" if exam['role'] == 'Responsable' else "badge-success"
                
                st.markdown(f"""
                <div class="exam-card {role_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="font-weight: bold; font-size: 1.1rem;">{exam['module']}</div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">{exam['formation']}</div>
                        </div>
                        <span class="badge {badge_color}">{exam['role']}</span>
                    </div>
                    <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 0.9rem;">
                        <div>📅 {exam['date_examen']}</div>
                        <div>⏰ {exam['heure_debut']} - {exam['heure_fin']}</div>
                        <div>⏱️ {exam['duree_minutes']} min</div>
                    </div>
                    <div style="margin-top: 5px; font-size: 0.9rem;">
                        🏫 Salle {exam.get('salle_id', 'Non assignée')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucun examen prévu pour cette période.")
        
        # Graphique de charge
        st.markdown("### 📈 Répartition par mois")
        
        if examens:
            df_examens = pd.DataFrame(examens)
            df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
            df_examens['mois'] = df_examens['date_examen'].dt.strftime('%b %Y')
            
            examens_par_mois = df_examens.groupby('mois').size().reset_index(name='count')
            
            fig = px.bar(
                examens_par_mois, 
                x='mois', 
                y='count',
                color='count',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        # Profil professeur
        st.markdown("### 👤 Profil Professeur")
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%); 
                     border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                     margin: 0 auto 15px; font-size: 2.5rem; color: white;">
                {prof['prenom'][0]}{prof['nom'][0]}
            </div>
            <div style="font-weight: bold; font-size: 1.2rem;">{prof['prenom']} {prof['nom']}</div>
            <div style="color: #3498db; font-size: 0.9rem;">{prof.get('departement', 'Non assigné')}</div>
        </div>
        
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span>🎓 Spécialité</span>
                <span style="font-weight: bold;">{prof['specialite']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span>⏰ Heures service</span>
                <span style="font-weight: bold;">{prof['heures_service']}h</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>👨‍🏫 ID</span>
                <span style="font-weight: bold;">{PROFESSEUR_ID}</span>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <div style="font-size: 0.9rem; margin-bottom: 5px;">Taux d'occupation</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {min(100, (total_examens * 100) / 50)}%"></div>
            </div>
            <div style="text-align: right; font-size: 0.8rem; color: #7f8c8d;">
                {min(100, (total_examens * 100) / 50):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prochain examen
        st.markdown("### ⏳ Prochain examen")
        
        if examens:
            # Trouver le prochain examen à venir
            now = datetime.now()
            examens_futurs = [e for e in examens if pd.to_datetime(e['date_examen']) >= now]
            
            if examens_futurs:
                exam = examens_futurs[0]
                st.markdown(f"""
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 2.5rem; margin-bottom: 10px;">📝</div>
                    <div style="font-weight: bold; font-size: 1.2rem; margin-bottom: 5px;">
                        {exam['module']}
                    </div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #3498db; margin: 10px 0;">
                        {exam['date_examen']}
                    </div>
                    <div style="color: #7f8c8d;">
                        ⏰ {exam['heure_debut']} - {exam['heure_fin']}
                    </div>
                    <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                        <div style="font-size: 0.9rem;">⏱️ Durée: {exam['duree_minutes']} minutes</div>
                        <div style="font-size: 0.9rem; margin-top: 5px;">🎯 Rôle: {exam['role']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 30px 20px;">
                    <div style="font-size: 3rem; margin-bottom: 10px;">🎉</div>
                    <div style="font-weight: bold; color: #2ecc71;">Aucun examen prévu</div>
                    <div style="color: #7f8c8d; margin-top: 5px;">Profitez de votre temps libre !</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 30px 20px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">📭</div>
                <div style="font-weight: bold; color: #e74c3c;">Aucun examen trouvé</div>
                <div style="color: #7f8c8d; margin-top: 5px;">Pour la période sélectionnée</div>
            </div>
            """, unsafe_allow_html=True)

elif selected_menu == "📅 Mes Examens":
    st.markdown("### 📅 Mes Examens")
    
    # Filtres avancés
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        role_filter = st.selectbox(
            "Rôle",
            ["Tous", "Responsable", "Surveillant"],
            key="role_filter"
        )
    
    with col_f2:
        session_filter = st.selectbox(
            "Session",
            ["Toutes", "Normal", "Rattrapage"],
            key="session_filter"
        )
    
    with col_f3:
        statut_filter = st.selectbox(
            "Statut",
            ["Tous", "confirmé", "planifié", "annulé"],
            key="statut_filter"
        )
    
    # Récupérer les examens avec filtres
    with st.spinner("Chargement des examens..."):
        examens = get_examens_professeur_optimise(
            PROFESSEUR_ID, 
            date_debut, 
            date_fin,
            role=role_filter if role_filter != "Tous" else None
        )
        
        # Appliquer les autres filtres localement
        if examens:
            if session_filter != "Toutes":
                examens = [e for e in examens if e['session'] == session_filter]
            
            if statut_filter != "Tous":
                examens = [e for e in examens if e['statut'] == statut_filter]
    
    if examens:
        # Métriques
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        total_examens = len(examens)
        responsable_examens = len([e for e in examens if e['role'] == 'Responsable'])
        surveillant_examens = len([e for e in examens if e['role'] == 'Surveillant'])
        total_heures = sum(e['duree_minutes'] for e in examens) / 60
        
        with col_m1:
            st.metric("Total Examens", total_examens)
        with col_m2:
            st.metric("En tant que Responsable", responsable_examens)
        with col_m3:
            st.metric("En tant que Surveillant", surveillant_examens)
        with col_m4:
            st.metric("Heures totales", f"{total_heures:.1f}h")
        
        st.markdown("---")
        
        # Vue calendrier ou liste
        view_mode = st.radio(
            "Mode d'affichage",
            ["📋 Liste", "📅 Calendrier"],
            horizontal=True,
            key="view_mode"
        )
        
        if view_mode == "📋 Liste":
            # Affichage en liste avec pagination
            items_per_page = 10
            total_pages = max(1, (len(examens) + items_per_page - 1) // items_per_page)
            page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="page_num")
            
            start_idx = (page_number - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(examens))
            
            st.caption(f"Affichage des examens {start_idx + 1} à {end_idx} sur {len(examens)}")
            
            for idx in range(start_idx, end_idx):
                exam = examens[idx]
                role_class = "responsable" if exam['role'] == 'Responsable' else "surveillant"
                badge_color = "badge-primary" if exam['role'] == 'Responsable' else "badge-success"
                statut_color = "badge-success" if exam['statut'] == 'confirmé' else "badge-warning"
                
                col_ex1, col_ex2 = st.columns([4, 1])
                
                with col_ex1:
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 10px; background: {'#f8f9fa' if exam['role'] == 'Responsable' else '#f0f7ff'}; 
                             border-left: 4px solid {'#3498db' if exam['role'] == 'Responsable' else '#2ecc71'};">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <div style="font-weight: bold; font-size: 1.1rem;">{exam['module']}</div>
                                <div style="color: #7f8c8d; font-size: 0.9rem;">{exam['formation']}</div>
                            </div>
                            <div style="display: flex; gap: 5px;">
                                <span class="badge {badge_color}">{exam['role']}</span>
                                <span class="badge {statut_color}">{exam['statut']}</span>
                            </div>
                        </div>
                        <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 0.9rem;">
                            <div><span style="color: #7f8c8d;">📅</span> {exam['date_examen']}</div>
                            <div><span style="color: #7f8c8d;">⏰</span> {exam['heure_debut']} - {exam['heure_fin']}</div>
                            <div><span style="color: #7f8c8d;">⏱️</span> {exam['duree_minutes']} min</div>
                        </div>
                        <div style="margin-top: 5px; font-size: 0.9rem;">
                            <span style="color: #7f8c8d;">🏫</span> Salle {exam.get('salle_id', 'Non assignée')} | 
                            <span style="color: #7f8c8d;">🎯</span> {exam['session']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_ex2:
                    if st.button("📋 Détails", key=f"detail_{exam['id']}", use_container_width=True):
                        st.session_state['selected_exam'] = exam['id']
                        st.rerun()
                
                st.markdown("---")
        else:
            # Affichage calendrier simplifié
            st.markdown("### 📅 Vue Calendrier")
            
            if examens:
                df_examens = pd.DataFrame(examens)
                df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
                
                # Afficher par semaine
                df_examens['semaine'] = df_examens['date_examen'].dt.strftime('Semaine %U')
                
                st.dataframe(
                    df_examens[['date_examen', 'heure_debut', 'module', 'formation', 'role', 'statut']],
                    column_config={
                        "date_examen": "Date",
                        "heure_debut": "Heure",
                        "module": "Module",
                        "formation": "Formation",
                        "role": "Rôle",
                        "statut": "Statut"
                    },
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("📭 Aucun examen trouvé pour les critères sélectionnés.")

elif selected_menu == "📈 Statistiques":
    st.markdown("### 📈 Statistiques Détaillées")
    
    with st.spinner("Calcul des statistiques..."):
        stats = get_statistiques_professeur(PROFESSEUR_ID, date_debut, date_fin)
        examens = get_examens_professeur_optimise(PROFESSEUR_ID, date_debut, date_fin)
    
    if examens:
        df_examens = pd.DataFrame(examens)
        df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
        
        # Graphiques en grille 2x2
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Répartition par rôle
            st.markdown("#### 📊 Répartition par rôle")
            
            role_counts = df_examens['role'].value_counts()
            
            fig1 = go.Figure(data=[go.Pie(
                labels=role_counts.index.tolist(),
                values=role_counts.values.tolist(),
                hole=.4,
                marker_colors=['#3498db', '#2ecc71']
            )])
            
            fig1.update_layout(
                height=300,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=1.1
                )
            )
            
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_chart2:
            # Charge mensuelle
            st.markdown("#### 📅 Charge mensuelle")
            
            df_examens['mois'] = df_examens['date_examen'].dt.strftime('%b')
            examens_par_mois = df_examens.groupby('mois').size().reset_index(name='count')
            
            fig2 = go.Figure(data=[
                go.Bar(
                    x=examens_par_mois['mois'],
                    y=examens_par_mois['count'],
                    marker_color='#3498db',
                    text=examens_par_mois['count'],
                    textposition='auto',
                )
            ])
            
            fig2.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        col_chart3, col_chart4 = st.columns(2)
        
        with col_chart3:
            # Répartition par statut
            st.markdown("#### 🎯 Répartition par statut")
            
            statut_counts = df_examens['statut'].value_counts()
            
            fig3 = go.Figure(data=[
                go.Scatter(
                    x=statut_counts.index.tolist(),
                    y=statut_counts.values.tolist(),
                    mode='lines+markers',
                    line=dict(color='#9b59b6', width=3),
                    marker=dict(size=10, color='#9b59b6')
                )
            ])
            
            fig3.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        with col_chart4:
            # Durée moyenne
            st.markdown("#### ⏱️ Durée moyenne par examen")
            
            duree_moyenne = df_examens['duree_minutes'].mean()
            
            fig4 = go.Figure(data=[
                go.Indicator(
                    mode = "gauge+number",
                    value = duree_moyenne,
                    title = {'text': "Minutes"},
                    gauge = {
                        'axis': {'range': [0, 180]},
                        'bar': {'color': "#3498db"},
                        'steps': [
                            {'range': [0, 60], 'color': "#e74c3c"},
                            {'range': [60, 120], 'color': "#f39c12"},
                            {'range': [120, 180], 'color': "#2ecc71"}
                        ]
                    }
                )
            ])
            
            fig4.update_layout(height=300)
            
            st.plotly_chart(fig4, use_container_width=True)
        
        # Tableau récapitulatif
        st.markdown("### 📋 Récapitulatif")
        
        recap_data = {
            'Métrique': ['Total examens', 'Heures totales', 'Responsable', 'Surveillant', 'Durée moyenne'],
            'Valeur': [
                len(df_examens),
                f"{df_examens['duree_minutes'].sum() / 60:.1f}h",
                len(df_examens[df_examens['role'] == 'Responsable']),
                len(df_examens[df_examens['role'] == 'Surveillant']),
                f"{duree_moyenne:.1f} min"
            ]
        }
        
        st.dataframe(pd.DataFrame(recap_data), use_container_width=True, hide_index=True)
    else:
        st.info("📊 Aucune donnée statistique disponible pour cette période.")

elif selected_menu == "📤 Export":
    st.markdown("### 📤 Export du Planning")
    
    with st.spinner("Préparation de l'export..."):
        examens = get_examens_professeur_optimise(PROFESSEUR_ID, date_debut, date_fin)
    
    if examens:
        # Options d'export
        export_type = st.radio(
            "Type d'export",
            ["📋 Planning complet", "📅 Par période", "🎯 Par module"],
            horizontal=True
        )
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            format_export = st.selectbox(
                "Format",
                ["CSV (Excel)", "HTML (Web)", "JSON (Données)"]
            )
        
        with col_exp2:
            include_details = st.multiselect(
                "Inclure",
                ["Détails examen", "Statut", "Rôle", "Session"],
                default=["Détails examen", "Rôle"]
            )
        
        # Conversion en DataFrame
        df_export = pd.DataFrame(examens)
        
        # Aperçu
        with st.expander("👁️ Aperçu des données"):
            st.dataframe(
                df_export[['date_examen', 'heure_debut', 'module', 'formation', 'role', 'statut']],
                use_container_width=True,
                hide_index=True
            )
        
        # Boutons d'export
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📥 Télécharger CSV", use_container_width=True, type="primary"):
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Cliquez pour télécharger",
                    data=csv,
                    file_name=f"planning_professeur_{prof['nom']}_{date_debut}_{date_fin}.csv",
                    mime="text/csv",
                    key="download_csv"
                )
        
        with col_btn2:
            if st.button("🌐 Générer HTML", use_container_width=True):
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Planning {prof['nom']}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                        th {{ background-color: #3498db; color: white; }}
                        .responsable {{ background-color: #d4edda; }}
                        .surveillant {{ background-color: #fff3cd; }}
                    </style>
                </head>
                <body>
                    <h1>📅 Planning d'Examens - {prof['prenom']} {prof['nom']}</h1>
                    <p>Période: {date_debut} au {date_fin}</p>
                    <p>Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    {df_export.to_html(index=False, classes='table')}
                </body>
                </html>
                """
                
                st.download_button(
                    label="💾 Télécharger HTML",
                    data=html_content.encode('utf-8'),
                    file_name=f"planning_professeur_{prof['nom']}.html",
                    mime="text/html"
                )
    else:
        st.info("📭 Aucun examen à exporter pour cette période.")

elif selected_menu == "⚙️ Paramètres":
    st.markdown("### ⚙️ Paramètres du Profil")
    
    # Formulaire de mise à jour
    with st.form("profile_form"):
        col_set1, col_set2 = st.columns(2)
        
        with col_set1:
            nom = st.text_input("Nom", prof['nom'])
            prenom = st.text_input("Prénom", prof['prenom'])
            email = st.text_input("Email", f"{prof['prenom'].lower()}.{prof['nom'].lower()}@universite.fr")
        
        with col_set2:
            telephone = st.text_input("Téléphone", "+33 1 23 45 67 89")
            specialite = st.text_input("Spécialité", prof['specialite'])
            heures_service = st.number_input("Heures de service", value=int(prof['heures_service']), min_value=0, max_value=100)
        
        # Préférences
        st.markdown("### 🔔 Préférences de notification")
        col_pref1, col_pref2 = st.columns(2)
        
        with col_pref1:
            notif_email = st.checkbox("Notifications par email", value=True)
            notif_sms = st.checkbox("Notifications SMS", value=False)
            rappel_examens = st.checkbox("Rappels d'examens", value=True)
        
        with col_pref2:
            jours_rappel = st.slider("Jours avant rappel", 1, 7, 2)
            heure_notif = st.time_input("Heure des notifications", time(8, 0))
            theme = st.selectbox("Thème de l'interface", ["Clair", "Sombre", "Auto"])
        
        # Boutons d'action
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            submit = st.form_submit_button("💾 Enregistrer les modifications", type="primary")
        
        with col_act2:
            reset = st.form_submit_button("🔄 Réinitialiser")
        
        with col_act3:
            cancel = st.form_submit_button("❌ Annuler")
        
        if submit:
            # Ici, vous pourriez ajouter la logique pour mettre à jour la base de données
            st.success("✅ Paramètres mis à jour avec succès !")
            st.cache_data.clear()  # Effacer le cache pour recharger les données

# === FOOTER ===
st.markdown("""
<hr style="margin: 40px 0 20px 0; border: none; border-top: 1px solid #e0e0e0;">

<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 10px;">
        <div>
            <div style="font-weight: bold; color: #2c3e50;">Tableau de Bord Professeur</div>
            <div style="font-size: 0.8rem;">Système de Gestion des Examens</div>
        </div>
        <div>
            <div style="font-weight: bold; color: #2c3e50;">Université</div>
            <div style="font-size: 0.8rem;">Département d'Informatique</div>
        </div>
        <div>
            <div style="font-weight: bold; color: #2c3e50;">Contact</div>
            <div style="font-size: 0.8rem;">support@universite.fr</div>
        </div>
    </div>
    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ecf0f1; font-size: 0.8rem;">
        © 2024-2026 Système de Planification des Examens • Version Optimisée • 
        <span style="color: #3498db;">{}</span>
    </div>
</div>
""".format(prof['prenom'] + " " + prof['nom']), unsafe_allow_html=True)
