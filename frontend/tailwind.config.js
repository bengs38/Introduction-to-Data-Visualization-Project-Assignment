/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "Arial"],
      },
      colors: {
        ink: "#172033",
        panel: "#ffffff",
        line: "#d8dee8",
        brand: "#0f766e",
        coral: "#e76f51",
        amber: "#d99a2b",
      },
      boxShadow: {
        soft: "0 16px 40px rgba(23, 32, 51, 0.08)",
      },
    },
  },
  plugins: [],
};
