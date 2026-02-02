# app.py - Page d'accueil avec image et emojis académiques
import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import time
from datetime import datetime
import os
from PIL import Image

image_path = "young-muslim-student-class.jpg"
st.set_page_config(
    page_title="My Page",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default UI elements
hide_streamlit_style = """
    <style>
       #MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
        /* Cache la navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    /* Hide top menu and footer */
    #MainMenu {display: none;}
    footer {display: none;}
    header {display: none;}
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide the sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Ensure main content takes full width */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    /* Optional: remove padding around the page */
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Vérifier et charger l'image
@st.cache_data
def load_image():
    try:
        if os.path.exists(image_path):
            return Image.open(image_path)
        else:
            # Télécharger une image de fallback
            st.warning(f"Image non trouvée à l'emplacement: {image_path}")
            # Retourner une image vide (noir) comme fallback
            return Image.new('RGB', (800, 450), color='#0a1429')
    except Exception as e:
        st.error(f"Erreur de chargement d'image: {e}")
        return Image.new('RGB', (800, 450), color='#0a1429')

# Emojis académiques professionnels
ACADEMIC_EMOJIS = {
    "system": "📚",  # Livres pour système
    "dashboard": "📊",  # Graphiques
    "calendar": "📅",  # Calendrier
    "teacher": "👨‍🏫",  # Professeur
    "student": "👨‍🎓",  # Étudiant diplômé
    "department": "🏛️",  # Bâtiment institutionnel
    "module": "📖",  # Livre ouvert
    "classroom": "🏫",  # École
    "exam": "✍️",  # Main écrivant
    "schedule": "⏱️",  # Minuterie
    "admin": "🔧",  # Outil
    "dean": "🎖️",  # Médaille
    "coordinator": "🤝",  # Poignée de main
    "security": "🔒",  
    "ai": "🤖",  # Robot
    "mobile": "📱",  # Smartphone
    "stats": "📈",  # Graphique croissant
    "report": "📋",  # Liste
    "notification": "🔔",  # Cloche
    "export": "📤",  # Flèche sortante
    "import": "📥",  # Flèche entrante
    "settings": "⚙️",  # Engrenage
    "help": "❓",  # Point d'interrogation
    "time": "🕒",  # Horloge
    "location": "📍",  # Épingle de carte
    "email": "📧",  # Enveloppe
    "phone": "📞",  # Téléphone
    "university": "🎓",  # Mortier de diplômé
    "graduation": "🎓",  # Mortier
    "diploma": "📜",  # Parchemin
    "research": "🔬",  # Microscope
    "library": "📚",  # Livres
    "computer": "💻",  # Ordinateur portable
    "cloud": "☁️",  # Nuage
    "database": "🗄️",  # Fichier
    "network": "🌐",  # Globe
    "analytics": "📊",  # Tableau de bord
    "quality": "⭐",  # Étoile
    "innovation": "💡",  # Ampoule
    "collaboration": "👥",  # Silhouettes
    "success": "✅",  # Coches
    "warning": "⚠️",  # Attention
    "error": "❌",  # Croix
    "loading": "⏳",  # Sablier
    "check": "✓",  # Check
    "arrow": "→",  # Flèche
    "refresh": "🔄",  # Flèches circulaires
    "search": "🔍",  # Loupe
    "filter": "🔎",  # Loupe avec zoom
    "sort": "↕️",  # Flèches haut/bas
    "download": "⬇️",  # Flèche bas
    "upload": "⬆️",  # Flèche haut
    "print": "🖨️",  # Imprimante
    "save": "💾",  # Disquette
    "edit": "✏️",  # Crayon
    "delete": "🗑️",  # Corbeille
    "add": "➕",  # Plus
    "remove": "➖",  # Moins
    "view": "👁️",  # Œil
    "hide": "👁️‍🗨️",  # Œil barré
    "lock": "🔐",  # Cadenas fermé
    "unlock": "🔓",  # Cadenas ouvert
    "key": "🔑",  # Clé
    "home": "🏠",  # Maison
    "back": "↩️",  # Flèche retour
    "forward": "↪️",  # Flèche avant
    "up": "⬆️",  # Flèche haut
    "down": "⬇️",  # Flèche bas
    "left": "⬅️",  # Flèche gauche
    "right": "➡️",  # Flèche droite
    "menu": "☰",  # Menu hamburger
    "close": "✕",  # Croix
    "info": "ℹ️",  # Information
    "question": "❔",  # Point d'interrogation
    "exclamation": "❗",  # Point d'exclamation
    "star": "★",  # Étoile pleine
    "heart": "❤️",  # Cœur
    "flag": "🏁",  # Drapeau
    "trophy": "🏆",  # Trophée
    "medal": "🥇",  # Médaille or
    "certificate": "📜",  # Certificat
    "book": "📘",  # Livre bleu
    "notebook": "📓",  # Cahier
    "pen": "🖊️",  # Stylo
    "paper": "📄",  # Page
    "clipboard": "📋",  # Presse-papier
    "folder": "📁",  # Dossier
    "archive": "🗃️",  # Boîte d'archives
    "bell": "🔔",  # Cloche
    "megaphone": "📣",  # Mégaphone
    "speech": "💬",  # Bulle de dialogue
    "thought": "💭",  # Bulle de pensée
    "money": "💰",  # Sac d'argent
    "budget": "💵",  # Billet
    "growth": "📈",  # Croissance
    "decline": "📉",  # Déclin
    "stable": "📊",  # Stable
    "target": "🎯",  # Cible
    "goal": "🥅",  # But de football
    "plan": "🗺️",  # Carte
    "strategy": "♟️",  # Pion d'échecs
    "team": "👨‍👩‍👧‍👦",  # Famille
    "meeting": "👥",  # Réunion
    "presentation": "📽️",  # Projecteur
    "video": "📹",  # Caméra
    "audio": "🎧",  # Casque
    "image": "🖼️",  # Cadre photo
    "link": "🔗",  # Chaîne
    "attachment": "📎",  # Trombone
    "zip": "🗜️",  # Pince
    "code": "💻",  # Code
    "bug": "🐛",  # Insecte
    "feature": "✨",  # Étincelles
    "update": "🔄",  # Mise à jour
    "version": "🏷️",  # Étiquette
    "release": "🚀",  # Fusée
    "launch": "🎆",  # Feux d'artifice
    "celebration": "🎉",  # Confettis
    "party": "🥳",  # Visage fêtard
    "confetti": "🎊",  # Confettis ballon
    "clock": "🕰️",  # Horloge murale
    "watch": "⌚",  # Montre
    "alarm": "⏰",  # Réveil
    "timer": "⏲️",  # Minuteur
    "stopwatch": "⏱️",  # Chronomètre
    "calendar_day": "📆",  # Calendrier du jour
    "date": "📅",  # Date
    "event": "📅",  # Événement
    "reminder": "🗓️",  # Calendrier avec date
    "deadline": "⏳",  # Échéance
    "urgent": "🚨",  # Gyrophare
    "important": "‼️",  # Double exclamation
    "priority": "🔥",  # Feu
    "critical": "💥",  # Explosion
    "normal": "🟢",  # Cercle vert
    "low": "🟡",  # Cercle jaune
    "medium": "🟠",  # Cercle orange
    "high": "🔴",  # Cercle rouge
}

# Page d'accueil
def main():
    # Charger l'image
    pil_image = load_image()
    
    # Style CSS personnalisé - Design académique professionnel
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS académiques */
    :root {{
        --navy: #0a1429;
        --navy-light: #1a2744;
        --navy-lighter: #2a3659;
        --gold: #d4a853;
        --gold-light: #e6c47a;
        --gold-dark: #b8923f;
        --ivory: #f8f5f0;
        --parchment: #f5efdc;
        --sage: #8a9a5b;
        --oxford-blue: #002147;
        --crimson: #990000;
        --bg-light: #f8fafc;
        --card-bg: #ffffff;
        --text-dark: #1e293b;
        --text-muted: #64748b;
        --border-light: #e2e8f0;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.08);
        --shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.12);
        --gradient-gold: linear-gradient(135deg, #d4a853, #f6d365);
        --gradient-navy: linear-gradient(135deg, #0a1429, #1a2744);
        --gradient-academic: linear-gradient(135deg, #0a1429, #002147, #1a2744);
        --gradient-card: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    }}
    
    /* Reset et base */
    .main {{
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #0a1429 0%, #1a2744 100%) !important;
        min-height: 100vh;
    }}
    
    /* Hero Header avec image universitaire */
    .hero-container {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3rem;
        align-items: center;
        padding: 3rem 1.5rem;
        background: var(--gradient-academic);
        border-radius: 0 0 1.5rem 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        min-height: 450px;
        position: relative;
        overflow: hidden;
    }}
    
    .hero-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
    }}
    
    .hero-content {{
        color: white;
        z-index: 2;
        padding-left: 1rem;
    }}
    
    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(212, 168, 83, 0.2);
        color: var(--gold-light);
        padding: 0.4rem 0.8rem;
        border-radius: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.75rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(212, 168, 83, 0.3);
        backdrop-filter: blur(10px);
    }}
    
    .hero-title {{
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0 0 1rem 0;
        line-height: 1.2;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }}
    
    .hero-title span {{
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .hero-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 90%;
    }}
    
    .hero-buttons {{
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
    }}
    
    .hero-button-primary {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--gradient-gold);
        color: var(--navy);
        padding: 0.8rem 1.8rem;
        border-radius: 0.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(212, 168, 83, 0.35);
        position: relative;
        overflow: hidden;
    }}
    
    .hero-button-primary:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212, 168, 83, 0.45);
    }}
    
    .hero-button-secondary {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 0.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }}
    
    .hero-button-secondary:hover {{
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.3);
    }}
    
    .hero-image-container {{
        position: relative;
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 2px solid var(--gold);
        height: 350px;
        width: 100%;
    }}
    
    .hero-image {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}
    
    .hero-stats {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .hero-stat {{
        text-align: center;
    }}
    
    .hero-stat-number {{
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--gold);
        line-height: 1;
        margin-bottom: 0.3rem;
    }}
    
    .hero-stat-label {{
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.8);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    
    /* Navigation Bar académique - FIXED */
    .nav-bar {{
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        padding: 1rem 2rem;
        border-radius: 0.8rem;
        box-shadow: var(--shadow-md);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-light);
        position: sticky;
        top: 0.5rem;
        z-index: 1000;
        transition: all 0.3s ease;
    }}
    
    .nav-brand {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }}
    
    .nav-brand-icon {{
        font-size: 1.5rem;
        color: var(--gold);
        background: rgba(212, 168, 83, 0.1);
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid var(--gold);
    }}
    
    .nav-brand-text {{
        display: flex;
        flex-direction: column;
    }}
    
    .nav-brand-title {{
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        font-weight: 700;
        background: var(--gradient-navy);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }}
    
    .nav-brand-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    
    .nav-info {{
        display: flex;
        align-items: center;
        gap: 1.2rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: var(--text-muted);
    }}
    
    .nav-info-item {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    
    .nav-buttons {{
        display: flex;
        gap: 0.8rem;
    }}
    
    .nav-btn-academic {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.6rem 1.2rem;
        background: var(--gradient-navy);
        border-radius: 0.6rem;
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        text-decoration: none;
        transition: all 0.2s ease;
        border: none;
        cursor: pointer;
    }}
    
    .nav-btn-academic:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(10, 20, 41, 0.2);
    }}
    
    .nav-btn-outline-academic {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.6rem 1.2rem;
        border: 2px solid var(--navy-light);
        border-radius: 0.6rem;
        color: var(--navy-light);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        text-decoration: none;
        transition: all 0.2s ease;
    }}
    
    .nav-btn-outline-academic:hover {{
        background: var(--navy-light);
        color: white;
        transform: translateY(-2px);
    }}
    
    /* Section Title académique */
    .section-title {{
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        position: relative;
        display: inline-block;
    }}
    
    .section-title::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 4rem;
        height: 4px;
        background: var(--gradient-gold);
        border-radius: 2px;
    }}
    
    /* Stats Grid amélioré */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.2rem;
        margin-bottom: 2.5rem;
        margin-top:1rem;
    }}
    
    .stat-card-academic {{
        background: var(--gradient-card);
        border-radius: 1rem;
        padding: 1.8rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
    }}
    
    .stat-card-academic:hover {{
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
        border-color: var(--gold);
    }}
    
    .stat-card-academic::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-gold);
    }}
    
    .stat-icon-academic {{
        font-size: 2rem;
        margin-bottom: 1rem;
        background: rgba(212, 168, 83, 0.1);
        width: 55px;
        height: 55px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid rgba(212, 168, 83, 0.3);
    }}
    
    .stat-number-academic {{
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: baseline;
        gap: 0.2rem;
    }}
    
    .stat-suffix-academic {{
        font-size: 1rem;
        color: var(--text-muted);
        font-weight: 500;
    }}
    
    .stat-label-academic {{
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.4rem;
    }}
    
    .stat-description {{
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: var(--text-muted);
        line-height: 1.4;
        margin-top: 0.4rem;
    }}
    
    /* Features Grid académique */
    .features-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2.5rem;
    }}
    
    .feature-card-academic {{
        background: var(--card-bg);
        border-radius: 1rem;
        padding: 2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
        margin-top:1rem;      
    }}
    
    .feature-card-academic:hover {{
        transform: translateY(-6px);
        box-shadow: var(--shadow-md);
        border-color: var(--gold);
    }}
    
    .feature-card-academic::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-gold);
    }}
    
    .feature-icon-academic {{
        width: 60px;
        height: 60px;
        background: var(--gradient-navy);
        border-radius: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        color: white;
        box-shadow: 0 6px 16px rgba(10, 20, 41, 0.15);
    }}
    
    .feature-title-academic {{
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 0.8rem;
        line-height: 1.3;
    }}
    
    .feature-description-academic {{
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: var(--text-muted);
        line-height: 1.5;
        margin-bottom: 1rem;
    }}
    
    .feature-list-academic {{
        list-style: none;
        padding: 0;
        margin: 0;
    }}
    
    .feature-list-academic li {{
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        padding: 0.6rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: var(--text-dark);
        border-bottom: 1px solid var(--border-light);
    }}
    
    .feature-list-academic li:last-child {{
        border-bottom: none;
    }}
    
    .feature-list-academic li::before {{
        content: '✓';
        color: var(--gold);
        font-weight: 700;
        font-size: 0.9rem;
        flex-shrink: 0;
        margin-top: 0.1rem;
    }}
    
    /* Roles Grid académique */
    .roles-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.2rem;
        margin-bottom: 2.5rem;
    }}
    
    .role-card-academic {{
        background: var(--gradient-card);
        border-radius: 1rem;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
        margin-top:1rem
    }}
    
    .role-card-academic:hover {{
        transform: translateY(-5px);
        box-shadow: var(--shadow-md);
        border-color: var(--gold);
    }}
    
    .role-card-academic::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-gold);
    }}
    
    .role-icon-academic {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: var(--navy);
        background: rgba(212, 168, 83, 0.1);
        width: 75px;
        height: 75px;
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 2px solid rgba(212, 168, 83, 0.3);
    }}
    
    .role-title-academic {{
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 1rem;
    }}
    
    .role-features-academic {{
        list-style: none;
        padding: 0;
        margin: 0;
    }}
    
    .role-features-academic li {{
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: var(--text-muted);
        padding: 0.6rem 0;
        position: relative;
    }}
    
    .role-features-academic li::before {{
        content: '•';
        color: var(--gold);
        font-weight: bold;
        position: absolute;
        left: -0.8rem;
        font-size: 1rem;
    }}
    
    /* CTA Section académique */
    .cta-section-academic {{
        text-align: center;
        padding: 3rem 1.5rem;
        margin: 2.5rem 0;
        background: var(--gradient-academic);
        border-radius: 1.5rem;
        position: relative;
        overflow: hidden;
    }}
    
    .cta-section-academic::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23d4a853' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
    }}
    
    .cta-title-academic {{
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1rem;
        position: relative;
        z-index: 2;
    }}
    
    .cta-subtitle-academic {{
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        max-width: 600px;
        line-height: 1.6;
        position: relative;
        z-index: 2;
        margin-left: auto;
        margin-right: auto;
    }}
    
    /* Custom Streamlit Button académique */
    .stButton > button {{
        /* Base styling */
        background: linear-gradient(135deg, #D4A853 0%, #B38B3C 50%, #9A7732 100%) !important;
        color: #0A1931 !important;
        border: none !important;
        padding: 1rem 3rem !important;
        border-radius: 0.8rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.02em !important;
        cursor: pointer !important;
        
        /* Layout & positioning */
        position: relative !important;
        overflow: hidden !important;
        isolation: isolate !important;
        outline: none !important;
        
        /* Transitions */
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        
        /* Shadows */
        box-shadow: 
            0 4px 14px rgba(212, 168, 83, 0.25),
            0 1px 3px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        
        /* Text rendering */
        text-transform: none !important;
        text-decoration: none !important;
        white-space: nowrap !important;
        user-select: none !important;
        
        /* Performance */
        backface-visibility: hidden !important;
        transform: translateZ(0) !important;
    }}

    /* Hover state */
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 
            0 8px 20px rgba(212, 168, 83, 0.35),
            0 3px 6px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }}

    /* Active/Click state */
    .stButton > button:active {{
        transform: translateY(0) !important;
        box-shadow: 
            0 2px 8px rgba(212, 168, 83, 0.3),
            0 1px 2px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        transition-duration: 0.1s !important;
    }}

    /* Focus state for accessibility */
    .stButton > button:focus {{
        outline: 2px solid rgba(212, 168, 83, 0.6) !important;
        outline-offset: 2px !important;
    }}

    /* Disabled state */
    .stButton > button:disabled {{
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
    }}

    /* Shine effect on hover */
    .stButton > button::after {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 50%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        transition: left 0.7s ease !important;
        z-index: 1;
    }}

    .stButton > button:hover::after {{
        left: 100%;
    }}

    /* Ensure text stays above shine effect */
    .stButton > button > * {{
        position: relative;
        z-index: 2;
    }}

    /* Add a subtle border for depth (optional) */
    .stButton > button::before {{
        content: '';
        position: absolute;
        inset: 1px;
        border-radius: calc(0.8rem - 1px);
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(0, 0, 0, 0.05) 100%
        );
        pointer-events: none;
        z-index: 1;
    }}
    
    /* Footer académique */
    .footer-academic {{
        background: var(--gradient-academic);
        padding: 3rem 1.5rem 2rem;
        border-radius: 1rem 1rem 0 0;
        margin: 3rem -1rem -1rem -1rem;
        position: relative;
        overflow: hidden;
    }}
    
    .footer-academic::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--gradient-gold);
    }}
    
    .footer-content {{
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
    }}
    
    .footer-brand-academic {{
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }}
    
    .footer-brand-header {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }}
    
    .footer-brand-icon {{
        font-size: 2rem;
        color: var(--gold);
    }}
    
    .footer-brand-title {{
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: white;
        line-height: 1.2;
    }}
    
    .footer-brand-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 0.2rem;
    }}
    
    .footer-description {{
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
        line-height: 1.5;
    }}
    
    .footer-section {{
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }}
    
    .footer-section-title {{
        font-family: 'Playfair Display', serif;
        font-size: 1rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.4rem;
    }}
    
    .footer-links {{
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }}
    
    .footer-links a {{
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
        text-decoration: none;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    
    .footer-links a:hover {{
        color: var(--gold-light);
        transform: translateX(3px);
    }}
    
    .footer-contact-info {{
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }}
    
    .footer-contact-item {{
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
    }}
    
    .footer-bottom {{
        max-width: 1200px;
        margin: 2rem auto 0;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    .footer-copyright {{
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.5);
    }}
    
    .footer-legal {{
        display: flex;
        gap: 1rem;
    }}
    
    .footer-legal a {{
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.5);
        text-decoration: none;
        transition: all 0.3s ease;
    }}
    
    .footer-legal a:hover {{
        color: var(--gold-light);
    }}
    
    /* Responsive Design */
    @media (max-width: 1024px) {{
        .hero-container {{
            grid-template-columns: 1fr;
            text-align: center;
            gap: 2rem;
            padding: 2rem 1rem;
        }}
        
        .hero-content {{
            padding-left: 0;
        }}
        
        .hero-subtitle {{
            max-width: 100%;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .hero-image-container {{
            height: 280px;
            max-width: 500px;
            margin: 0 auto;
        }}
    }}
    
    @media (max-width: 768px) {{
        .hero-title {{
            font-size: 2rem;
        }}
        
        .hero-buttons {{
            flex-direction: column;
            align-items: center;
        }}
        
        .nav-bar {{
            flex-direction: column;
            gap: 1rem;
            text-align: center;
            padding: 1rem;
        }}
        
        .nav-info {{
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .nav-buttons {{
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .section-title {{
            font-size: 1.5rem;
        }}
        
        .feature-card-academic,
        .role-card-academic,
        .stat-card-academic {{
            padding: 1.5rem;
        }}
        
        .cta-section-academic {{
            padding: 2rem 1rem;
        }}
        
        .cta-title-academic {{
            font-size: 1.8rem;
        }}
        
        .footer-content {{
            grid-template-columns: 1fr;
            text-align: center;
        }}
        
        .footer-links a,
        .footer-contact-item {{
            justify-content: center;
        }}
        
        .footer-bottom {{
            flex-direction: column;
            text-align: center;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # Navigation Bar
    current_date = datetime.now().strftime("%d/%m/%Y")
    current_time = datetime.now().strftime("%H:%M")
    
    st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-brand">
            <div class="nav-brand-icon">
                {ACADEMIC_EMOJIS['university']}
            </div>
            <div class="nav-brand-text">
                <div class="nav-brand-title">Gestion Examens Pro</div>
                <div class="nav-brand-subtitle">Plateforme Académique Officielle</div>
            </div>
        </div>
        <div class="nav-info">
            <div class="nav-info-item">
                <span>{ACADEMIC_EMOJIS['calendar_day']}</span>
                <span>{current_date}</span>
            </div>
            <div class="nav-info-item">
                <span>{ACADEMIC_EMOJIS['time']}</span>
                <span>{current_time}</span>
            </div>
            <div class="nav-info-item">
                <span>{ACADEMIC_EMOJIS['location']}</span>
                <span>Université Boumerdes</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
<style>
/* Hero section container */
.hero-content {
    background-color: #001f3f; /* Navy background */
    background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e'); /* optional image */
    background-size: cover;  /* Cover entire container */
    background-position: center;
    padding: 50px;
    border-radius: 15px;
    color: white;  /* Make text readable on dark bg */
}

/* Buttons styling */
.hero-button-primary, .hero-button-secondary {
    display: inline-block;
    padding: 12px 25px;
    margin: 10px 10px 0 0;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
}

.hero-button-primary {
    background-color: #ff6f61;
    color: white;
}

.hero-button-secondary {
    background-color: transparent;
    border: 2px solid white;
    color: white;
}

/* Stats */
.hero-stats {
    display: flex;
    gap: 30px;
    margin-top: 30px;
}
.hero-stat-number {
    font-size: 2em;
    font-weight: bold;
}
.hero-stat-label {
    font-size: 0.9em;
    color: #ddd;
}
</style>
""", unsafe_allow_html=True)
    # Hero Section avec colonnes Streamlit
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown(f"""
        <div class="hero-content">
            <div class="hero-badge">
                {ACADEMIC_EMOJIS['university']} Système Académique Officiel
            </div>
            <h1 class="hero-title">
                {ACADEMIC_EMOJIS['system']} Système de Gestion <span>des Examens</span>
            </h1>
            <p class="hero-subtitle">
                Solution complète et intuitive pour la planification, l'organisation et la gestion optimisée des examens universitaires. 
                Gérez vos sessions d'examens avec efficacité et précision professionnelle.
            </p>
            <div class="hero-buttons">
                <a class="hero-button-primary">
                    <span>{ACADEMIC_EMOJIS['calendar']} Données fiables et mises à jour </span>
                </a>
                <a class="hero-button-secondary">
                    <span>{ACADEMIC_EMOJIS['stats']} Disponible 24h/24 et 7j/7</span>
                    <span>{ACADEMIC_EMOJIS['analytics']}</span>
                </a>
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="hero-stat-number">10+</div>
                    <div class="hero-stat-label">Établissements</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-number">500+</div>
                    <div class="hero-stat-label">Examens gérés</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-number">99.8%</div>
                    <div class="hero-stat-label">Satisfaction</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Container pour l'image avec style CSS
        # Afficher l'image avec Streamlit
        st.image(pil_image, use_container_width=True, 
                caption="", 
                output_format="auto")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Modified columns layout for two buttons
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    
    with col2:
        if st.button(f"{ACADEMIC_EMOJIS['calendar']} Voir Planning", use_container_width=True, type="secondary"):
            st.switch_page("pages/app_etudiant.py")
    
    with col4:
        if st.button(f"{ACADEMIC_EMOJIS['key']} Connexion", use_container_width=True, type="primary"):
            st.switch_page("pages/log.py")
    
    # Statistiques principales
    st.markdown(f'<h2 class="section-title">{ACADEMIC_EMOJIS["dashboard"]} Tableau de Bord Global</h2>', unsafe_allow_html=True)
    
    with st.spinner("Chargement des statistiques académiques..."):
        time.sleep(0.5)
        
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card-academic">
                <div class="stat-icon-academic">{ACADEMIC_EMOJIS['department']}</div>
                <div class="stat-number-academic">12<span class="stat-suffix-academic">+</span></div>
                <div class="stat-label-academic">Départements Actifs</div>
                <div class="stat-description">Filières académiques en activité</div>
            </div>
            <div class="stat-card-academic">
                <div class="stat-icon-academic">{ACADEMIC_EMOJIS['graduation']}</div>
                <div class="stat-number-academic">28<span class="stat-suffix-academic"></span></div>
                <div class="stat-label-academic">Formations Diplômantes</div>
                <div class="stat-description">Programmes de formation accrédités</div>
            </div>
            <div class="stat-card-academic">
                <div class="stat-icon-academic">{ACADEMIC_EMOJIS['teacher']}</div>
                <div class="stat-number-academic">245<span class="stat-suffix-academic"></span></div>
                <div class="stat-label-academic">Enseignants-Chercheurs</div>
                <div class="stat-description">Corps professoral qualifié</div>
            </div>
            <div class="stat-card-academic">
                <div class="stat-icon-academic">{ACADEMIC_EMOJIS['student']}</div>
                <div class="stat-number-academic">13000<span class="stat-suffix-academic"></span></div>
                <div class="stat-label-academic">Étudiants Inscrits</div>
                <div class="stat-description">Effectif étudiant actuel</div>
            </div>
            <div class="stat-card-academic">
                <div class="stat-icon-academic">{ACADEMIC_EMOJIS['module']}</div>
                <div class="stat-number-academic">186<span class="stat-suffix-academic"></span></div>
                <div class="stat-label-academic">Unités d'Enseignement</div>
                <div class="stat-description">Modules pédagogiques actifs</div>
            </div>
            <div class="stat-card-academic">
                <div class="stat-icon-academic">{ACADEMIC_EMOJIS['classroom']}</div>
                <div class="stat-number-academic">42<span class="stat-suffix-academic"></span></div>
                <div class="stat-label-academic">Salles d'Examen</div>
                <div class="stat-description">Amphithéâtres et salles équipées</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Fonctionnalités principales
    st.markdown(f'<h2 class="section-title">{ACADEMIC_EMOJIS["feature"]} Fonctionnalités Avancées</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card-academic">
            <div class="feature-icon-academic">{ACADEMIC_EMOJIS['ai']}</div>
            <h3 class="feature-title-academic">Intelligence Artificielle</h3>
            <p class="feature-description-academic">
                Planification intelligente avec algorithmes d'optimisation avancés pour une gestion optimale des ressources.
            </p>
            <ul class="feature-list-academic">
                <li>Génération automatique des plannings</li>
                <li>Détection des conflits en temps réel</li>
                <li>Optimisation des ressources académiques</li>
                <li>Prévision des besoins en surveillance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card-academic">
            <div class="feature-icon-academic">{ACADEMIC_EMOJIS['mobile']}</div>
            <h3 class="feature-title-academic">Interface Mobile</h3>
            <p class="feature-description-academic">
                Accédez à toutes les fonctionnalités depuis votre mobile avec une application native dédiée.
            </p>
            <ul class="feature-list-academic">
                <li>Application mobile multiplateforme</li>
                <li>Notifications push en temps réel</li>
                <li>Scan QR code pour présence</li>
                <li>Consultation hors ligne sécurisée</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="feature-card-academic">
            <div class="feature-icon-academic">{ACADEMIC_EMOJIS['security']}</div>
            <h3 class="feature-title-academic">Sécurité & Conformité</h3>
            <p class="feature-description-academic">
                Système sécurisé conforme aux réglementations académiques et standards internationaux.
            </p>
            <ul class="feature-list-academic">
                <li>Chiffrement des données de bout en bout</li>
                <li>Audit complet des modifications</li>
                <li>Conformité RGPD et standards</li>
                <li>Sauvegarde automatique cloud</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Espaces personnalisés
    st.markdown(f'<h2 class="section-title">{ACADEMIC_EMOJIS["collaboration"]} Espaces Personnalisés</h2>', unsafe_allow_html=True)
    
    roles_col1, roles_col2, roles_col3, roles_col4 = st.columns(4)
    
    with roles_col1:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['admin']}</div>
            <h4 class="role-title-academic">Administrateur</h4>
            <ul class="role-features-academic">
                <li>Gestion complète du système</li>
                <li>Supervision des utilisateurs</li>
                <li>Configuration avancée</li>
                <li>Rapports détaillés</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with roles_col2:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['dean']}</div>
            <h4 class="role-title-academic">Direction</h4>
            <ul class="role-features-academic">
                <li>Vue stratégique globale</li>
                <li>Indicateurs de performance</li>
                <li>Validation des décisions</li>
                <li>Planification annuelle</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with roles_col3:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['coordinator']}</div>
            <h4 class="role-title-academic">Coordination</h4>
            <ul class="role-features-academic">
                <li>Gestion départementale</li>
                <li>Supervision pédagogique</li>
                <li>Coordination des examens</li>
                <li>Communication interne</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with roles_col4:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['teacher']}</div>
            <h4 class="role-title-academic">Enseignants</h4>
            <ul class="role-features-academic">
                <li>Gestion des examens</li>
                <li>Suivi des corrections</li>
                <li>Communication étudiants</li>
                <li>Statistiques personnelles</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown(f"""
    <div class="cta-section-academic">
        <h2 class="cta-title-academic">Prêt à optimiser vos examens ?</h2>
        <p class="cta-subtitle-academic">
            Rejoignez plus de 50 établissements d'enseignement supérieur qui utilisent déjà notre système 
            pour gérer leurs examens avec efficacité, sécurité et sérénité.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # FOOTER
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1429, #002147);
        padding: 2rem;
        color: white;
        text-align: center;
        border-radius: 1rem;
        margin-top: 2rem;
    ">
        <h3>🎓 Système de Gestion des Examens</h3>
        <p>© 2024 Université des Sciences et Technologies</p>
        <p>Contact: support@univ-examens.edu</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
