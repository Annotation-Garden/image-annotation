/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'agi-teal': {
          DEFAULT: '#184A3D',
          50: '#E8F5F1',
          100: '#D1EBE4',
          200: '#A3D7C9',
          300: '#75C3AE',
          400: '#47AF93',
          500: '#2A7B68',
          600: '#215F50',
          700: '#184A3D',
          800: '#0F352A',
          900: '#062017',
        },
        'agi-orange': {
          DEFAULT: '#E99852',
          50: '#FDF5EE',
          100: '#FBEBDD',
          200: '#F7D7BB',
          300: '#F3C399',
          400: '#EFAF77',
          500: '#E99852',
          600: '#D17D36',
          700: '#A5612A',
          800: '#79471E',
          900: '#4D2D12',
        },
        'agi-purple': {
          DEFAULT: '#4B4967',
          50: '#F0F0F3',
          100: '#E1E0E7',
          200: '#C3C2CF',
          300: '#A5A3B7',
          400: '#87859F',
          500: '#6A6887',
          600: '#4B4967',
          700: '#3A3850',
          800: '#292739',
          900: '#181622',
        },
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-in-out',
      },
    },
  },
  plugins: [],
}