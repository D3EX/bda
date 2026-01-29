import streamlit as st
import mysql.connector
from mysql.connector import Error
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Connexion - Système Examens",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with better styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary-dark: #0a1429;
    --primary-medium: #1e293b;
    --accent-gold: #d4a853;
    --accent-gold-light: #f6d365;
    --accent-light: #fef3c7;
    --success: #10b981;
    --error: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    --background: #f8fafc;
    --surface: #ffffff;
    --border: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.12);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    --shadow-lg: 0 10px 25px rgba(0,0,0,0.15);
    --shadow-xl: 0 20px 40px rgba(0,0,0,0.2);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    :root {
        --primary-dark: #f1f5f9;
        --primary-medium: #cbd5e1;
        --background: #0f172a;
        --surface: #1e293b;
        --border: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
}

/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%) !important;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    animation: fadeIn 0.5s ease-out;
}

@media (prefers-color-scheme: dark) {
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
    }
}

/* Hide Streamlit elements */
#MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {
    display: none !important;
}

.stSidebar, [data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

/* Main container */
.main-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
    position: relative;
    overflow: hidden;
}

/* Animated background elements */
.background-shapes {
    position: absolute;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
}

.shape {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-gold), transparent);
    opacity: 0.1;
    animation: float 20s infinite linear;
}

.shape-1 { width: 300px; height: 300px; top: -150px; right: -150px; animation-delay: 0s; }
.shape-2 { width: 200px; height: 200px; bottom: -100px; left: -100px; animation-delay: 5s; animation-duration: 25s; }
.shape-3 { width: 150px; height: 150px; top: 50%; right: 10%; animation-delay: 10s; animation-duration: 30s; }

@keyframes float {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(30px, 50px) rotate(120deg); }
    66% { transform: translate(-20px, -30px) rotate(240deg); }
}

/* Login card */
.login-card {
    background: var(--surface);
    width: 1000px;
    max-width: 90vw;
    min-height: 600px;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-xl);
    display: flex;
    overflow: hidden;
    position: relative;
    z-index: 1;
    animation: slideUp 0.6s cubic-bezier(0.22, 1, 0.36, 1);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(30px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* Hero section */
.hero-section {
    flex: 1.2;
    background: linear-gradient(135deg, var(--primary-dark) 0%, #15203d 100%);
    padding: 50px 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: white;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 80%, rgba(212, 168, 83, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
}

.hero-content {
    position: relative;
    z-index: 1;
}

.hero-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    margin-bottom: 30px;
    box-shadow: 0 15px 35px rgba(212, 168, 83, 0.4);
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1) rotate(0deg); box-shadow: 0 15px 35px rgba(212, 168, 83, 0.4); }
    50% { transform: scale(1.05) rotate(5deg); box-shadow: 0 20px 40px rgba(212, 168, 83, 0.6); }
}

.hero-title {
    font-family: 'Poppins', sans-serif;
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 20px;
    line-height: 1.2;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    opacity: 0.9;
    margin-bottom: 40px;
    line-height: 1.6;
}

.features-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 30px;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 15px;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    padding: 15px 20px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    cursor: default;
}

.feature-item:hover {
    background: rgba(255, 255, 255, 0.12);
    transform: translateX(10px);
    border-color: rgba(212, 168, 83, 0.3);
}

.feature-icon {
    font-size: 18px;
    color: var(--accent-gold);
    min-width: 24px;
}

.feature-text {
    flex: 1;
}

/* Form section */
.form-section {
    flex: 1;
    padding: 50px 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Header */
.auth-header {
    margin-bottom: 40px;
    text-align: center;
}

.branding {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 25px;
    padding: 12px 24px;
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
}

.logo {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: var(--primary-dark);
    font-weight: bold;
}

.brand-name {
    font-family: 'Poppins', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: white;
}

.page-title {
    font-family: 'Poppins', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.page-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    color: var(--text-secondary);
    line-height: 1.6;
}

/* Form styling */
.login-form {
    margin-top: 20px;
}

.form-group {
    margin-bottom: 25px;
    animation: fadeIn 0.5s ease-out forwards;
    opacity: 0;
}

.form-group:nth-child(1) { animation-delay: 0.2s; }
.form-group:nth-child(2) { animation-delay: 0.3s; }

@keyframes fadeIn {
    to { opacity: 1; }
}



/* Options row */
.options-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 25px 0;
    animation: fadeIn 0.5s ease-out 0.4s both;
}

