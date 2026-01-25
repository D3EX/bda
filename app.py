# app.py - Page d'accueil avec image et emojis académiques - OPTIMISÉ
import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import time
from datetime import datetime
import base64
import sqlite3     
import os

image_path = r"young-muslim-student-class.jpg"
st.set_page_config(
    page_title="My Page",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cache the image encoding - FIX 1
@st.cache_data(ttl=3600)
def get_base64_image():
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return None
    except Exception as e:
        st.error(f"Erreur de chargement d'image: {e}")
        return None

# Cache CSS - FIX 2
@st.cache_data(ttl=3600)
def load_css():
    return """
    <style>
    /* Using system fonts for speed - FIX 3 */
    :root {
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
    }
    
    /* System fonts for speed */
    .main {
        background-color: var(--bg-light);
        font-family: 'Segoe UI', system-ui, sans-serif;
        line-height: 1.6;
    }
    
    .stApp {
        background: var(--bg-light);
        min-height: 100vh;
    }
    
    /* Hero Header optimisé */
    .hero-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        align-items: center;
        padding: 2rem;
        background: var(--gradient-academic);
        border-radius: 0 0 1.5rem 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        min-height: 400px;
        position: relative;
        overflow: hidden;
    }
    
    .hero-content {
        color: white;
        z-index: 2;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(212, 168, 83, 0.2);
        color: var(--gold-light);
        padding: 0.4rem 0.8rem;
        border-radius: 1.5rem;
        font-weight: 600;
        font-size: 0.75rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(212, 168, 83, 0.3);
    }
    
    .hero-title {
        font-family: 'Georgia', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: white;
        margin: 0 0 1rem 0;
        line-height: 1.2;
    }
    
    .hero-title span {
        background: var(--gradient-gold);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        line-height: 1.5;
    }
    
    .hero-buttons {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
    }
    
    .hero-button-primary {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--gradient-gold);
        color: var(--navy);
        padding: 0.7rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.85rem;
        text-decoration: none;
        transition: transform 0.2s ease;
        box-shadow: 0 4px 12px rgba(212, 168, 83, 0.3);
    }
    
    .hero-button-primary:hover {
        transform: translateY(-2px);
    }
    
    .hero-button-secondary {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 0.7rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        font-size: 0.85rem;
        text-decoration: none;
        transition: all 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .hero-button-secondary:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .hero-image-container {
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 2px solid var(--gold);
        height: 320px;
    }
    
    .hero-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        background-color: var(--navy);
    }
    
    .hero-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-stat-number {
        font-family: 'Georgia', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--gold);
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    
    .hero-stat-label {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.8);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    /* Navigation Bar */
    .nav-bar {
        background: rgba(255, 255, 255, 0.98);
        padding: 1rem;
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
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .nav-brand-icon {
        font-size: 1.3rem;
        color: var(--gold);
        background: rgba(212, 168, 83, 0.1);
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid var(--gold);
    }
    
    .nav-brand-text {
        display: flex;
        flex-direction: column;
    }
    
    .nav-brand-title {
        font-family: 'Georgia', serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1.2;
    }
    
    .nav-brand-subtitle {
        font-size: 0.6rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    .nav-info {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.75rem;
        color: var(--text-muted);
    }
    
    /* Section Title */
    .section-title {
        font-family: 'Georgia', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        position: relative;
        display: inline-block;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 3rem;
        height: 3px;
        background: var(--gradient-gold);
        border-radius: 2px;
    }
    
    /* Stats Grid simplifié */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
        margin-top: 1rem;
    }
    
    .stat-card-academic {
        background: var(--gradient-card);
        border-radius: 1rem;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
    }
    
    .stat-card-academic:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }
    
    .stat-card-academic::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-gold);
    }
    
    .stat-icon-academic {
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    .stat-number-academic {
        font-family: 'Georgia', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    
    .stat-label-academic {
        font-weight: 600;
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    .stat-description {
        font-size: 0.75rem;
        color: var(--text-muted);
        line-height: 1.3;
        margin-top: 0.3rem;
    }
    
    /* Features Grid */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .feature-card-academic {
        background: var(--card-bg);
        border-radius: 1rem;
        padding: 1.5rem;
        transition: transform 0.2s ease;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        position: relative;
        margin-top: 1rem;
    }
    
    .feature-card-academic:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
    }
    
    .feature-card-academic::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-gold);
    }
    
    .feature-icon-academic {
        width: 50px;
        height: 50px;
        background: var(--gradient-navy);
        border-radius: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        font-size: 1.3rem;
        color: white;
    }
    
    .feature-title-academic {
        font-family: 'Georgia', serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 0.8rem;
    }
    
    .feature-description-academic {
        font-size: 0.85rem;
        color: var(--text-muted);
        line-height: 1.4;
        margin-bottom: 1rem;
    }
    
    .feature-list-academic {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .feature-list-academic li {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.4rem 0;
        font-size: 0.8rem;
        color: var(--text-dark);
        border-bottom: 1px solid var(--border-light);
    }
    
    .feature-list-academic li:last-child {
        border-bottom: none;
    }
    
    .feature-list-academic li::before {
        content: '✓';
        color: var(--gold);
        font-weight: 700;
    }
    
    /* Roles Grid */
    .roles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .role-card-academic {
        background: var(--gradient-card);
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s ease;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        position: relative;
        margin-top: 1rem;
    }
    
    .role-card-academic:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }
    
    .role-card-academic::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-gold);
    }
    
    .role-icon-academic {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: var(--navy);
    }
    
    .role-title-academic {
        font-family: 'Georgia', serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 1rem;
    }
    
    .role-features-academic {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .role-features-academic li {
        font-size: 0.8rem;
        color: var(--text-muted);
        padding: 0.4rem 0;
        position: relative;
    }
    
    /* CTA Section */
    .cta-section-academic {
        text-align: center;
        padding: 2rem;
        margin: 2rem 0;
        background: var(--gradient-academic);
        border-radius: 1rem;
        position: relative;
    }
    
    .cta-title-academic {
        font-family: 'Georgia', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1rem;
    }
    
    .cta-subtitle-academic {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        max-width: 600px;
        line-height: 1.5;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Custom Button */
    .stButton > button {
        background: linear-gradient(135deg, #D4A853 0%, #B38B3C 100%) !important;
        color: #0A1931 !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 0.6rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: transform 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-container {
            grid-template-columns: 1fr;
            text-align: center;
            gap: 1.5rem;
            padding: 1.5rem;
        }
        
        .hero-image-container {
            height: 250px;
            max-width: 100%;
        }
        
        .hero-title {
            font-size: 1.8rem;
        }
        
        .hero-buttons {
            flex-direction: column;
            align-items: center;
        }
        
        .nav-bar {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .nav-info {
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    /* Hide Streamlit default */
    [data-testid="stSidebarNav"] { display: none; }
    #MainMenu { display: none; }
    footer { display: none; }
    header { visibility: hidden; }
    </style>
    """

# Hide Streamlit default UI elements
hide_streamlit_style = """
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        #MainMenu { display: none; }
        footer { display: none; }
        header { visibility: hidden; }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Emojis académiques
ACADEMIC_EMOJIS = {
    "system": "📚", "dashboard": "📊", "calendar": "📅", 
    "teacher": "👨‍🏫", "student": "👨‍🎓", "department": "🏛️",
    "module": "📖", "classroom": "🏫", "exam": "✍️",
    "admin": "🔧", "dean": "🎖️", "coordinator": "🤝",
    "security": "🔒", "ai": "🤖", "mobile": "📱",
    "stats": "📈", "university": "🎓", "graduation": "🎓",
    "library": "📚", "quality": "⭐", "innovation": "💡",
    "collaboration": "👥", "success": "✅", "warning": "⚠️",
    "error": "❌", "check": "✓", "arrow": "→"
}

# Page d'accueil
def main():
    # Load cached CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
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
                <div class="nav-brand-subtitle">Plateforme Académique</div>
            </div>
        </div>
        <div class="nav-info">
            <div class="nav-info-item">
                <span>{ACADEMIC_EMOJIS['calendar']}</span>
                <span>{current_date}</span>
            </div>
            <div class="nav-info-item">
                <span>{current_time}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Section avec image - OPTIMISÉ
    img_base64 = get_base64_image()
    
    if img_base64:
        # Use HTML image for hero section
        hero_image_html = f"""
        <div class="hero-container">
            <div class="hero-content">
                <div class="hero-badge">
                    {ACADEMIC_EMOJIS['university']} Système Académique
                </div>
                <h1 class="hero-title">
                    {ACADEMIC_EMOJIS['system']} Gestion des <span>Examens</span>
                </h1>
                <p class="hero-subtitle">
                    Solution complète pour la planification et gestion optimisée des examens universitaires.
                </p>
                <div class="hero-buttons">
                    <div class="hero-button-primary">
                        <span>{ACADEMIC_EMOJIS['calendar']} Données fiables</span>
                    </div>
                    <div class="hero-button-secondary">
                        <span>{ACADEMIC_EMOJIS['stats']} Disponible 24/7</span>
                    </div>
                </div>
                <div class="hero-stats">
                    <div class="hero-stat">
                        <div class="hero-stat-number">12+</div>
                        <div class="hero-stat-label">Départements</div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-number">500+</div>
                        <div class="hero-stat-label">Examens</div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-number">99.8%</div>
                        <div class="hero-stat-label">Satisfaction</div>
                    </div>
                </div>
            </div>
            <div class="hero-image-container">
                <img src="data:image/jpeg;base64,{img_base64}" class="hero-image">
            </div>
        </div>
        """
        st.markdown(hero_image_html, unsafe_allow_html=True)
    else:
        # Fallback without image
        st.markdown(f"""
        <div class="hero-container" style="grid-template-columns: 1fr; text-align: center;">
            <div class="hero-content">
                <div class="hero-badge">
                    {ACADEMIC_EMOJIS['university']} Système Académique
                </div>
                <h1 class="hero-title">
                    {ACADEMIC_EMOJIS['system']} Gestion des <span>Examens</span>
                </h1>
                <p class="hero-subtitle">
                    Solution complète pour la planification et gestion optimisée des examens universitaires.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Boutons principaux
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    
    with col2:
        if st.button(f"{ACADEMIC_EMOJIS['calendar']} Voir Planning", use_container_width=True, type="secondary"):
            st.switch_page("pages/app_etudiant.py")
    
    with col4:
        if st.button(f"{ACADEMIC_EMOJIS['check']} Connexion", use_container_width=True, type="primary"):
            st.switch_page("pages/log.py")
    
    # Statistiques principales
    st.markdown(f'<h2 class="section-title">{ACADEMIC_EMOJIS["dashboard"]} Tableau de Bord</h2>', unsafe_allow_html=True)
    
    # Formater les grands nombres
    def format_number(num):
        if num >= 1000:
            return f"{num:,}".replace(",", " ")
        return str(num)
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card-academic">
            <div class="stat-icon-academic">{ACADEMIC_EMOJIS['department']}</div>
            <div class="stat-number-academic">12<span style="font-size: 1rem;">+</span></div>
            <div class="stat-label-academic">Départements</div>
            <div class="stat-description">Filières académiques</div>
        </div>
        <div class="stat-card-academic">
            <div class="stat-icon-academic">{ACADEMIC_EMOJIS['graduation']}</div>
            <div class="stat-number-academic">28</div>
            <div class="stat-label-academic">Formations</div>
            <div class="stat-description">Programmes diplômants</div>
        </div>
        <div class="stat-card-academic">
            <div class="stat-icon-academic">{ACADEMIC_EMOJIS['teacher']}</div>
            <div class="stat-number-academic">245</div>
            <div class="stat-label-academic">Enseignants</div>
            <div class="stat-description">Corps professoral</div>
        </div>
        <div class="stat-card-academic">
            <div class="stat-icon-academic">{ACADEMIC_EMOJIS['student']}</div>
            <div class="stat-number-academic">13k</div>
            <div class="stat-label-academic">Étudiants</div>
            <div class="stat-description">Effectif actuel</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Fonctionnalités principales
    st.markdown(f'<h2 class="section-title">{ACADEMIC_EMOJIS["feature"]} Fonctionnalités</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card-academic">
            <div class="feature-icon-academic">{ACADEMIC_EMOJIS['ai']}</div>
            <h3 class="feature-title-academic">Intelligence Artificielle</h3>
            <p class="feature-description-academic">
                Planification intelligente avec optimisation avancée des ressources.
            </p>
            <ul class="feature-list-academic">
                <li>Génération automatique</li>
                <li>Détection des conflits</li>
                <li>Optimisation des salles</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card-academic">
            <div class="feature-icon-academic">{ACADEMIC_EMOJIS['mobile']}</div>
            <h3 class="feature-title-academic">Mobile First</h3>
            <p class="feature-description-academic">
                Accès mobile avec application native et notifications.
            </p>
            <ul class="feature-list-academic">
                <li>App multiplateforme</li>
                <li>Notifications push</li>
                <li>Scan QR code</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="feature-card-academic">
            <div class="feature-icon-academic">{ACADEMIC_EMOJIS['security']}</div>
            <h3 class="feature-title-academic">Sécurité</h3>
            <p class="feature-description-academic">
                Système sécurisé conforme aux standards académiques.
            </p>
            <ul class="feature-list-academic">
                <li>Chiffrement des données</li>
                <li>Audit des modifications</li>
                <li>Sauvegarde cloud</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Espaces personnalisés
    st.markdown(f'<h2 class="section-title">{ACADEMIC_EMOJIS["collaboration"]} Espaces</h2>', unsafe_allow_html=True)
    
    roles_col1, roles_col2, roles_col3, roles_col4 = st.columns(4)
    
    with roles_col1:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['admin']}</div>
            <h4 class="role-title-academic">Admin</h4>
            <ul class="role-features-academic">
                <li>Gestion système</li>
                <li>Supervision</li>
                <li>Configuration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with roles_col2:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['dean']}</div>
            <h4 class="role-title-academic">Direction</h4>
            <ul class="role-features-academic">
                <li>Vue stratégique</li>
                <li>Indicateurs</li>
                <li>Validation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with roles_col3:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['coordinator']}</div>
            <h4 class="role-title-academic">Coordination</h4>
            <ul class="role-features-academic">
                <li>Gestion dépt.</li>
                <li>Supervision</li>
                <li>Communication</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with roles_col4:
        st.markdown(f"""
        <div class="role-card-academic">
            <div class="role-icon-academic">{ACADEMIC_EMOJIS['teacher']}</div>
            <h4 class="role-title-academic">Enseignants</h4>
            <ul class="role-features-academic">
                <li>Gestion examens</li>
                <li>Suivi corrections</li>
                <li>Communication</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown(f"""
    <div class="cta-section-academic">
        <h2 class="cta-title-academic">Prêt à optimiser vos examens ?</h2>
        <p class="cta-subtitle-academic">
            Rejoignez les établissements qui utilisent déjà notre système pour une gestion efficace.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0a1429, #002147);
        padding: 1.5rem;
        color: white;
        text-align: center;
        border-radius: 1rem;
        margin-top: 2rem;
    ">
        <h4 style="margin: 0 0 0.5rem 0;">🎓 Système de Gestion des Examens</h4>
        <p style="margin: 0; font-size: 0.85rem;">© 2024 Université des Sciences et Technologies</p>
        <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.8;">Contact: support@univ-examens.edu</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
