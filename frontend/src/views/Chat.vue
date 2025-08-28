<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <!-- Chat Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">AI Health Assistant</h2>
        <div class="flex items-center space-x-2">
          <button
            @click="clearConversation"
            class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          >
            New Chat
          </button>
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            <span class="text-sm text-gray-600">Connected</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages Container -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto px-4 py-6 space-y-4"
    >
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="text-center py-8">
        <div class="bg-blue-50 rounded-lg p-6 max-w-md mx-auto">
          <h3 class="text-lg font-medium text-blue-900 mb-2">Welcome to P360 AI Assistant!</h3>
          <p class="text-blue-700">
            I'm here to help you with health and wellness questions, provide personalized recommendations, 
            and assist with your wellness journey. What would you like to know?
          </p>
        </div>
      </div>

      <!-- Messages -->
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="flex"
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg"
          :class="{
            'bg-blue-600 text-white': message.role === 'user',
            'bg-white text-gray-800 shadow-sm border border-gray-200': message.role === 'assistant'
          }"
        >
          <div class="text-sm" v-html="formatMessage(message.content)"></div>
          <div class="text-xs mt-1 opacity-70">
            {{ formatTime(message.timestamp) }}
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="flex justify-start">
        <div class="bg-white text-gray-800 shadow-sm border border-gray-200 rounded-lg px-4 py-2">
          <div class="flex items-center space-x-1">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="bg-white border-t border-gray-200 px-4 py-4">
      <form @submit.prevent="sendMessage" class="flex space-x-2">
        <input
          v-model="newMessage"
          type="text"
          placeholder="Ask me anything about health and wellness..."
          class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          :disabled="isLoading"
        />
        <button
          type="submit"
          :disabled="isLoading || !newMessage.trim()"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ isLoading ? 'Sending...' : 'Send' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { chatAPI, type ChatMessage, type ChatRequest } from '@/services/api'
import { format } from 'date-fns'

const toast = useToast()

// Component state
const messages = ref<ChatMessage[]>([])
const newMessage = ref('')
const isLoading = ref(false)
const isTyping = ref(false)
const conversationId = ref<string | null>(null)
const messagesContainer = ref<HTMLElement>()

// Load conversation history on mount
onMounted(() => {
  loadConversationHistory()
})

// Auto-scroll to bottom when new messages arrive
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

const loadConversationHistory = async () => {
  try {
    const response = await chatAPI.getUserConversations()
    const conversations = response.data
    
    // Load the most recent conversation if exists
    if (conversations.length > 0) {
      const latestConversation = conversations[0]
      conversationId.value = latestConversation.conversation_id
      
      const historyResponse = await chatAPI.getConversationHistory(latestConversation.conversation_id)
      messages.value = historyResponse.data.messages
    }
  } catch (error) {
    console.error('Error loading conversation history:', error)
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return

  const userMessage: ChatMessage = {
    role: 'user',
    content: newMessage.value,
    timestamp: new Date().toISOString()
  }

  messages.value.push(userMessage)
  const messageText = newMessage.value
  newMessage.value = ''
  isLoading.value = true
  isTyping.value = true

  try {
    const request: ChatRequest = {
      message: messageText,
      conversation_id: conversationId.value || undefined,
      system_prompt: `You are P360's AI health and wellness assistant. You help users with:
        - General health questions and advice
        - Wellness tips and recommendations
        - Lifestyle guidance for better health
        - Mental health and stress management
        
        Always provide helpful, accurate information while reminding users to consult healthcare professionals for medical concerns.
        Be empathetic, supportive, and encouraging in your responses.`,
      stream: false
    }

    const response = await chatAPI.sendMessage(request)
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: response.data.message,
      timestamp: response.data.timestamp
    }

    // Update conversation ID if new
    if (response.data.conversation_id && !conversationId.value) {
      conversationId.value = response.data.conversation_id
    }

    messages.value.push(assistantMessage)
  } catch (error: any) {
    toast.error('Failed to send message. Please try again.')
    console.error('Chat error:', error)
    
    // Remove the user message if request failed
    messages.value.pop()
    newMessage.value = messageText // Restore the message
  } finally {
    isLoading.value = false
    isTyping.value = false
  }
}

const clearConversation = () => {
  messages.value = []
  conversationId.value = null
  toast.info('Started new conversation')
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (content: string) => {
  // Basic markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp?: string) => {
  if (!timestamp) return ''
  return format(new Date(timestamp), 'HH:mm')
}
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
