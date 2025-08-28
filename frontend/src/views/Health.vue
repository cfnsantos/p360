<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Health Dashboard</h1>
        <p class="text-gray-600 mt-2">Track your health metrics and get AI-powered recommendations</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Health Profile -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Health Profile</h2>
            
            <form @submit.prevent="updateProfile" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Age</label>
                  <input
                    v-model.number="userProfile.age"
                    type="number"
                    class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                  <select
                    v-model="userProfile.gender"
                    class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select...</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="prefer_not_to_say">Prefer not to say</option>
                  </select>
                </div>
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Height (cm)</label>
                  <input
                    v-model.number="userProfile.height"
                    type="number"
                    class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Weight (kg)</label>
                  <input
                    v-model.number="userProfile.weight"
                    type="number"
                    class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Activity Level</label>
                <select
                  v-model="userProfile.activity_level"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select...</option>
                  <option value="sedentary">Sedentary</option>
                  <option value="lightly_active">Lightly Active</option>
                  <option value="moderately_active">Moderately Active</option>
                  <option value="very_active">Very Active</option>
                  <option value="extremely_active">Extremely Active</option>
                </select>
              </div>

              <button
                type="submit"
                class="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors"
                :disabled="isUpdatingProfile"
              >
                {{ isUpdatingProfile ? 'Updating...' : 'Update Profile' }}
              </button>
            </form>

            <!-- Get AI Recommendations -->
            <div class="mt-6 pt-6 border-t border-gray-200">
              <button
                @click="getAIRecommendations"
                class="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition-colors"
                :disabled="isGettingRecommendations"
              >
                {{ isGettingRecommendations ? 'Generating...' : 'Get AI Health Recommendations' }}
              </button>
            </div>
          </div>

          <!-- Wellness Tips -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Daily Tips</h2>
              <button
                @click="generatePersonalizedTips"
                class="text-blue-600 hover:text-blue-700 text-sm"
                :disabled="isGeneratingTips"
              >
                {{ isGeneratingTips ? 'Generating...' : 'Generate New Tips' }}
              </button>
            </div>
            
            <div class="space-y-3">
              <div
                v-for="tip in wellnessTips"
                :key="tip.id"
                class="p-3 bg-blue-50 rounded-lg"
              >
                <h4 class="font-medium text-blue-900 text-sm">{{ tip.title }}</h4>
                <p class="text-blue-700 text-xs mt-1">{{ tip.content }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Health Data & Recommendations -->
        <div class="lg:col-span-2">
          <!-- AI Recommendations -->
          <div v-if="aiRecommendations" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">AI Health Recommendations</h2>
            <div class="prose prose-sm max-w-none text-gray-700" v-html="formatRecommendations(aiRecommendations.recommendations)"></div>
            <div class="mt-4 text-xs text-gray-500">
              Generated: {{ formatDateTime(aiRecommendations.generated_at) }} | 
              Confidence: {{ Math.round(aiRecommendations.confidence_score * 100) }}%
            </div>
          </div>

          <!-- Health Data Input -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Log Health Data</h2>
            
            <form @submit.prevent="logHealthData" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Sleep (hours)</label>
                <input
                  v-model.number="healthData.sleep_hours"
                  type="number"
                  step="0.5"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Exercise (minutes)</label>
                <input
                  v-model.number="healthData.exercise_minutes"
                  type="number"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Water (liters)</label>
                <input
                  v-model.number="healthData.water_intake"
                  type="number"
                  step="0.1"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Stress Level (1-10)</label>
                <input
                  v-model.number="healthData.stress_level"
                  type="number"
                  min="1"
                  max="10"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Mood (1-10)</label>
                <input
                  v-model.number="healthData.mood"
                  type="number"
                  min="1"
                  max="10"
                  class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div class="md:col-span-1">
                <button
                  type="submit"
                  class="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors mt-6"
                  :disabled="isLoggingData"
                >
                  {{ isLoggingData ? 'Logging...' : 'Log Data' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Recent Health Data -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Recent Health Data</h2>
            
            <div v-if="recentHealthData.length === 0" class="text-gray-500 text-center py-8">
              No health data logged yet. Start tracking your metrics above!
            </div>
            
            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Sleep</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Exercise</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Water</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Stress</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Mood</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="data in recentHealthData" :key="data.date" class="hover:bg-gray-50">
                    <td class="px-4 py-2 text-sm text-gray-900">{{ formatDate(data.date) }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ data.sleep_hours || '-' }}h</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ data.exercise_minutes || '-' }}min</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ data.water_intake || '-' }}L</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ data.stress_level || '-' }}/10</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ data.mood || '-' }}/10</td>
                  </tr>
                </tbody>
              </table>
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
import { healthAPI, type HealthRecommendationRequest } from '@/services/api'
import { format } from 'date-fns'

