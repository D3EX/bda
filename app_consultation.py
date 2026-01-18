# app_consultation.py
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import numpy as np
import requests
from io import BytesIO

# Configuration de la page avec thème moderne
st.set_page_config(
    page_title="Planning d'Examens - Université",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un thème moderne
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .examen-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .examen-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .stat-confirme {
        border-left-color: #4CAF50;
    }
    
    .stat-planifie {
        border-left-color: #FFC107;
    }
    
    .stat-annule {
        border-left-color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Fonction de connexion à MySQL
@st.cache_resource
def init_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )
        return conn
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Initialiser la connexion
conn = init_connection()

# Fonction pour exécuter les requêtes SQL
def run_query(query, params=None, fetch=True):
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return None

# Fonction pour obtenir la liste des départements
def get_departements():
    query = "SELECT id, nom FROM departements ORDER BY nom"
    return run_query(query)

# Fonction pour obtenir les formations d'un département
def get_formations_departement(dept_id):
    query = """
        SELECT id, nom FROM formations 
        WHERE dept_id = %s 
        ORDER BY nom
    """
    return run_query(query, (dept_id,))

# Fonction pour obtenir les étudiants d'une formation
def get_etudiants_formation(formation_id):
    query = """
        SELECT 
            e.id,
            CONCAT(e.nom, ' ', e.prenom) as nom_complet,
            e.promo,
            f.nom as formation,
            d.nom as departement
        FROM etudiants e
        JOIN formations f ON e.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        WHERE f.id = %s
        ORDER BY e.nom, e.prenom
    """
    return run_query(query, (formation_id,))

# Fonction pour obtenir les professeurs d'un département
def get_professeurs_departement(dept_id):
    query = """
        SELECT 
            p.id,
            CONCAT(p.nom, ' ', p.prenom) as nom_complet,
            p.specialite,
            d.nom as departement
        FROM professeurs p
        JOIN departements d ON p.dept_id = d.id
        WHERE d.id = %s
        ORDER BY p.nom, p.prenom
    """
    return run_query(query, (dept_id,))

# Fonction pour obtenir le planning d'un étudiant (uniquement confirmés)
def get_planning_etudiant_confirme(etudiant_id, date_debut=None, date_fin=None):
    query = """
        SELECT 
            e.id as examen_id,
            ex.date_examen,
            ex.heure_debut,
            ex.heure_fin,
            ex.duree_minutes,
            ex.statut,
            ex.session,
            m.nom as module,
            f.nom as formation,
            d.nom as departement,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            le.batiment,
            CONCAT(p_resp.nom, ' ', p_resp.prenom) as professeur_responsable,
            CONCAT(p_surv.nom, ' ', p_surv.prenom) as professeur_surveillant
        FROM examens ex
        JOIN modules m ON ex.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN lieu_examen le ON ex.salle_id = le.id
        LEFT JOIN professeurs p_resp ON ex.professeur_id = p_resp.id
        LEFT JOIN professeurs p_surv ON ex.surveillant_id = p_surv.id
        JOIN inscriptions i ON m.id = i.module_id 
            AND i.annee_scolaire = ex.annee_scolaire
        JOIN etudiants et ON i.etudiant_id = et.id
        WHERE et.id = %s
        AND ex.statut = 'confirmé'
    """
    
    params = [etudiant_id]
    
    if date_debut and date_fin:
        query += " AND ex.date_examen BETWEEN %s AND %s"
        params.extend([date_debut, date_fin])
    
    query += " ORDER BY ex.date_examen, ex.heure_debut"
    
    return run_query(query, params)

# Fonction pour obtenir le planning d'un professeur (uniquement confirmés)
def get_planning_professeur_confirme(professeur_id, date_debut=None, date_fin=None):
    query = """
        SELECT 
            ex.id as examen_id,
            ex.date_examen,
            ex.heure_debut,
            ex.heure_fin,
            ex.duree_minutes,
            ex.statut,
            ex.session,
            m.nom as module,
            f.nom as formation,
            d.nom as departement,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            le.batiment,
            CONCAT(p_resp.nom, ' ', p_resp.prenom) as professeur_responsable,
            CONCAT(p_surv.nom, ' ', p_surv.prenom) as professeur_surveillant,
            p.nom as nom_professeur,
            p.prenom as prenom_professeur,
            CASE 
                WHEN ex.professeur_id = %s THEN 'Responsable'
                WHEN ex.surveillant_id = %s THEN 'Surveillant'
                ELSE 'Autre'
            END as role_professeur,
            COUNT(DISTINCT i.etudiant_id) as nb_etudiants
        FROM examens ex
        JOIN modules m ON ex.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN lieu_examen le ON ex.salle_id = le.id
        LEFT JOIN professeurs p_resp ON ex.professeur_id = p_resp.id
        LEFT JOIN professeurs p_surv ON ex.surveillant_id = p_surv.id
        JOIN professeurs p ON (ex.professeur_id = p.id OR ex.surveillant_id = p.id)
        LEFT JOIN inscriptions i ON m.id = i.module_id 
            AND i.annee_scolaire = ex.annee_scolaire
        WHERE (ex.professeur_id = %s OR ex.surveillant_id = %s)
        AND ex.statut = 'confirmé'
    """
    
    params = [professeur_id, professeur_id, professeur_id, professeur_id]
    
    if date_debut and date_fin:
        query += " AND ex.date_examen BETWEEN %s AND %s"
        params.extend([date_debut, date_fin])
    
    query += " GROUP BY ex.id ORDER BY ex.date_examen, ex.heure_debut"
    
    return run_query(query, params)

# Fonction pour obtenir le planning par formation (uniquement confirmés)
def get_planning_formation_confirme(formation_id, date_debut=None, date_fin=None):
    query = """
        SELECT 
            ex.id as examen_id,
            ex.date_examen,
            ex.heure_debut,
            ex.heure_fin,
            ex.duree_minutes,
            ex.statut,
            ex.session,
            m.nom as module,
            f.nom as formation,
            d.nom as departement,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            le.batiment,
            CONCAT(p_resp.nom, ' ', p_resp.prenom) as professeur_responsable,
            CONCAT(p_surv.nom, ' ', p_surv.prenom) as professeur_surveillant,
            COUNT(DISTINCT i.etudiant_id) as nb_etudiants
        FROM examens ex
        JOIN modules m ON ex.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN lieu_examen le ON ex.salle_id = le.id
        LEFT JOIN professeurs p_resp ON ex.professeur_id = p_resp.id
        LEFT JOIN professeurs p_surv ON ex.surveillant_id = p_surv.id
        LEFT JOIN inscriptions i ON m.id = i.module_id 
            AND i.annee_scolaire = ex.annee_scolaire
        WHERE f.id = %s
        AND ex.statut = 'confirmé'
    """
    
    params = [formation_id]
    
    if date_debut and date_fin:
        query += " AND ex.date_examen BETWEEN %s AND %s"
        params.extend([date_debut, date_fin])
    
    query += " GROUP BY ex.id ORDER BY ex.date_examen, ex.heure_debut"
    
    return run_query(query, params)

# Fonction pour créer un planning visuel (timeline)
def create_timeline_planning(planning_data, title):
    if not planning_data:
        return None
    
    df = pd.DataFrame(planning_data)
    
    # Créer une colonne pour l'affichage
    df['display_text'] = df.apply(
        lambda row: f"{row['module']}<br>{row['salle']}<br>{row['heure_debut']} - {row['heure_fin']}",
        axis=1
    )
    
    # Convertir date et heure en datetime pour le graphique
    df['start_datetime'] = pd.to_datetime(df['date_examen'].astype(str) + ' ' + df['heure_debut'].astype(str))
    df['end_datetime'] = pd.to_datetime(df['date_examen'].astype(str) + ' ' + df['heure_fin'].astype(str))
    
    # Créer la timeline
    fig = px.timeline(
        df, 
        x_start="start_datetime", 
        x_end="end_datetime",
        y="module",
        color="formation",
        title=title,
        hover_data=['salle', 'professeur_responsable', 'statut']
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=400,
        xaxis_title="Date et Heure",
        yaxis_title="Module",
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

# En-tête principal avec design moderne
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎓 Planning d'Examens Universitaires</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">Consultez les emplois du temps confirmés</p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour la sélection
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2 style="margin: 0;">🔍 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection du mode
    user_type = st.radio(
        "Mode de consultation",
        ["👨‍🎓 Espace Étudiant", "👨‍🏫 Espace Professeur", "🏢 Vue Globale"],
        key="user_type"
    )
    
    st.markdown("---")
    
    # Période d'analyse
    st.subheader("📅 Période de consultation")
    date_debut = st.date_input("Date début", datetime.now() - timedelta(days=7))
    date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=30))
    
    # Image éducative
    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&auto=format&fit=crop", 
             caption="Campus Universitaire", use_column_width=True)

