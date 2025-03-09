interface BaseParams {
    model: string,
    apiKey?: string
    baseUrl?: string
    githubToken?: string
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
}

export interface Message {
    content: string
    isUser: boolean
    timestamp: Date
    streaming?: boolean
}

export interface Config {
    apiKey: string
    baseUrl: string
    githubToken: string
}