/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // bật dark mode dựa trên class 'dark'
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/app/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6c63ff',
        secondary: '#4ecdc4',
        accent: '#ff6b8b',
        dark: '#2c3e50',        // có thể dùng bg-dark
        'dark-color': '#2c3e50', // dùng dark:bg-dark-color
      },
    },
  },
  plugins: [],
};
