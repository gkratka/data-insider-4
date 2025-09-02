import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunk for React and related libraries
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // UI components chunk
          ui: ['@radix-ui/react-slot', '@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
          // Chart and visualization libraries
          charts: ['recharts'],
          // Form handling
          forms: ['react-hook-form', '@hookform/resolvers', 'zod'],
          // Date utilities
          dates: ['date-fns', 'react-day-picker'],
          // HTTP and state management
          api: ['axios', '@tanstack/react-query'],
          // Icons and styling
          icons: ['lucide-react'],
        }
      }
    },
    chunkSizeWarningLimit: 1000,
  },
}));
