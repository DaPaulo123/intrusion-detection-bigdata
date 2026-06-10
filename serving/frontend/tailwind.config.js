/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          main: '#0b0f19',
          panel: 'rgba(17, 24, 39, 0.7)',
          hover: 'rgba(31, 41, 55, 0.8)',
        },
        accent: {
          primary: '#3b82f6',
          hover: '#2563eb',
        },
        status: {
          critical: '#ef4444',
          high: '#f59e0b',
          medium: '#eab308',
          low: '#10b981',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
