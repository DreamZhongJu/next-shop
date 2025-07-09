// app/api/chat/route.ts
import { NextResponse } from 'next/server'
import OpenAI from 'openai'

const openai = new OpenAI({
    apiKey: process.env.DEEPSEEK_API_KEY,
    baseURL: 'https://api.deepseek.com',
})

export async function POST(req: Request) {
    const { message } = await req.json()

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
        async start(controller) {
            try {
                const completion = await openai.chat.completions.create({
                    model: 'deepseek-chat',
                    stream: true,
                    messages: [
                        { role: 'system', content: '你是一个乐于助人的助手。' },
                        { role: 'user', content: message },
                    ],
                })

                for await (const chunk of completion) {
                    const content = chunk.choices?.[0]?.delta?.content
                    if (content) {
                        controller.enqueue(encoder.encode(content))
                    }
                }

                controller.close()
            } catch (err) {
                console.error('❌ 流式请求失败:', err)
                controller.enqueue(encoder.encode('（发生错误）'))
                controller.close()
            }
        },
    })

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/plain; charset=utf-8',
            'Cache-Control': 'no-cache',
        },
    })
}
