module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'risk-low': '#10b981',
        'risk-medium': '#f59e0b',
        'risk-high': '#ef4444',
        'primary': '#7c3aed',
        'primary-light': '#a78bfa',
        'secondary': '#06b6d4',
        'secondary-light': '#22d3ee',
        'accent': '#f97316',
        'accent-light': '#fed7aa'
      }
    },
  },
  plugins: [],
}
