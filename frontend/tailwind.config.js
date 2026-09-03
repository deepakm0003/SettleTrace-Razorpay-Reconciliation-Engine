/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'navy': '#0F2A4A',
        'navy-light': '#1a3a52',
        'accent-blue': '#0066FF',
        'accent-blue-dark': '#0052cc',
      },
    },
  },
  plugins: [],
}
