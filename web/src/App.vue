<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex">
    <!-- 侧边栏 -->
    <transition name="slide">
      <div
        v-if="!isSidebarCollapsed"
        class="w-64 bg-gray-800 border-r border-gray-700 flex flex-col"
      >
        <div class="p-4 border-b border-gray-700">
          <button
            @click="startNewChat"
            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90 text-white px-4 py-3 rounded-lg transition-all"
          >
            新建对话
          </button>
        </div>

        <div class="flex-1 overflow-y-auto">
          <div
            v-for="chat in chatHistory"
            :key="chat.id"
            @click="selectChat(chat.id)"
            :class="['p-3 cursor-pointer hover:bg-gray-700 transition-colors',
              currentChatId === chat.id ? 'bg-gray-700 border-l-4 border-blue-500' : '']"
          >
            <div class="text-gray-300 text-sm truncate">{{ chat.title }}</div>
            <div class="text-gray-500 text-xs mt-1">{{ chat.date }}</div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col">
      <!-- 顶部栏 -->
      <div class="h-16 bg-gray-800 flex items-center px-4 border-b border-gray-700">
        <button
          @click="toggleSidebar"
          class="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <Bars3Icon class="w-6 h-6" />
        </button>
      </div>

      <!-- 消息区域 -->
      <!-- <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['flex', message.isUser ? 'justify-end' : 'justify-start']"
        >
          <div :class="['max-w-2xl p-4 rounded-2xl',
            message.isUser
              ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white'
              : 'bg-gray-800 text-gray-100']">
            <MarkdownRenderer :content="message.content" />
          </div>
        </div>
      </div> -->
      <div class="flex-1 relative">
        <div
          ref="messagesContainer"
          class="absolute inset-0 overflow-y-auto p-4 space-y-4"
        >
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['flex', message.isUser ? 'justify-end' : 'justify-start']"
          >
            <div :class="['max-w-2xl p-4 rounded-2xl',
              message.isUser
                ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white'
                : 'bg-gray-800 text-gray-100']">
              <!-- 修改为实时渲染模式 -->
              <StreamingMarkdown
                :content="message.content"
                :streaming="message.streaming"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- 输入区 -->
      <div class="p-4 bg-gray-800 border-t border-gray-700">
        <form
          @submit.prevent="handleSubmit"
          class="max-w-4xl mx-auto relative"
        >
          <input
            v-model="inputUrl"
            type="text"
            :placeholder="currentChatHasMessages ? '请输入问题...' : '请输入GitHub项目URL...'"
            class="w-full pl-6 pr-24 py-4 bg-gray-900 text-gray-100 rounded-xl
                   border border-gray-700 focus:border-blue-500 focus:ring-2
                   focus:ring-blue-500 outline-none transition-all"
          />
          <button
            type="submit"
            :disabled="isLoading"
            class="absolute right-2 top-2 bg-gradient-to-r from-blue-500 to-purple-600 
                   px-6 py-2 rounded-lg text-white hover:opacity-90 disabled:opacity-50
                   transition-opacity flex items-center"
          >
            <span v-if="!isLoading">分析项目</span>
            <Spinner
              v-else
              class="w-5 h-5"
            />
          </button>
        </form>
      </div>
    </div>

    <!-- 悬浮按钮 -->
    <button
      @click="startNewChat"
      class="fixed bottom-8 right-8 bg-gradient-to-r from-blue-500 to-purple-600 
             p-4 rounded-full shadow-xl hover:scale-105 transition-transform"
    >
      <PlusIcon class="w-6 h-6 text-white" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, unref } from 'vue'
import { Bars3Icon, PlusIcon } from '@heroicons/vue/24/outline'
import StreamingMarkdown from '@/components/StreamingMarkdown.vue'
import Spinner from '@/components/Spinner.vue'
import { chatGithub, chatCompletions } from '@/apis'
import type { Chat } from '@/types'
import { AIConfig, chatHistory } from '@/states'


const isSidebarCollapsed = ref(false)
const inputUrl = ref('')
const isLoading = ref(false)
const currentChatId = ref<string>('')

const currentChatHasMessages = computed(() => {
  const chat = chatHistory.value.find(c => c.id === currentChatId.value)
  return chat ? chat.messages.length > 0 : false
})

const messages = computed(() => {
  const chat = chatHistory.value.find(c => c.id === currentChatId.value)
  return chat?.messages || []
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const startNewChat = () => {
  const newChat: Chat = {
    id: Date.now().toString(),
    title: '新对话',
    date: new Date().toLocaleDateString(),
    messages: []
  }
  chatHistory.value.unshift(newChat)
  currentChatId.value = newChat.id
}

const selectChat = (id: string) => {
  currentChatId.value = id
}

const handleSubmit = async () => {
  // const config = unref(AIConfig)
  // for (const key in config) {
  //   if ((config as any)[key] === '') {

  //   }
  // }

  if (!inputUrl.value || isLoading.value) return

  try {
    isLoading.value = true

    let content = ""
    if (!chatHistory.value.length) {
      startNewChat()
    }
    // 添加到当前对话
    const chat = chatHistory.value.find(c => c.id === currentChatId.value)
    if (chat) {
      chat.messages.push(
        { content: inputUrl.value, isUser: true, timestamp: new Date() },
        { content: content, isUser: false, timestamp: new Date(), streaming: true }
      )
      chat.title = '项目分析'
    }
    const lastMessage = chat?.messages[chat.messages.length - 1]

    let stream
    if (currentChatHasMessages.value) {
      stream = await chatCompletions({
        model: 'gpt-4o',
        messages: chat!.messages.map(m => ({ role: m.isUser ? 'user' : 'assistant', content: m.content }))
      })
    } else {
      stream = await chatGithub({
        url: inputUrl.value,
        model: 'gpt-4o',
      })
    }
    for await (let event of stream) {
      try {
        const msg = JSON.parse(event.data ?? '')
        if (msg.content && lastMessage) {
          content += msg.content
          lastMessage.content = content
          lastMessage.streaming = true
        }
      } catch (e) {

      }
    }

    if (lastMessage) {
      lastMessage.streaming = false
    }

    inputUrl.value = ''
  } finally {
    isLoading.value = false
  }
}

const messagesContainer = ref<HTMLElement>()

watch(messages, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTo({
        top: messagesContainer.value.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}, { deep: true })
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-600 rounded-full hover:bg-gray-500;
}
</style>