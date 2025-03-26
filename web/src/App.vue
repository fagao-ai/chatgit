<template>
  <div class="h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex relative">
    <!-- 侧边栏 -->
    <transition name="slide">
      <div
        v-if="!isSidebarCollapsed"
        class="h-full w-64 bg-gray-900 flex flex-col absolute left-0 top-0 bottom-0"
      >
        <Logo class="cursor-pointer" @click="currentChatId = ''" />
        <div class="p-3">
          <Button
            class="w-full !border-none !bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90 !text-white px-3 py-2 rounded-lg transition-all"
            label="新建对话"
            icon="pi pi-plus"
            @click="currentChatId = ''"
          />
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
                : 'hover:bg-gray-600 rounded-2xl',
            ]"
          >
            <div
              v-if="!chat.titleEdit"
              v-tooltip.top="chat.title"
              class="text-gray-300 text-sm truncate"
            >
              {{ chat.title || '新对话' }}
            </div>
            <template v-else>
              <OnClickOutside @trigger="chat.titleEdit = false">
                <InputText
                  v-focus
                  :minlength="1"
                  type="text"
                  size="small"
                  v-model="chat.title"
                  @blur="chat.titleEdit = false"
                  @keyup.enter="chat.titleEdit = false"
                  class="w-full"
                  @click.stop
                />
              </OnClickOutside>
            </template>
            <div class="text-gray-500 text-xs mt-1">{{ chat.date }}</div>
            <button
              v-show="!chat.titleEdit"
              class="absolute right-2 top-1/3 w-6 h-6 rounded-lg hover:bg-gray-800 flex items-center justify-center text-gray-400"
              :class="
                currentChatId === chat.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
              "
              @click="(e) => toggle(e, chat.id)"
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
          <Popover ref="chatOperator">
            <div class="flex flex-col">
              <ul class="list-none p-0 m-0 flex flex-col">
                <li
                  v-for="member in members"
                  :key="member.name"
                  class="flex items-center gap-2 px-2 py-3 hover:bg-emphasis cursor-pointer rounded-border"
                  @click="selectMember(member)"
                >
                  <div>
                    <span class="font-medium">{{ member.name }}</span>
                  </div>
                </li>
              </ul>
            </div>
          </Popover>
        </div>
        <!--设置-->
        <div class="flex p-3">
          <Button
            class="w-full"
            label="设置"
            variant="text"
            icon="pi pi-cog"
            @click="openSettingDialog"
          />
        </div>
      </div>
    </transition>

    <!-- 主内容区 -->
    <div
      :class="[
        'flex flex-col bg-gray-800 transition-[margin] duration-300 ease-in-out flex-1',
        !currentChatHasMessage ? 'justify-center' : 'justify-end',
        isSidebarCollapsed ? '' : 'ml-64',
      ]"
    >
      <!-- 顶部栏 -->
      <div class="min-h-[65px] bg-gray-800 flex items-center px-4">
        <button
          @click="toggleSidebar"
          class="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <i class="pi pi-list" />
        </button>
        <div class="flex-1 text-center text-lg font-medium text-gray-100">
          {{ currentChat?.title }}
        </div>
        <a
          v-tooltip.bottom="'Star on GitHub'"
          target="_blank"
          href="https://github.com/fagao-ai/chatgit"
          class="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-700 transition-colors ml-2"
        >
          <i class="pi pi-github"></i>
        </a>
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
                  : 'bg-gray-700 text-gray-100',
              ]"
            >
              <!-- 修改为实时渲染模式 -->
              <StreamingMarkdown
                :content="message.content"
                :reasoning-content="message.reasoningContent"
                :streaming="message.streaming"
                :reasoning-time="elapsedTime"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- 输入区 -->
      <div
        :class="[
          !currentChatHasMessage
            ? 'h-full flex flex-col items-center justify-center pb-20' // 无对话时居中
            : 'border-gray-700 pb-6', // 有对话时底部样式
        ]"
        class="px-4 bg-gray-800 transition-all duration-500 gap-2"
      >
        <template v-if="!currentChatHasMessage">
          <Logo class="!w-[192px] !h-16" />
          <div class="flex text-sm">
            只需一个 URL, <strong>30秒</strong>掌握项目精髓, 快来和我聊聊吧(*^▽^*)
          </div>
        </template>
        <form
          @submit.prevent="handleSubmit"
          class="flex gap-2 mx-auto items-center"
          :class="!currentChatHasMessage ? 'max-w-2xl w-full' : 'max-w-4xl w-full'"
        >
          <textarea
            v-auto-resize
            :disabled="isLoading"
            v-model="inputUrl"
            :placeholder="currentChat?.hasMessage ? '请输入问题...' : '请输入GitHub项目URL...'"
            rows="1"
            class="flex-1 pl-4 pr-4 py-3 bg-gray-900 text-gray-100 rounded-xl border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none min-h-[48px] max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600"
            @keyup.enter.prevent="handleSubmit"
          />
          <Button
            class="!h-12 !w-12 !text-white !rounded-xl !border-none flex-shrink-0 !bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90 disabled:opacity-50 transition-opacity"
            :loading="isLoading"
            type="submit"
            loading-icon="pi pi-spin pi-spinner"
          >
            <template #icon>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            </template>
          </Button>
        </form>
      </div>
    </div>

    <!-- 悬浮按钮 -->
    <Button
      @click="startNewChat"
      class="!fixed !text-white !bottom-20 !right-4 !bg-gradient-to-r !border-none from-blue-500 to-purple-600 hover:scale-105 transition-transform"
      icon="pi pi-plus"
      severity="info"
      rounded
      aria-label="Add"
      size="large"
    />
    <ConfirmDialog group="positioned"></ConfirmDialog>
    <DynamicDialog />
    <Toast position="top-left" group="tl" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, defineAsyncComponent, unref } from 'vue'
