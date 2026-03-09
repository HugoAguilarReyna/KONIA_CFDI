
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

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker).sidebar-open {
      left: 0 !important;
      box-shadow: 4px 0 48px rgba(0, 0, 0, 0.35) !important;
    }

    /* Estilos de scrollbar personalizados */
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

    /* 📦 SELECTBOX */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stSelectbox"] > div > div {
      background: var(--filter-bg-glass) !important;
      border: 1px solid var(--filter-border) !important;
      border-radius: 12px !important;
      backdrop-filter: blur(12px) saturate(180%) !important;
      color: var(--color-text-primary) !important;
    }

    /* 🏷️ MULTISELECT */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMultiSelect"] > div > div {
      background: var(--filter-bg-glass) !important;
      border: 1px solid var(--filter-border) !important;
      border-radius: 16px !important;
    }

    /* 🔄 BOTÓN FLOTANTE */
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
      z-index: 2147483647 !important;
      box-shadow: var(--shadow-lg);
      transition: all var(--transition-base);
    }
    
    #premium-filter-btn:hover {
      transform: scale(1.1) translateY(-4px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }

    /* ========== ANIMACIONES ==========*/
    @keyframes sidebar-enter {
      from { opacity: 0; transform: translateX(-20px); }
      to { opacity: 1; transform: translateX(0); }
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker).sidebar-open > * {
      animation: sidebar-enter 0.3s ease-out forwards;
    }
    </style>
    """

    # ========== JAVASCRIPT PREMIUM ==========
    premium_js = """
    <script>
    (function() {
      'use strict';
      
      const CONFIG = {
        className: 'premium-sidebar-wrapper',
        markerSelector: '#filter-sidebar-marker',
        buttonId: 'premium-filter-btn',
        sidebarOpenClass: 'sidebar-open',
        mainContentSelector: '.block-container'
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
          const observer = new MutationObserver(() => this.attemptInitialization());
          observer.observe(document.body, { childList: true, subtree: true });
          setInterval(() => this.attemptInitialization(), 1000);
        }

        attemptInitialization() {
            const marker = document.querySelector(CONFIG.markerSelector);
            if (marker) {
                const container = marker.closest('[data-testid="stVerticalBlock"]');
                if (container && !container.classList.contains(CONFIG.className)) {
                    container.classList.add(CONFIG.className);
                    this.sidebar = container;
                }
            }

            if (!document.getElementById(CONFIG.buttonId)) {
                this.createButton();
                this.setupEventListeners();
            }
        }

        createButton() {
          if (document.getElementById(CONFIG.buttonId)) return;
          this.button = document.createElement('button');
          this.button.id = CONFIG.buttonId;
          this.button.innerHTML = '⚙️';
          this.button.style.zIndex = "2147483647"; 
          document.body.appendChild(this.button);
        }

        setupEventListeners() {
          if (!this.button) return;
          this.button.onclick = (e) => { 
             e.preventDefault(); e.stopPropagation(); this.toggleSidebar(); 
          };
          document.addEventListener('click', (e) => this.handleOutsideClick(e));
        }

        toggleSidebar() {
            this.isOpen ? this.closeSidebar() : this.openSidebar();
        }

        openSidebar() {
          const sidebar = document.querySelector('.' + CONFIG.className);
          if (sidebar) sidebar.classList.add(CONFIG.sidebarOpenClass);
          this.animateElements(true);
          this.isOpen = true;
          this.button.innerHTML = '✕';
        }

        closeSidebar() {
          const sidebar = document.querySelector('.' + CONFIG.className);
          if (sidebar) sidebar.classList.remove(CONFIG.sidebarOpenClass);
          this.animateElements(false);
          this.isOpen = false;
          this.button.innerHTML = '⚙️';
        }

        handleOutsideClick(event) {
          if (!this.isOpen) return;
          const sidebar = document.querySelector('.' + CONFIG.className);
          if (sidebar && !sidebar.contains(event.target) && !this.button.contains(event.target)) {
              this.closeSidebar();
          }
        }

        animateElements(isOpen) {
          if (this.button) this.button.style.left = isOpen ? '360px' : '20px';
          const mainContent = document.querySelector(CONFIG.mainContentSelector);
          if (mainContent) {
              mainContent.style.marginLeft = isOpen ? '360px' : '0';
              mainContent.style.width = isOpen ? 'calc(100% - 360px)' : '100%';
          }
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

    st.markdown(premium_css, unsafe_allow_html=True)
    st.markdown(premium_js, unsafe_allow_html=True)
