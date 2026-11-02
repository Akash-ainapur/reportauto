// Backend base URL (Render in production, Flask on :5000 locally); empty uses the Vite proxy
export const API_BASE = import.meta.env.VITE_API_URL || "";
