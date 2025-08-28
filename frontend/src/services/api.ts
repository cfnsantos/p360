import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth tokens (when implemented)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

export interface ChatRequest {
  message: string
  conversation_id?: string
  system_prompt?: string
  stream?: boolean
}

export interface HealthRecommendationRequest {
  user_profile: {
    age?: number
    gender?: string
    height?: number
    weight?: number
    activity_level?: string
    health_goals?: string[]
    medical_conditions?: string[]
    medications?: string[]
    allergies?: string[]
  }
  recent_health_data?: any[]
  symptoms?: string[]
  specific_concerns?: string
}

export interface ContentRequest {
  content_type: string
  topic: string
  target_audience?: string
  length?: string
  tone?: string
  keywords?: string[]
}

export interface CodeAssistanceRequest {
  query: string
  language?: string
  context?: string
  code_snippet?: string
}

// Chat API
export const chatAPI = {
  sendMessage: (request: ChatRequest) => api.post('/chat', request),
  getConversationHistory: (conversationId: string) => api.get(`/chat/conversations/${conversationId}`),
  getUserConversations: (userId?: number) => api.get('/chat/conversations'),
}

// Health API
export const healthAPI = {
  getRecommendations: (request: HealthRecommendationRequest) => api.post('/health/recommendations', request),
  logHealthData: (healthData: any) => api.post('/health/data', healthData),
  getHealthData: (userId: number, days: number = 30) => api.get(`/health/data/${userId}?days=${days}`),
  logSymptoms: (symptomData: any) => api.post('/health/symptoms', symptomData),
  getWellnessTips: (category?: string, personalized: boolean = false, limit: number = 10) => 
    api.get('/health/tips', { params: { category, personalized, limit } }),
  generatePersonalizedTips: (userId: number = 1, category: string = 'general', count: number = 3) => 
    api.post('/health/tips/generate', null, { params: { user_id: userId, category, count } }),
}

// Content API
export const contentAPI = {
  generateContent: (request: ContentRequest) => api.post('/content/generate', request),
  getContentLibrary: (contentType?: string, topic?: string, approvedOnly: boolean = true, limit: number = 20) => 
    api.get('/content/library', { params: { content_type: contentType, topic, approved_only: approvedOnly, limit } }),
  generateTemplates: (category: string = 'wellness', count: number = 5) => 
    api.post('/content/templates', null, { params: { category, count } }),
  approveContent: (contentId: number, approvedBy: string) => 
    api.put(`/content/approve/${contentId}`, { approved_by: approvedBy }),
}

// Code Assistance API
export const codeAPI = {
  getAssistance: (request: CodeAssistanceRequest) => api.post('/code/assist', request),
  getCodeReview: (code: string, language: string = 'python', focusAreas?: string[]) => 
    api.post('/code/review', { code, language, focus_areas: focusAreas }),
  getDebugHelp: (errorMessage: string, codeSnippet: string, language: string = 'python', expectedBehavior?: string) => 
    api.post('/code/debug', { 
      error_message: errorMessage, 
      code_snippet: codeSnippet, 
      language, 
      expected_behavior: expectedBehavior 
    }),
  getAssistanceHistory: (userId?: number, language?: string, limit: number = 20) => 
    api.get('/code/history', { params: { user_id: userId, language, limit } }),
  provideFeedback: (assistanceId: number, wasHelpful: boolean, rating?: number) => 
    api.post(`/code/feedback/${assistanceId}`, { was_helpful: wasHelpful, rating }),
}

export default api
