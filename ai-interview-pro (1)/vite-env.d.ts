/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_BACKEND_URL: string;
    // Add other environment variables here as you use them
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
