/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#17624f',
        'primary-dark': '#104b3d',
        'primary-light': '#e5f0ec',
        secondary: '#a56b16',
        'secondary-dark': '#8a5710',
        success: '#237a57',
        warning: '#a56b16',
        danger: '#b44f4f',
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
        },
      },
    },
  },
  plugins: [],
};
