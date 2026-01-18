# streamlit_components.py
import streamlit as st
import time

def add_custom_css_and_js():
    """Injecte le CSS et JS personnalisé dans Streamlit"""
    
    # CSS de styles.css
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
    
    :root {
      --background: hsl(210, 40%, 98%);
      --foreground: hsl(222, 47%, 11%);
      --card: hsl(0, 0%, 100%);
      --card-foreground: hsl(222, 47%, 11%);
      --primary: hsl(221, 83%, 53%);
      --primary-foreground: hsl(210, 40%, 98%);
      --secondary: hsl(210, 40%, 96%);
      --secondary-foreground: hsl(222, 47%, 11%);
      --muted: hsl(210, 40%, 96%);
      --muted-foreground: hsl(215, 16%, 47%);
      --accent: hsl(199, 89%, 48%);
      --accent-foreground: hsl(210, 40%, 98%);
      --border: hsl(214, 32%, 91%);
      --radius: 0.75rem;
      --gradient-hero: linear-gradient(135deg, hsl(221, 83%, 53%) 0%, hsl(199, 89%, 48%) 100%);
      --shadow-card: 0 4px 6px -1px hsla(221, 83%, 53%, 0.1), 0 2px 4px -2px hsla(221, 83%, 53%, 0.1);
      --shadow-card-hover: 0 20px 25px -5px hsla(221, 83%, 53%, 0.15), 0 8px 10px -6px hsla(221, 83%, 53%, 0.1);
      --shadow-button: 0 4px 14px 0 hsla(221, 83%, 53%, 0.4);
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    .stApp {
      background: var(--background);
      font-family: 'Inter', system-ui, sans-serif;
      color: var(--foreground);
    }
    
    /* Cacher les éléments par défaut de Streamlit */
    .stApp > header {
      display: none;
    }
    
    #MainMenu {
      display: none;
    }
    
    footer {
      display: none;
    }
    
    .stApp > div:first-child {
      padding-top: 0;
    }
    
    /* Classes utilitaires */
    .container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 1rem;
    }
    
    .gradient-text {
      background: var(--gradient-hero);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    /* Header */
    .custom-header {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1000;
      background: rgba(250, 251, 252, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(214, 221, 230, 0.5);
      padding: 1rem 0;
    }
    
    .header-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 4rem;
    }
    
    .logo {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      text-decoration: none;
      color: inherit;
    }
    
    .logo-icon {
      width: 2.5rem;
      height: 2.5rem;
      border-radius: 0.75rem;
      background: var(--gradient-hero);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .logo-text {
      font-size: 1.25rem;
      font-weight: 700;
      font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Navigation */
    .nav-desktop {
      display: flex;
      align-items: center;
      gap: 2rem;
    }
    
    .nav-link {
      position: relative;
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--muted-foreground);
      padding: 0.5rem 0;
      text-decoration: none;
      transition: color 0.2s;
      cursor: pointer;
    }
    
    .nav-link:hover {
      color: var(--foreground);
    }
    
    .nav-link::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 0;
      height: 2px;
      background: var(--primary);
      transition: width 0.3s;
    }
    
    .nav-link:hover::after {
      width: 100%;
    }
    
    /* Buttons */
    .custom-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      font-weight: 600;
      font-size: 0.875rem;
      border-radius: 0.75rem;
      transition: all 0.3s;
      cursor: pointer;
      border: none;
      white-space: nowrap;
      padding: 0 1rem;
      height: 2.25rem;
      text-decoration: none;
    }
    
    .btn-hero {
      background: var(--gradient-hero);
      color: var(--primary-foreground);
      box-shadow: var(--shadow-button);
    }
    
    .btn-hero:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px hsla(221, 83%, 53%, 0.4);
    }
    
    .btn-hero-outline {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(8px);
      color: var(--foreground);
      border: 2px solid rgba(59, 130, 246, 0.2);
    }
    
    .btn-hero-outline:hover {
      border-color: var(--primary);
      background: rgba(59, 130, 246, 0.05);
    }
    
    /* Hero Section */
    .hero {
      padding-top: 8rem;
      padding-bottom: 4rem;
      position: relative;
      overflow: hidden;
    }
    
    .hero-bg {
      position: absolute;
      inset: 0;
      z-index: -1;
      overflow: hidden;
    }
    
    .hero-bg-circle {
      position: absolute;
      width: 24rem;
      height: 24rem;
      border-radius: 50%;
      filter: blur(60px);
    }
    
    .hero-bg-circle-1 {
      top: 0;
      left: 25%;
      background: hsla(221, 83%, 53%, 0.05);
    }
    
    .hero-bg-circle-2 {
      bottom: 0;
      right: 25%;
      background: hsla(199, 89%, 48%, 0.05);
    }
    
    .hero-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 3rem;
      align-items: center;
    }
    
    @media (min-width: 1024px) {
      .hero-grid {
        grid-template-columns: 1fr 1fr;
        gap: 4rem;
      }
    }
    
    .hero-content {
      text-align: center;
    }
    
    @media (min-width: 1024px) {
      .hero-content {
        text-align: left;
      }
    }
    
    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      background: hsla(221, 83%, 53%, 0.1);
      color: var(--primary);
      font-size: 0.875rem;
      font-weight: 500;
      margin-bottom: 1.5rem;
    }
    
    .hero-title {
      font-size: 2.25rem;
      font-weight: 700;
      line-height: 1.1;
      margin-bottom: 1.5rem;
      font-family: 'Space Grotesk', sans-serif;
    }
    
    @media (min-width: 640px) {
      .hero-title {
        font-size: 3rem;
      }
    }
    
    @media (min-width: 1024px) {
      .hero-title {
        font-size: 3.75rem;
      }
    }
    
    .hero-description {
      font-size: 1.125rem;
      color: var(--muted-foreground);
      margin-bottom: 2rem;
      line-height: 1.6;
    }
    
    .hero-buttons {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      justify-content: center;
    }
    
    @media (min-width: 640px) {
      .hero-buttons {
        flex-direction: row;
      }
    }
    
    @media (min-width: 1024px) {
      .hero-buttons {
        justify-content: flex-start;
      }
    }
    
    /* Stats Section */
    .stats-section {
      padding: 4rem 0;
      background: hsla(210, 40%, 96%, 0.3);
    }
    
    .section-header {
      text-align: center;
      margin-bottom: 3rem;
    }
    
    .section-title {
      font-size: 1.875rem;
      font-weight: 700;
      margin-bottom: 1rem;
      font-family: 'Space Grotesk', sans-serif;
    }
    
    .section-description {
      font-size: 1.125rem;
      color: var(--muted-foreground);
      max-width: 42rem;
      margin: 0 auto;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }
    
    @media (min-width: 640px) {
      .stats-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (min-width: 1024px) {
      .stats-grid {
        grid-template-columns: repeat(4, 1fr);
      }
    }
    
    .stat-card {
      padding: 1.5rem;
      border-radius: 1rem;
      background: linear-gradient(135deg, hsla(221, 83%, 53%, 0.05) 0%, hsla(199, 89%, 48%, 0.05) 100%);
      border: 1px solid var(--border);
    }
    
    .stat-card-inner {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    
    .stat-icon {
      width: 3rem;
      height: 3rem;
      border-radius: 0.75rem;
      background: var(--gradient-hero);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .stat-icon svg {
      width: 1.5rem;
      height: 1.5rem;
      color: var(--primary-foreground);
    }
    
    .stat-value {
      font-size: 1.875rem;
      font-weight: 700;
      font-family: 'Space Grotesk', sans-serif;
      color: var(--foreground);
    }
    
    .stat-label {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--muted-foreground);
    }
    
    /* Features Section */
    .features-section {
      padding: 4rem 0 6rem;
    }
    
    .section-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      font-size: 0.875rem;
      font-weight: 500;
      margin-bottom: 1rem;
    }
    
    .section-badge.accent {
      background: hsla(199, 89%, 48%, 0.1);
      color: var(--accent);
    }
    
    .features-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }
    
    @media (min-width: 768px) {
      .features-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (min-width: 1024px) {
      .features-grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
      }
    }
    
    .feature-card {
      padding: 1.5rem;
      border-radius: 1rem;
      background: var(--card);
      box-shadow: var(--shadow-card);
      transition: all 0.3s;
    }
    
    .feature-card:hover {
      box-shadow: var(--shadow-card-hover);
      transform: translateY(-4px);
    }
    
    .feature-icon {
      width: 3.5rem;
      height: 3.5rem;
      border-radius: 1rem;
      background: hsla(221, 83%, 53%, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1.25rem;
    }
    
    .feature-icon svg {
      width: 1.75rem;
      height: 1.75rem;
      color: var(--primary);
    }
    
    .feature-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
      font-family: 'Space Grotesk', sans-serif;
    }
    
    .feature-description {
      color: var(--muted-foreground);
      line-height: 1.6;
    }
    
    /* About Section */
    .about-section {
      padding: 4rem 0 6rem;
      background: hsla(210, 40%, 96%, 0.3);
    }
    
    .about-content {
      max-width: 56rem;
      margin: 0 auto;
      text-align: center;
    }
    
    .about-description {
      font-size: 1.125rem;
      color: var(--muted-foreground);
      line-height: 1.8;
      margin-bottom: 2rem;
    }
    
    .about-buttons {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      justify-content: center;
    }
    
    @media (min-width: 640px) {
      .about-buttons {
        flex-direction: row;
      }
    }
    
    /* CTA Section */
    .cta-section {
      padding: 4rem 0 6rem;
    }
    
    .cta-card {
      position: relative;
      border-radius: 1.5rem;
      background: var(--gradient-hero);
      padding: 2rem;
      overflow: hidden;
    }
    
    @media (min-width: 1024px) {
      .cta-card {
        padding: 4rem;
      }
    }
    
    .cta-content {
      position: relative;
      text-align: center;
    }
    
    .cta-title {
      font-size: 1.875rem;
      font-weight: 700;
      color: var(--primary-foreground);
      margin-bottom: 1.5rem;
      font-family: 'Space Grotesk', sans-serif;
    }
    
    @media (min-width: 1024px) {
      .cta-title {
        font-size: 3rem;
      }
    }
    
    .cta-description {
      font-size: 1.125rem;
      color: rgba(255, 255, 255, 0.8);
      max-width: 42rem;
      margin: 0 auto 2rem;
    }
    
    .cta-buttons {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      justify-content: center;
    }
    
    @media (min-width: 640px) {
      .cta-buttons {
        flex-direction: row;
      }
    }
    
    .btn-white {
      background: white;
      color: var(--primary);
      box-shadow: 0 4px 14px rgba(0,0,0,0.1);
    }
    
    .btn-outline-white {
      background: transparent;
      color: white;
      border: 2px solid rgba(255,255,255,0.3);
    }
    
    /* Footer */
    .custom-footer {
      background: var(--foreground);
      color: var(--primary-foreground);
      padding: 4rem 0;
    }
    
    .footer-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 3rem;
    }
    
    @media (min-width: 768px) {
      .footer-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (min-width: 1024px) {
      .footer-grid {
        grid-template-columns: 2fr 1fr 1fr;
      }
    }
    
    .footer-brand {
      max-width: 28rem;
    }
    
    .footer-logo {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
      text-decoration: none;
      color: inherit;
    }
    
    .footer-description {
      color: rgba(255, 255, 255, 0.7);
      margin-bottom: 1.5rem;
      line-height: 1.6;
    }
    
    .social-links {
      display: flex;
      gap: 1rem;
    }
    
    .social-link {
      width: 2.5rem;
      height: 2.5rem;
      border-radius: 0.5rem;
      background: rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
      text-decoration: none;
      color: inherit;
    }
    
    .footer-column h4 {
      font-size: 1.125rem;
      font-weight: 600;
      font-family: 'Space Grotesk', sans-serif;
      margin-bottom: 1rem;
    }
    
    .footer-links {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    
    .footer-link {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      color: rgba(255, 255, 255, 0.7);
      text-decoration: none;
      transition: color 0.2s;
    }
    
    .footer-bottom {
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      margin-top: 3rem;
      padding-top: 2rem;
      text-align: center;
    }
    
    /* Streamlit specific overrides */
    .element-container {
      margin: 0 !important;
    }
    
    .stButton > button {
      width: 100%;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
      .nav-desktop {
        display: none;
      }
      
      .hero-title {
        font-size: 2.5rem;
      }
      
      .hero-description {
        font-size: 1rem;
      }
    }
    
    /* Animation */
    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .animate-fade-in {
      animation: fadeIn 0.6s ease-out;
    }
    </style>
    """
    
    # JS de script.js
    js = """
    <script>
    // Animation des compteurs
    function animateCounter(element, target, duration = 2000, suffix = '') {
      let start = null;
      const startValue = 0;
      
      function step(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const percentage = Math.min(progress / duration, 1);
        
        // Ease out quart
        const ease = 1 - Math.pow(1 - percentage, 4);
        const currentValue = Math.floor(ease * target);
        
        element.textContent = currentValue.toLocaleString() + suffix;
        
        if (percentage < 1) {
          requestAnimationFrame(step);
        }
      }
      
      requestAnimationFrame(step);
    }
    
    // Démarrer l'animation des compteurs
    document.addEventListener('DOMContentLoaded', function() {
      const counters = document.querySelectorAll('.stat-value');
      counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-counter')) || 0;
        const suffix = counter.getAttribute('data-suffix') || '';
        animateCounter(counter, target, 2000, suffix);
      });
    });
    
    // Smooth scroll pour les liens
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
    </script>
    """
    
    st.markdown(css + js, unsafe_allow_html=True)

def render_header():
    """Rend le header de la page"""
    st.markdown("""
    <header class="custom-header">
      <div class="container">
        <div class="header-inner">
          <!-- Logo -->
          <a href="#" class="logo">
            <div class="logo-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>
              </svg>
            </div>
            <span class="logo-text">Optim<span class="gradient-text">EDT</span></span>
          </a>

          <!-- Desktop Navigation -->
          <nav class="nav-desktop">
            <a href="#features" class="nav-link">Features</a>
            <a href="#about" class="nav-link">About</a>
            <a href="#contact" class="nav-link">Contact</a>
          </nav>

          <!-- Desktop CTA -->
          <div class="nav-cta" style="display: flex; align-items: center; gap: 0.75rem;">
            <button onclick="window.location.href='/login'" class="custom-btn btn-hero-outline">Sign In</button>
            <button onclick="window.location.href='/get_started'" class="custom-btn btn-hero">Get Started</button>
          </div>
        </div>
      </div>
    </header>
    """, unsafe_allow_html=True)

def render_hero():
    """Rend la section hero"""
    st.markdown("""
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-bg-circle hero-bg-circle-1"></div>
        <div class="hero-bg-circle hero-bg-circle-2"></div>
      </div>

      <div class="container">
        <div class="hero-grid">
          <!-- Hero Content -->
          <div class="hero-content animate-fade-in">
            <div class="hero-badge">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
              </svg>
              Trusted by 50+ Universities
            </div>

            <h1 class="hero-title">
              Smart Exam Scheduling for <span class="gradient-text">Universities</span>
            </h1>

            <p class="hero-description">
              Streamline your exam management with intelligent scheduling, conflict detection, and real-time collaboration tools designed for modern academic institutions.
            </p>

            <div class="hero-buttons">
              <button onclick="window.location.href='/get_started'" class="custom-btn btn-hero" style="height: 3.5rem; padding: 0 2rem; font-size: 1rem;">Get Started Free</button>
              <button onclick="window.location.href='/demo'" class="custom-btn btn-hero-outline" style="height: 3.5rem; padding: 0 2rem; font-size: 1rem;">Watch Demo</button>
            </div>

            <p class="hero-note" style="margin-top: 1.5rem; font-size: 0.875rem; color: var(--muted-foreground);">No credit card required • 14-day free trial • Cancel anytime</p>
          </div>
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