import { OnClickOutside } from '@vueuse/components'
import Popover from 'primevue/popover'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import InputText from 'primevue/inputtext'
import ConfirmDialog from 'primevue/confirmdialog'
import DynamicDialog from 'primevue/dynamicdialog'
import { useConfirm } from 'primevue/useconfirm'
import { useDialog } from 'primevue/usedialog'
import type { ConfirmationOptions } from 'primevue/confirmationoptions'
import { useToast } from 'primevue/usetoast'
import StreamingMarkdown from '@/components/StreamingMarkdown.vue'
import Logo from '@/components/Logo.vue'
import { chatGithub, chatCompletions, getTitle } from '@/apis'
import type { Chat, Config } from '@/types'
import { AIConfig, chatHistory } from '@/states'
import { useTimer } from '@/composables/useTimer'

const { elapsedTime, startTimer, stopTimer } = useTimer()
const confirm = useConfirm()
const toast = useToast()
const dialog = useDialog()
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
  return chat?.hasMessage || chat?.messages.length || isLoading.value || false
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
    titleEdit: false,
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

const validateConfig = (obj: Config) => {
  const { apiKey, baseUrl, model } = obj

  const isAnyNotEmpty = apiKey || baseUrl || model
  const areAllNotEmpty = apiKey && baseUrl && model

  if (isAnyNotEmpty && !areAllNotEmpty) {
    return false // 当有一个不为空时，其他两个也必须不为空
  }
  return true // 全部为空或全部不为空
}

