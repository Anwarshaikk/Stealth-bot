/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./public/index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        'surface-tier-0': '#FFFFFF',
        'surface-tier-1': '#F9FAFB',
        'surface-tier-2': '#F1F5F9',
        'text-primary': '#0F172A',
        'text-secondary': '#475569',
        'primary': '#2563EB',
        'accent': '#14B8A6',
        'warn': '#F59E0B',
        'error': '#DC2626'
      }
    }
  },
  plugins: [],
} 