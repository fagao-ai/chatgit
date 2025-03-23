import { useLocalStorage } from "@vueuse/core"
import type { Chat, Config } from "@/types"

export const chatHistory = useLocalStorage<Chat[]>('chatHistory', [])

export const AIConfig = useLocalStorage<Config>('AIConfig', {
    apiKey: null,
    baseUrl: null,
    githubToken: null,
    model: null,
})
