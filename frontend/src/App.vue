<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <h1 class="text-2xl font-bold text-blue-600">P360</h1>
              <span class="ml-2 text-gray-600">Health & Wellness</span>
            </router-link>
          </div>
          
          <div class="flex items-center space-x-4">
            <router-link
              to="/chat"
              class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              AI Chat
            </router-link>
            <router-link
              to="/health"
              class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Health Dashboard
            </router-link>
            <router-link
              to="/content"
              class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Content Library
            </router-link>
            <router-link
              to="/code"
              class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Code Assistant
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 py-8 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center text-gray-600">
          <p>&copy; {{ new Date().getFullYear() }} P360 Health & Wellness Platform. All rights reserved.</p>
          <p class="mt-2 text-sm">AI-powered health recommendations and content generation.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useToast } from 'vue-toastification'

const toast = useToast()

onMounted(() => {
  // Check API connectivity on app load
  checkApiConnection()
})

const checkApiConnection = async () => {
  try {
    const response = await fetch('/api/v1/health')
    if (response.ok) {
      console.log('API connection successful')
    }
  } catch (error) {
    toast.error('Unable to connect to P360 API. Please check your connection.')
  }
}
</script>

<style>
/* Global styles */
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.router-link-active {
  @apply text-blue-600 bg-blue-50;
}
</style>
