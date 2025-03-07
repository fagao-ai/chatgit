<template>
    <div
        class="markdown-body"
        v-html="processedContent"
    ></div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import { ref, watchEffect } from 'vue'

const props = defineProps<{
    content: string
}>()

// 配置marked
marked.setOptions({
    highlight: (code: any, lang: any) => {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext'
        return hljs.highlight(code, { language }).value
    },
    breaks: true,
    gfm: true
})

// 创建自定义渲染器处理链接
const renderer = new marked.Renderer()
renderer.link = ({ href, title, text }) => {
    return `<a href="${href}" target="_blank" rel="noopener noreferrer" 
         class="text-blue-400 hover:text-blue-300 underline">${text}</a>`
}

const processedContent = ref('')

watchEffect(() => {
    const rawHtml = marked(props.content, { renderer })
    processedContent.value = DOMPurify.sanitize(rawHtml)
})
</script>

<style>
.markdown-body {
    @apply text-gray-100 leading-relaxed;
}

.markdown-body h1 {
    @apply text-3xl font-bold mb-4 mt-6 border-b border-gray-700 pb-2;
}

.markdown-body h2 {
    @apply text-2xl font-semibold mb-3 mt-5;
}

.markdown-body p {
    @apply mb-4;
}

.markdown-body a {
    @apply text-blue-400 hover:text-blue-300 transition-colors;
}

.markdown-body code {
    @apply font-mono bg-gray-700 rounded px-2 py-1 text-sm;
}

.markdown-body pre {
    @apply bg-gray-800 rounded-xl p-4 my-4 overflow-x-auto;
}

.markdown-body pre code {
    @apply bg-transparent p-0 text-sm leading-5;
}

.markdown-body blockquote {
    @apply border-l-4 border-blue-500 pl-4 my-4 text-gray-400;
}

.markdown-body ul {
    @apply list-disc pl-6 mb-4;
}

.markdown-body ol {
    @apply list-decimal pl-6 mb-4;
}

/* 代码高亮主题 - 可替换为其他主题 */
.hljs {
    @apply bg-gray-800 rounded-lg;
}

.hljs-keyword {
    @apply text-purple-400;
}

.hljs-string {
    @apply text-green-400;
}

.hljs-built_in {
    @apply text-blue-400;
}
</style>