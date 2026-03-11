import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["src/**/*.test.{js,jsx}"],
    exclude: ["e2e/**"],
    environment: "jsdom",
    setupFiles: ["./src/test/setup.js"],
  },
});
