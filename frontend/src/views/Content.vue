<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Content Library</h1>
        <p class="text-gray-600 mt-2">Generate AI-powered health and wellness content</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Content Generation Form -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Generate New Content</h2>
            
            <form @submit.prevent="generateContent" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
                <select
                  v-model="contentRequest.content_type"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select type...</option>
                  <option value="article">Article</option>
                  <option value="blog_post">Blog Post</option>
                  <option value="social_media">Social Media Post</option>
                  <option value="newsletter">Newsletter</option>
                  <option value="infographic_text">Infographic Text</option>
                  <option value="tip_sheet">Tip Sheet</option>
                  <option value="recipe">Healthy Recipe</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Topic</label>
                <input
                  v-model="contentRequest.topic"
                  type="text"
                  placeholder="e.g., Morning Exercise Routines"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
                <select
                  v-model="contentRequest.target_audience"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="general">General Public</option>
                  <option value="beginners">Beginners</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="seniors">Seniors</option>
                  <option value="young_adults">Young Adults</option>
                  <option value="professionals">Working Professionals</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Length</label>
                <select
                  v-model="contentRequest.length"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="short">Short (200-300 words)</option>
                  <option value="medium">Medium (500-700 words)</option>
                  <option value="long">Long (1000-1500 words)</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Keywords (optional)</label>
                <input
                  v-model="keywordsInput"
                  type="text"
                  placeholder="exercise, nutrition, mindfulness (comma-separated)"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                class="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors"
                :disabled="isGenerating"
              >
                {{ isGenerating ? 'Generating...' : 'Generate Content' }}
              </button>
            </form>

            <!-- Quick Templates -->
            <div class="mt-6 pt-6 border-t border-gray-200">
              <h3 class="text-sm font-medium text-gray-700 mb-3">Quick Templates</h3>
              <div class="space-y-2">
                <button
                  v-for="template in quickTemplates"
                  :key="template.category"
                  @click="generateTemplates(template.category)"
                  class="w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                  :disabled="isGeneratingTemplates"
                >
                  {{ template.label }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Generated Content Display -->
        <div class="lg:col-span-2">
          <!-- Current Generated Content -->
          <div v-if="currentContent" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Generated Content</h2>
              <div class="flex space-x-2">
                <button
                  @click="copyToClipboard(currentContent.content)"
                  class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                >
                  Copy
                </button>
                <button
                  @click="saveContent"
                  class="px-3 py-1 text-sm bg-green-100 hover:bg-green-200 text-green-700 rounded-md transition-colors"
                >
                  Save to Library
                </button>
              </div>
            </div>
            
            <div class="mb-4 text-sm text-gray-600">
              <span class="font-medium">Type:</span> {{ currentContent.content_type }} | 
              <span class="font-medium">Topic:</span> {{ currentContent.topic }} | 
              <span class="font-medium">Audience:</span> {{ currentContent.target_audience }} |
              <span class="font-medium">Tokens:</span> {{ currentContent.token_count }}
            </div>
            
            <div class="prose prose-sm max-w-none text-gray-700" v-html="formatContent(currentContent.content)"></div>
          </div>

          <!-- Content Library -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Content Library</h2>
              <button
                @click="loadContentLibrary"
                class="text-blue-600 hover:text-blue-700 text-sm"
                :disabled="isLoadingLibrary"
              >
                {{ isLoadingLibrary ? 'Loading...' : 'Refresh' }}
              </button>
            </div>

            <!-- Content Filters -->
            <div class="flex space-x-4 mb-4">
              <select
                v-model="libraryFilters.content_type"
                @change="loadContentLibrary"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option value="article">Articles</option>
                <option value="blog_post">Blog Posts</option>
                <option value="social_media">Social Media</option>
                <option value="newsletter">Newsletters</option>
              </select>
              
              <input
                v-model="libraryFilters.topic"
                @input="debounceSearch"
                type="text"
                placeholder="Search topics..."
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Content Items -->
            <div v-if="contentLibrary.length === 0" class="text-gray-500 text-center py-8">
              No content found. Generate some content to get started!
            </div>
            
            <div v-else class="space-y-4">
              <div
                v-for="item in contentLibrary"
                :key="item.id"
                class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                @click="viewContent(item)"
              >
                <div class="flex items-center justify-between mb-2">
                  <h3 class="font-medium text-gray-900">{{ item.topic }}</h3>
                  <span
                    class="px-2 py-1 text-xs rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': item.is_approved,
                      'bg-yellow-100 text-yellow-800': !item.is_approved
                    }"
                  >
                    {{ item.is_approved ? 'Published' : 'Draft' }}
                  </span>
                </div>
                
                <div class="text-sm text-gray-600 mb-2">
                  {{ item.content_type }} • {{ item.target_audience }} • {{ formatDate(item.generated_at) }}
                </div>
                
                <p class="text-sm text-gray-700 line-clamp-2">
                  {{ item.content.substring(0, 150) }}...
                </p>
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
import { contentAPI, type ContentRequest } from '@/services/api'
import { format } from 'date-fns'

