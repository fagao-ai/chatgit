interface BaseParams {
    model?: string | null
    apiKey?: string | null
    baseUrl?: string | null
    githubToken?: string | null
}
export interface ChatGithubParams extends BaseParams {
    url: string,
}

export interface QAParams extends BaseParams {
    messages: { role: string, content: string }[]
}

export interface Chat {
    id: string
    title: string
    date: string
    messages: Message[]
    hasMessage: boolean
    titleEdit: boolean
}

export interface Message {
    content: string
    reasoningContent?: string
    reasoningTime?: number
    isUser: boolean
    timestamp: Date
    streaming?: boolean
}

export interface Config {
    apiKey: string | null
    baseUrl: string | null
    githubToken: string | null
    model: string | null
}