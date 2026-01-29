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

# Combined CSS styles with no scroll modifications
st.markdown("""
<style>
    /* Hide Streamlit UI elements */
    #MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Main layout - FIXED NO SCROLL */
    .main .block-container {
        padding: 0 !important;
        max-width: 1000px !important;
        margin: auto !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        background-color: white !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100vw !important;
    }
    
    .stApp {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        width: 100vw;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
    }
    
    [data-testid="column"] {
        padding: 0 !important;
        height: 100% !important;
    }
    
    /* Force full viewport height */
    div[data-testid="column"] > div {
        height: 100% !important;
    }
    
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-dark: #0a1429;
        --primary-medium: #1e293b;
        --accent-gold: #d4a853;
        --accent-light: #fef3c7;
        --success: #10b981;
        --error: #ef4444;
        --background: #f8fafc;
        --surface: #ffffff;
        --border: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-dark: #f1f5f9;
            --primary-medium: #cbd5e1;
            --background: #0f172a;
            --surface: #1e293b;
            --border: #475569;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
        }
        
        .login-card {
            background: var(--surface) !important;
        }
        
        .stTextInput > div > div,
        .stNumberInput > div > div {
            background: #2d3748 !important;
            border-color: #4a5568 !important;
        }
        
        .stTextInput input,
        .stNumberInput input {
            color: var(--text-primary) !important;
            background: transparent !important;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    
    @keyframes ripple {
        0% { transform: scale(0, 0); opacity: 0.5; }
        100% { transform: scale(40, 40); opacity: 0; }
    }
    
    /* Login card - FIXED HEIGHT */
    .login-card {
        background: white;
        width: 300px;
        max-width: 90vw;
        box-shadow: 0 25px 70px rgba(10, 20, 41, 0.15), 0 10px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.95);
        overflow: hidden;
        display: flex;
        height: 600px; /* Fixed height instead of min-height */
        max-height: 95vh;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1);
    }
    
    /* Hero section - FIXED HEIGHT */
    .hero-section {
        width: 100%;
        height: 100%; /* Fixed height */
        padding: 40px 30px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        color: white;
        border-radius: 24px 0 0 24px;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
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
        max-width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .hero-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(212, 168, 83, 0.3);
        animation: float 6s ease-in-out infinite;
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 15px;
        line-height: 1.2;
        background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 30px;
        line-height: 1.5;
    }
    
    .features-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 25px;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        padding: 10px 15px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(5px);
    }
    
    .feature-item::before {
        content: '✓';
        color: var(--accent-gold);
        font-weight: bold;
        font-size: 14px;
    }
    
    /* Form section - FIXED HEIGHT */
    .form-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
        padding: 20px 30px;
        margin-top:-30px;
    }
    
    /* Header */
    .auth-header {
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.2s both;
    }
    
    .branding {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .logo {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-medium) 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        color: white;
        box-shadow: 0 8px 20px rgba(10, 20, 41, 0.2);
    }
    
    .brand-name {
        font-family: 'Poppins', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .beta-tag {
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%);
        color: var(--primary-dark);
        font-size: 10px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 15px;
        margin-left: 8px;
        letter-spacing: 0.5px;
    }
    
    .page-title {
        font-family: 'Poppins', sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;
        line-height: 1.2;
    }
    
    .page-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* Form styling */
    .form-group {
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        opacity: 0;
    }
    
    .form-group:nth-child(1) { animation-delay: 0.3s; }
    .form-group:nth-child(2) { animation-delay: 0.4s; }
    
    .custom-label {
        font-family: 'Poppins', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: 0.5px !important;
        display: block;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    input:focus-visible {
        outline: none !important;
    }
    
    /* Checkbox and forgot password */
    .options-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.5s both;
        margin: 20px 0;
    }
    
    .checkbox-container {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .checkbox-container input[type="checkbox"] {
        width: 16px;
        height: 16px;
        accent-color: var(--accent-gold);
        cursor: pointer;
    }
    
    .checkbox-label {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--text-primary);
        cursor: pointer;
        user-select: none;
    }
    
    .forgot-password {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--accent-gold);
        text-decoration: none;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .forgot-password:hover {
        text-decoration: underline;
        color: var(--primary-dark);
    }
    
    /* Login button */
    .stButton > button {
        width: 100% !important;
        height: 48px !important;
        background: linear-gradient(135deg, var(--accent-gold) 0%, #f6d365 100%) !important;
        color: var(--primary-dark) !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 6px 20px rgba(212, 168, 83, 0.4) !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(212, 168, 83, 0.5) !important;
    }
    
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }
    
    .stButton > button:focus:not(:active)::after {
        animation: ripple 1s ease-out;
    }
    
    /* Footer */
    .auth-footer {
        margin-top: 25px;
        padding-top: 20px;
        border-top: 1px solid var(--border);
        text-align: center;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.6s both;
    }
    
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 12px;
    }
    
    .footer-links a {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: var(--text-secondary);
        text-decoration: none;
        transition: color 0.2s ease;
    }
    
    .footer-links a:hover {
        color: var(--accent-gold);
    }
    
    .version {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: var(--text-secondary);
        opacity: 0.7;
    }
    
    /* Language selector */
    .language-selector {
        position: absolute;
        top: 20px;
        right: 20px;
    }
    
    .language-selector select {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 8px 12px;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        cursor: pointer;
    }
    
    /* Responsive */
    @media (max-width: 992px) {
        .login-card {
            flex-direction: column;
            height: auto;
            max-height: 90vh;
            width: 95%;
        }
        
        .hero-section {
            padding: 30px 25px;
            border-radius: 24px 24px 0 0;
            height: auto;
            min-height: 250px;
        }
        
        .form-section {
            padding: 30px 25px;
            height: auto;
        }
        
        .hero-content {
            max-width: 100%;
        }
    }
    
    @media (max-width: 480px) {
        .page-title {
            font-size: 22px;
        }
        
        .hero-title {
            font-size: 22px;
        }
        
        .features-list {
            gap: 8px;
        }
        
        .feature-item {
            padding: 8px 12px;
            font-size: 12px;
        }
        
        .login-card {
            max-height: 95vh;
        }
    }
    
    /* Hide streamlit labels */
    .stTextInput label,
    .stNumberInput label {
        display: none !important;
    }
    
    /* Error/Success messages */
    .stAlert {
        border-radius: 12px !important;
        border-left: none !important;
        animation: fadeInUp 0.4s ease-out;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* Ensure form elements don't overflow */
    form {
        max-height: 100% !important;
        overflow: visible !important;
    }
    
    /* Prevent any scrollbars */
    * {
        scrollbar-width: none !important;
    }
    
    *::-webkit-scrollbar {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Database connection functions (same as before)
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
    # Create two columns with specific heights
    col1, col2 = st.columns([1.4, 1])
    
    # HERO SECTION (Left Column)
    with col1:
        st.markdown("""
        <div class="hero-section">
            <div class="hero-content">
                <div class="hero-icon">🎓</div>
                <h1 class="hero-title">Système de Gestion des Examens</h1>
                <p class="hero-subtitle">
                    Plateforme intelligente pour la planification, surveillance et évaluation 
                    des examens universitaires.
                </p>
                <div class="features-list">
                    <div class="feature-item">Interface intuitive et moderne</div>
                    <div class="feature-item">Sécurité et authentification renforcées</div>
                    <div class="feature-item">Gestion centralisée des examens</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # FORM SECTION (Right Column)
    with col2:
        # Container for form section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="auth-header">
            <div class="branding">
                <div class="logo">🔐</div>
                <div class="brand-name">ExamensPro</div>
                <div class="beta-tag">BETA</div>
            </div>
            <h1 class="page-title">Connexion Sécurisée</h1>
            <p class="page-subtitle">Accédez à votre espace personnel</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with fixed height container
        with st.container():
            with st.form("login_form", clear_on_submit=True):
                # User ID field
                st.markdown('<div class="form-group">', unsafe_allow_html=True)
                st.markdown('<span class="custom-label">IDENTIFIANT UTILISATEUR</span>', unsafe_allow_html=True)
                user_id = st.number_input(
                    "ID Utilisateur",
                    min_value=1,
                    step=1,
                    key="user_id_input",
                    label_visibility="collapsed",
                    placeholder="Entrez votre identifiant"
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Password field
                st.markdown('<div class="form-group">', unsafe_allow_html=True)
                st.markdown('<span class="custom-label">MOT DE PASSE</span>', unsafe_allow_html=True)
                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    key="password",
                    label_visibility="collapsed",
                    placeholder="••••••••••••"
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Options row
                st.markdown("""
                <div class="options-row">
                    <div class="checkbox-container">
                        <input type="checkbox" id="remember" checked>
                        <label for="remember" class="checkbox-label">Se souvenir</label>
                    </div>
                    <a class="forgot-password" href="#" onclick="alert('Contactez l\\'administrateur système pour réinitialiser votre mot de passe.'); return false;">
                        Mot de passe oublié ?
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # Login button
                submit = st.form_submit_button("🔐 SE CONNECTER", type="primary", use_container_width=True)
                
                if submit:
                    if not user_id or not password:
                        st.error("⛔ Veuillez remplir tous les champs obligatoires")
                    else:
                        # Create a progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Simulate loading with progress
                        for percent in range(101):
                            time.sleep(0.01)
                            progress_bar.progress(percent)
                            if percent < 30:
                                status_text.text("🔍 Vérification...")
                            elif percent < 70:
                                status_text.text("🔐 Authentification...")
                            elif percent < 90:
                                status_text.text("👤 Chargement...")
                            else:
                                status_text.text("✅ Connexion...")
                        
                        # Clear progress elements
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Authenticate
                        if authenticate_user(int(user_id), password):
                            # Success message
                            st.success("""
                            🎉 **Connexion réussie !**  
                            Bienvenue dans le système de gestion des examens.
                            """)
                            st.balloons()
                            
                            # Show welcome message
                            if 'nom_complet' in st.session_state:
                                st.info(f"**👋 Bienvenue, {st.session_state['nom_complet']} !**")
                            
                            # Short delay before redirect
                            time.sleep(1.5)
                            
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
                            st.error("""
                            ❌ **Échec de l'authentification**  
                            Veuillez vérifier vos identifiants et réessayer.
                            """)
        
        # Footer
        st.markdown("""
        <div class="auth-footer">
            <div class="footer-links">
                <a href="#" onclick="alert('Support technique: support@examenspro.edu'); return false;">
                    💻 Aide
                </a>
                <a href="#" onclick="alert('Politique de confidentialité'); return false;">
                    🔒 Confidentialité
                </a>
                <a href="#" onclick="alert('Conditions générales'); return false;">
                    📄 Conditions
                </a>
            </div>
            <div class="version">Version 2.1.4 | © 2024 ExamensPro</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
