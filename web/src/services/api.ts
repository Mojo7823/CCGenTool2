import axios from 'axios'

function resolveBaseURL(): string {
	const envUrl = (import.meta as any).env.VITE_API_URL
	if (envUrl) return envUrl
	// Default to same host as the frontend but port 8000
	if (typeof window !== 'undefined' && window.location) {
		const { protocol, hostname } = window.location
		return `${protocol}//${hostname}:8000`
	}
	return 'http://localhost:8000'
}

const api = axios.create({ baseURL: resolveBaseURL() })

export default api
