/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172026",
        panel: "#ffffff",
        line: "#d8dee4",
        good: "#15803d",
        warn: "#b45309",
        bad: "#b91c1c"
      }
    }
  },
  plugins: []
};

