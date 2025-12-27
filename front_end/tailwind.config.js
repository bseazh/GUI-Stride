/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./App.tsx"
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
        'jetbrains-mono': ['JetBrains Mono', 'monospace'],
        'crimson-pro': ['Crimson Pro', 'serif'],
      },
      colors: {
        // 添加自定义颜色
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}