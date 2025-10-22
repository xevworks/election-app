import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
})

http.interceptors.request.use((config) => {
  const adminKey = localStorage.getItem('adminKey')
  if (adminKey) config.headers['X-Admin-Key'] = adminKey
  return config
})

export default http
