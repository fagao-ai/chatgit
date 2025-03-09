import http from '@/apis/http'
import type { ChatGithubParams, QAParams } from '@/types'
import { events, stream } from 'fetch-event-stream'
import snakecaseKeys from "snakecase-keys"

export const health = async () => {
    const res = await http.get('/api/v1/chat/health')
}

export const chatGithub = async (params: ChatGithubParams) => {
    // const res = await http.post("/api/v1/chat/completions", params, { responseType: 'stream' })
    // // @ts-ignore
    // res.body = res.data
    const res = await stream('/api/v1/chat/git-repo', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer `,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(snakecaseKeys(params as any, { deep: true })),
    })
    // let abort = new AbortController()
    // let stream = events(res as any, abort.signal)
    // return stream
    return res
}

export const chatCompletions = async (params: QAParams) => {
    const res = await stream('/api/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer `,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(snakecaseKeys(params as any, { deep: true })),
    })
    return res
}