const toast = useToast()

// Component state
const contentRequest = reactive<ContentRequest>({
  content_type: '',
  topic: '',
  target_audience: 'general',
  length: 'medium',
  keywords: []
})

const keywordsInput = ref('')
const currentContent = ref<any>(null)
const contentLibrary = ref<any[]>([])
const libraryFilters = reactive({
  content_type: '',
  topic: ''
})

const isGenerating = ref(false)
const isGeneratingTemplates = ref(false)
const isLoadingLibrary = ref(false)

const quickTemplates = [
  { category: 'wellness', label: 'Wellness Articles' },
  { category: 'fitness', label: 'Fitness Content' },
  { category: 'nutrition', label: 'Nutrition Guides' }
]

onMounted(() => {
  loadContentLibrary()
})

const generateContent = async () => {
  isGenerating.value = true
  try {
    // Process keywords
    if (keywordsInput.value.trim()) {
      contentRequest.keywords = keywordsInput.value.split(',').map(k => k.trim())
    }
    
    const response = await contentAPI.generateContent(contentRequest)
    currentContent.value = response.data
    
    toast.success('Content generated successfully!')
  } catch (error) {
    toast.error('Failed to generate content')
    console.error('Content generation error:', error)
  } finally {
    isGenerating.value = false
  }
}

const generateTemplates = async (category: string) => {
  isGeneratingTemplates.value = true
  try {
    const response = await contentAPI.generateTemplates(category, 5)
    toast.success(`Generated ${response.data.content.length} ${category} templates!`)
    
    // Refresh library to show new content
    loadContentLibrary()
  } catch (error) {
    toast.error('Failed to generate templates')
    console.error('Template generation error:', error)
  } finally {
    isGeneratingTemplates.value = false
  }
}

const loadContentLibrary = async () => {
  isLoadingLibrary.value = true
  try {
    const response = await contentAPI.getContentLibrary(
      libraryFilters.content_type || undefined,
      libraryFilters.topic || undefined,
      false, // Show both approved and draft content
      50
    )
    contentLibrary.value = response.data
  } catch (error) {
    console.error('Error loading content library:', error)
  } finally {
    isLoadingLibrary.value = false
  }
}

const viewContent = (item: any) => {
  currentContent.value = item
}

const saveContent = async () => {
  if (!currentContent.value) return
  
  try {
    // In a real implementation, you might want to show a save dialog
    // For now, we'll just approve the content
    await contentAPI.approveContent(currentContent.value.content_id, 'User')
    toast.success('Content saved to library!')
    
    // Refresh library
    loadContentLibrary()
  } catch (error) {
    toast.error('Failed to save content')
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

const formatContent = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>')
}

const formatDate = (dateStr: string) => {
  return format(new Date(dateStr), 'MMM dd, yyyy')
}

// Debounced search for topic filter
let searchTimeout: NodeJS.Timeout
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadContentLibrary()
  }, 500)
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
</style>
