import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export function buildApiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

export { API_BASE_URL };
