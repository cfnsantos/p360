import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Chat from '@/views/Chat.vue'
import Health from '@/views/Health.vue'
import Content from '@/views/Content.vue'
import CodeAssistant from '@/views/CodeAssistant.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
      meta: {
        title: 'P360 - Health & Wellness Platform'
      }
    },
    {
      path: '/chat',
      name: 'Chat',
      component: Chat,
      meta: {
        title: 'AI Chat - P360'
      }
    },
    {
      path: '/health',
      name: 'Health',
      component: Health,
      meta: {
        title: 'Health Dashboard - P360'
      }
    },
    {
      path: '/content',
      name: 'Content',
      component: Content,
      meta: {
        title: 'Content Library - P360'
      }
    },
    {
      path: '/code',
      name: 'CodeAssistant',
      component: CodeAssistant,
      meta: {
        title: 'Code Assistant - P360'
      }
    }
  ]
})

// Update document title based on route
router.beforeEach((to, from, next) => {
  document.title = to.meta.title as string || 'P360'
  next()
})

export default router
