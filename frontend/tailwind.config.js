/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
        serif: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
      },
      colors: {
        midnight: '#080b14',
        sidebar: '#0b0e1a',
        surface: '#10131f',
        elevated: '#161a2b',
        raised: '#1d2236',
        aubergine: '#211530',
        indigo: {
          DEFAULT: '#5b4bdb',
          dark: '#4536b8',
        },
        violet: '#8b5cf6',
        gold: '#d6a84f',
        emerald: '#1f8f6f',
        burgundy: '#b1445b',
        cream: '#f5f1e8',
      },
      maxWidth: {
        content: '1180px',
      },
    },
  },
  plugins: [],
};