const toast = useToast()

// Component state
const userProfile = reactive({
  age: null as number | null,
  gender: '',
  height: null as number | null,
  weight: null as number | null,
  activity_level: '',
  health_goals: [] as string[],
  medical_conditions: [] as string[],
  medications: [] as string[],
  allergies: [] as string[]
})

const healthData = reactive({
  user_id: 1, // TODO: Get from auth
  date: new Date().toISOString(),
  sleep_hours: null as number | null,
  exercise_minutes: null as number | null,
  water_intake: null as number | null,
  stress_level: null as number | null,
  mood: null as number | null
})

const recentHealthData = ref<any[]>([])
const aiRecommendations = ref<any>(null)
const wellnessTips = ref<any[]>([])

const isUpdatingProfile = ref(false)
const isLoggingData = ref(false)
const isGettingRecommendations = ref(false)
const isGeneratingTips = ref(false)

onMounted(() => {
  loadHealthData()
  loadWellnessTips()
})

const updateProfile = async () => {
  isUpdatingProfile.value = true
  try {
    // Profile update logic would go here
    toast.success('Profile updated successfully!')
  } catch (error) {
    toast.error('Failed to update profile')
  } finally {
    isUpdatingProfile.value = false
  }
}

const logHealthData = async () => {
  isLoggingData.value = true
  try {
    await healthAPI.logHealthData({
      ...healthData,
      date: new Date().toISOString()
    })
    
    toast.success('Health data logged successfully!')
    
    // Reset form
    Object.assign(healthData, {
      sleep_hours: null,
      exercise_minutes: null,
      water_intake: null,
      stress_level: null,
      mood: null
    })
    
    // Reload recent data
    loadHealthData()
  } catch (error) {
    toast.error('Failed to log health data')
  } finally {
    isLoggingData.value = false
  }
}

const loadHealthData = async () => {
  try {
    const response = await healthAPI.getHealthData(1, 30) // TODO: Use actual user ID
    recentHealthData.value = response.data.slice(0, 10) // Show last 10 entries
  } catch (error) {
    console.error('Error loading health data:', error)
  }
}

const getAIRecommendations = async () => {
  isGettingRecommendations.value = true
  try {
    const request: HealthRecommendationRequest = {
      user_profile: userProfile,
      symptoms: [] // Could be expanded to include symptom input
    }
    
    const response = await healthAPI.getRecommendations(request)
    aiRecommendations.value = response.data
    
    toast.success('AI recommendations generated!')
  } catch (error) {
    toast.error('Failed to generate recommendations')
  } finally {
    isGettingRecommendations.value = false
  }
}

const loadWellnessTips = async () => {
  try {
    const response = await healthAPI.getWellnessTips('general', false, 5)
    wellnessTips.value = response.data
  } catch (error) {
    console.error('Error loading wellness tips:', error)
  }
}

const generatePersonalizedTips = async () => {
  isGeneratingTips.value = true
  try {
    const response = await healthAPI.generatePersonalizedTips(1, 'general', 3)
    wellnessTips.value = response.data.tips
    toast.success('New personalized tips generated!')
  } catch (error) {
    toast.error('Failed to generate tips')
  } finally {
    isGeneratingTips.value = false
  }
}

const formatRecommendations = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatDate = (dateStr: string) => {
  return format(new Date(dateStr), 'MMM dd')
}

const formatDateTime = (dateStr: string) => {
  return format(new Date(dateStr), 'MMM dd, yyyy HH:mm')
}
</script>
