<template>
  <div class="h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex">
    <!-- 侧边栏 -->
    <transition name="slide">
      <div
        v-if="!isSidebarCollapsed"
        class="h-full w-64 bg-gray-800 border-r border-gray-700 flex flex-col"
      >
        <div class="p-3 border-b border-gray-700">
          <button
            @click="startNewChat"
            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90 text-white px-3 py-2 rounded-lg transition-all"
          >
            新建对话
          </button>
        </div>

        <div class="flex-1 h-full overflow-y-auto">
          <div
            v-for="chat in chatHistory"
            :key="chat.id"
            @click="selectChat(chat.id)"
            :class="[
              'group relative p-3 cursor-pointer transition-colors',
              currentChatId === chat.id
                ? 'bg-gray-700 border-l-4 border-blue-500'
                : 'hover:bg-gray-600',
            ]"
          >
            <div class="text-gray-300 text-sm truncate">{{ chat.title || '新对话' }}</div>
            <div class="text-gray-500 text-xs mt-1">{{ chat.date }}</div>
            <button
              class="absolute right-2 top-1/3 w-6 h-6 rounded-lg hover:bg-gray-800 flex items-center justify-center text-gray-400"
              :class="
                currentChatId === chat.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
              "
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  fill-rule="evenodd"
                  d="M3 12a2 2 0 1 1 4 0 2 2 0 0 1-4 0m7 0a2 2 0 1 1 4 0 2 2 0 0 1-4 0m7 0a2 2 0 1 1 4 0 2 2 0 0 1-4 0"
                  clip-rule="evenodd"
                ></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 主内容区 -->
    <div
      :class="[
        'flex flex-col bg-gray-800 transition-all duration-300 flex-1',
        !currentChatHasMessage ? 'justify-center' : 'justify-end',
      ]"
    >
      <!-- 顶部栏 -->
      <div class="min-h-[65px] bg-gray-800 flex items-center px-4 border-b border-gray-700">
        <button
          @click="toggleSidebar"
          class="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <Bars3Icon class="w-6 h-6" />
        </button>
      </div>
      <div class="flex-1 relative">
        <div ref="messagesContainer" class="absolute inset-0 overflow-y-auto p-4 space-y-4">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['flex', message.isUser ? 'justify-end' : 'justify-start']"
          >
            <div
              :class="[
                'max-w-2xl p-4 rounded-2xl',
                message.isUser
                  ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white'
                  : 'bg-gray-800 text-gray-100',
              ]"
            >
              <!-- 修改为实时渲染模式 -->
              <StreamingMarkdown :content="message.content" :streaming="message.streaming" />
            </div>
          </div>
        </div>
      </div>
      <!-- 输入区 -->
      <div
        :class="[
          !currentChatHasMessage
            ? 'h-full flex items-center justify-center pb-20' // 无对话时居中
            : 'border-gray-700 pb-6', // 有对话时底部样式
        ]"
        class="px-4 bg-gray-800 transition-all duration-500"
      >
        <form
          @submit.prevent="handleSubmit"
          class="flex gap-2 mx-auto items-end"
          :class="!currentChatHasMessage ? 'max-w-2xl w-full' : 'max-w-4xl w-full'"
        >
          <textarea
            v-auto-resize
            v-model="inputUrl"
            :placeholder="currentChat?.hasMessage ? '请输入问题...' : '请输入GitHub项目URL...'"
            rows="1"
            class="flex-1 pl-4 pr-4 py-3 bg-gray-900 text-gray-100 rounded-xl border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none min-h-[48px] max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600"
          />
          <button
            type="submit"
            :disabled="isLoading"
            class="h-[48px] w-[48px] mb-0.5 flex-shrink-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white hover:opacity-90 disabled:opacity-50 transition-opacity flex items-center justify-center"
          >
            <svg
              v-if="!isLoading"
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
            <Spinner v-else class="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>

    <!-- 悬浮按钮 -->
    <button
      @click="startNewChat"
      class="fixed bottom-8 right-8 bg-gradient-to-r from-blue-500 to-purple-600 p-4 rounded-full shadow-xl hover:scale-105 transition-transform"
    >
      <PlusIcon class="w-6 h-6 text-white" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { Bars3Icon, PlusIcon } from '@heroicons/vue/24/outline'
