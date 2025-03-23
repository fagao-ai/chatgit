import http from '@/apis/http'
import type { ChatGithubParams, QAParams } from '@/types'
import { events, stream } from 'fetch-event-stream'
import snakecaseKeys from "snakecase-keys"

export const health = async () => {
    const res = await http.get('/api/v1/chat/health')
}

export const chatGithub = async (params: ChatGithubParams) => {
    try {
        const res = await stream('/api/v1/chat/git-repo', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer `,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(snakecaseKeys(params as any, { deep: true })),
        })
        return res
    } catch (error) {
        console.error(error)
        return
    }
}

export const chatCompletions = async (params: QAParams) => {
    try {
        const res = await stream('/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer `,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(snakecaseKeys(params as any, { deep: true })),
        })
        return res
    } catch (error) {
        console.error(error)
        return
    }
}

export const getTitle = async (params: QAParams) => {
    try {
        const res = await http.post<{ title: string }>('/api/v1/chat/title', params)
        return res.data
    } catch (error) {
        console.error(error)
        return { title: '' }
    }
}