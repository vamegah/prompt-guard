import axios from 'axios';

const headers: Record<string, string> = {
  'Content-Type': 'application/json',
};

if (import.meta.env.VITE_API_KEY) {
  headers['X-API-Key'] = import.meta.env.VITE_API_KEY;
}

if (import.meta.env.VITE_USER_ID) {
  headers['X-User-Id'] = import.meta.env.VITE_USER_ID;
}

if (import.meta.env.VITE_ORG_ID) {
  headers['X-Org-Id'] = import.meta.env.VITE_ORG_ID;
}

if (import.meta.env.VITE_ROLE) {
  headers['X-Role'] = import.meta.env.VITE_ROLE;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers,
});

// Optional: add request/response interceptors for auth, error handling

export default api;
