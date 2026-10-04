import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
    // Coverage instrumentation makes the jsdom suites materially slower than a
    // plain run, so the default 5s per-test budget is not enough headroom.
    testTimeout: 20000,
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      reporter: ["text", "lcov"],
      reportsDirectory: "./coverage",
      exclude: [
        "src/**/*.d.ts",
        "src/types/**",
        "src/main.tsx",
        "src/test-setup.ts",
        "src/test-utils.tsx",
        "src/__tests__/**",
        "src/**/__tests__/**",
        "src/router.tsx",
        "src/ops-router.tsx",
      ],
      thresholds: {
        lines: 80,
        statements: 80,
        functions: 80,
        branches: 80,
      },
    },
  },
});
