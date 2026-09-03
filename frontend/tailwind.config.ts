import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Aligned with CSS custom properties in globals.css
        primary: '#17624f',        // == var(--accent)
        'primary-dark': '#104b3d', // == var(--accent-dark)
        'primary-light': '#e5f0ec',// == var(--accent-soft)
        secondary: '#a56b16',      // == var(--amber)
        'secondary-dark': '#8a5710',
        success: '#237a57',        // == var(--success)
        warning: '#a56b16',        // == var(--warning)
        danger: '#b44f4f',         // == var(--error)
        neutral: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        }
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#374151',
            a: {
              color: '#065f46',
              '&:hover': {
                color: '#064e3b',
              },
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}

export default config