const handleSubmit = async () => {
  const config = unref(AIConfig)
  if (!validateConfig) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: '模型配置不完整,请检查',
      life: 3000,
    })
    return
  }

  if (!inputUrl.value || isLoading.value) return
  const inputValue = unref(inputUrl)

  try {
    isLoading.value = true

    let content = ''
    let reasoningContent = ''
    if (
      !chatHistory.value.length ||
      chatHistory.value.find((c) => c.id === currentChatId.value) === void 0
    ) {
      startNewChat()
    }

    currentChat.value!.messages.push(
      { content: inputValue, isUser: true, timestamp: new Date() },
      { content: content, isUser: false, timestamp: new Date(), streaming: true },
    )
    const lastMessage = currentChat.value!.messages[currentChat.value!.messages.length - 1]
    inputUrl.value = ''
    let stream
    if (currentChat.value!.hasMessage) {
      stream = await chatCompletions({
        messages: currentChat.value!.messages.map((m) => ({
          role: m.isUser ? 'user' : 'assistant',
          content: m.content,
        })),
        ...config,
      })
    } else {
      stream = await chatGithub({
        url: inputValue,
        ...config,
      })
    }
    if (!stream) {
      lastMessage.content = '服务器出错了，请稍后再试'
      lastMessage.streaming = false
      return
    }
    currentChat.value!.hasMessage = true
    for await (let event of stream) {
      try {
        const msg = JSON.parse(event.data ?? '')
        if (msg.reasoning_content) {
          if (!reasoningContent) {
            startTimer()
          }
          reasoningContent += msg.reasoning_content
          lastMessage.reasoningContent = reasoningContent
          lastMessage.streaming = true
        }
        if (msg.content) {
          content += msg.content
          lastMessage.content = content
          lastMessage.streaming = true
        }
      } catch (e) {
        stopTimer()
        if (elapsedTime.value > 0) {
          lastMessage.reasoningTime = elapsedTime.value
        }
      }
    }
    stopTimer()
    if (elapsedTime.value > 0) {
      lastMessage.reasoningTime = elapsedTime.value
    }
    lastMessage.streaming = false
    if (!lastMessage.content) {
      lastMessage.content = '服务器出错了，请稍后再试'
      if (currentChat.value!.messages.length === 2) {
        currentChat.value!.hasMessage = false
      }
      return
    }

    if (!currentChat.value!.title) {
      const res = await getTitle({
        messages: currentChat.value!.messages.map((m) => ({
          role: m.isUser ? 'user' : 'assistant',
          content: m.content,
        })),
        ...config,
      })
      if (res.title) {
        fakeStream(res.title, (char) => {
          currentChat.value!.title += char
        })
      }
    }
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

const confirmDeleteChat = (position: ConfirmationOptions['position'], chatId: string) => {
  confirm.require({
    group: 'positioned',
    message: '删除后无法恢复,确认删除吗?',
    header: '永久删除对话',
    icon: 'pi pi-info-circle',
    position: position,
    rejectProps: {
      label: '取消',
      severity: 'secondary',
    },
    acceptProps: {
      label: '删除',
      severity: 'danger',
    },
    accept: () => {
      const findChatIndex = chatHistory.value.findIndex((c) => c.id === chatId)
      if (findChatIndex === -1) return
      chatHistory.value.splice(findChatIndex, 1)
      toast.add({
        severity: 'success',
        group: 'tl',
        summary: 'Confirmed',
        detail: '删除成功',
        life: 3000,
      })
    },
    reject: () => {},
  })
}
const chatOperator = ref<InstanceType<typeof Popover>>()
const members = ref([
  {
    name: '重命名',
    type: 'normal' as const,
    fn: (chatId: string) => {
      const chat = chatHistory.value.find((c) => c.id === chatId)
      if (!chat) return
      if (!chat.title) {
        chat.title = '新对话'
      }
      chat.titleEdit = true
    },
  },
  {
    name: '删除',
    type: 'danger' as const,
    fn: (chatId: string) => {
      confirmDeleteChat('left', chatId)
    },
  },
])

let chatOperatorId: string | null = null

const toggle = (event: MouseEvent, chatId: string) => {
  event.stopPropagation()
  chatOperator.value?.toggle(event)
  chatOperatorId = chatId
}

const selectMember = (member: (typeof members.value)[number]) => {
  chatOperator.value?.hide()
  member.fn(chatOperatorId!)
}
// setting dialog
const openSettingDialog = async () => {
  dialog.open(
    defineAsyncComponent(() => import('@/views/Settings.vue')),
    {
      props: {
        header: '系统设置',
        style: {
          width: '800px',
          '--p-dialog-header-padding': '20px 20px 0 20px',
        },
        modal: true,
      },
    },
  )
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