import StreamingMarkdown from '@/components/StreamingMarkdown.vue'
import Spinner from '@/components/Spinner.vue'
import { chatGithub, chatCompletions, getTitle } from '@/apis'
import type { Chat } from '@/types'
import { AIConfig, chatHistory } from '@/states'

const isSidebarCollapsed = ref(false)
const inputUrl = ref('')
const isLoading = ref(false)
const currentChatId = ref<string>('')

const currentChat = computed(() => {
  const chat = chatHistory.value.find((c) => c.id === currentChatId.value)
  return chat
})

const currentChatHasMessage = computed(() => {
  const chat = chatHistory.value.find((c) => c.id === currentChatId.value)
  return chat?.hasMessage || false
})

const messages = computed(() => {
  const chat = chatHistory.value.find((c) => c.id === currentChatId.value)
  return chat?.messages || []
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const startNewChat = () => {
  const newChat: Chat = {
    id: Date.now().toString(),
    title: '',
    date: new Date().toLocaleDateString(),
    messages: [],
    hasMessage: false,
  }
  chatHistory.value.unshift(newChat)
  currentChatId.value = newChat.id
  return newChat
}

const selectChat = (id: string) => {
  currentChatId.value = id
}

function fakeStream(text: string, setFn: (char: string) => void, speed?: number) {
  let index = 0
  if (speed === void 0) {
    speed = Math.floor(Math.random() * 100) + 1
  }

  const timer = setInterval(() => {
    if (index < text.length) {
      setFn(text.charAt(index))
      index++
    } else {
      clearInterval(timer)
    }
  }, speed)
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

    let content = ''
    if (
      !chatHistory.value.length ||
      chatHistory.value.find((c) => c.id === currentChatId.value) === void 0
    ) {
      startNewChat()
    }

    currentChat.value!.messages.push(
      { content: inputUrl.value, isUser: true, timestamp: new Date() },
      { content: content, isUser: false, timestamp: new Date(), streaming: true },
    )
    const lastMessage = currentChat.value!.messages[currentChat.value!.messages.length - 1]

    let stream
    if (currentChat.value!.hasMessage) {
      stream = await chatCompletions({
        model: 'gpt-4o',
        messages: currentChat.value!.messages.map((m) => ({
          role: m.isUser ? 'user' : 'assistant',
          content: m.content,
        })),
      })
    } else {
      stream = await chatGithub({
        url: inputUrl.value,
        model: 'gpt-4o',
      })
    }
    if (!stream) {
      return
    }
    for await (let event of stream) {
      try {
        const msg = JSON.parse(event.data ?? '')
        if (msg.content) {
          content += msg.content
          lastMessage.content = content
          lastMessage.streaming = true
        }
      } catch (e) {}
    }
    currentChat.value!.hasMessage = true
    lastMessage.streaming = false

    if (!currentChat.value!.title) {
      const res = await getTitle({
        model: 'gpt-4o',
        messages: currentChat.value!.messages.map((m) => ({
          role: m.isUser ? 'user' : 'assistant',
          content: m.content,
        })),
      })
      if (res.title) {
        fakeStream(res.title, (char) => {
          currentChat.value!.title += char
        })
      }
    }
    inputUrl.value = ''
  } finally {
    isLoading.value = false
  }
}

const messagesContainer = ref<HTMLElement>()

watch(
  messages,
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTo({
          top: messagesContainer.value.scrollHeight,
          behavior: 'smooth',
        })
      }
    })
  },
  { deep: true },
)

// 在setup()之前添加这个指令
const vAutoResize = {
  mounted(el: HTMLTextAreaElement) {
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'

    const resize = () => {
      el.style.height = 'auto'
      const maxHeight = 160 // 对应max-h-40
      const newHeight = Math.min(el.scrollHeight, maxHeight)
      el.style.height = newHeight + 'px'
    }

    el.addEventListener('input', resize)
  },
  updated(el: HTMLTextAreaElement) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 160) + 'px'
  },
}
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
