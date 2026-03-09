
import streamlit as st

def inject_premium_sidebar_styles_and_scripts():
    """
    Inyecta los estilos CSS y scripts JavaScript premium en la aplicación Streamlit.
    """
    
    # ========== CSS PREMIUM ==========
    premium_css = """
    <style>
    /* ========================================
       PREMIUM SIDEBAR STYLES - ÚLTIMA GENERACIÓN (SaaS Edition)
       ======================================== */

    /* ========== VARIABLES DE DISEÑO ==========*/
    :root {
      --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      --gradient-hover: linear-gradient(135deg, #7c8ff0 0%, #8b5fb3 100%);
      --gradient-active: linear-gradient(135deg, #4f63d9 0%, #5a3888 100%);
      --gradient-accent: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
      
      --color-bg-transparent: rgba(255, 255, 255, 0.05);
      --color-bg-hover: rgba(255, 255, 255, 0.1);
      --color-border: rgba(255, 255, 255, 0.15);
      --color-border-hover: rgba(255, 255, 255, 0.3);
      --color-text-primary: #ffffff;
      --color-text-secondary: rgba(255, 255, 255, 0.7);
      
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-xl: 20px;
      --radius-2xl: 24px;
      
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
      --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.15);
      --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.2);
      --shadow-focus: 0 0 20px rgba(0, 212, 255, 0.3);
      
      --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
      --transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
      --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
      
      /* Variables Filtros SaaS */
      --filter-bg-glass: rgba(255, 255, 255, 0.08);
      --filter-border: rgba(255, 255, 255, 0.2);
      --filter-border-hover: rgba(0, 212, 255, 0.6);
      --filter-glow: 0 0 20px rgba(0, 212, 255, 0.3);
      --filter-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
      --accent-cyan: #00d4ff;
    }

      /* ========== CONTENEDOR SIDEBAR PRINCIPAL (NO MODIFICAR) ==========*/
    /* ========== CONTENEDOR SIDEBAR PRINCIPAL (ROBUST CLASS TARGETING) ==========*/
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker),
    .premium-sidebar-wrapper {
      position: fixed !important;
      top: 0 !important;
      left: -340px !important;
      width: 340px !important;
      height: 100vh !important;
      background: var(--gradient-primary) !important;
      background-attachment: fixed !important;
      border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
      box-shadow: 4px 0 32px rgba(0, 0, 0, 0.25) !important;
      z-index: 2147483647 !important; /* MAX Z-INDEX */
      transition: left var(--transition-base), box-shadow var(--transition-base) !important;
      padding: 24px !important;
      padding-top: 80px !important;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      color: var(--color-text-primary) !important;
      backdrop-filter: blur(10px) !important;
      -webkit-backdrop-filter: blur(10px) !important;
      display: block !important;
      visibility: visible !important;
    }

    /* Force all text elements inside sidebar to be white */
    .premium-sidebar-wrapper *, 
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) * {
        color: #FFFFFF !important;
    }

    /* ... */
    
    /* ========== BOTÓN FLOTANTE PREMIUM (NO MODIFICAR) ==========*/
    #premium-filter-btn {
      position: fixed;
      bottom: 30px;
      left: 20px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: var(--gradient-primary);
      border: 2px solid rgba(255, 255, 255, 0.2);
      color: white;
      font-size: 24px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2147483647 !important; /* MAX Z-INDEX */
      box-shadow: var(--shadow-lg);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      transition: all var(--transition-base);
      border: 2px solid rgba(0, 212, 255, 0.3);
      font-weight: 700;
    }
    
    /* ... */

    (function() {
      'use strict';
      
      console.log("🚀 Premium Sidebar JS Loaded");

      // ========== CONFIGURACIÓN ==========
      const CONFIG = {
        sidebarSelector: '[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)',
        buttonId: 'premium-filter-btn',
        markerSelector: '#filter-sidebar-marker',
        // ...
      };
      
      // ... (rest of the code) ...
      
      class SidebarManager {
         // ...
         createButton() {
            // ...
            console.log("Creating Premium Button...");
            this.button = document.createElement('button');
            this.button.id = CONFIG.buttonId;
            this.button.innerHTML = '⚙️';
            this.button.style.zIndex = "2147483647"; // Force via JS too
            // ...
            document.body.appendChild(this.button);
            console.log("Button appended to body");
         }
         // ...
      }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker).sidebar-open {
      left: 0;
      box-shadow: 4px 0 48px rgba(0, 0, 0, 0.35);
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) {
      scrollbar-width: thin;
      scrollbar-color: rgba(0, 212, 255, 0.4) transparent;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)::-webkit-scrollbar {
      width: 6px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)::-webkit-scrollbar-track {
      background: transparent;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)::-webkit-scrollbar-thumb {
      background: rgba(0, 212, 255, 0.4);
      border-radius: 3px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)::-webkit-scrollbar-thumb:hover {
      background: rgba(0, 212, 255, 0.7);
    }

    /* ========== ESTILOS DE FILTROS SAAS PREMIUM ==========*/

    /* 📌 LABELS */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) label {
      font-family: 'Inter', sans-serif !important;
      font-size: 13px !important;
      font-weight: 600 !important;
      text-transform: uppercase !important;
      letter-spacing: 0.5px !important;
      color: var(--color-text-primary) !important;
      text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
      margin-bottom: 12px !important;
      display: flex !important;
      align-items: center !important;
      gap: 8px !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) label::before {
      content: '';
      display: inline-block;
      width: 6px;
      height: 6px;
      background: var(--accent-cyan);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--accent-cyan);
      margin-right: 4px;
    }

    /* 📦 SELECTBOX (Año & Mes) */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stSelectbox"] > div > div {
      background: var(--filter-bg-glass) !important;
      border: 1px solid var(--filter-border) !important;
      border-radius: 12px !important;
      backdrop-filter: blur(12px) saturate(180%) !important;
      -webkit-backdrop-filter: blur(12px) saturate(180%) !important;
      color: var(--color-text-primary) !important;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stSelectbox"] > div > div:hover {
      background: rgba(255, 255, 255, 0.12) !important;
      border-color: rgba(255, 255, 255, 0.4) !important;
      transform: translateY(-2px) !important;
      box-shadow: var(--filter-shadow) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stSelectbox"] > div > div:focus-within {
      border-color: var(--filter-border-hover) !important;
      box-shadow: var(--filter-glow) !important;
      background: rgba(255, 255, 255, 0.15) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stSelectbox"] svg {
      fill: var(--color-text-secondary) !important;
      transition: transform 0.3s ease !important;
    }
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stSelectbox"]:hover svg {
      fill: var(--accent-cyan) !important;
      transform: scale(1.1) !important;
    }

    /* 🏷️ MULTISELECT (Tipo & Método) */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMultiSelect"] > div > div {
      background: var(--filter-bg-glass) !important;
      border: 1px solid var(--filter-border) !important;
      border-radius: 16px !important;
      backdrop-filter: blur(12px) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMultiSelect"] > div > div:focus-within {
      border-color: var(--filter-border-hover) !important;
      box-shadow: var(--filter-glow) !important;
    }

    /* Tags/Chips */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"] {
      background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
      border: 1px solid rgba(255,255,255,0.2) !important;
      color: white !important;
      border-radius: 20px !important;
      padding: 4px 12px !important;
      transition: all 0.2s ease !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"]:hover {
      background: linear-gradient(135deg, var(--accent-cyan), #0099ff) !important;
      border-color: transparent !important;
      transform: scale(1.05) !important;
      box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"] svg {
        transition: transform 0.2s ease !important;
    }
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"]:hover svg {
        transform: rotate(90deg) scale(1.2) !important;
    }

    /* 🔍 TEXT INPUT (Search) */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stTextInput"] input {
      background: var(--filter-bg-glass) !important;
      border: 1px solid var(--filter-border) !important;
      border-radius: 12px !important;
      padding: 12px 16px !important;
      color: white !important;
      backdrop-filter: blur(12px) !important;
      transition: all 0.3s ease !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stTextInput"] input::placeholder {
      color: rgba(255,255,255,0.5) !important;
      font-style: italic !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stTextInput"] input:focus {
      background: rgba(255,255,255,0.15) !important;
      border-color: var(--filter-border-hover) !important;
      box-shadow: var(--filter-glow), inset 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    /* 🔄 UPDATE BUTTON */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stButton"] button {
      width: 100% !important;
      background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%) !important;
      border: none !important;
      border-radius: 12px !important;
      padding: 12px 24px !important;
      color: white !important;
      font-weight: 700 !important;
      text-transform: uppercase !important;
      letter-spacing: 1px !important;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
      box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3) !important;
      margin-top: 10px !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stButton"] button:hover {
      transform: scale(1.02) translateY(-2px) !important;
      box-shadow: 0 8px 32px rgba(0, 212, 255, 0.5) !important;
      background: linear-gradient(135deg, #00e5ff 0%, #29adff 100%) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stButton"] button:active {
      transform: scale(0.98) !important;
      box-shadow: 0 2px 8px rgba(0, 212, 255, 0.2) !important;
    }

    /* ➖ DIVIDERS */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) hr {
      border: none !important;
      height: 1px !important;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent) !important;
      margin: 24px 0 !important;
    }

    /* ========== EFECTO FONDO ANIMADO (NO MODIFICAR) ==========*/
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)::before {
      content: '';
      position: fixed;
      top: -50%;
      right: -25%;
      width: 500px;
      height: 500px;
      background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
      border-radius: 50%;
      pointer-events: none;
      animation: blob-float 8s ease-in-out infinite;
      z-index: 1;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)::after {
      content: '';
      position: fixed;
      bottom: -25%;
      left: -10%;
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(102, 126, 234, 0.08) 0%, transparent 70%);
      border-radius: 50%;
      pointer-events: none;
      animation: blob-float 10s ease-in-out infinite reverse;
      z-index: 1;
    }

    @keyframes blob-float {
      0%, 100% {
        transform: translate(0px, 0px) scale(1);
      }
      33% {
        transform: translate(20px, -30px) scale(1.05);
      }
      66% {
        transform: translate(-15px, 15px) scale(0.95);
      }
    }

    /* ========== BOTÓN FLOTANTE PREMIUM (NO MODIFICAR) ==========*/
    #premium-filter-btn {
      position: fixed;
      bottom: 30px;
      left: 20px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: var(--gradient-primary);
      border: 2px solid rgba(255, 255, 255, 0.2);
      color: white;
      font-size: 24px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2147483647 !important; /* MAX Z-INDEX */
      box-shadow: var(--shadow-lg);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      transition: all var(--transition-base);
      border: 2px solid rgba(0, 212, 255, 0.3);
      font-weight: 700;
    }

    #premium-filter-btn:hover {
      transform: scale(1.1) translateY(-4px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(0, 212, 255, 0.3);
      background: var(--gradient-hover);
      border-color: rgba(0, 212, 255, 0.6);
    }

    #premium-filter-btn:active {
      transform: scale(0.95);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    /* Animación ripple */
    #premium-filter-btn::after {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 60px;
      height: 60px;
      background: radial-gradient(circle, rgba(255, 255, 255, 0.5) 0%, transparent 70%);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      opacity: 0;
      animation: ripple-effect 0.6s ease-out;
      pointer-events: none;
    }

    #premium-filter-btn.ripple::after {
      animation: ripple-effect 0.6s ease-out;
    }

    @keyframes ripple-effect {
      0% {
        width: 60px;
        height: 60px;
        opacity: 1;
      }
      100% {
        width: 200px;
        height: 200px;
        opacity: 0;
      }
    }

    /* ========== MAIN CONTENT SHIFT ==========*/
    .block-container {
      transition: margin-left var(--transition-base), width var(--transition-base);
    }

    /* ========== RESPONSIVO ==========*/
    @media (max-width: 768px) {
      div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) {
        width: 300px;
        left: -300px;
      }
      
      div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker).sidebar-open {
        box-shadow: 2px 0 24px rgba(0, 0, 0, 0.3);
      }
      
      #premium-filter-btn {
        bottom: 20px;
        left: 10px;
        width: 54px;
        height: 54px;
        font-size: 22px;
      }
    }

    /* ========== ANIMACIÓN DE ENTRADA ==========*/
    @keyframes sidebar-enter {
      from {
        opacity: 0;
        transform: translateX(-20px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker).sidebar-open > * {
      animation: sidebar-enter 0.3s ease-out forwards;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker).sidebar-open > *:nth-child(n) {
      animation-delay: calc(0.05s * var(--order, 0));
    }
    </style>
    """

    # ========== JAVASCRIPT PREMIUM ==========
    premium_js = """
    <script>
    (function() {
      'use strict';
      
      console.log("🚀 Premium Sidebar JS Loaded");

      // ========== CONFIGURACIÓN ==========
      const CONFIG = {
        sidebarSelector: '.premium-sidebar-wrapper', // Priority selector
        fallbackSelector: '[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)',
        buttonId: 'premium-filter-btn',
        markerSelector: '#filter-sidebar-marker',
        mainContentSelector: '.block-container',
        sidebarOpenClass: 'sidebar-open',
        className: 'premium-sidebar-wrapper'
      };

      class SidebarManager {
        constructor() {
          this.sidebar = null;
          this.button = null;
          this.isOpen = false;
          this.init();
        }

        init() {
          this.attemptInitialization();

          const observer = new MutationObserver((mutations) => {
             for (const mutation of mutations) {
                if (mutation.addedNodes.length) {
                    this.attemptInitialization();
                }
             }
          });

          observer.observe(document.body, { childList: true, subtree: true });
          
          // Fallback periodico
          setInterval(() => this.attemptInitialization(), 1000);
        }

        attemptInitialization() {
            // 1. Encontrar y Taggear el Container
            const marker = document.querySelector(CONFIG.markerSelector);
            if (marker) {
                const container = marker.closest('[data-testid="stVerticalBlock"]');
                if (container && !container.classList.contains(CONFIG.className)) {
                    console.log("✅ Tagging Sidebar Container with class:", CONFIG.className);
                    container.classList.add(CONFIG.className);
                    this.sidebar = container;
                }
            }

            // 2. Crear Botón si no existe
            if (!document.getElementById(CONFIG.buttonId)) {
                this.createButton();
                this.setupEventListeners();
            }
        }

        getSidebar() {
            return document.querySelector('.' + CONFIG.className) || 
                   document.querySelector(CONFIG.fallbackSelector);
        }

        createButton() {
          const existingBtn = document.getElementById(CONFIG.buttonId);
          if (existingBtn) return;
          
          console.log("Creating Premium Button...");
          this.button = document.createElement('button');
          this.button.id = CONFIG.buttonId;
          this.button.innerHTML = '⚙️';
          this.button.style.zIndex = "2147483647"; 
          this.button.setAttribute('title', 'Abrir Filtros Premium');
          
          Object.assign(this.button.style, {
              position: 'fixed',
              bottom: '30px',
              left: '20px',
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: '2px solid rgba(255,255,255,0.3)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              boxShadow: '0 4px 15px rgba(0,0,0,0.3)',
              transition: 'all 0.3s ease'
          });

          document.body.appendChild(this.button);
        }

        setupEventListeners() {
          if (!this.button) return;
          this.button.onclick = (e) => { 
             e.preventDefault(); e.stopPropagation(); this.toggleSidebar(); 
          };
          document.addEventListener('click', (e) => this.handleOutsideClick(e));
          document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) this.closeSidebar();
          });
        }

        toggleSidebar() {
            if (this.isOpen) this.closeSidebar();
            else this.openSidebar();
        }

        openSidebar() {
          const sidebar = this.getSidebar();
          if (!sidebar) return;

          sidebar.classList.add(CONFIG.sidebarOpenClass);
          this.animateButtonPosition(true);
          this.animateMainContent(true);
          this.isOpen = true;
          this.button.innerHTML = '✕';
          this.button.setAttribute('title', 'Cerrar Filtros Premium');
        }

        closeSidebar() {
          const sidebar = this.getSidebar();
          if (sidebar) sidebar.classList.remove(CONFIG.sidebarOpenClass);

          this.animateButtonPosition(false);
          this.animateMainContent(false);
          this.isOpen = false;
          this.button.innerHTML = '⚙️';
          this.button.setAttribute('title', 'Abrir Filtros Premium');
        }

        handleOutsideClick(event) {
          if (!this.isOpen) return;
          const sidebar = this.getSidebar();
          const isClickOnSidebar = sidebar && sidebar.contains(event.target);
          const isClickOnButton = this.button && this.button.contains(event.target);

          if (!isClickOnSidebar && !isClickOnButton) this.closeSidebar();
        }

        animateButtonPosition(isOpen) {
          if (!this.button) return;
          const targetLeft = isOpen ? '360px' : '20px';
          this.button.style.left = targetLeft;
        }

        animateMainContent(isOpen) {
          const mainContent = document.querySelector(CONFIG.mainContentSelector);
          if (!mainContent) return;
          const targetMargin = isOpen ? '360px' : '0';
          mainContent.style.marginLeft = targetMargin;
          mainContent.style.width = isOpen ? 'calc(100% - 360px)' : '100%';
        }
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new SidebarManager());
      } else {
        new SidebarManager();
      }
    })();
    </script>
    """

    # Inyectar CSS y JS
    st.markdown(premium_css, unsafe_allow_html=True)
    st.markdown(premium_js, unsafe_allow_html=True)
