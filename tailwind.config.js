/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./case/**/*.html",
    "./dynapac/**/*.html",
    "./*/index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        case: {
          yellow: '#E58E1A',
          dark: '#050505',
          gray: '#1A1A1A',
          panel: '#121212',
          border: '#333333'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Archivo', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'grid-pattern': "linear-gradient(to right, #262626 1px, transparent 1px), linear-gradient(to bottom, #262626 1px, transparent 1px)",
        'stripe-pattern': "repeating-linear-gradient(45deg, #E58E1A, #E58E1A 10px, #000 10px, #000 20px)"
      },
      animation: {
        'marquee': 'marquee 25s linear infinite',
        'spin-slow': 'spin 12s linear infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-100%)' },
        }
      }
    }
  },
  plugins: [],
}
