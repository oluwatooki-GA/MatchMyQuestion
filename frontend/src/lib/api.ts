import axios from 'axios'
import type { SearchRequest, SearchResult } from '../types'

const API_URL = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function searchQuestions(request: SearchRequest): Promise<SearchResult> {
  const response = await api.post<SearchResult>('/v1/search', request)
  return response.data
}
