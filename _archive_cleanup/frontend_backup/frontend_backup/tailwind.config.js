/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"]
      },
      colors: {
        ink: "#0f172a",
        mist: "#e2e8f0",
        frost: "#f8fafc",
        lagoon: "#1f8ef1",
        ember: "#ff7a59",
        moss: "#0f766e"
      },
      boxShadow: {
        soft: "0 20px 50px rgba(15, 23, 42, 0.12)"
      }
    }
  },
  plugins: []
};
