<template>
  <div class="markdown-stream">
    <div
      v-if="streaming && !renderedContent"
      class="flex items-center text-gray-400"
    >
      <Spinner
        size="sm"
        class="mr-2"
      />
      Analyzing...
    </div>
    <div
      ref="markdownContent"
      class="markdown-body"
      v-html="processedContent"
      @click="handleCopy"
    ></div>
    <div
      v-if="streaming"
      class="blinking-caret"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import hljs from 'highlight.js'
import Spinner from '@/components/Spinner.vue'
import DOMPurify from 'dompurify'
import { ref, watch, computed, nextTick, onMounted } from 'vue'
// import { DocumentDuplicateIcon } from '@heroicons/vue/24/outline';
declare module 'marked' {
  interface MarkedOptions {
    highlight?: (code: string, lang: string) => string | Promise<string>
  }
}

const props = defineProps<{
  content: string
  streaming?: boolean
}>()

// 配置marked渲染器
const renderer = new marked.Renderer()
const code_renderer = new marked.Renderer()
// 自定义链接渲染
renderer.link = ({ href, title, tokens }) => {
  return `<a href="${href}" target="_blank" rel="noopener" class="text-blue-400 hover:text-blue-300 underline">${tokens[0].raw}</a>`
}

// 自定义代码块渲染（添加复制按钮和语言标签）
renderer.code = ({ text: code, lang: language, escaped: isEscaped }) => {
  const validLang = language && hljs.getLanguage(language) ? language : 'plaintext'
  const langClass = validLang === 'plaintext' ? '' : `language-${validLang}`

  console.log(`code: ${code}`)
  return `
    <div class="code-block relative group">
      <div class="code-toolbar flex gap-2 absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <span class="language-tag text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">${validLang}</span>
        <button 
          class="copy-btn p-1.5 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
          onclick="this.nextElementSibling?.click()"
        >
          <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
        </button>
        <button 
          class="copy-trigger hidden" 
          @click="handleCopy(event, \`${DOMPurify.sanitize(code)}\`)"
        ></button>
      </div>
      <pre><code class="hljs ${langClass}">${hljs.highlightAuto(code, [validLang]).value}</code></pre>
    </div>
  `
}

marked.setOptions({
  highlight: (code: any, lang: any) => {
    debugger
    try {
      return hljs.highlight(code, { language: hljs.getLanguage(lang) ? lang : 'plaintext' }).value
    } catch (e) {
      return hljs.highlightAuto(code).value
    }
  },
  breaks: true,
  gfm: true,
  renderer
})

// 响应式数据
const processedContent = ref('')
const debouncedContent = ref('')
const markdownContent = ref<HTMLElement | null>(null)
let updateTimer: ReturnType<typeof setTimeout>
let highlightTimer: ReturnType<typeof setTimeout>

// 复制处理
const handleCopy = (event: MouseEvent) => {
  const target = event.target as HTMLElement

  if (!target.classList.contains('copy-trigger')) return

  const container = target.closest('.code-block')
  const code = container?.querySelector('code')?.textContent || ""

  navigator.clipboard.writeText(code).then(() => {
    const btn = container?.querySelector('.copy-btn')
    if (btn) {
      btn.classList.add('copied')
      setTimeout(() => btn.classList.remove('copied'), 2000)
    }
  })
}

// Markdown处理 
const processMarkdown = (content: string) => {
  const rawHtml = marked(content)
  return DOMPurify.sanitize(rawHtml as string, {
    ADD_TAGS: ['pre', 'code', 'button'],
    ADD_ATTR: ['class', 'onclick']
  })
}

// 智能高亮更新
const updateHighlight = () => {
  clearTimeout(highlightTimer)
  highlightTimer = setTimeout(() => {
    nextTick(() => {
      markdownContent.value?.querySelectorAll('pre code').forEach((block) => {
        if (!block.classList.contains('hljs')) {
          hljs.highlightElement(block as HTMLElement)
        }
      })
    })
  }, props.streaming ? 300 : 0)
}

// 内容监听
watch(() => props.content, (newVal) => {
  clearTimeout(updateTimer)

  if (props.streaming) {
    debouncedContent.value = newVal
    processedContent.value = processMarkdown(newVal)
    updateHighlight()
  } else {
    updateTimer = setTimeout(() => {
      debouncedContent.value = newVal
      processedContent.value = processMarkdown(newVal)
      updateHighlight()
    }, 200)
  }
})

// 初始处理
onMounted(() => {
  processedContent.value = processMarkdown(props.content)
  updateHighlight()
})

const renderedContent = computed(() => processedContent.value.length > 0)
</script>

<style>
.markdown-stream {
  @apply relative;
}

.code-block {
  @apply relative my-4;
}

.code-toolbar {
  z-index: 10;
}

.copy-btn {
  @apply cursor-pointer transition-transform hover:scale-105;
}

.copy-btn.copied {
  @apply bg-green-600 !important;
}

.copy-btn.copied svg {
  @apply text-white;
}

.language-tag {
  @apply font-mono uppercase text-[0.65rem] tracking-wide;
}

.blinking-caret {
  @apply inline-block w-1 h-5 bg-gray-400;
  animation: blink 1s step-end infinite;
}

@keyframes blink {

  0%,
  100% {
    opacity: 1
  }

  50% {
    opacity: 0
  }
}

.markdown-body pre {
  @apply bg-gray-800 rounded-xl p-4 overflow-x-auto;
}

.markdown-body pre code {
  @apply bg-transparent p-0 text-sm leading-5 font-mono;
}

.markdown-body code:not(pre code) {
  @apply bg-gray-700 rounded px-1.5 py-0.5 text-sm;
}

/* 代码高亮主题 */
.hljs {
  @apply bg-gray-800;
}

.hljs-keyword {
  @apply text-purple-400;
}

.hljs-string {
  @apply text-green-400;
}

.hljs-title {
  @apply text-blue-400;
}

.hljs-built_in {
  @apply text-blue-300;
}

.hljs-comment {
  @apply text-gray-500;
}

/* 流式段落动画 */
.markdown-body p:last-child {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(2px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>