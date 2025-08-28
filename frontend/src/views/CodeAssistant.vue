<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Code Assistant</h1>
        <p class="text-gray-600 mt-2">Get AI-powered coding help, reviews, and debugging assistance</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Code Assistance Form -->
        <div>
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Ask for Code Help</h2>
            
            <form @submit.prevent="getCodeAssistance" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Programming Language</label>
                <select
                  v-model="assistanceRequest.language"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="vue">Vue.js</option>
                  <option value="react">React</option>
                  <option value="java">Java</option>
                  <option value="csharp">C#</option>
                  <option value="php">PHP</option>
                  <option value="go">Go</option>
                  <option value="rust">Rust</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Your Question</label>
                <textarea
                  v-model="assistanceRequest.query"
                  rows="3"
                  placeholder="e.g., How do I implement user authentication in FastAPI?"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Code Context (optional)</label>
                <textarea
                  v-model="assistanceRequest.context"
                  rows="2"
                  placeholder="Provide any additional context about your project or specific requirements..."
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Code Snippet (optional)</label>
                <textarea
                  v-model="assistanceRequest.code_snippet"
                  rows="6"
                  placeholder="Paste your code here if you need help with specific code..."
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                ></textarea>
              </div>

              <button
                type="submit"
                class="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors"
                :disabled="isGettingAssistance"
              >
                {{ isGettingAssistance ? 'Getting Help...' : 'Get Code Assistance' }}
              </button>
            </form>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            
            <div class="grid grid-cols-1 gap-3">
              <!-- Code Review -->
              <div class="border border-gray-200 rounded-lg p-4">
                <h3 class="font-medium text-gray-900 mb-2">Code Review</h3>
                <textarea
                  v-model="reviewCode"
                  rows="4"
                  placeholder="Paste code you want reviewed..."
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                ></textarea>
                <button
                  @click="getCodeReview"
                  class="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition-colors text-sm"
                  :disabled="isGettingReview || !reviewCode.trim()"
                >
                  {{ isGettingReview ? 'Reviewing...' : 'Review Code' }}
                </button>
              </div>

              <!-- Debug Help -->
              <div class="border border-gray-200 rounded-lg p-4">
                <h3 class="font-medium text-gray-900 mb-2">Debug Assistance</h3>
                <input
                  v-model="debugRequest.error_message"
                  type="text"
                  placeholder="Error message..."
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                />
                <textarea
                  v-model="debugRequest.code_snippet"
                  rows="3"
                  placeholder="Problematic code..."
                  class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                ></textarea>
                <button
                  @click="getDebugHelp"
                  class="w-full bg-red-600 text-white py-2 rounded-md hover:bg-red-700 transition-colors text-sm"
                  :disabled="isGettingDebugHelp || !debugRequest.error_message.trim() || !debugRequest.code_snippet.trim()"
                >
                  {{ isGettingDebugHelp ? 'Debugging...' : 'Get Debug Help' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Results Display -->
        <div>
          <!-- Current Assistance Response -->
          <div v-if="currentAssistance" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">AI Assistance</h2>
              <div class="flex space-x-2">
                <button
                  @click="copyToClipboard(currentAssistance.assistance || currentAssistance.review || currentAssistance.debug_assistance)"
                  class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                >
                  Copy
                </button>
                <button
                  @click="provideFeedback(currentAssistance.assistance_id, true)"
                  class="px-3 py-1 text-sm bg-green-100 hover:bg-green-200 text-green-700 rounded-md transition-colors"
                >
                  👍 Helpful
                </button>
              </div>
            </div>
            
            <div class="mb-4 text-sm text-gray-600">
              <span class="font-medium">Language:</span> {{ currentAssistance.language }} |
              <span class="font-medium">Generated:</span> {{ formatDateTime(currentAssistance.generated_at) }} |
              <span class="font-medium">Tokens:</span> {{ currentAssistance.token_count }}
            </div>
            
            <div class="prose prose-sm max-w-none text-gray-700" v-html="formatCodeResponse(currentAssistance.assistance || currentAssistance.review || currentAssistance.debug_assistance)"></div>
          </div>

          <!-- Assistance History -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Recent Assistance</h2>
              <button
                @click="loadAssistanceHistory"
                class="text-blue-600 hover:text-blue-700 text-sm"
                :disabled="isLoadingHistory"
              >
                {{ isLoadingHistory ? 'Loading...' : 'Refresh' }}
              </button>
            </div>

            <div v-if="assistanceHistory.length === 0" class="text-gray-500 text-center py-8">
              No assistance history yet. Ask a coding question to get started!
            </div>
            
            <div v-else class="space-y-3">
              <div
                v-for="item in assistanceHistory"
                :key="item.id"
                class="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 cursor-pointer"
                @click="viewAssistance(item)"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="font-medium text-gray-900 text-sm">{{ item.language }}</span>
                  <span class="text-xs text-gray-500">{{ formatDate(item.created_at) }}</span>
                </div>
                
                <p class="text-sm text-gray-700 line-clamp-2">
                  {{ item.query }}
                </p>
                
                <div class="flex items-center mt-2 space-x-2">
                  <span
                    v-if="item.was_helpful !== null"
                    class="text-xs px-2 py-1 rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': item.was_helpful,
                      'bg-red-100 text-red-800': !item.was_helpful
                    }"
                  >
                    {{ item.was_helpful ? 'Helpful' : 'Not Helpful' }}
                  </span>
                  
                  <span v-if="item.user_rating" class="text-xs text-gray-500">
                    ⭐ {{ item.user_rating }}/5
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { codeAPI, type CodeAssistanceRequest } from '@/services/api'
import { format } from 'date-fns'

const toast = useToast()

// Component state
const assistanceRequest = reactive<CodeAssistanceRequest>({
  query: '',
  language: 'python',
  context: '',
  code_snippet: ''
})

const reviewCode = ref('')
const debugRequest = reactive({
  error_message: '',
  code_snippet: '',
  language: 'python'
})

const currentAssistance = ref<any>(null)
const assistanceHistory = ref<any[]>([])

const isGettingAssistance = ref(false)
const isGettingReview = ref(false)
const isGettingDebugHelp = ref(false)
const isLoadingHistory = ref(false)

onMounted(() => {
  loadAssistanceHistory()
})

const getCodeAssistance = async () => {
  isGettingAssistance.value = true
  try {
    const response = await codeAPI.getAssistance(assistanceRequest)
    currentAssistance.value = response.data
    
    toast.success('Code assistance generated!')
    
    // Reset form
    Object.assign(assistanceRequest, {
      query: '',
      context: '',
      code_snippet: ''
    })
    
    // Refresh history
    loadAssistanceHistory()
  } catch (error) {
    toast.error('Failed to get code assistance')
    console.error('Code assistance error:', error)
  } finally {
    isGettingAssistance.value = false
  }
}

const getCodeReview = async () => {
  isGettingReview.value = true
  try {
    const response = await codeAPI.getCodeReview(
      reviewCode.value,
      assistanceRequest.language,
      ['best_practices', 'performance', 'security', 'maintainability']
    )
    
    currentAssistance.value = {
      ...response.data,
      language: assistanceRequest.language
    }
    
    toast.success('Code review completed!')
    reviewCode.value = ''
    loadAssistanceHistory()
  } catch (error) {
    toast.error('Failed to get code review')
    console.error('Code review error:', error)
  } finally {
    isGettingReview.value = false
  }
}

const getDebugHelp = async () => {
  isGettingDebugHelp.value = true
  try {
    const response = await codeAPI.getDebugHelp(
      debugRequest.error_message,
      debugRequest.code_snippet,
      debugRequest.language
    )
    
    currentAssistance.value = {
      ...response.data,
      language: debugRequest.language
    }
    
    toast.success('Debug assistance generated!')
    
    // Reset debug form
    Object.assign(debugRequest, {
      error_message: '',
      code_snippet: ''
    })
    
    loadAssistanceHistory()
  } catch (error) {
    toast.error('Failed to get debug help')
    console.error('Debug assistance error:', error)
  } finally {
    isGettingDebugHelp.value = false
  }
}

const loadAssistanceHistory = async () => {
  isLoadingHistory.value = true
  try {
    const response = await codeAPI.getAssistanceHistory(undefined, undefined, 20)
    assistanceHistory.value = response.data
  } catch (error) {
    console.error('Error loading assistance history:', error)
  } finally {
    isLoadingHistory.value = false
  }
}

const viewAssistance = (item: any) => {
  currentAssistance.value = {
    assistance: item.assistance_response,
    language: item.language,
    generated_at: item.created_at,
    token_count: 0, // Not stored in history
    assistance_id: item.id
  }
}

const provideFeedback = async (assistanceId: number, wasHelpful: boolean, rating?: number) => {
  try {
    await codeAPI.provideFeedback(assistanceId, wasHelpful, rating)
    toast.success('Thank you for your feedback!')
    loadAssistanceHistory()
  } catch (error) {
    toast.error('Failed to record feedback')
  }
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    toast.success('Content copied to clipboard!')
  } catch (error) {
    toast.error('Failed to copy content')
  }
}

const formatCodeResponse = (content: string) => {
  return content
    .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-3 rounded-md overflow-x-auto"><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm">$1</code>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>')
}

const formatDate = (dateStr: string) => {
  return format(new Date(dateStr), 'MMM dd')
}

const formatDateTime = (dateStr: string) => {
  return format(new Date(dateStr), 'MMM dd, yyyy HH:mm')
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.prose p {
  margin-bottom: 1em;
}

.prose pre {
  background: #f7f7f7;
  padding: 1rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.prose code {
  background: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}
</style>