# PAGE: Consultation Étudiant
if user_type == "👨‍🎓 Espace Étudiant":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2 style="margin: 0;">👨‍🎓 Consultation des Examens - Étudiant</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Sélectionnez votre département et formation pour voir votre planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection en cascade : Département -> Formation -> Étudiant
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sélection du département
        departements = get_departements()
        if departements:
            dept_options = {d['nom']: d['id'] for d in departements}
            selected_dept = st.selectbox(
                "1. Sélectionnez votre département",
                options=list(dept_options.keys()),
                key="select_dept_etudiant"
            )
    
    with col2:
        # Sélection de la formation
        if 'selected_dept' in locals():
            dept_id = dept_options[selected_dept]
            formations = get_formations_departement(dept_id)
            if formations:
                formation_options = {f['nom']: f['id'] for f in formations}
                selected_formation = st.selectbox(
                    "2. Sélectionnez votre formation",
                    options=list(formation_options.keys()),
                    key="select_formation_etudiant"
                )
    
    with col3:
        # Sélection de l'étudiant
        if 'selected_formation' in locals():
            formation_id = formation_options[selected_formation]
            etudiants = get_etudiants_formation(formation_id)
            if etudiants:
                etudiant_options = {e['nom_complet']: e['id'] for e in etudiants}
                selected_etudiant = st.selectbox(
                    "3. Sélectionnez votre nom",
                    options=list(etudiant_options.keys()),
                    key="select_etudiant"
                )
    
    # Afficher le planning si un étudiant est sélectionné
    if 'selected_etudiant' in locals() and selected_etudiant:
        etudiant_id = etudiant_options[selected_etudiant]
        
        # Récupérer le planning
        planning = get_planning_etudiant_confirme(etudiant_id, date_debut, date_fin)
        
        if planning:
            df_planning = pd.DataFrame(planning)
            
            # Statistiques
            total_examens = len(df_planning)
            heures_total = df_planning['duree_minutes'].sum() / 60 if not df_planning.empty else 0
            modules_count = df_planning['module'].nunique()
            
            # Afficher les statistiques
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{total_examens}</h3>
                    <p style="margin: 0; opacity: 0.9;">Examens confirmés</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{heures_total:.1f}h</h3>
                    <p style="margin: 0; opacity: 0.9;">Heures d'examens</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{modules_count}</h3>
                    <p style="margin: 0; opacity: 0.9;">Modules différents</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Timeline visuelle
            st.markdown("### 📊 Planning Visuel")
            if not df_planning.empty:
                timeline_fig = create_timeline_planning(
                    df_planning.to_dict('records'), 
                    f"Planning d'Examens - {selected_etudiant}"
                )
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
            
            # Liste des examens avec design de cartes
            st.markdown("### 📋 Détail des Examens")
            
            for idx, row in df_planning.iterrows():
                # Déterminer la classe CSS selon le statut
                statut_class = "stat-confirme"
                
                # Formatage de la date
                date_formatted = row['date_examen'].strftime('%d/%m/%Y')
                
                # Créer la carte d'examen
                st.markdown(f"""
                <div class="examen-card {statut_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{row['module']}</h4>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>📅 Date:</strong> {date_formatted} | 
                                <strong>⏰ Horaire:</strong> {row['heure_debut']} - {row['heure_fin']}
                            </p>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>🏫 Salle:</strong> {row['salle']} ({row['type_salle']}) | 
                                <strong>👨‍🏫 Professeur:</strong> {row['professeur_responsable']}
                            </p>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>📚 Formation:</strong> {row['formation']} | 
                                <strong>🎓 Département:</strong> {row['departement']}
                            </p>
                        </div>
                        <div style="background: #4CAF50; color: white; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                            ✅ Confirmé
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Export CSV
            csv_data = df_planning.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le planning (CSV)",
                data=csv_data,
                file_name=f"planning_etudiant_{selected_etudiant.replace(' ', '_')}_{date_debut}_{date_fin}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("Aucun examen confirmé trouvé pour cet étudiant pour la période sélectionnée.")
    
    # Afficher une image si aucun étudiant sélectionné
    else:
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.image("https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=600&auto=format&fit=crop", 
                     caption="Bibliothèque Universitaire")
        with col_img2:
            st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop", 
                     caption="Salle d'examen")

# PAGE: Consultation Professeur
elif user_type == "👨‍🏫 Espace Professeur":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2 style="margin: 0;">👨‍🏫 Consultation des Examens - Professeur</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Sélectionnez votre département pour voir votre planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection en cascade : Département -> Professeur
    col1, col2 = st.columns(2)
    
    with col1:
        # Sélection du département
        departements = get_departements()
        if departements:
            dept_options = {d['nom']: d['id'] for d in departements}
            selected_dept = st.selectbox(
                "1. Sélectionnez votre département",
                options=list(dept_options.keys()),
                key="select_dept_professeur"
            )
    
    with col2:
        # Sélection du professeur
        if 'selected_dept' in locals():
            dept_id = dept_options[selected_dept]
            professeurs = get_professeurs_departement(dept_id)
            if professeurs:
                professeur_options = {p['nom_complet']: p['id'] for p in professeurs}
                selected_professeur = st.selectbox(
                    "2. Sélectionnez votre nom",
                    options=list(professeur_options.keys()),
                    key="select_professeur"
                )
    
    # Afficher le planning si un professeur est sélectionné
    if 'selected_professeur' in locals() and selected_professeur:
        professeur_id = professeur_options[selected_professeur]
        
        # Récupérer le planning
        planning = get_planning_professeur_confirme(professeur_id, date_debut, date_fin)
        
        if planning:
            df_planning = pd.DataFrame(planning)
            
            # Calculer les statistiques
            total_examens = len(df_planning)
            examens_responsable = df_planning[df_planning['role_professeur'] == 'Responsable'].shape[0]
            examens_surveillant = df_planning[df_planning['role_professeur'] == 'Surveillant'].shape[0]
            heures_total = df_planning['duree_minutes'].sum() / 60 if not df_planning.empty else 0
            
            # Afficher les statistiques
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{total_examens}</h3>
                    <p style="margin: 0; opacity: 0.9;">Total examens</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{examens_responsable}</h3>
                    <p style="margin: 0; opacity: 0.9;">En tant que responsable</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{examens_surveillant}</h3>
                    <p style="margin: 0; opacity: 0.9;">En tant que surveillant</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{heures_total:.1f}h</h3>
                    <p style="margin: 0; opacity: 0.9;">Heures totales</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Timeline visuelle
            st.markdown("### 📊 Planning Visuel")
            if not df_planning.empty:
                timeline_fig = create_timeline_planning(
                    df_planning.to_dict('records'), 
                    f"Planning d'Examens - {selected_professeur}"
                )
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
            
            # Liste des examens avec design de cartes
            st.markdown("### 📋 Détail des Examens")
            
            for idx, row in df_planning.iterrows():
                # Déterminer la classe CSS et l'icône selon le rôle
                if row['role_professeur'] == 'Responsable':
                    role_icon = "👨‍🏫"
                    role_color = "#3498db"
                else:
                    role_icon = "👥"
                    role_color = "#2ecc71"
                
                # Formatage de la date
                date_formatted = row['date_examen'].strftime('%d/%m/%Y')
                
                # Créer la carte d'examen
                st.markdown(f"""
                <div class="examen-card stat-confirme">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{row['module']}</h4>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>📅 Date:</strong> {date_formatted} | 
                                <strong>⏰ Horaire:</strong> {row['heure_debut']} - {row['heure_fin']}
                            </p>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>🏫 Salle:</strong> {row['salle']} ({row['type_salle']}) | 
                                <strong>👥 Étudiants:</strong> {row['nb_etudiants'] if row['nb_etudiants'] else 'N/A'}
                            </p>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>📚 Formation:</strong> {row['formation']} | 
                                <strong>🎓 Département:</strong> {row['departement']}
                            </p>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: end; gap: 0.5rem;">
                            <div style="background: {role_color}; color: white; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                                {role_icon} {row['role_professeur']}
                            </div>
                            <div style="background: #4CAF50; color: white; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                                ✅ Confirmé
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Graphique de répartition par rôle
            st.markdown("### 📈 Répartition par Rôle")
            if not df_planning.empty:
                role_dist = df_planning['role_professeur'].value_counts().reset_index()
                role_dist.columns = ['Rôle', 'Nombre']
                
                fig = px.pie(
                    role_dist,
                    values='Nombre',
                    names='Rôle',
                    title="Répartition des Examens par Rôle",
                    color='Rôle',
                    color_discrete_map={'Responsable': '#3498db', 'Surveillant': '#2ecc71'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Export CSV
            csv_data = df_planning.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le planning (CSV)",
                data=csv_data,
                file_name=f"planning_professeur_{selected_professeur.replace(' ', '_')}_{date_debut}_{date_fin}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("Aucun examen confirmé trouvé pour ce professeur pour la période sélectionnée.")
    
    # Afficher une image si aucun professeur sélectionné
    else:
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.image("https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=600&auto=format&fit=crop", 
                     caption="Amphithéâtre")
        with col_img2:
            st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&auto=format&fit=crop", 
                     caption="Laboratoire de recherche")

# PAGE: Vue Globale (Département/Formation)
else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2 style="margin: 0;">🏢 Vue Globale par Formation</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Consultez tous les examens confirmés d'une formation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection en cascade : Département -> Formation
    col1, col2 = st.columns(2)
    
    with col1:
        # Sélection du département
        departements = get_departements()
        if departements:
            dept_options = {d['nom']: d['id'] for d in departements}
            selected_dept = st.selectbox(
                "1. Sélectionnez un département",
                options=list(dept_options.keys()),
                key="select_dept_global"
            )
    
    with col2:
        # Sélection de la formation
        if 'selected_dept' in locals():
            dept_id = dept_options[selected_dept]
            formations = get_formations_departement(dept_id)
            if formations:
                formation_options = {f['nom']: f['id'] for f in formations}
                selected_formation = st.selectbox(
                    "2. Sélectionnez une formation",
                    options=list(formation_options.keys()),
                    key="select_formation_global"
                )
    
    # Afficher le planning si une formation est sélectionnée
    if 'selected_formation' in locals() and selected_formation:
        formation_id = formation_options[selected_formation]
        
        # Récupérer le planning
        planning = get_planning_formation_confirme(formation_id, date_debut, date_fin)
        
        if planning:
            df_planning = pd.DataFrame(planning)
            
            # Statistiques
            total_examens = len(df_planning)
            modules_count = df_planning['module'].nunique()
            etudiants_total = df_planning['nb_etudiants'].sum() if 'nb_etudiants' in df_planning.columns else 0
            
            # Afficher les statistiques
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{total_examens}</h3>
                    <p style="margin: 0; opacity: 0.9;">Examens confirmés</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{modules_count}</h3>
                    <p style="margin: 0; opacity: 0.9;">Modules différents</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; font-size: 2rem;">{etudiants_total}</h3>
                    <p style="margin: 0; opacity: 0.9;">Étudiants concernés</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Timeline visuelle
            st.markdown("### 📊 Planning Visuel")
            if not df_planning.empty:
                timeline_fig = create_timeline_planning(
                    df_planning.to_dict('records'), 
                    f"Planning de la Formation {selected_formation}"
                )
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
            
            # Liste des examens avec design de cartes
            st.markdown("### 📋 Détail des Examens")
            
            for idx, row in df_planning.iterrows():
                # Formatage de la date
                date_formatted = row['date_examen'].strftime('%d/%m/%Y')
                
                # Créer la carte d'examen
                st.markdown(f"""
                <div class="examen-card stat-confirme">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{row['module']}</h4>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>📅 Date:</strong> {date_formatted} | 
                                <strong>⏰ Horaire:</strong> {row['heure_debut']} - {row['heure_fin']}
                            </p>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>🏫 Salle:</strong> {row['salle']} ({row['type_salle']}, {row['capacite']} places) | 
                                <strong>👨‍🏫 Professeur:</strong> {row['professeur_responsable']}
                            </p>
                            <p style="margin: 0.2rem 0; color: #7f8c8d;">
                                <strong>👥 Étudiants:</strong> {row['nb_etudiants'] if row['nb_etudiants'] else 'N/A'} | 
                                <strong>📋 Session:</strong> {row['session']}
                            </p>
                        </div>
                        <div style="background: #4CAF50; color: white; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                            ✅ Confirmé
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Graphique de répartition par module
            st.markdown("### 📈 Répartition par Module")
            if not df_planning.empty:
                module_dist = df_planning['module'].value_counts().reset_index()
                module_dist.columns = ['Module', 'Nombre d\'Examens']
                
                fig = px.bar(
                    module_dist,
                    x='Module',
                    y='Nombre d\'Examens',
                    title="Nombre d'Examens par Module",
                    color='Nombre d\'Examens',
                    color_continuous_scale='Viridis'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Export CSV
            csv_data = df_planning.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le planning (CSV)",
                data=csv_data,
                file_name=f"planning_formation_{selected_formation.replace(' ', '_')}_{date_debut}_{date_fin}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning(f"Aucun examen confirmé trouvé pour la formation {selected_formation} pour cette période.")
    
    # Afficher une image si aucune formation sélectionnée
    else:
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=600&auto=format&fit=crop", 
                     caption="Cérémonie de remise des diplômes")
        with col_img2:
            st.image("https://images.unsplash.com/photo-1524178234883-043d5c3f3cf4?w=600&auto=format&fit=crop", 
                     caption="Équipe pédagogique")

# Pied de page
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 2rem;">
    <div style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="40" height="40">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135768.png" width="40" height="40">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135789.png" width="40" height="40">
    </div>
    <p style="margin: 0; font-size: 1.1rem;"><strong>Planning d'Examens Universitaires</strong></p>
    <p style="margin: 0.5rem 0; opacity: 0.8;">Système de consultation des emplois du temps confirmés</p>
    <p style="margin: 0; font-size: 0.9rem; opacity: 0.6;">© 2024 Université - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)