.checkbox-container {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
}

.checkbox-container input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: var(--accent-gold);
    cursor: pointer;
    border-radius: 4px;
}

.checkbox-label {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: var(--text-primary);
    cursor: pointer;
    user-select: none;
}

.forgot-password {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: var(--accent-gold);
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s ease;
    cursor: pointer;
    position: relative;
}

.forgot-password::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: var(--accent-gold);
    transition: width 0.3s ease;
}

.forgot-password:hover::after {
    width: 100%;
}

/* Enhanced login button */
.stButton > button {
    width: 100% !important;
    height: 56px !important;
    background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%) !important;
    color: var(--primary-dark) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    box-shadow: var(--shadow-md) !important;
    transition: all 0.3s ease !important;
    position: relative;
    overflow: hidden;
    animation: fadeIn 0.5s ease-out 0.5s both;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
    background: linear-gradient(135deg, var(--accent-gold-light) 0%, var(--accent-gold) 100%) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.stButton > button:hover::before {
    left: 100%;
}

/* Role indicator */
.role-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 20px;
    padding: 12px 16px;
    background: rgba(212, 168, 83, 0.1);
    border-radius: var(--radius-md);
    border-left: 4px solid var(--accent-gold);
    animation: fadeIn 0.5s ease-out 0.6s both;
}

.role-icon {
    font-size: 18px;
    color: var(--accent-gold);
}

.role-text {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: var(--text-primary);
    flex: 1;
}

/* Footer */
.auth-footer {
    margin-top: 40px;
    padding-top: 25px;
    border-top: 1px solid var(--border);
    text-align: center;
    animation: fadeIn 0.5s ease-out 0.7s both;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 25px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}

.footer-links a {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 5px;
}

.footer-links a:hover {
    color: var(--accent-gold);
    transform: translateY(-2px);
}

.footer-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    flex-wrap: wrap;
    gap: 10px;
}

.version {
    font-family: 'Inter', monospace;
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
}

.time-display {
    font-family: 'Inter', monospace;
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
}

/* Progress animation */
.progress-container {
    width: 100%;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
    margin: 20px 0;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-gold), var(--accent-gold-light));
    border-radius: 2px;
    transition: width 0.3s ease;
}

