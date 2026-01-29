import streamlit as st
import mysql.connector
from mysql.connector import Error
import time

# Page config
st.set_page_config(
    page_title="Connexion - Système Examens",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide all Streamlit UI elements
hide_streamlit_style = """
    <style>
    /* Hide everything */
    #MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide the sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Remove padding */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    /* Full height */
    .stApp {
        overflow: hidden;
        height: 100vh;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
    }
    
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        }
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Database connection
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

def main():
    # Ultimate CSS design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-dark: #0a1429;
        --primary-medium: #1e293b;
        --accent-gold: #d4a853;
        --accent-light: #fef3c7;
        --background: #f8fafc;
        --surface: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border: #e2e8f0;
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
        --shadow-md: 0 10px 20px rgba(0,0,0,0.1);
        --shadow-lg: 0 25px 50px rgba(0,0,0,0.15);
        --radius-sm: 8px;
        --radius-md: 16px;
        --radius-lg: 24px;
    }
    
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-dark: #f1f5f9;
            --primary-medium: #cbd5e1;
            --background: #0f172a;
            --surface: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --border: #475569;
        }
    }
    
    /* Login card wrapper */
    .login-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 20px;
    }
    
    /* Main card container - Reduced width */
    .login-card {
        display: grid;
        grid-template-columns: 1fr 1fr;
        width: 900px; /* Reduced from 1000px */
        max-width: 95vw;
        background: var(--surface);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg);
        overflow: hidden;
        animation: slideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Hero section - Reduced height */
    .hero-section {
        background: linear-gradient(135deg, var(--primary-dark) 0%, #15203d 100%);
        padding: 40px 35px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 580px; /* Reduced height */
    }
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 15% 85%, rgba(212, 168, 83, 0.12) 0%, transparent 60%),
            radial-gradient(circle at 85% 15%, rgba(255, 255, 255, 0.08) 0%, transparent 60%);
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
    }
    
    .hero-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(212, 168, 83, 0.25);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin-bottom: 15px;
        line-height: 1.3;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: rgba(255, 255, 255, 0.85);
        margin-bottom: 30px;
        line-height: 1.6;
    }
    
    .features-grid {
        display: grid;
        gap: 12px;
        margin-top: 25px;
    }
    
    .feature {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 15px;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-radius: var(--radius-sm);
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .feature:hover {
        background: rgba(255, 255, 255, 0.12);
        transform: translateX(5px);
    }
    
    .feature-icon {
        color: var(--accent-gold);
        font-size: 16px;
        flex-shrink: 0;
    }
    
    .feature-text {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.4;
    }
    
    /* Form section */
    .form-section {
        padding: 40px 35px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 580px; /* Match hero height */
    }
    
    .form-header {
        margin-bottom: 35px;
    }
    
    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .brand-logo {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .brand-text {
        font-family: 'Poppins', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .brand-tag {
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%);
        color: var(--primary-dark);
        font-size: 10px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
        margin-left: 8px;
        letter-spacing: 0.3px;
    }
    
    .form-title {
        font-family: 'Poppins', sans-serif;
        font-size: 26px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .form-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* Form inputs */
    .form-input-group {
        margin-bottom: 20px;
        animation: fadeIn 0.5s ease-out forwards;
        opacity: 0;
    }
    
    .form-input-group:nth-child(1) { animation-delay: 0.1s; }
    .form-input-group:nth-child(2) { animation-delay: 0.2s; }
    
    @keyframes fadeIn {
        to { opacity: 1; }
    }
    
    .input-label {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
        display: block;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    
    .stTextInput > div > div,
    .stNumberInput > div > div {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 3px rgba(212, 168, 83, 0.1) !important;
    }
    
    .stTextInput input,
    .stNumberInput input {
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 12px 0 !important;
        color: var(--text-primary) !important;
    }
    
    /* Options row */
    .form-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        animation: fadeIn 0.5s ease-out 0.3s both;
    }
    
    .remember-me {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
    }
    
    .remember-checkbox {
        width: 16px;
        height: 16px;
        accent-color: var(--accent-gold);
        cursor: pointer;
    }
    
    .remember-label {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--text-primary);
        user-select: none;
    }
    
    .forgot-link {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--accent-gold);
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .forgot-link:hover {
        text-decoration: underline;
    }
    
    /* Login button */
    .login-button-container {
        margin-bottom: 25px;
        animation: fadeIn 0.5s ease-out 0.4s both;
    }
    
    .stButton > button {
        width: 100% !important;
        height: 48px !important;
        background: linear-gradient(135deg, var(--accent-gold) 0%, #e6b850 100%) !important;
        color: var(--primary-dark) !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(212, 168, 83, 0.3) !important;
    }
    
    /* Footer */
    .form-footer {
        margin-top: auto;
        padding-top: 25px;
        border-top: 1px solid var(--border);
        text-align: center;
        animation: fadeIn 0.5s ease-out 0.5s both;
    }
    
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }
    
    .footer-link {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: var(--text-secondary);
        text-decoration: none;
        transition: color 0.2s ease;
        cursor: pointer;
    }
    
    .footer-link:hover {
        color: var(--accent-gold);
    }
    
    .footer-version {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: var(--text-secondary);
        opacity: 0.7;
    }
    
    /* Hide Streamlit labels */
    .stTextInput label,
    .stNumberInput label {
        display: none !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .login-card {
            grid-template-columns: 1fr;
            width: 95%;
        }
        
        .hero-section,
        .form-section {
            min-height: auto;
            padding: 30px 25px;
        }
        
        .hero-section {
            order: 2;
        }
        
        .form-section {
            order: 1;
        }
    }
    
    @media (max-width: 480px) {
        .hero-title {
            font-size: 24px;
        }
        
        .form-title {
            font-size: 22px;
        }
        
        .brand-text {
            font-size: 20px;
        }
        
        .footer-links {
            gap: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Main wrapper
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    # Login card
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-icon">🎓</div>
            <h1 class="hero-title">Système de Gestion<br>des Examens</h1>
            <p class="hero-subtitle">
                Plateforme centralisée pour la planification, 
                surveillance et évaluation des examens universitaires.
            </p>
            <div class="features-grid">
                <div class="feature">
                    <span class="feature-icon">✓</span>
                    <span class="feature-text">Interface intuitive et moderne</span>
                </div>
                <div class="feature">
                    <span class="feature-icon">✓</span>
                    <span class="feature-text">Sécurité et authentification renforcées</span>
                </div>
                <div class="feature">
                    <span class="feature-icon">✓</span>
                    <span class="feature-text">Accès multi-rôles personnalisé</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Form Section
    st.markdown("""
    <div class="form-section">
        <div class="form-header">
            <div class="brand-container">
                <div class="brand-logo">🔐</div>
                <span class="brand-text">ExamensPro</span>
                <span class="brand-tag">BETA</span>
            </div>
            <h2 class="form-title">Connexion Sécurisée</h2>
            <p class="form-subtitle">Accédez à votre espace personnel avec vos identifiants</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Login Form
    with st.form("login_form", clear_on_submit=True):
        # User ID
        st.markdown('<span class="input-label">IDENTIFIANT UTILISATEUR</span>', unsafe_allow_html=True)
        user_id = st.number_input(
            "ID Utilisateur",
            min_value=1,
            step=1,
            key="user_id",
            label_visibility="collapsed",
            placeholder="Votre identifiant unique"
        )
        
        # Password
        st.markdown('<span class="input-label">MOT DE PASSE</span>', unsafe_allow_html=True)
        password = st.text_input(
            "Mot de passe",
            type="password",
            key="password",
            label_visibility="collapsed",
            placeholder="Votre mot de passe"
        )
        
        # Options
        st.markdown("""
        <div class="form-options">
            <label class="remember-me">
                <input type="checkbox" class="remember-checkbox" checked>
                <span class="remember-label">Se souvenir de moi</span>
            </label>
            <span class="forgot-link" onclick="alert('Contactez votre administrateur système pour réinitialiser votre mot de passe.');">
                Mot de passe oublié ?
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Submit button
        submit = st.form_submit_button("SE CONNECTER", type="primary", use_container_width=True)
        
        if submit:
            if not user_id or not password:
                st.error("⚠️ Veuillez remplir tous les champs obligatoires")
            else:
                # Animated loading
                with st.spinner("Authentification en cours..."):
                    time.sleep(0.5)
                    
                    if authenticate_user(int(user_id), password):
                        # Success animation
                        st.success("✅ Connexion réussie ! Redirection en cours...")
                        time.sleep(1)
                        
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
                        st.error("❌ Identifiants incorrects. Veuillez réessayer.")
    
    # Footer
    st.markdown("""
        <div class="form-footer">
            <div class="footer-links">
                <span class="footer-link" onclick="alert('Support: support@examenspro.edu | Tél: +33 1 23 45 67 89')">Aide & Support</span>
                <span class="footer-link" onclick="alert('Politique de confidentialité')">Confidentialité</span>
                <span class="footer-link" onclick="alert('Conditions d\\'utilisation')">Conditions</span>
            </div>
            <div class="footer-version">v2.1.4 | © 2024 Université ExamensPro</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Close containers
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-card
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-wrapper

if __name__ == "__main__":
    main()
