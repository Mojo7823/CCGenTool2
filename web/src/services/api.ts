import axios from 'axios'

function resolveBaseURL(): string {
	const envUrl = (import.meta as any).env.VITE_API_URL
	if (envUrl) return envUrl
	// In dev, use Vite proxy at /api to avoid CORS and port juggling
	if ((import.meta as any).env.DEV) return '/api'
	// In prod, default to same host with port 8000
	if (typeof window !== 'undefined' && window.location) {
		const { protocol, hostname } = window.location
		return `${protocol}//${hostname}:8000`
	}
	return 'http://localhost:8000'
}

const api = axios.create({ baseURL: resolveBaseURL() })

export default api
