import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";
import svgr from "vite-plugin-svgr";

export default defineConfig({
    server: {
        port: 3001,
    },
    plugins: [
        svgr({
            svgrOptions: { exportType: "named", ref: true, svgo: false, titleProp: true },
            include: "**/*.svg",
        }),
        react(),
    ],
});