def render_stats_section():
    """Rend la section statistiques"""
    st.markdown("""
    <section class="stats-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">Powering Academic Excellence</h2>
          <p class="section-description">Join thousands of students and faculty members who trust OptimEDT for seamless exam scheduling.</p>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-card-inner">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <div>
                <div class="stat-value" data-counter="25000" data-suffix="+">0</div>
                <div class="stat-label">Active Students</div>
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-inner">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/>
                </svg>
              </div>
              <div>
                <div class="stat-value" data-counter="1250">0</div>
                <div class="stat-label">Exams Scheduled</div>
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-inner">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/>
                </svg>
              </div>
              <div>
                <div class="stat-value" data-counter="48">0</div>
                <div class="stat-label">Departments</div>
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-card-inner">
              <div class="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>
                </svg>
              </div>
              <div>
                <div class="stat-value" data-counter="320">0</div>
                <div class="stat-label">Upcoming Exams</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

def render_features_section():
    """Rend la section features"""
    st.markdown("""
    <section id="features" class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-badge accent">Features</span>
          <h2 class="section-title">Everything You Need to Succeed</h2>
          <p class="section-description">Powerful tools designed specifically for academic institutions to streamline exam scheduling and management.</p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
              </svg>
            </div>
            <h3 class="feature-title">Smart Scheduling</h3>
            <p class="feature-description">AI-powered algorithms automatically detect and resolve scheduling conflicts, ensuring no student has overlapping exams.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>
              </svg>
            </div>
            <h3 class="feature-title">Role-Based Access</h3>
            <p class="feature-description">Secure access control for students, professors, and administrators with tailored dashboards and permissions.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <h3 class="feature-title">Real-Time Updates</h3>
            <p class="feature-description">Instant notifications for schedule changes, room assignments, and important announcements.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
              </svg>
            </div>
            <h3 class="feature-title">Analytics Dashboard</h3>
            <p class="feature-description">Comprehensive insights into exam distribution, room utilization, and scheduling efficiency.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
            </div>
            <h3 class="feature-title">Quick Setup</h3>
            <p class="feature-description">Import your existing data and get started in minutes with our intuitive onboarding process.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>
              </svg>
            </div>
            <h3 class="feature-title">Multi-Campus Support</h3>
            <p class="feature-description">Manage exam schedules across multiple campuses and locations from a single platform.</p>
          </div>
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

def render_about_section():
    """Rend la section about"""
    st.markdown("""
    <section id="about" class="about-section">
      <div class="container">
        <div class="about-content">
          <span class="section-badge primary">About OptimEDT</span>
          <h2 class="section-title">Built by Educators, for Educators</h2>
          <p class="about-description">
            OptimEDT was born from a simple observation: exam scheduling shouldn't be a headache. Our team of educators and technologists came together to create a platform that eliminates scheduling conflicts, reduces administrative burden, and gives everyone more time to focus on what matters—education.
          </p>
          <div class="about-buttons">
            <button onclick="window.location.href='/get_started'" class="custom-btn btn-hero" style="height: 3.5rem; padding: 0 2rem; font-size: 1rem;">Start Your Free Trial</button>
            <button onclick="window.location.href='/contact'" class="custom-btn btn-hero-outline" style="height: 3.5rem; padding: 0 2rem; font-size: 1rem;">Contact Sales</button>
          </div>
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

def render_cta_section():
    """Rend la section CTA"""
    st.markdown("""
    <section class="cta-section">
      <div class="container">
        <div class="cta-card">
          <div class="cta-content">
            <h2 class="cta-title">Ready to Transform Your Exam Scheduling?</h2>
            <p class="cta-description">Join 50+ universities already using OptimEDT to streamline their academic scheduling. Get started in minutes.</p>
            <div class="cta-buttons">
              <button onclick="window.location.href='/get_started'" class="custom-btn btn-white" style="height: 3.5rem; padding: 0 2rem; font-size: 1rem;">Get Started Free</button>
              <button onclick="window.location.href='/demo'" class="custom-btn btn-outline-white" style="height: 3.5rem; padding: 0 2rem; font-size: 1rem;">Schedule a Demo</button>
            </div>
          </div>
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

def render_footer():
    """Rend le footer"""
    st.markdown(f"""
    <footer id="contact" class="custom-footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <a href="#" class="footer-logo">
              <div class="logo-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>
                </svg>
              </div>
              <span>OptimEDT</span>
            </a>
            <p class="footer-description">
              The smart exam scheduling platform trusted by universities worldwide. Simplify scheduling, reduce conflicts, and enhance the academic experience.
            </p>
            <div class="social-links">
              <a href="#" class="social-link" aria-label="Twitter">
                <svg viewBox="0 0 24 24" width="24" height="24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
              </a>
              <a href="#" class="social-link" aria-label="GitHub">
                <svg viewBox="0 0 24 24" width="24" height="24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
              </a>
              <a href="#" class="social-link" aria-label="LinkedIn">
                <svg viewBox="0 0 24 24" width="24" height="24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
              </a>
            </div>
          </div>

          <div class="footer-column">
            <h4>Contact</h4>
            <ul class="footer-links">
              <li>
                <a href="mailto:contact@optimedt.com" class="footer-link">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                  </svg>
                  contact@optimedt.com
                </a>
              </li>
              <li>
                <a href="tel:+1234567890" class="footer-link">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                  </svg>
                  +1 (234) 567-890
                </a>
              </li>
              <li>
                <span class="footer-link">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
                  </svg>
                  123 University Ave, City
                </span>
              </li>
            </ul>
          </div>

          <div class="footer-column">
            <h4>Quick Links</h4>
            <ul class="footer-links">
              <li><a href="#features" class="footer-link">Features</a></li>
              <li><a href="#about" class="footer-link">About Us</a></li>
              <li><a href="#" class="footer-link">Privacy Policy</a></li>
              <li><a href="#" class="footer-link">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        <div class="footer-bottom">
          <p>© {time.strftime("%Y")} OptimEDT. All rights reserved. Built for universities worldwide.</p>
        </div>
      </div>
    </footer>
    """, unsafe_allow_html=True)