import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  publicDir: "frontend/public",
  server: {
    port: Number(process.env.PORT) || 3000,
    host: "0.0.0.0",
  },
});
