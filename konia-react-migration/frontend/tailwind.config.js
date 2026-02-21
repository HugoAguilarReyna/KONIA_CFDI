/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#667eea',
          DEFAULT: '#667eea',
          dark: '#5a67d8',
          hover: '#764ba2',
        },
        // Premium Palette
        pue: "#6B84F3",
        ppd: "#785799",
        otros: "#CBD0DA",
        alerta: "#FF8A65",
        precaucion: "#FFCA28",
        exito: "#26A69A",
        cian: "#00BCD4",
        marino: "#283593",

        success: '#26A69A', // Override default green
        warning: '#FFCA28', // Override default amber
        danger: '#FF8A65', // Override default red
        info: '#00BCD4', // Override default blue
        background: {
          dark: '#ffffff',
          card: '#f8fafc',
          hover: '#f1f5f9',
        }
      },
      fontFamily: {
        // Montserrat como fuente principal en TODA la app
        sans: ["Montserrat", "Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
        display: ["Montserrat", "sans-serif"]
      },
      backgroundImage: {
        'primary-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0))',
      },
      boxShadow: {
        'glass': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
        'neon': '0 0 0px transparent', // Placeholder for consistency
      }
    },
  },
  plugins: [],
}
