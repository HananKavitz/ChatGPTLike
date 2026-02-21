/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ChatGPT Dark Theme Colors
        bg: {
          primary: '#212121',
          secondary: '#171717',
          input: '#2F2F2F',
          'user-msg': '#2F2F2F',
          'ai-msg': '#444654',
          hover: '#2A2B32',
        },
        text: {
          primary: '#ECECF1',
          secondary: '#C5C5D2',
        },
        border: '#424242',
        accent: '#10a37f',
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}
