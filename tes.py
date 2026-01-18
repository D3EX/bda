# app_chef_departement.py
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

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord Chef de Département",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ID du département (Informatique = 1)
DEPARTEMENT_ID = 1

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

# Fonction pour convertir les Decimal en float
def convert_decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, dict):
        return {k: convert_decimal_to_float(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert_decimal_to_float(item) for item in value]
    else:
        return value

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
            
            # Convertir les timedelta en time et Decimal en float
            for row in result:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        total_seconds = value.total_seconds()
                        hours = int(total_seconds // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        row[key] = time(hours, minutes, seconds)
                    elif isinstance(value, Decimal):
                        row[key] = float(value)
            
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        st.error(f"Erreur SQL: {e}")
        return None

# Titre de l'application
st.title("👨‍💼 Tableau de Bord Chef de Département")
st.markdown("---")

# Récupérer le nom du département
departement_info = run_query("SELECT nom FROM departements WHERE id = %s", (DEPARTEMENT_ID,))
if departement_info:
    departement_nom = departement_info[0]['nom']
    st.header(f"📋 Département : {departement_nom}")
else:
    st.error("Département non trouvé")
    st.stop()

# Sidebar pour la navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Chef de Département")
    st.markdown(f"**Département:** {departement_nom}")
    st.markdown(f"**ID:** {DEPARTEMENT_ID}")
    st.markdown("---")
    
    menu = st.radio(
        "Navigation",
        ["🏠 Tableau de Bord", 
         "✅ Validation EDT",
         "📊 Statistiques Département",
         "⚠️ Conflits par Formation",
         "👨‍🏫 Gestion Professeurs",
         "📅 Planning Département"]
    )
    
    st.markdown("---")
    
    # Période d'analyse
    st.subheader("📅 Période d'analyse")
    date_debut = st.date_input("Date début", datetime.now())
    date_fin = st.date_input("Date fin", datetime.now() + timedelta(days=30))
    
    st.markdown("---")
    st.info(f"Période: {date_debut} au {date_fin}")
    
    if st.button("🔄 Actualiser les données"):
        st.rerun()

# Fonctions spécifiques au département
def get_info_departement(dept_id):
    """Informations générales du département"""
    query = """
        SELECT 
            d.nom,
            COUNT(DISTINCT f.id) as nb_formations,
            COUNT(DISTINCT m.id) as nb_modules,
            COUNT(DISTINCT p.id) as nb_professeurs,
            COUNT(DISTINCT et.id) as nb_etudiants,
            COUNT(DISTINCT le.id) as nb_salles,
            (SELECT COUNT(DISTINCT e.id) FROM examens e 
             JOIN modules m ON e.module_id = m.id 
             JOIN formations f ON m.formation_id = f.id 
             WHERE f.dept_id = %s AND e.date_examen BETWEEN %s AND %s) as nb_examens_planifies
        FROM departements d
        LEFT JOIN formations f ON d.id = f.dept_id
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN professeurs p ON d.id = p.dept_id
        LEFT JOIN etudiants et ON f.id = et.formation_id
        LEFT JOIN lieu_examen le ON 1=1
        WHERE d.id = %s
        GROUP BY d.id
    """
    return run_query(query, (dept_id, date_debut, date_fin, dept_id))

def get_examens_departement(dept_id, date_debut, date_fin):
    """Tous les examens du département"""
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
            CONCAT(ps.nom, ' ', ps.prenom) as surveillant,
            le.nom as salle,
            le.type as type_salle,
            le.capacite,
            COUNT(DISTINCT i.etudiant_id) as nb_etudiants,
            ROUND((COUNT(DISTINCT i.etudiant_id) / le.capacite) * 100, 1) as taux_occupation
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        LEFT JOIN professeurs p ON e.professeur_id = p.id
        LEFT JOIN professeurs ps ON e.surveillant_id = ps.id
        JOIN lieu_examen le ON e.salle_id = le.id
        LEFT JOIN inscriptions i ON m.id = i.module_id AND i.annee_scolaire = e.annee_scolaire
        WHERE d.id = %s
        AND e.date_examen BETWEEN %s AND %s
        GROUP BY e.id
        ORDER BY e.date_examen, e.heure_debut
    """
    return run_query(query, (dept_id, date_debut, date_fin))

def get_statistiques_validation_departement(dept_id, date_debut, date_fin):
    """Statistiques de validation pour le département"""
    query = """
        SELECT 
            f.nom as formation,
            COUNT(DISTINCT e.id) as total_examens,
            SUM(CASE WHEN e.statut = 'planifié' THEN 1 ELSE 0 END) as en_attente,
            SUM(CASE WHEN e.statut = 'confirmé' THEN 1 ELSE 0 END) as confirmes,
            SUM(CASE WHEN e.statut = 'annulé' THEN 1 ELSE 0 END) as annules,
            ROUND((SUM(CASE WHEN e.statut = 'confirmé' THEN 1 ELSE 0 END) / 
                   COUNT(DISTINCT e.id)) * 100, 1) as taux_validation
        FROM formations f
        JOIN modules m ON f.id = m.formation_id
        JOIN examens e ON m.id = e.module_id
        WHERE f.dept_id = %s
        AND e.date_examen BETWEEN %s AND %s
        GROUP BY f.id
        HAVING total_examens > 0
        ORDER BY taux_validation DESC
    """
    return run_query(query, (dept_id, date_debut, date_fin))

def get_conflits_par_formation(dept_id, date_debut, date_fin):
    """Conflits détaillés par formation"""
    query = """
        SELECT 
            f.nom as formation,
            COUNT(DISTINCT e.id) as total_examens,
            -- Conflits étudiants
            SUM(CASE WHEN ce.conflit_etudiant > 0 THEN 1 ELSE 0 END) as conflits_etudiants,
            -- Conflits salles
            SUM(CASE WHEN cs.conflit_salle > 0 THEN 1 ELSE 0 END) as conflits_salles,
            -- Conflits professeurs
            SUM(CASE WHEN cp.conflit_professeur > 0 THEN 1 ELSE 0 END) as conflits_professeurs,
            -- Total conflits
            SUM(CASE WHEN ce.conflit_etudiant > 0 OR cs.conflit_salle > 0 OR cp.conflit_professeur > 0 THEN 1 ELSE 0 END) as total_conflits,
            -- Taux de conflits
            ROUND((SUM(CASE WHEN ce.conflit_etudiant > 0 OR cs.conflit_salle > 0 OR cp.conflit_professeur > 0 THEN 1 ELSE 0 END) / 
                   COUNT(DISTINCT e.id)) * 100, 1) as taux_conflits
        FROM formations f
        JOIN modules m ON f.id = m.formation_id
        JOIN examens e ON m.id = e.module_id AND e.date_examen BETWEEN %s AND %s
        LEFT JOIN (
            -- Conflits étudiants par examen
            SELECT e1.module_id, COUNT(*) as conflit_etudiant
            FROM inscriptions e1
            JOIN examens ex ON e1.module_id = ex.module_id
            WHERE ex.date_examen BETWEEN %s AND %s
            GROUP BY e1.module_id, e1.etudiant_id
            HAVING COUNT(DISTINCT ex.date_examen) < COUNT(DISTINCT ex.id)
        ) ce ON e.module_id = ce.module_id
        LEFT JOIN (
            -- Conflits salles
            SELECT e1.salle_id, e1.date_examen, COUNT(*) as conflit_salle
            FROM examens e1
            WHERE e1.date_examen BETWEEN %s AND %s
            GROUP BY e1.salle_id, e1.date_examen
            HAVING COUNT(*) > 1
        ) cs ON e.salle_id = cs.salle_id AND e.date_examen = cs.date_examen
        LEFT JOIN (
            -- Conflits professeurs
            SELECT e1.professeur_id, e1.date_examen, COUNT(*) as conflit_professeur
            FROM examens e1
            WHERE e1.date_examen BETWEEN %s AND %s
            GROUP BY e1.professeur_id, e1.date_examen
            HAVING COUNT(*) > 1
        ) cp ON e.professeur_id = cp.professeur_id AND e.date_examen = cp.date_examen
        WHERE f.dept_id = %s
        GROUP BY f.id
        ORDER BY taux_conflits DESC
    """
    return run_query(query, (date_debut, date_fin, date_debut, date_fin, 
                           date_debut, date_fin, date_debut, date_fin, dept_id))

def get_professeurs_departement(dept_id):
    """Liste des professeurs du département"""
    query = """
        SELECT 
            p.id,
            CONCAT(p.nom, ' ', p.prenom) as nom_complet,
            p.specialite,
            p.heures_service,
            COUNT(DISTINCT e.id) as nb_examens_responsable,
            COUNT(DISTINCT e2.id) as nb_examens_surveillant,
            ROUND(SUM(e.duree_minutes)/60, 1) as heures_responsable,
            ROUND(SUM(e2.duree_minutes)/60, 1) as heures_surveillant,
            ROUND((COALESCE(SUM(e.duree_minutes), 0) + COALESCE(SUM(e2.duree_minutes), 0))/60, 1) as total_heures
        FROM professeurs p
        LEFT JOIN examens e ON p.id = e.professeur_id AND e.date_examen BETWEEN %s AND %s
        LEFT JOIN examens e2 ON p.id = e2.surveillant_id AND e2.date_examen BETWEEN %s AND %s
        WHERE p.dept_id = %s
        GROUP BY p.id
        ORDER BY p.nom, p.prenom
    """
    return run_query(query, (date_debut, date_fin, date_debut, date_fin, dept_id))

def get_formations_departement(dept_id):
    """Liste des formations du département"""
    query = """
        SELECT 
            f.id,
            f.nom,
            COUNT(DISTINCT m.id) as nb_modules,
            COUNT(DISTINCT et.id) as nb_etudiants,
            COUNT(DISTINCT e.id) as nb_examens_planifies
        FROM formations f
        LEFT JOIN modules m ON f.id = m.formation_id
        LEFT JOIN etudiants et ON f.id = et.formation_id
        LEFT JOIN examens e ON m.id = e.module_id AND e.date_examen BETWEEN %s AND %s
        WHERE f.dept_id = %s
        GROUP BY f.id
        ORDER BY f.nom
    """
    return run_query(query, (date_debut, date_fin, dept_id))

def valider_examen_departement(examen_id):
    """Valider un examen spécifique"""
    query = "UPDATE examens SET statut = 'confirmé' WHERE id = %s"
    return run_query(query, (examen_id,), False)

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
    return run_query(query, (formation_id, date_debut, date_fin), False)

def get_occupation_salles_departement(dept_id, date_debut, date_fin):
    """Occupation des salles pour le département"""
    query = """
        SELECT 
            le.type,
            le.nom as salle,
            le.capacite,
            COUNT(DISTINCT e.id) as nb_examens,
            COUNT(DISTINCT e.date_examen) as jours_utilises,
            ROUND((SUM(e.duree_minutes) / (480 * COUNT(DISTINCT e.date_examen))) * 100, 1) as taux_occupation
        FROM lieu_examen le
        JOIN examens e ON le.id = e.salle_id 
            AND e.date_examen BETWEEN %s AND %s
            AND e.statut != 'annulé'
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        WHERE f.dept_id = %s
        GROUP BY le.id
        ORDER BY le.type, taux_occupation DESC
    """
    return run_query(query, (date_debut, date_fin, dept_id))

# PAGE: Tableau de Bord
if menu == "🏠 Tableau de Bord":
    st.header("🏠 Tableau de Bord Département")
    
    # Informations générales
    info = get_info_departement(DEPARTEMENT_ID)
    
    if info:
        info_data = info[0]
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Formations", int(info_data.get('nb_formations', 0)))
        
        with col2:
            st.metric("Modules", int(info_data.get('nb_modules', 0)))
        
        with col3:
            st.metric("Professeurs", int(info_data.get('nb_professeurs', 0)))
        
        with col4:
            st.metric("Examens planifiés", int(info_data.get('nb_examens_planifies', 0)))
        
        # Deuxième ligne de métriques
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric("Étudiants", int(info_data.get('nb_etudiants', 0)))
        
        with col6:
            st.metric("Salles disponibles", int(info_data.get('nb_salles', 0)))
        
        with col7:
            # Taux de validation
            examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
            if examens:
                df_examens = pd.DataFrame(examens)
                total_examens = len(df_examens)
                confirmes = len(df_examens[df_examens['statut'] == 'confirmé'])
                taux_validation = (float(confirmes) / float(total_examens) * 100) if total_examens > 0 else 0
                st.metric("Taux Validation", f"{taux_validation:.1f}%")
            else:
                st.metric("Taux Validation", "0%")
    
    # Graphiques rapides
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Examens par Formation")
        examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if examens:
            df_examens = pd.DataFrame(examens)
            exams_par_formation = df_examens.groupby('formation').size().reset_index(name='nb_examens')
            
            if not exams_par_formation.empty:
                fig = px.pie(exams_par_formation, values='nb_examens', names='formation',
                            title="Répartition des examens par formation")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Évolution des Examens")
        if examens:
            df_examens = pd.DataFrame(examens)
            df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
            exams_par_jour = df_examens.groupby('date_examen').size().reset_index(name='nb_examens')
            
            if not exams_par_jour.empty:
                fig = px.line(exams_par_jour, x='date_examen', y='nb_examens',
                             title="Nombre d'examens par jour",
                             markers=True)
                st.plotly_chart(fig, use_container_width=True)
    
    # Derniers examens
    st.subheader("📋 Derniers Examens Planifiés")
    if examens:
        df_recent = pd.DataFrame(examens)
        df_recent = df_recent.sort_values('date_examen', ascending=False).head(10)
        
        st.dataframe(
            df_recent[['date_examen', 'heure_debut', 'heure_fin', 'module', 'formation', 'statut', 'salle']],
            column_config={
                "date_examen": "Date",
                "heure_debut": "Heure début",
                "heure_fin": "Heure fin",
                "module": "Module",
                "formation": "Formation",
                "statut": "Statut",
                "salle": "Salle"
            },
            use_container_width=True
        )

# PAGE: Validation EDT
elif menu == "✅ Validation EDT":
    st.header("✅ Validation des Emplois du Temps")
    
    tab1, tab2 = st.tabs(["📋 Validation Individuelle", "✅ Validation par Formation"])
    
    with tab1:
        st.subheader("📋 Validation des Examens Individuels")
        
        # Filtres
        col1, col2 = st.columns(2)
        
        with col1:
            statut_filter = st.selectbox(
                "Filtrer par statut",
                options=['Tous', 'planifié', 'confirmé', 'annulé']
            )
        
        with col2:
            formations = get_formations_departement(DEPARTEMENT_ID)
            formation_options = ['Toutes'] + [f['nom'] for f in formations]
            formation_filter = st.selectbox("Filtrer par formation", formation_options)
        
        # Récupérer les examens
        examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if examens:
            df_examens = pd.DataFrame(examens)
            
            # Appliquer les filtres
            if statut_filter != 'Tous':
                df_examens = df_examens[df_examens['statut'] == statut_filter]
            
            if formation_filter != 'Toutes':
                df_examens = df_examens[df_examens['formation'] == formation_filter]
            
            # Afficher les examens
            st.subheader(f"📝 {len(df_examens)} Examens à Valider")
            
            for idx, row in df_examens.iterrows():
                with st.container():
                    col_info, col_action = st.columns([4, 1])
                    
                    with col_info:
                        # Définir la couleur selon le statut
                        if row['statut'] == 'confirmé':
                            status_color = "🟢"
                            status_text = "✅ Validé"
                        elif row['statut'] == 'annulé':
                            status_color = "🔴"
                            status_text = "❌ Annulé"
                        else:
                            status_color = "🟡"
                            status_text = "⏳ En attente"
                        
                        # Afficher les informations
                        st.write(f"""
                        **{status_color} {row['module']}** - {row['formation']}
                        
                        📅 **Date:** {row['date_examen']} | ⏰ **Horaire:** {row['heure_debut']} - {row['heure_fin']}
                        
                        🏫 **Salle:** {row['salle']} ({row['type_salle']}) | 
                        👨‍🏫 **Professeur:** {row['professeur']} | 
                        👥 **Étudiants:** {row['nb_etudiants']} ({row['taux_occupation']}% occupation)
                        
                        📊 **Statut:** {status_text}
                        """)
                    
                    with col_action:
                        st.write("")  # Espacement
                        if row['statut'] == 'planifié':
                            if st.button(f"✅ Valider", key=f"val_{row['id']}", use_container_width=True):
                                if valider_examen_departement(row['id']):
                                    st.success(f"Examen {row['module']} validé!")
                                    st.rerun()
                        elif row['statut'] == 'confirmé':
                            st.success("✅ Validé")
                        else:
                            st.error("❌ Annulé")
                    
                    st.divider()
        
        else:
            st.info("Aucun examen trouvé pour la période sélectionnée.")
    
    with tab2:
        st.subheader("✅ Validation Globale par Formation")
        
        # Statistiques par formation
        stats = get_statistiques_validation_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if stats:
            df_stats = pd.DataFrame(stats)
            
            # Convertir les colonnes en float
            for col in ['total_examens', 'confirmes', 'en_attente', 'annules', 'taux_validation']:
                if col in df_stats.columns:
                    df_stats[col] = pd.to_numeric(df_stats[col], errors='coerce').fillna(0)
            
            for _, formation in df_stats.iterrows():
                with st.container():
                    col_stat, col_action = st.columns([3, 1])
                    
                    with col_stat:
                        # Calculer la progression
                        confirmes_float = float(formation['confirmes'])
                        total_examens_float = float(formation['total_examens'])
                        progress = (confirmes_float / total_examens_float) if total_examens_float > 0 else 0
                        
                        st.write(f"**🎓 {formation['formation']}**")
                        st.progress(float(progress), text=f"{int(formation['confirmes'])}/{int(formation['total_examens'])} examens validés")
                        
                        # Détail des statuts
                        col_det1, col_det2, col_det3 = st.columns(3)
                        with col_det1:
                            st.metric("Confirmés", int(formation['confirmes']))
                        with col_det2:
                            st.metric("En attente", int(formation['en_attente']))
                        with col_det3:
                            st.metric("Annulés", int(formation['annules']))
                    
                    with col_action:
                        st.write("")  # Espacement
                        if formation['en_attente'] > 0:
                            # Récupérer l'ID de la formation
                            formation_id_query = run_query(
                                "SELECT id FROM formations WHERE nom = %s AND dept_id = %s", 
                                (formation['formation'], DEPARTEMENT_ID)
                            )
                            if formation_id_query:
                                formation_id = formation_id_query[0]['id']
                                if st.button(f"✅ Tout Valider", key=f"val_all_{formation_id}", use_container_width=True):
                                    if valider_tous_examens_formation(formation_id, date_debut, date_fin):
                                        st.success(f"Tous les examens de {formation['formation']} validés!")
                                        st.rerun()
                        else:
                            st.success("✅ Complètement validé")
                    
                    st.divider()
            
            # Graphique de synthèse
            st.subheader("📊 Synthèse de Validation")
            
            # Convertir les valeurs pour le graphique
            df_stats['confirmes_float'] = df_stats['confirmes'].astype(float)
            df_stats['en_attente_float'] = df_stats['en_attente'].astype(float)
            df_stats['annules_float'] = df_stats['annules'].astype(float)
            
            fig = px.bar(df_stats, x='formation', y=['confirmes_float', 'en_attente_float', 'annules_float'],
                        title="Statut de Validation par Formation",
                        labels={'value': "Nombre d'examens", 'formation': 'Formation', 'variable': 'Statut'},
                        barmode='stack',
                        color_discrete_map={'confirmes_float': '#2ecc71', 'en_attente_float': '#f39c12', 'annules_float': '#e74c3c'})
            
            # Renommer les légendes
            fig.for_each_trace(lambda t: t.update(name='Confirmés' if 'confirmes' in t.name else 
                                                'En Attente' if 'attente' in t.name else 'Annulés'))
            
            st.plotly_chart(fig, use_container_width=True)

# PAGE: Statistiques Département
elif menu == "📊 Statistiques Département":
    st.header("📊 Statistiques du Département")
    
    tab1, tab2, tab3 = st.tabs(["📈 Vue Globale", "👨‍🏫 Ressources Humaines", "🏫 Ressources Matérielles"])
    
    with tab1:
        st.subheader("📈 Vue Globale du Département")
        
        # Récupérer les données
        examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if examens:
            df_examens = pd.DataFrame(examens)
            
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_examens = len(df_examens)
                st.metric("Total Examens", total_examens)
            
            with col2:
                formations_uniques = df_examens['formation'].nunique()
                st.metric("Formations concernées", formations_uniques)
            
            with col3:
                salles_utilisees = df_examens['salle'].nunique()
                st.metric("Salles utilisées", salles_utilisees)
            
            with col4:
                profs_impliques = df_examens['professeur'].nunique()
                st.metric("Professeurs impliqués", profs_impliques)
            
            # Graphiques
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Répartition par statut
                statuts = df_examens['statut'].value_counts().reset_index()
                statuts.columns = ['statut', 'count']
                
                fig = px.pie(statuts, values='count', names='statut',
                            title="Répartition par statut",
                            color_discrete_map={'planifié': '#f39c12', 'confirmé': '#2ecc71', 'annulé': '#e74c3c'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                # Charge par jour
                df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
                charge_jour = df_examens.groupby('date_examen').agg({
                    'id': 'count',
                    'duree_minutes': 'sum'
                }).reset_index()
                
                fig = px.bar(charge_jour, x='date_examen', y='id',
                            title="Nombre d'examens par jour",
                            labels={'id': "Nombre d'examens", 'date_examen': 'Date'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Tableau récapitulatif
            st.subheader("📋 Récapitulatif par Formation")
            
            recap = df_examens.groupby('formation').agg({
                'id': 'count',
                'nb_etudiants': 'sum',
                'duree_minutes': 'sum',
                'statut': lambda x: (x == 'confirmé').sum()
            }).reset_index()
            
            recap.columns = ['Formation', 'Nb Examens', 'Total Étudiants', 'Durée Totale (min)', 'Examens Validés']
            
            # Convertir les valeurs en float
            recap['Total Étudiants'] = recap['Total Étudiants'].astype(float)
            recap['Durée Totale (min)'] = recap['Durée Totale (min)'].astype(float)
            recap['Examens Validés'] = recap['Examens Validés'].astype(float)
            recap['Nb Examens'] = recap['Nb Examens'].astype(float)
            
            recap['Taux Validation'] = (recap['Examens Validés'] / recap['Nb Examens'] * 100).round(1)
            recap['Durée Totale (min)'] = recap['Durée Totale (min)'].astype(int)
            recap['Nb Examens'] = recap['Nb Examens'].astype(int)
            recap['Total Étudiants'] = recap['Total Étudiants'].astype(int)
            recap['Examens Validés'] = recap['Examens Validés'].astype(int)
            
            st.dataframe(recap, use_container_width=True)
    
    with tab2:
        st.subheader("👨‍🏫 Statistiques des Ressources Humaines")
        
        # Récupérer les professeurs
        professeurs = get_professeurs_departement(DEPARTEMENT_ID)
        
        if professeurs:
            df_profs = pd.DataFrame(professeurs)
            
            # Convertir les colonnes en float
            for col in ['total_heures', 'heures_responsable', 'heures_surveillant', 'nb_examens_responsable', 'nb_examens_surveillant']:
                if col in df_profs.columns:
                    df_profs[col] = pd.to_numeric(df_profs[col], errors='coerce').fillna(0)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                charge_moyenne = float(df_profs['total_heures'].mean())
                st.metric("Charge moyenne", f"{charge_moyenne:.1f}h")
            
            with col2:
                profs_surveillants = df_profs[df_profs['nb_examens_surveillant'] > 0].shape[0]
                st.metric("Professeurs surveillants", profs_surveillants)
            
            with col3:
                profs_responsables = df_profs[df_profs['nb_examens_responsable'] > 0].shape[0]
                st.metric("Professeurs responsables", profs_responsables)
            
            # Graphique de charge
            st.subheader("📊 Charge de Travail des Professeurs")
            
            df_profs_sorted = df_profs.sort_values('total_heures', ascending=False).head(10)
            
            fig = px.bar(df_profs_sorted, x='nom_complet', y='total_heures',
                        title="Top 10 - Charge de travail (heures)",
                        labels={'nom_complet': 'Professeur', 'total_heures': 'Total Heures'},
                        text='total_heures',
                        color='total_heures',
                        color_continuous_scale='RdYlGn_r')
            
            fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau détaillé
            st.subheader("📋 Détail par Professeur")
            
            df_display = df_profs[['nom_complet', 'specialite', 'nb_examens_responsable', 
                                  'nb_examens_surveillant', 'heures_responsable', 
                                  'heures_surveillant', 'total_heures']].copy()
            
            # Formater l'affichage
            df_display['total_heures'] = df_display['total_heures'].apply(lambda x: f"{float(x):.1f}h")
            df_display['heures_responsable'] = df_display['heures_responsable'].apply(lambda x: f"{float(x):.1f}h" if x else "0.0h")
            df_display['heures_surveillant'] = df_display['heures_surveillant'].apply(lambda x: f"{float(x):.1f}h" if x else "0.0h")
            
            st.dataframe(
                df_display.sort_values('total_heures', ascending=False, key=lambda col: col.str.replace('h', '').astype(float)),
                column_config={
                    "nom_complet": "Professeur",
                    "specialite": "Spécialité",
                    "nb_examens_responsable": "Nb Examens Responsable",
                    "nb_examens_surveillant": "Nb Examens Surveillant",
                    "heures_responsable": "Heures Responsable",
                    "heures_surveillant": "Heures Surveillant",
                    "total_heures": "Total Heures"
                },
                use_container_width=True
            )
    
    with tab3:
        st.subheader("🏫 Statistiques des Ressources Matérielles")
        
        # Occupation des salles
        occupation = get_occupation_salles_departement(DEPARTEMENT_ID, date_debut, date_fin)
        
        if occupation:
            df_occupation = pd.DataFrame(occupation)
            
            # Convertir les colonnes en float
            for col in ['taux_occupation', 'capacite', 'nb_examens']:
                if col in df_occupation.columns:
                    df_occupation[col] = pd.to_numeric(df_occupation[col], errors='coerce').fillna(0)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                taux_occup_moyen = float(df_occupation['taux_occupation'].mean())
                st.metric("Occupation moyenne", f"{taux_occup_moyen:.1f}%")
            
            with col2:
                salles_utilisees = df_occupation[df_occupation['nb_examens'] > 0].shape[0]
                total_salles = df_occupation.shape[0]
                st.metric("Salles utilisées", f"{salles_utilisees}/{total_salles}")
            
            with col3:
                capacite_moyenne = float(df_occupation['capacite'].mean())
                st.metric("Capacité moyenne", f"{capacite_moyenne:.0f} places")
            
            # Graphique d'occupation
            st.subheader("📊 Occupation des Salles")
            
            fig = px.bar(df_occupation, x='salle', y='taux_occupation',
                        color='type',
                        title="Taux d'occupation par salle",
                        labels={'taux_occupation': "Taux d'occupation (%)", 'salle': 'Salle'},
                        text='taux_occupation')
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau détaillé
            st.subheader("📋 Détail des Salles Utilisées")
            
            df_display = df_occupation[['type', 'salle', 'capacite', 'nb_examens', 'jours_utilises', 'taux_occupation']].copy()
            df_display['taux_occupation'] = df_display['taux_occupation'].apply(lambda x: f"{float(x):.1f}%")
            df_display['capacite'] = df_display['capacite'].apply(lambda x: f"{int(x)} places")
            
            st.dataframe(
                df_display.sort_values('taux_occupation', ascending=False, key=lambda col: col.str.replace('%', '').astype(float)),
                column_config={
                    "type": "Type",
                    "salle": "Salle",
                    "capacite": "Capacité",
                    "nb_examens": "Nb Examens",
                    "jours_utilises": "Jours Utilisés",
                    "taux_occupation": "Taux Occupation"
                },
                use_container_width=True
            )

# PAGE: Conflits par Formation
elif menu == "⚠️ Conflits par Formation":
    st.header("⚠️ Analyse des Conflits par Formation")
    
    # Récupérer les conflits
    conflits = get_conflits_par_formation(DEPARTEMENT_ID, date_debut, date_fin)
    
    if conflits:
        df_conflits = pd.DataFrame(conflits)
        
        # Convertir les colonnes en float
        for col in ['total_conflits', 'conflits_etudiants', 'conflits_salles', 
                   'conflits_professeurs', 'total_examens', 'taux_conflits']:
            if col in df_conflits.columns:
                df_conflits[col] = pd.to_numeric(df_conflits[col], errors='coerce').fillna(0)
        
        # KPIs globaux
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_conflits = float(df_conflits['total_conflits'].sum())
            st.metric("Total Conflits", int(total_conflits))
        
        with col2:
            taux_moyen = float(df_conflits['taux_conflits'].mean())
            st.metric("Taux Conflits Moyen", f"{taux_moyen:.1f}%")
        
        with col3:
            if not df_conflits.empty:
                formation_max = df_conflits.loc[df_conflits['taux_conflits'].idxmax()]['formation']
                st.metric("Formation Critique", formation_max)
            else:
                st.metric("Formation Critique", "N/A")
        
        with col4:
            total_examens = float(df_conflits['total_examens'].sum())
            taux_global = (total_conflits / total_examens * 100) if total_examens > 0 else 0
            st.metric("Taux Conflits Global", f"{taux_global:.1f}%")
        
        # Graphique des conflits par formation
        st.subheader("📊 Répartition des Conflits par Formation")
        
        fig = px.bar(df_conflits, x='formation', y='taux_conflits',
                    color='taux_conflits',
                    title="Taux de Conflits par Formation",
                    labels={'formation': 'Formation', 'taux_conflits': 'Taux de Conflits (%)'},
                    text='taux_conflits',
                    color_continuous_scale='RdYlGn_r')
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique radar des types de conflits
        st.subheader("🎯 Types de Conflits par Formation")
        
        # Préparer les données pour le radar
        types_conflits = ['Étudiants', 'Salles', 'Professeurs']
        
        fig = go.Figure()
        
        for idx, row in df_conflits.iterrows():
            valeurs = [
                float(row['conflits_etudiants']),
                float(row['conflits_salles']),
                float(row['conflits_professeurs'])
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=valeurs,
                theta=types_conflits,
                fill='toself',
                name=row['formation']
            ))
        
        # Calculer la valeur maximale pour l'échelle
        max_val = max(
            df_conflits[['conflits_etudiants', 'conflits_salles', 'conflits_professeurs']].max().max(),
            1
        )
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, float(max_val) * 1.2]
                )),
            showlegend=True,
            title="Répartition des Types de Conflits par Formation"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        st.subheader("📋 Détail des Conflits par Formation")
        
        df_display = df_conflits.copy()
        df_display['taux_conflits'] = df_display['taux_conflits'].apply(lambda x: f"{float(x):.1f}%")
        
        st.dataframe(
            df_display[['formation', 'total_examens', 'conflits_etudiants', 
                       'conflits_salles', 'conflits_professeurs', 'total_conflits', 'taux_conflits']],
            column_config={
                "formation": "Formation",
                "total_examens": "Total Examens",
                "conflits_etudiants": "Conflits Étudiants",
                "conflits_salles": "Conflits Salles",
                "conflits_professeurs": "Conflits Professeurs",
                "total_conflits": "Total Conflits",
                "taux_conflits": "Taux Conflits"
            },
            use_container_width=True
        )
        
        # Analyse des conflits critiques
        st.subheader("🔍 Analyse des Conflits Critiques")
        
        df_critiques = df_conflits[df_conflits['taux_conflits'] > 10].copy()
        
        if not df_critiques.empty:
            for _, formation in df_critiques.iterrows():
                with st.expander(f"⚠️ {formation['formation']} - Taux: {float(formation['taux_conflits']):.1f}%"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Conflits Étudiants", int(formation['conflits_etudiants']))
                    
                    with col2:
                        st.metric("Conflits Salles", int(formation['conflits_salles']))
                    
                    with col3:
                        st.metric("Conflits Professeurs", int(formation['conflits_professeurs']))
                    
                    # Recommandations
                    st.info("**Recommandations:**")
                    
                    if formation['conflits_etudiants'] > 0:
                        st.write("• Réorganiser les horaires des examens pour éviter les chevauchements d'étudiants")
                    
                    if formation['conflits_salles'] > 0:
                        st.write("• Attribuer des salles différentes pour les examens qui se chevauchent")
                    
                    if formation['conflits_professeurs'] > 0:
                        st.write("• Redistribuer les surveillances entre les professeurs")
        
        else:
            st.success("✅ Aucune formation avec un taux de conflits critique (>10%)")
    
    else:
        st.info("Aucun conflit détecté pour la période sélectionnée.")

# PAGE: Gestion Professeurs
elif menu == "👨‍🏫 Gestion Professeurs":
    st.header("👨‍🏫 Gestion des Professeurs du Département")
    
    # Récupérer les professeurs
    professeurs = get_professeurs_departement(DEPARTEMENT_ID)
    
    if professeurs:
        df_profs = pd.DataFrame(professeurs)
        
        # Convertir les colonnes en float
        for col in ['total_heures', 'heures_responsable', 'heures_surveillant']:
            if col in df_profs.columns:
                df_profs[col] = pd.to_numeric(df_profs[col], errors='coerce').fillna(0)
        
        # Statistiques globales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre de professeurs", len(df_profs))
        
        with col2:
            profs_actifs = df_profs[df_profs['total_heures'] > 0].shape[0]
            st.metric("Professeurs actifs", profs_actifs)
        
        with col3:
            charge_totale = float(df_profs['total_heures'].sum())
            st.metric("Charge totale", f"{charge_totale:.1f}h")
        
        # Recherche et filtres
        st.subheader("🔍 Recherche et Filtres")
        
        col_search1, col_search2 = st.columns(2)
        
        with col_search1:
            recherche_nom = st.text_input("Rechercher par nom")
        
        with col_search2:
            min_heures = st.slider("Charge minimale (heures)", 0, 100, 0)
        
        # Appliquer les filtres
        df_filtre = df_profs.copy()
        
        if recherche_nom:
            df_filtre = df_filtre[df_filtre['nom_complet'].str.contains(recherche_nom, case=False, na=False)]
        
        df_filtre = df_filtre[df_filtre['total_heures'] >= min_heures]
        
        # Tableau des professeurs
        st.subheader("📋 Liste des Professeurs")
        
        df_display = df_filtre[['nom_complet', 'specialite', 'nb_examens_responsable', 
                               'nb_examens_surveillant', 'heures_responsable', 
                               'heures_surveillant', 'total_heures']].copy()
        
        # Formater l'affichage
        df_display['total_heures'] = df_display['total_heures'].apply(lambda x: f"{float(x):.1f}h")
        df_display['heures_responsable'] = df_display['heures_responsable'].apply(lambda x: f"{float(x):.1f}h" if pd.notnull(x) else "0.0h")
        df_display['heures_surveillant'] = df_display['heures_surveillant'].apply(lambda x: f"{float(x):.1f}h" if pd.notnull(x) else "0.0h")
        
        # Fonction pour trier par heures (en convertissant la chaîne en float)
        def sort_by_hours(col):
            return col.str.replace('h', '').astype(float)
        
        st.dataframe(
            df_display.sort_values('total_heures', ascending=False, key=sort_by_hours),
            column_config={
                "nom_complet": "Professeur",
                "specialite": "Spécialité",
                "nb_examens_responsable": "Examens Responsable",
                "nb_examens_surveillant": "Examens Surveillant",
                "heures_responsable": "Heures Responsable",
                "heures_surveillant": "Heures Surveillant",
                "total_heures": "Total Heures"
            },
            use_container_width=True
        )
        
        # Graphique de répartition
        st.subheader("📊 Répartition de la Charge")
        
        fig = px.scatter(df_profs, x='nb_examens_responsable', y='nb_examens_surveillant',
                        size='total_heures', color='specialite',
                        hover_data=['nom_complet'],
                        title="Relation Examens Responsable vs Surveillant",
                        labels={'nb_examens_responsable': 'Examens Responsable',
                               'nb_examens_surveillant': 'Examens Surveillant'})
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Export des données
        st.subheader("📤 Export des Données")
        
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"professeurs_departement_{departement_nom}_{date_debut}_{date_fin}.csv",
            mime="text/csv"
        )

# PAGE: Planning Département
elif menu == "📅 Planning Département":
    st.header("📅 Planning Complet du Département")
    
    # Sélection de l'affichage
    display_mode = st.radio(
        "Mode d'affichage",
        ["📋 Vue Tableau", "📊 Vue Calendrier", "🎯 Vue Graphique"],
        horizontal=True
    )
    
    # Récupérer les examens
    examens = get_examens_departement(DEPARTEMENT_ID, date_debut, date_fin)
    
    if examens:
        df_examens = pd.DataFrame(examens)
        
        if display_mode == "📋 Vue Tableau":
            st.subheader("📋 Planning Détaillé")
            
            # Filtres
            col1, col2, col3 = st.columns(3)
            
            with col1:
                formation_filter = st.selectbox(
                    "Filtrer par formation",
                    options=['Toutes'] + list(df_examens['formation'].unique())
                )
            
            with col2:
                statut_filter = st.selectbox(
                    "Filtrer par statut",
                    options=['Tous'] + list(df_examens['statut'].unique())
                )
            
            with col3:
                salle_filter = st.selectbox(
                    "Filtrer par salle",
                    options=['Toutes'] + list(df_examens['salle'].unique())
                )
            
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
                           'professeur', 'salle', 'nb_etudiants', 'taux_occupation', 'statut']],
                column_config={
                    "date_examen": "Date",
                    "heure_debut": "Heure début",
                    "heure_fin": "Heure fin",
                    "module": "Module",
                    "formation": "Formation",
                    "professeur": "Professeur",
                    "salle": "Salle",
                    "nb_etudiants": "Étudiants",
                    "taux_occupation": "Occupation",
                    "statut": "Statut"
                },
                use_container_width=True
            )
        
        elif display_mode == "📊 Vue Calendrier":
            st.subheader("📊 Planning Calendrier")
            
            # Grouper par date
            df_examens['date_examen'] = pd.to_datetime(df_examens['date_examen'])
            dates_uniques = sorted(df_examens['date_examen'].unique())
            
            for date in dates_uniques:
                df_date = df_examens[df_examens['date_examen'] == date]
                
                with st.expander(f"📅 {date.strftime('%A %d %B %Y')} ({len(df_date)} examens)"):
                    for _, exam in df_date.iterrows():
                        col_ex1, col_ex2 = st.columns([3, 1])
                        with col_ex1:
                            st.write(f"**{exam['module']}** - {exam['formation']}")
                            st.write(f"⏰ {exam['heure_debut']} - {exam['heure_fin']} | 👨‍🏫 {exam['professeur']}")
                        with col_ex2:
                            status_color = "🟢" if exam['statut'] == 'confirmé' else "🟡" if exam['statut'] == 'planifié' else "🔴"
                            st.write(f"{status_color} **{exam['statut']}**")
                            st.write(f"🏫 {exam['salle']} | 👥 {int(exam['nb_etudiants'])}")
                        
                        st.divider()
        
        elif display_mode == "🎯 Vue Graphique":
            st.subheader("🎯 Vue Graphique du Planning")
            
            # Préparer les données pour le graphique Gantt
            df_gantt = df_examens.copy()
            df_gantt['date_examen'] = pd.to_datetime(df_gantt['date_examen'])
            df_gantt['datetime_debut'] = pd.to_datetime(
                df_gantt['date_examen'].astype(str) + ' ' + df_gantt['heure_debut'].astype(str)
            )
            df_gantt['datetime_fin'] = pd.to_datetime(
                df_gantt['date_examen'].astype(str) + ' ' + df_gantt['heure_fin'].astype(str)
            )
            
            # Graphique Gantt
            fig = px.timeline(
                df_gantt,
                x_start="datetime_debut",
                x_end="datetime_fin",
                y="formation",
                color="module",
                hover_data=["professeur", "salle", "nb_etudiants", "statut"],
                title="Planning des Examens - Vue Gantt"
            )
            
            fig.update_yaxes(categoryorder="total ascending")
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap d'occupation des salles
            st.subheader("🔥 Heatmap d'Occupation des Salles")
            
            # Créer une heatmap par jour et par salle
            pivot_data = df_examens.pivot_table(
                index='date_examen',
                columns='salle',
                values='id',
                aggfunc='count',
                fill_value=0
            ).reset_index()
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_data.drop(columns=['date_examen']).values.T,
                x=pivot_data['date_examen'],
                y=pivot_data.drop(columns=['date_examen']).columns,
                colorscale='Viridis',
                colorbar=dict(title="Nombre d'examens")
            ))
            
            fig.update_layout(
                title="Occupation des Salles par Jour",
                xaxis_title="Date",
                yaxis_title="Salle",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Export du planning
        st.subheader("📤 Export du Planning")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv_data = df_examens.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_data,
                file_name=f"planning_{departement_nom}_{date_debut}_{date_fin}.csv",
                mime="text/csv"
            )
        
        with col_exp2:
            # Générer un rapport HTML simple
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Planning {departement_nom}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #2c3e50; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #3498db; color: white; }}
                    .valide {{ background-color: #d4edda; }}
                    .attente {{ background-color: #fff3cd; }}
                    .annule {{ background-color: #f8d7da; }}
                </style>
            </head>
            <body>
                <h1>📅 Planning d'Examens - {departement_nom}</h1>
                <p>Période: {date_debut} au {date_fin}</p>
                <p>Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                {df_examens.to_html(index=False, classes='table')}
            </body>
            </html>
            """
            
            st.download_button(
                label="📥 Télécharger HTML",
                data=html_content.encode('utf-8'),
                file_name=f"planning_{departement_nom}_{date_debut}_{date_fin}.html",
                mime="text/html"
            )
    
    else:
        st.info("Aucun examen trouvé pour la période sélectionnée.")

# Pied de page
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        Tableau de Bord Chef de Département - {departement_nom}<br>
        Version 1.0 • Gestion Départementale • © 2024
    </div>
    """,
    unsafe_allow_html=True
)