import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(() => {
	const apiUrl = process.env.VITE_API_URL || "http://localhost:8000";
	const wsUrl = apiUrl.replace(/^http/, "ws");
	const devHost = process.env.VITE_DEV_HOST || "localhost";

	return {
		server: {
			host: devHost,
			port: 8080,
			strictPort: true,
			hmr: {
				overlay: false,
			},
			proxy: {
				"/api": {
					target: apiUrl,
					changeOrigin: true,
				},
				"/health": {
					target: apiUrl,
					changeOrigin: true,
				},
				"/ws": {
					target: wsUrl,
					ws: true,
				},
			},
		},
		plugins: [react()],
		resolve: {
			alias: {
				"@": path.resolve(__dirname, "./src"),
			},
		},
	};
});
