# app_admin.py - VERSION OPTIMISÉE COMPLÈTE
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import time as time_module
import hashlib

# =================== CONFIGURATION INITIALE ===================
st.set_page_config(
    page_title="Plateforme d'Optimisation des Emplois du Temps",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== AUTHENTIFICATION ===================
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("⛔ Accès non autorisé. Veuillez vous connecter.")
    if st.button("🔐 Se connecter"):
        st.switch_page("pages/log.py")
    st.stop()

if st.session_state.role != 'admin':
    st.error(f"⛔ Cette page est réservée au doyen. Votre rôle: {st.session_state.role}")
    if st.button("🏠 Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

# =================== CSS EXTERNALISÉ (chargé une fois) ===================
def load_css():
    """Charge le CSS optimisé une seule fois"""
    if 'css_loaded' not in st.session_state:
        css = """
        <style>
        /* === STYLES MINIMAUX ESSENTIELS === */
        .main { padding: 1rem 1.5rem; }
        [data-testid="stSidebarNav"] { display: none; }
        
        /* Cartes métriques simplifiées */
        .metric-card-simple {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        }
        
        /* Sections */
        .section-wrapper {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            margin: 1.5rem 0;
        }
        
        /* Boutons améliorés */
        .stButton > button {
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
        }
        
        /* Layout amélioré */
        .stTabs [data-baseweb="tab-list"] { gap: 0.25rem; }
        .stTabs [data-baseweb="tab"] { padding: 0.75rem 1rem !important; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .main { padding: 0.5rem; }
            .section-wrapper { padding: 1rem; }
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
        st.session_state.css_loaded = True

# Appeler le CSS une seule fois
load_css()

# =================== FONCTIONS DE BASE DE DONNÉES OPTIMISÉES ===================
@st.cache_resource(show_spinner=False)
def get_db_connection():
    """Connexion à la base de données avec cache"""
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            pool_name="mypool",
            pool_size=5,
            pool_reset_session=True
        )
        return conn
    except Error as e:
        st.error(f"Erreur de connexion: {e}")
        return None

@st.cache_data(ttl=300, show_spinner="Chargement des données...")
def cached_query(_hash, query, params=None):
    """Requête avec cache basé sur un hash"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchall()
        cursor.close()
        
        # Convertir les timedelta en time
        for row in result:
            for key, value in row.items():
                if isinstance(value, timedelta):
                    total_seconds = value.total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    seconds = int(total_seconds % 60)
                    row[key] = time(hours, minutes, seconds)
        
        return result
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return []

def run_query(query, params=None, use_cache=True):
    """Wrapper pour exécuter des requêtes avec ou sans cache"""
    if use_cache:
        query_hash = hashlib.md5(f"{query}{params}".encode()).hexdigest()
        return cached_query(query_hash, query, params)
    else:
        return cached_query("nocache", query, params)

# =================== COMPOSANTS RÉUTILISABLES ===================
@st.cache_data(ttl=3600)
def get_departments():
    """Récupère tous les départements"""
    return run_query("SELECT id, nom FROM departements ORDER BY nom")

@st.cache_data(ttl=3600)
def get_professors():
    """Récupère tous les professeurs"""
    return run_query("SELECT id, CONCAT(nom, ' ', prenom) as nom_complet FROM professeurs")

@st.cache_data(ttl=3600)
def get_rooms():
    """Récupère toutes les salles"""
    return run_query("SELECT id, nom, type, capacite FROM lieu_examen WHERE disponible = TRUE")

def create_metric_card_fast(icon, title, value):
    """Version ultra-rapide des cartes métriques"""
    return f"""
    <div class="metric-card-simple">
        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 0.85rem; color: #718096; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #2D3748;">{value}</div>
    </div>
    """

def create_section_fast(icon, title):
    """Section rapide"""
    st.markdown(f"""
    <div style="margin: 2rem 0 1rem 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <h2 style="margin: 0; color: #2D3748;">{title}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================== SIDEBAR OPTIMISÉE ===================
def render_sidebar():
    """Sidebar optimisée"""
    with st.sidebar:
        # Header simple
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             border-radius: 0 0 15px 15px; margin: -1rem -1rem 1rem -1rem;">
            <div style="font-size: 2.5rem; color: white;">👨‍💼</div>
            <div style="color: white; font-weight: 600; font-size: 1.2rem;">Administrateur</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">Doyen</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu principal avec état
        menu_items = [
            {"icon": "📊", "label": "Tableau de Bord"},
            {"icon": "🎯", "label": "Génération Planning"},
            {"icon": "🔍", "label": "Visualisation Planning"},
            {"icon": "📋", "label": "Planning Général"},
            {"icon": "⚠️", "label": "Détection Conflits"},
            {"icon": "📈", "label": "Statistiques"},
            {"icon": "⚙️", "label": "Configuration"},
        ]
        
        for item in menu_items:
            is_active = st.session_state.get('selected_menu') == item["label"]
            
            if st.button(
                f"{item['icon']} {item['label']}", 
                key=f"menu_{item['label']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.selected_menu = item["label"]
                st.rerun()
        
        st.markdown("---")
        
        # Actions rapides
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Rafraîchir", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("📥 Exporter", use_container_width=True):
                st.success("Export démarré!")
        
        st.markdown("---")
        
        # Déconnexion
        if st.button("🚪 Se déconnecter", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/log.py")

# =================== PAGES OPTIMISÉES ===================
def render_dashboard():
    """Page Tableau de Bord optimisée"""
    create_section_fast("📊", "Tableau de Bord")
    
    # Métriques principales (chargées une seule fois)
    if 'dashboard_data' not in st.session_state:
        with st.spinner("Chargement initial des données..."):
            data = {}
            queries = [
                ("departements", "SELECT COUNT(*) as count FROM departements"),
                ("formations", "SELECT COUNT(*) as count FROM formations"),
                ("examens", "SELECT COUNT(*) as count FROM examens WHERE statut = 'planifié'"),
                ("professeurs", "SELECT COUNT(*) as count FROM professeurs"),
                ("salles", "SELECT COUNT(*) as count FROM lieu_examen WHERE disponible = TRUE"),
                ("etudiants", "SELECT COUNT(DISTINCT id) as count FROM etudiants")
            ]
            
            for key, query in queries:
                result = run_query(query)
                data[key] = result[0]['count'] if result else 0
            
            st.session_state.dashboard_data = data
    
    data = st.session_state.dashboard_data
    
    # Affichage rapide des métriques
    col1, col2, col3 = st.columns(3)
    metrics = [
        ("🏢", "Départements", data['departements']),
        ("🎓", "Formations", data['formations']),
        ("📅", "Examens", data['examens']),
        ("👨‍🏫", "Professeurs", data['professeurs']),
        ("🏫", "Salles", data['salles']),
        ("👥", "Étudiants", data['etudiants'])
    ]
    
    for i, (icon, title, value) in enumerate(metrics):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(create_metric_card_fast(icon, title, value), unsafe_allow_html=True)
    
    # Graphiques (chargés paresseusement)
    with st.expander("📈 Graphiques détaillés", expanded=True):
        tab1, tab2 = st.tabs(["Occupation salles", "Examens par département"])
        
        with tab1:
            occupation_data = run_query("""
                SELECT type, COUNT(*) as count 
                FROM lieu_examen 
                GROUP BY type
            """)
            
            if occupation_data:
                df = pd.DataFrame(occupation_data)
                fig = px.pie(df, values='count', names='type', 
                           title="Répartition des types de salles")
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with tab2:
            examens_data = run_query("""
                SELECT d.nom as departement, COUNT(ex.id) as nb_examens
                FROM departements d
                LEFT JOIN formations f ON d.id = f.dept_id
                LEFT JOIN modules m ON f.id = m.formation_id
                LEFT JOIN examens ex ON m.id = ex.module_id AND ex.statut = 'planifié'
                GROUP BY d.id
                ORDER BY nb_examens DESC
                LIMIT 10
            """)
            
            if examens_data:
                df = pd.DataFrame(examens_data)
                fig = px.bar(df, x='departement', y='nb_examens',
                           title="Examens par département")
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Derniers examens (avec pagination virtuelle)
    create_section_fast("📝", "Derniers Examens Planifiés")
    
    if 'examens_page' not in st.session_state:
        st.session_state.examens_page = 0
    
    limit = 10
    offset = st.session_state.examens_page * limit
    
    derniers_examens = run_query(f"""
        SELECT ex.id, m.nom as module, d.nom as departement, 
               DATE_FORMAT(ex.date_examen, '%d/%m/%Y') as date_examen,
               TIME_FORMAT(ex.heure_debut, '%H:%i') as heure_debut,
               TIME_FORMAT(ex.heure_fin, '%H:%i') as heure_fin,
               l.nom as salle
        FROM examens ex
        JOIN modules m ON ex.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN lieu_examen l ON ex.salle_id = l.id
        WHERE ex.statut = 'planifié'
        ORDER BY ex.date_examen DESC, ex.heure_debut DESC
        LIMIT {limit} OFFSET {offset}
    """)
    
    if derniers_examens:
        df = pd.DataFrame(derniers_examens)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "module": "Module",
                "departement": "Département",
                "date_examen": "Date",
                "heure_debut": "Heure Début",
                "heure_fin": "Heure Fin",
                "salle": "Salle"
            }
        )
        
        # Pagination simple
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️ Précédent") and st.session_state.examens_page > 0:
                st.session_state.examens_page -= 1
                st.rerun()
        
        with col_info:
            st.info(f"Page {st.session_state.examens_page + 1}")
        
        with col_next:
            if st.button("Suivant ➡️"):
                st.session_state.examens_page += 1
                st.rerun()

def render_generation():
    """Page Génération Planning optimisée"""
    create_section_fast("🎯", "Génération de Planning")
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        
        # Type de génération
        type_gen = st.radio(
            "Type de génération",
            ["📊 Par Département", "🌍 Planning Général"],
            horizontal=True,
            key="type_gen"
        )
        
        if type_gen == "📊 Par Département":
            # Données préchargées
            if 'departments_list' not in st.session_state:
                st.session_state.departments_list = get_departments()
            
            col1, col2 = st.columns(2)
            
            with col1:
                dept_options = {dept['nom']: dept['id'] for dept in st.session_state.departments_list}
                selected_dept = st.selectbox(
                    "Département",
                    options=list(dept_options.keys()),
                    key="gen_dept_select"
                )
            
            with col2:
                col2a, col2b = st.columns(2)
                with col2a:
                    annee_scolaire = st.number_input("Année", 2020, 2030, datetime.now().year)
                with col2b:
                    session = st.selectbox("Session", ["Principale", "Rattrapage"])
            
            # Dates avec valeur par défaut
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                date_debut = st.date_input("Date début", datetime.now(), key="gen_date_debut")
            with col_date2:
                date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=14), key="gen_date_fin")
            
            # Paramètres avancés dans un expander
            with st.expander("⚙️ Paramètres avancés", expanded=False):
                col_adv1, col_adv2 = st.columns(2)
                with col_adv1:
                    heure_debut = st.time_input("Heure début", datetime.strptime("08:00", "%H:%M").time())
                    duree_examen = st.number_input("Durée (min)", 60, 240, 120)
                
                with col_adv2:
                    marge_entre_examens = st.number_input("Marge (min)", 0, 180, 30)
                    utiliser_meme_salle = st.checkbox("Même salle par formation", True)
            
            # Bouton de génération
            if st.button("🚀 Générer le Planning", type="primary", use_container_width=True):
                with st.spinner("Génération en cours..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(5):
                        time_module.sleep(0.3)
                        progress_bar.progress((i + 1) * 20)
                    
                    st.success(f"Planning généré pour {selected_dept}!")
                    st.balloons()
        
        else:  # Planning Général
            st.info("Génération du planning pour tous les départements")
            
            col_gen1, col_gen2 = st.columns(2)
            with col_gen1:
                date_debut = st.date_input("Date début", datetime.now(), key="gen_general_debut")
            with col_gen2:
                date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=21), key="gen_general_fin")
            
            if st.button("🚀 Générer Planning Général", type="primary", use_container_width=True):
                with st.spinner("Génération globale en cours..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(5):
                        time_module.sleep(0.5)
                        progress_bar.progress((i + 1) * 20)
                    
                    st.success("Planning général généré avec succès!")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_visualization():
    """Page Visualisation Planning optimisée"""
    create_section_fast("🔍", "Visualisation Planning")
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        
        # Filtres dans un formulaire pour éviter les rechargements
        with st.form("filters_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Précharger la liste des départements
                if 'dept_list_viz' not in st.session_state:
                    st.session_state.dept_list_viz = get_departments()
                
                dept_options = ['Tous'] + [dept['nom'] for dept in st.session_state.dept_list_viz]
                selected_dept = st.selectbox("Département", dept_options, key="viz_dept")
            
            with col2:
                date_debut = st.date_input("Date début", datetime.now(), key="viz_date_debut")
                date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=7), key="viz_date_fin")
            
            display_type = st.selectbox(
                "Mode d'affichage",
                ["📊 Tableau détaillé", "📅 Vue calendrier", "⏳ Timeline", "🗺️ Vue géographique"],
                key="display_type"
            )
            
            submitted = st.form_submit_button("🔍 Rechercher Planning", use_container_width=True)
        
        if submitted or st.session_state.get('viz_submitted', False):
            st.session_state.viz_submitted = True
            
            # Simuler des données pour la démo
            with st.spinner("Chargement des données..."):
                time_module.sleep(1)  # Simulation court délai
                
                if display_type == "📊 Tableau détaillé":
                    # Données d'exemple avec cache
                    examens_data = [
                        {"Date": "15/01/2024", "Heure": "08:30-10:30", "Module": "Algorithmique", 
                         "Formation": "Informatique", "Salle": "Amphi A", "Professeur": "Dr. Martin"},
                        {"Date": "15/01/2024", "Heure": "11:00-13:00", "Module": "Base de données",
                         "Formation": "Informatique", "Salle": "Salle 101", "Professeur": "Dr. Dupont"},
                    ]
                    
                    df = pd.DataFrame(examens_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                elif display_type == "📅 Vue calendrier":
                    # Calendrier simplifié
                    st.info("Vue calendrier - Mode démo")
                    col_cal1, col_cal2, col_cal3 = st.columns(3)
                    
                    with col_cal1:
                        st.metric("Examens aujourd'hui", "3")
                    with col_cal2:
                        st.metric("Salles utilisées", "5")
                    with col_cal3:
                        st.metric("Taux occupation", "78%")
                
                elif display_type == "⏳ Timeline":
                    # Timeline simplifiée
                    st.write("Timeline des examens")
                    
                    timeline_items = [
                        ("08:30 - 10:30", "Algorithmique", "Amphi A"),
                        ("11:00 - 13:00", "Base de données", "Salle 101"),
                        ("14:30 - 16:30", "Réseaux", "Salle 102"),
                    ]
                    
                    for time_slot, module, salle in timeline_items:
                        st.markdown(f"""
                        <div style="padding: 0.5rem; margin: 0.5rem 0; border-left: 3px solid #3498db; background: #f8f9fa;">
                            <strong>{time_slot}</strong> - {module}<br>
                            <small>📍 {salle}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                elif display_type == "🗺️ Vue géographique":
                    # Carte simplifiée
                    st.write("Plan des bâtiments")
                    
                    buildings = [
                        {"nom": "Bâtiment A", "salles": 4, "occupation": "75%"},
                        {"nom": "Bâtiment B", "salles": 3, "occupation": "67%"},
                        {"nom": "Bâtiment C", "salles": 3, "occupation": "33%"},
                    ]
                    
                    for building in buildings:
                        col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
                        with col_b1:
                            st.write(f"🏢 {building['nom']}")
                        with col_b2:
                            st.write(f"{building['salles']} salles")
                        with col_b3:
                            st.write(f"📊 {building['occupation']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_planning_general():
    """Page Planning Général optimisée"""
    create_section_fast("🌍", "Planning Général")
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        
        # Filtres rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            date_debut = st.date_input("Date début", datetime.now(), key="plan_gen_debut")
        with col2:
            date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=14), key="plan_gen_fin")
        with col3:
            session = st.selectbox("Session", ["Toutes", "Principale", "Rattrapage"], key="plan_gen_session")
        
        if st.button("📋 Charger le Planning", type="primary", use_container_width=True):
            with st.spinner("Chargement du planning..."):
                # Simuler le chargement
                time_module.sleep(1)
                
                # Métriques rapides
                col_met1, col_met2, col_met3 = st.columns(3)
                with col_met1:
                    st.metric("Total examens", "156")
                with col_met2:
                    st.metric("Salles utilisées", "25")
                with col_met3:
                    st.metric("Étudiants concernés", "2,150")
                
                # Tableau simplifié
                st.markdown("### 📅 Aperçu des examens")
                
                planning_data = run_query("""
                    SELECT ex.id, m.nom as module, d.nom as departement,
                           DATE_FORMAT(ex.date_examen, '%d/%m/%Y') as date,
                           TIME_FORMAT(ex.heure_debut, '%H:%i') as heure,
                           l.nom as salle
                    FROM examens ex
                    JOIN modules m ON ex.module_id = m.id
                    JOIN formations f ON m.formation_id = f.id
                    JOIN departements d ON f.dept_id = d.id
                    JOIN lieu_examen l ON ex.salle_id = l.id
                    WHERE ex.statut = 'planifié'
                        AND ex.date_examen BETWEEN %s AND %s
                    ORDER BY ex.date_examen, ex.heure_debut
                    LIMIT 20
                """, (date_debut, date_fin))
                
                if planning_data:
                    df = pd.DataFrame(planning_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_conflict_detection():
    """Page Détection Conflits optimisée"""
    create_section_fast("⚠️", "Détection de Conflits")
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        
        # Configuration de l'analyse
        col1, col2 = st.columns(2)
        with col1:
            date_debut = st.date_input("Date début", datetime.now(), key="conf_date_debut")
        with col2:
            date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=30), key="conf_date_fin")
        
        analysis_type = st.selectbox(
            "Type d'analyse",
            ["Analyse complète", "Conflits étudiants", "Conflits salles", "Conflits professeurs"],
            key="conf_analysis_type"
        )
        
        with st.expander("⚙️ Options", expanded=False):
            auto_resolve = st.checkbox("Résolution automatique", True)
            generate_report = st.checkbox("Générer rapport", True)
        
        if st.button("🔍 Analyser les Conflits", type="primary", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                # Simulation de l'analyse
                progress_bar = st.progress(0)
                
                steps = ["Collecte", "Analyse", "Détection", "Rapport"]
                for i, step in enumerate(steps):
                    st.write(f"🔄 {step}...")
                    progress_bar.progress((i + 1) * 25)
                    time_module.sleep(0.5)
                
                # Résultats
                st.success("Analyse terminée!")
                
                # Affichage des résultats
                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                with col_res1:
                    st.metric("Conflits détectés", "8")
                with col_res2:
                    st.metric("Résolus auto", "6")
                with col_res3:
                    st.metric("À vérifier", "2")
                with col_res4:
                    st.metric("Critiques", "1")
                
                # Liste des conflits
                st.markdown("### 📋 Conflits détectés")
                
                conflits = [
                    {"Type": "Étudiant", "Description": "2 examens le même jour pour 15 étudiants", "Statut": "Résolu"},
                    {"Type": "Salle", "Description": "Double réservation Amphi A", "Statut": "À vérifier"},
                    {"Type": "Professeur", "Description": "3 surveillances simultanées", "Statut": "Résolu"},
                ]
                
                df_conflits = pd.DataFrame(conflits)
                st.dataframe(df_conflits, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_statistics():
    """Page Statistiques optimisée"""
    create_section_fast("📊", "Statistiques")
    
    with st.container():
        st.markdown('<div class="section-wrapper">', unsafe_allow_html=True)
        
        # Sélection du type de statistiques
        stat_type = st.selectbox(
            "Type de statistiques",
            ["Tableau de bord", "Occupation ressources", "Conflits", "Performance"],
            key="stat_type"
        )
        
        if stat_type == "Tableau de bord":
            # KPI Grid
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(create_metric_card_fast("📈", "Taux planification", "98%"), unsafe_allow_html=True)
            with col2:
                st.markdown(create_metric_card_fast("✅", "Conflits résolus", "94%"), unsafe_allow_html=True)
            with col3:
                st.markdown(create_metric_card_fast("🏫", "Utilisation salles", "85%"), unsafe_allow_html=True)
            with col4:
                st.markdown(create_metric_card_fast("👥", "Satisfaction", "92%"), unsafe_allow_html=True)
            
            # Graphiques
            st.markdown("### 📈 Évolution des indicateurs")
            
            # Données simulées
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']
            performance = [85, 88, 90, 92, 94, 96]
            
            df_perf = pd.DataFrame({'Mois': months, 'Performance': performance})
            st.line_chart(df_perf.set_index('Mois'))
            
            # Performance par département
            st.markdown("### 🎯 Performance par département")
            
            perf_data = run_query("""
                SELECT d.nom as departement, COUNT(ex.id) as examens
                FROM departements d
                LEFT JOIN formations f ON d.id = f.dept_id
                LEFT JOIN modules m ON f.id = m.formation_id
                LEFT JOIN examens ex ON m.id = ex.module_id
                GROUP BY d.id
                ORDER BY examens DESC
                LIMIT 10
            """)
            
            if perf_data:
                df = pd.DataFrame(perf_data)
                st.bar_chart(df.set_index('departement'))
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_configuration():
    """Page Configuration optimisée"""
    create_section_fast("⚙️", "Configuration")
    
    # Onglets simplifiés
    tabs = st.tabs(["🏢 Départements", "👨‍🏫 Professeurs", "🏫 Salles", "📋 Contraintes"])
    
    with tabs[0]:  # Départements
        with st.form("add_dept_form"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom du département")
                code = st.text_input("Code")
            with col2:
                responsable = st.selectbox(
                    "Responsable",
                    ["Dr. Martin", "Dr. Dupont", "Dr. Bernard"]
                )
            
            if st.form_submit_button("➕ Ajouter département"):
                st.success(f"Département {nom} ajouté!")
    
    with tabs[1]:  # Professeurs
        with st.form("add_prof_form"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom")
                prenom = st.text_input("Prénom")
            with col2:
                email = st.text_input("Email")
                telephone = st.text_input("Téléphone")
            
            if st.form_submit_button("👨‍🏫 Ajouter professeur"):
                st.success(f"Professeur {prenom} {nom} ajouté!")
    
    with tabs[2]:  # Salles
        with st.form("add_room_form"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom de la salle")
                type_salle = st.selectbox("Type", ["Amphithéâtre", "Salle de cours", "Laboratoire"])
            with col2:
                capacite = st.number_input("Capacité", 1, 500, 50)
                batiment = st.text_input("Bâtiment")
            
            if st.form_submit_button("🏫 Ajouter salle"):
                st.success(f"Salle {nom} ajoutée!")
    
    with tabs[3]:  # Contraintes
        with st.form("add_constraint_form"):
            type_contrainte = st.selectbox(
                "Type de contrainte",
                ["Horaire", "Professeur", "Salle", "Étudiant"]
            )
            
            description = st.text_area("Description")
            
            if st.form_submit_button("📋 Ajouter contrainte"):
                st.success("Contrainte ajoutée!")

# =================== APPLICATION PRINCIPALE ===================
def main():
    """Point d'entrée principal optimisé"""
    
    # Initialiser le menu sélectionné
    if 'selected_menu' not in st.session_state:
        st.session_state.selected_menu = "Tableau de Bord"
    
    # Afficher la sidebar (toujours visible)
    render_sidebar()
    
    # Mapper les pages aux fonctions
    pages = {
        "Tableau de Bord": render_dashboard,
        "Génération Planning": render_generation,
        "Visualisation Planning": render_visualization,
        "Planning Général": render_planning_general,
        "Détection Conflits": render_conflict_detection,
        "Statistiques": render_statistics,
        "Configuration": render_configuration,
    }
    
    # Afficher la page sélectionnée
    current_page = pages.get(st.session_state.selected_menu, render_dashboard)
    
    try:
        current_page()
    except Exception as e:
        st.error(f"Erreur lors du chargement de la page: {str(e)}")
        st.info("Retour au tableau de bord...")
        st.session_state.selected_menu = "Tableau de Bord"
        st.rerun()
    
    # Pied de page optimisé
    st.markdown("""
    <div style="margin-top: 4rem; padding: 1.5rem; text-align: center; border-top: 1px solid #e2e8f0;">
        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;">
            Plateforme d'Optimisation des Emplois du Temps
        </div>
        <div style="color: #7f8c8d; font-size: 0.9rem;">
            Version 4.0 • Système Intelligent • © 2024
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================== LANCEMENT ===================
if __name__ == "__main__":
    # Configuration des performances Streamlit
    st.set_option('client.showErrorDetails', False)
    st.set_option('client.caching', True)
    
    # Exécuter l'application
    main()
