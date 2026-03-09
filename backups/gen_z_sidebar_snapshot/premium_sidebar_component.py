
import streamlit as st

def inject_premium_sidebar_styles_and_scripts():
    """
    Inyecta los estilos CSS y scripts JavaScript premium en la aplicación Streamlit.
    """
    
    # ========== CSS PREMIUM ==========
    premium_css = """
    <style>
    /* ========================================
       PREMIUM SIDEBAR STYLES - ÚLTIMA GENERACIÓN
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
    }

    /* ========== CONTENEDOR SIDEBAR PRINCIPAL ==========*/
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker):not(:has([data-testid="stVerticalBlock"])) {
      position: fixed;
      top: 0;
      left: -340px;
      width: 340px;
      height: 100vh;
      background: var(--gradient-primary);
      background-attachment: fixed;
      border-right: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 4px 0 32px rgba(0, 0, 0, 0.25);
      z-index: 999999;
      transition: left var(--transition-base), box-shadow var(--transition-base);
      padding: 24px;
      padding-top: 80px;
      overflow-y: auto;
      overflow-x: hidden;
      color: var(--color-text-primary);
      
      /* Efecto backdrop blur para elementos detrás */
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }

    /* Estado abierto */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker).sidebar-open {
      left: 0;
      box-shadow: 4px 0 48px rgba(0, 0, 0, 0.35);
    }

    /* Scrollbar personalizado */
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

    /* ========== HEADER DE FILTROS ==========*/
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMarkdownContainer"] {
      margin-bottom: 28px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) h1,
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) h2,
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) h3 {
      color: var(--color-text-primary) !important;
      font-weight: 700 !important;
      letter-spacing: -0.5px;
      margin-bottom: 16px !important;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    /* Línea divisoria premium */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) hr {
      border: none;
      height: 1px;
      background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
      margin: 24px 0 !important;
    }

    /* ========== MULTISELECT PREMIUM ==========*/
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMultiSelect"] {
      margin-bottom: 20px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect label {
      color: var(--color-text-primary) !important;
      font-weight: 600 !important;
      font-size: 13px !important;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin-bottom: 12px !important;
      display: flex !important;
      align-items: center !important;
      gap: 8px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect label::before {
      content: '';
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #00d4ff;
      box-shadow: 0 0 12px rgba(0, 212, 255, 0.5);
    }

    /* Select Input */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMultiSelect"] > div > div:first-child {
      background: var(--color-bg-transparent) !important;
      border: 1px solid var(--color-border) !important;
      border-radius: var(--radius-lg) !important;
      backdrop-filter: blur(8px) !important;
      transition: all var(--transition-base) !important;
      padding: 10px 12px !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMultiSelect"] > div > div:first-child:hover,
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMultiSelect"] > div > div:first-child:focus-within {
      background: var(--color-bg-hover) !important;
      border-color: var(--color-border-hover) !important;
      box-shadow: 0 0 20px rgba(0, 212, 255, 0.2) !important;
    }

    /* Tags/Chips Premium */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"] {
      background: linear-gradient(135deg, #4f63d9 0%, #5a3888 100%) !important;
      border: 1px solid rgba(0, 212, 255, 0.3) !important;
      color: white !important;
      font-weight: 600 !important;
      border-radius: var(--radius-full) !important;
      padding: 6px 12px !important;
      font-size: 12px !important;
      transition: all var(--transition-fast) !important;
      box-shadow: 0 4px 12px rgba(79, 99, 217, 0.3) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"]:hover {
      background: linear-gradient(135deg, #6373e6 0%, #6b4899 100%) !important;
      box-shadow: 0 6px 16px rgba(79, 99, 217, 0.5) !important;
      transform: translateY(-2px);
    }

    /* X Button en tags */
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"] svg {
      transition: transform var(--transition-fast) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stMultiSelect [data-testid="stBaseButton-secondary"]:hover svg {
      transform: rotate(90deg) scale(1.2) !important;
    }

    /* ========== TEXT INPUT PREMIUM ==========*/
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stTextInput"] {
      margin-bottom: 20px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stTextInput label {
      color: var(--color-text-primary) !important;
      font-weight: 600 !important;
      font-size: 13px !important;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin-bottom: 12px !important;
      display: flex !important;
      align-items: center !important;
      gap: 8px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) .stTextInput label::before {
      content: '🔍';
      font-size: 14px;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) input[type="text"] {
      background: var(--color-bg-transparent) !important;
      border: 1px solid var(--color-border) !important;
      color: var(--color-text-primary) !important;
      border-radius: var(--radius-lg) !important;
      padding: 12px 16px !important;
      transition: all var(--transition-base) !important;
      font-weight: 500 !important;
      backdrop-filter: blur(8px) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) input[type="text"]::placeholder {
      color: var(--color-text-secondary) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) input[type="text"]:hover {
      background: var(--color-bg-hover) !important;
      border-color: var(--color-border-hover) !important;
    }

    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) input[type="text"]:focus {
      outline: none !important;
      border-color: rgba(0, 212, 255, 0.6) !important;
      box-shadow: 0 0 20px rgba(0, 212, 255, 0.25), inset 0 0 8px rgba(0, 212, 255, 0.1) !important;
      background: var(--color-bg-hover) !important;
    }

    /* ========== DIVIDERS Y SEPARADORES ==========*/
    div[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker) [data-testid="stMarkdownContainer"] + [data-testid="stMarkdownContainer"] hr {
      margin: 24px 0 !important;
    }

    /* ========== EFECTO FONDO ANIMADO ==========*/
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

    /* ========== BOTÓN FLOTANTE PREMIUM ==========*/
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
      z-index: 999998;
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

      // ========== CONFIGURACIÓN ==========
      const CONFIG = {
        sidebarSelector: '[data-testid="stVerticalBlock"]:has(#filter-sidebar-marker)',
        buttonId: 'premium-filter-btn',
        markerSelector: '#filter-sidebar-marker',
        mainContentSelector: '.block-container',
        sidebarOpenClass: 'sidebar-open',
        animationDuration: 300,
        hapticFeedback: true,
      };

      // ========== UTILIDADES ==========
      class SidebarManager {
        constructor() {
          this.sidebar = null;
          this.button = null;
          this.isOpen = false;
          this.isAnimating = false;
          this.init();
        }

        init() {
          this.createButton();
          this.setupEventListeners();
          this.setupObservers();
        }

        createButton() {
          // Eliminar botón anterior si existe
          const existingBtn = document.getElementById(CONFIG.buttonId);
          if (existingBtn) existingBtn.remove();

          // Crear nuevo botón
          this.button = document.createElement('button');
          this.button.id = CONFIG.buttonId;
          this.button.innerHTML = '⚙️';
          this.button.setAttribute('aria-label', 'Toggle Filtros Premium');
          this.button.setAttribute('title', 'Abrir Filtros Premium');

          document.body.appendChild(this.button);
        }

        setupEventListeners() {
          if (this.button) {
            this.button.addEventListener('click', (e) => this.handleButtonClick(e));
            this.button.addEventListener('touchstart', (e) => this.handleTouchStart(e));
          }

          // Cerrar sidebar al hacer clic fuera
          document.addEventListener('click', (e) => this.handleOutsideClick(e));

          // Keyboard: ESC para cerrar
          document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
              this.closeSidebar();
            }
          });
        }

        setupObservers() {
          // Observer para detectar cambios en el DOM
          const observer = new MutationObserver(() => {
            const sidebar = document.querySelector(CONFIG.sidebarSelector);
            if (sidebar && this.sidebar !== sidebar) {
              this.sidebar = sidebar;
              this.updateState();
            }
          });

          observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: false,
          });
        }

        handleButtonClick(event) {
          event.stopPropagation();
          this.triggerRippleEffect();

          if (CONFIG.hapticFeedback && navigator.vibrate) {
            navigator.vibrate(10);
          }

          if (this.isOpen) {
            this.closeSidebar();
          } else {
            this.openSidebar();
          }
        }

        handleTouchStart(event) {
          // Feedback háptico adicional para móvil
          if (navigator.vibrate) {
            navigator.vibrate([10, 5, 10]);
          }
        }

        handleOutsideClick(event) {
          if (!this.isOpen) return;

          const sidebar = document.querySelector(CONFIG.sidebarSelector);
          const isClickOnSidebar = sidebar && sidebar.contains(event.target);
          const isClickOnButton = this.button && this.button.contains(event.target);

          if (!isClickOnSidebar && !isClickOnButton) {
            this.closeSidebar();
          }
        }

        openSidebar() {
          if (this.isAnimating || this.isOpen) return;
          this.isAnimating = true;

          const sidebar = document.querySelector(CONFIG.sidebarSelector);
          if (!sidebar) {
            this.isAnimating = false;
            return;
          }

          sidebar.classList.add(CONFIG.sidebarOpenClass);
          this.animateButtonPosition(true);
          this.animateMainContent(true);
          this.isOpen = true;

          // Animar entrada de elementos
          this.animateSidebarContent();

          setTimeout(() => {
            this.isAnimating = false;
          }, CONFIG.animationDuration);

          // Cambiar icono del botón
          this.updateButtonIcon('✕');
          this.button.setAttribute('title', 'Cerrar Filtros Premium');
        }

        closeSidebar() {
          if (this.isAnimating || !this.isOpen) return;
          this.isAnimating = true;

          const sidebar = document.querySelector(CONFIG.sidebarSelector);
          if (sidebar) {
            sidebar.classList.remove(CONFIG.sidebarOpenClass);
          }

          this.animateButtonPosition(false);
          this.animateMainContent(false);
          this.isOpen = false;

          setTimeout(() => {
            this.isAnimating = false;
          }, CONFIG.animationDuration);

          // Cambiar icono del botón
          this.updateButtonIcon('⚙️');
          this.button.setAttribute('title', 'Abrir Filtros Premium');
        }

        animateButtonPosition(isOpen) {
          if (!this.button) return;

          const targetLeft = isOpen ? '320px' : '20px';
          this.button.style.transition = `left ${CONFIG.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
          this.button.style.left = targetLeft;
        }

        animateMainContent(isOpen) {
          const mainContent = document.querySelector(CONFIG.mainContentSelector);
          if (!mainContent) return;

          const targetMargin = isOpen ? '340px' : '0';
          const targetWidth = isOpen ? 'calc(100% - 340px)' : '100%';

          mainContent.style.transition = `margin-left ${CONFIG.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1), width ${CONFIG.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
          mainContent.style.marginLeft = targetMargin;
          mainContent.style.width = targetWidth;
        }

        animateSidebarContent() {
          const sidebar = document.querySelector(CONFIG.sidebarSelector);
          if (!sidebar) return;

          const elements = sidebar.querySelectorAll('[data-testid="stMarkdownContainer"], [data-testid="stMultiSelect"], [data-testid="stTextInput"]');
          elements.forEach((el, index) => {
            el.style.animation = `none`;
            setTimeout(() => {
              el.style.animation = `sidebar-enter 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards`;
              el.style.animationDelay = `${index * 50}ms`;
            }, 10);
          });
        }

        triggerRippleEffect() {
          if (!this.button) return;

          this.button.classList.add('ripple');
          setTimeout(() => {
            this.button.classList.remove('ripple');
          }, 600);
        }

        updateButtonIcon(icon) {
          if (this.button) {
            this.button.innerHTML = icon;
          }
        }

        updateState() {
          const sidebar = document.querySelector(CONFIG.sidebarSelector);
          if (sidebar) {
            this.isOpen = sidebar.classList.contains(CONFIG.sidebarOpenClass);
          }
        }
      }

      // ========== INICIALIZACIÓN ==========
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
          new SidebarManager();
        });
      } else {
        new SidebarManager();
      }

      // ========== REINICIALIZAR PERIÓDICAMENTE (Streamlit Teleport Pattern) ==========
      setInterval(() => {
        const existingBtn = document.getElementById(CONFIG.buttonId);
        const sidebarMarker = document.querySelector(CONFIG.markerSelector);

        if (sidebarMarker && !existingBtn) {
          new SidebarManager();
        }
      }, 1000);
    })();
    </script>
    """

    # Inyectar CSS y JS
    st.markdown(premium_css, unsafe_allow_html=True)
    st.markdown(premium_js, unsafe_allow_html=True)