/* Custom alerts */
.custom-alert {
    padding: 16px 20px;
    border-radius: var(--radius-md);
    margin: 15px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideIn 0.3s ease-out;
    border-left: 4px solid;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.custom-alert.success {
    background: rgba(16, 185, 129, 0.1);
    border-color: var(--success);
    color: var(--success);
}

.custom-alert.error {
    background: rgba(239, 68, 68, 0.1);
    border-color: var(--error);
    color: var(--error);
}

.custom-alert.info {
    background: rgba(59, 130, 246, 0.1);
    border-color: var(--info);
    color: var(--info);
}

/* Language selector */
.language-selector {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 100;
}

.language-selector select {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid var(--border);
    color: var(--text-primary);
    padding: 8px 12px;
    padding-right: 30px;
    border-radius: var(--radius-md);
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%2364748b' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 8px center;
    background-size: 16px;
    transition: all 0.2s ease;
}

.language-selector select:hover {
    border-color: var(--accent-gold);
    box-shadow: 0 0 0 3px rgba(212, 168, 83, 0.1);
}

/* Responsive */
@media (max-width: 1024px) {
    .login-card {
        flex-direction: column;
        width: 95%;
        max-width: 500px;
        min-height: auto;
    }
    
    .hero-section {
        padding: 40px 30px;
        border-radius: 0;
    }
    
    .form-section {
        padding: 40px 30px;
    }
    
    .hero-title {
        font-size: 28px;
    }
}

@media (max-width: 480px) {
    .main-container {
        padding: 10px;
    }
    
    .login-card {
        width: 100%;
        border-radius: var(--radius-lg);
    }
    
    .hero-section,
    .form-section {
        padding: 30px 20px;
    }
    
    .hero-title {
        font-size: 24px;
    }
    
    .page-title {
        font-size: 24px;
    }
    
    .footer-info {
        flex-direction: column;
        text-align: center;
        gap: 5px;
    }
    
    .footer-links {
        gap: 15px;
    }
}

/* Hide Streamlit labels */
.stTextInput label,
.stNumberInput label,
.stButton label {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Database connection functions (unchanged)
def get_connection():
    if "conn" not in st.session_state:
        try:
            cfg = st.secrets["mysql"]
            st.session_state.conn = mysql.connector.connect(
                host=cfg["host"],
                port=int(cfg["port"]),
                database=cfg["database"],
                user=cfg["user"],
                password=cfg["password"],
                autocommit=True
            )
        except Error as e:
            st.error(f"Erreur DB : {e}")
            st.stop()
    return st.session_state.conn

conn = get_connection()

def run_query(query, params=None, fetch=True):
    try:
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params) if params else cursor.execute(query)
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        conn.commit()
        cursor.close()
        return True
    except Error:
        return None

def authenticate_user(user_id, password):
    if conn is None:
        return False
    query = """
        SELECT u.*, p.nom, p.prenom, p.dept_id, d.nom as departement
        FROM utilisateurs u
        LEFT JOIN professeurs p ON u.id = p.id
        LEFT JOIN departements d ON p.dept_id = d.id
        WHERE u.id = %s AND u.mot_de_passe = %s
    """
    result = run_query(query, (user_id, password))
    if result:
        user = result[0]
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user['id']
        st.session_state['role'] = user['role']
        st.session_state['nom_complet'] = f"{user.get('prenom','')} {user.get('nom','')}".strip()
        st.session_state['departement_id'] = user.get('dept_id')
        st.session_state['departement'] = user.get('departement')
        return True
    return False

def get_user_role_info(role):
    role_info = {
        'professeur': {'icon': '👨‍🏫', 'desc': 'Gestion des examens et surveillance'},
        'admin': {'icon': '👨‍💼', 'desc': 'Administration complète du système'},
        'doyen': {'icon': '🎓', 'desc': 'Supervision académique'},
        'chef': {'icon': '👔', 'desc': 'Gestion départementale'}
    }
    for key, info in role_info.items():
        if key in role.lower():
            return info
    return {'icon': '👤', 'desc': 'Utilisateur système'}

def main():
    # Background shapes
    st.markdown('<div class="background-shapes"><div class="shape shape-1"></div><div class="shape shape-2"></div><div class="shape shape-3"></div></div>', unsafe_allow_html=True)
    
    # Language selector
    st.markdown("""
    <div class="language-selector">
        <select onchange="alert('Fonctionnalité à venir : Sélection de langue')">
            <option value="fr">🇫🇷 Français</option>
            <option value="en">🇬🇧 English</option>
            <option value="es">🇪🇸 Español</option>
        </select>
    </div>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Login card
    col1, col2 = st.columns([1.2, 1], gap="small")
    
    # HERO SECTION (Left Column)
    with col1:
        st.markdown("""
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-icon">🎓</div>
                <h1 class="hero-title">Système Intelligent de Gestion des Examens</h1>
                <p class="hero-subtitle">
                    Plateforme unifiée pour la planification, surveillance et évaluation 
                    des examens universitaires. Accédez à tous vos outils pédagogiques 
                    en toute sécurité depuis un seul espace.
                </p>
                <div class="features-list">
                    <div class="feature-item">
                        <span class="feature-icon">✅</span>
                        <span class="feature-text">Interface moderne et intuitive</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🔒</span>
                        <span class="feature-text">Sécurité et authentification renforcées</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">⚡</span>
                        <span class="feature-text">Performance optimisée pour les grandes sessions</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📊</span>
                        <span class="feature-text">Analytique en temps réel et rapports détaillés</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # FORM SECTION (Right Column)
    with col2:
        st.markdown("""
        <div class="form-section">
            <div class="auth-header">
                <div class="branding">
                    <div class="logo">E</div>
                    <div class="brand-name">ExamensPro</div>
                </div>
                <h1 class="page-title">Connexion Sécurisée</h1>
                <p class="page-subtitle">Accédez à votre espace personnel</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            
            # User ID field
            st.markdown('<div class="form-group"><span class="custom-label">👤 IDENTIFIANT UTILISATEUR</span></div>', unsafe_allow_html=True)
            user_id = st.number_input(
                "ID Utilisateur",
                min_value=1,
                step=1,
                key="user_id_input",
                label_visibility="collapsed",
                placeholder="Entrez votre identifiant unique"
            )
            
            # Password field
            st.markdown('<div class="form-group"><span class="custom-label">🔒 MOT DE PASSE</span></div>', unsafe_allow_html=True)
            password = st.text_input(
                "Mot de passe",
                type="password",
                key="password_input",
                label_visibility="collapsed",
                placeholder="••••••••••••"
            )
            
            # Options row
            st.markdown("""
            <div class="options-row">
                <div class="checkbox-container">
                    <input type="checkbox" id="remember" checked>
                    <label for="remember" class="checkbox-label">Se souvenir de moi</label>
                </div>
                <div class="forgot-password" onclick="alert('Pour réinitialiser votre mot de passe, contactez le support technique à support@examenspro.edu')">
                    Mot de passe oublié ?
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Login button
            submit = st.form_submit_button("🚀 SE CONNECTER", type="primary", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close login-form
            
        if submit:
            if not user_id or not password:
                st.markdown("""
                <div class="custom-alert error">
                    <span>⛔</span>
                    <span>Veuillez remplir tous les champs obligatoires</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Create progress animation
                progress_placeholder = st.empty()
                with progress_placeholder.container():
                    st.markdown('<div class="progress-container"><div class="progress-bar" id="progress"></div></div>', unsafe_allow_html=True)
                    status_text = st.empty()
                
                # Animated authentication process
                steps = [
                    ("🔍 Vérification des identifiants...", 30),
                    ("🔐 Authentification en cours...", 60),
                    ("👤 Chargement du profil...", 85),
                    ("✅ Finalisation de la connexion...", 100)
                ]
                
                for step_text, progress in steps:
                    status_text.text(step_text)
                    st.markdown(f"""
                    <script>
                        document.getElementById('progress').style.width = '{progress}%';
                    </script>
                    """, unsafe_allow_html=True)
                    time.sleep(0.5)
                
                progress_placeholder.empty()
                status_text.empty()
                
                # Authenticate user
                if authenticate_user(int(user_id), password):
                    # Get role information
                    role_info = get_user_role_info(st.session_state.get('role', ''))
                    
                    # Success message
                    st.markdown(f"""
                    <div class="custom-alert success">
                        <span>🎉</span>
                        <div>
                            <strong>Connexion réussie !</strong><br>
                            Bienvenue dans le système de gestion des examens.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Role indicator
                    st.markdown(f"""
                    <div class="role-indicator">
                        <span class="role-icon">{role_info['icon']}</span>
                        <span class="role-text">
                            <strong>{st.session_state.get('role', 'Utilisateur').title()}</strong><br>
                            {role_info['desc']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show welcome message
                    if 'nom_complet' in st.session_state:
                        st.info(f"**👋 Bienvenue, {st.session_state['nom_complet']} !**")
                    
                    # Short delay before redirect
                    time.sleep(2)
                    
                    # Redirect based on role
                    role = st.session_state.get('role', '').lower()
                    if 'professeur' in role:
                        st.switch_page("pages/app_professeur.py")
                    elif 'admin' in role:
                        st.switch_page("pages/app_admin.py")
                    elif 'doyen' in role:
                        st.switch_page("pages/app_vice_doyen.py")
                    elif 'chef' in role:
                        st.switch_page("pages/app_chef_departement.py")
                    else:
                        st.switch_page("app.py")
                else:
                    st.markdown("""
                    <div class="custom-alert error">
                        <span>❌</span>
                        <div>
                            <strong>Échec de l'authentification</strong><br>
                            Identifiants incorrects. Veuillez vérifier et réessayer.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Footer
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        </div>
        <div class="auth-footer">
            <div class="footer-links">
                <a href="#" onclick="alert('Support technique disponible du lundi au vendredi, 9h-18h\\nEmail: support@examenspro.edu\\nTéléphone: +33 1 23 45 67 89')">
                    🆘 Aide & Support
                </a>
                <a href="#" onclick="alert('Politique de confidentialité conforme au RGPD\\nVos données sont sécurisées et cryptées')">
                    🔒 Confidentialité
                </a>
                <a href="#" onclick="alert('Conditions générales d\\'utilisation\\nVersion 2.1 - Janvier 2024')">
                    📄 Mentions légales
                </a>
            </div>
            <div class="footer-info">
                <div class="version">Version 2.1.4 | © 2024 ExamensPro</div>
                <div class="time-display">🕒 {current_time}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Close containers
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

if __name__ == "__main__":
    main()
