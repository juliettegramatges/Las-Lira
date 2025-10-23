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
          50: '#fdf4f8',
          100: '#fbe8f1',
          200: '#f8d1e5',
          300: '#f3aad0',
          400: '#ea76b2',
          500: '#de4b96',
          600: '#ca2d75',
          700: '#ad1f5c',
          800: '#8f1d4d',
          900: '#781c43',
        },
      },
    },
  },
  plugins: [],
}

