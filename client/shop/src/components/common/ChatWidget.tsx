'use client'

import { useRef, useState } from 'react'
import { marked } from 'marked'

export default function ChatWidget() {
    const [open, setOpen] = useState(false)
    const [messages, setMessages] = useState<{ role: string; content: string }[]>([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [size, setSize] = useState({ width: 320, height: 400 })
    const [position, setPosition] = useState(() => {
        if (typeof window !== 'undefined') {
            const width = 320
            const height = 400
            return {
                x: window.innerWidth - width - 24, // 距右边 24px
                y: window.innerHeight - height - 24, // 距底部 24px
            }
        }
        return { x: 0, y: 0 } // SSR fallback
    })


    const widgetRef = useRef<HTMLDivElement>(null)
    const isResizing = useRef(false)
    // const resizeDirection = useRef<string | null>(null)
    const lastMouse = useRef({ x: 0, y: 0 })

    // const MIN_WIDTH = 280
    // const MIN_HEIGHT = 300
    // const MAX_WIDTH = 600  // 你可以根据页面布局调整
    // const MAX_HEIGHT = 700

    const isDragging = useRef(false)

    const onDragStart = (e: React.MouseEvent) => {
        isDragging.current = true
        lastMouse.current = { x: e.clientX, y: e.clientY }
        document.addEventListener('mousemove', onDragging)
        document.addEventListener('mouseup', stopDragging)
    }

    const onDragging = (e: MouseEvent) => {
        if (!isDragging.current) return
        const dx = e.clientX - lastMouse.current.x
        const dy = e.clientY - lastMouse.current.y
        lastMouse.current = { x: e.clientX, y: e.clientY }

        setPosition(prev => ({
            x: prev.x + dx,
            y: prev.y + dy,
        }))
    }

    const stopDragging = () => {
        isDragging.current = false
        document.removeEventListener('mousemove', onDragging)
        document.removeEventListener('mouseup', stopDragging)
    }


    // const startResizing = (e: React.MouseEvent, direction: string) => {
    //     e.preventDefault()
    //     isResizing.current = true
    //     resizeDirection.current = direction
    //     lastMouse.current = { x: e.clientX, y: e.clientY }
    //     document.addEventListener('mousemove', handleResize)
    //     document.addEventListener('mouseup', stopResizing)
    // }

    // const handleResize = (e: MouseEvent) => {
    //     if (!isResizing.current || !resizeDirection.current) return  // ✅ 先判断是否为 null

    //     const direction = resizeDirection.current // ⬅️ 提前缓存，防止中间变成 null
    //     const dx = e.clientX - lastMouse.current.x
    //     const dy = e.clientY - lastMouse.current.y
    //     lastMouse.current = { x: e.clientX, y: e.clientY }

    //     setSize(prevSize => {
    //         let newWidth = prevSize.width
    //         let newHeight = prevSize.height
    //         let newX = position.x
    //         let newY = position.y

    //         if (direction.includes('right')) newWidth += dx
    //         if (direction.includes('left')) {
    //             newWidth -= dx
    //             newX += dx
    //         }
    //         if (direction.includes('bottom')) newHeight += dy
    //         if (direction.includes('top')) {
    //             newHeight -= dy
    //             newY += dy
    //         }

    //         newWidth = Math.min(Math.max(MIN_WIDTH, newWidth), MAX_WIDTH)
    //         newHeight = Math.min(Math.max(MIN_HEIGHT, newHeight), MAX_HEIGHT)

    //         // ✅ 同步更新位置
    //         setPosition({ x: newX, y: newY })

    //         return { width: newWidth, height: newHeight }
    //     })
    // }


    // const stopResizing = () => {
    //     isResizing.current = false
    //     resizeDirection.current = null
    //     document.removeEventListener('mousemove', handleResize)
    //     document.removeEventListener('mouseup', stopResizing)
    // }

    const sendMessage = async () => {
        if (!input.trim()) return
        const newMessages = [...messages, { role: 'user', content: input }]
        setMessages([...newMessages, { role: 'assistant', content: '' }])
        setInput('')
        setLoading(true)

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input }),
            })

            const reader = res.body?.getReader()
            const decoder = new TextDecoder('utf-8')
            let botReply = ''

            if (reader) {
                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break
                    botReply += decoder.decode(value, { stream: true })
                    const html = marked.parse(botReply)

                    setMessages(prev => {
                        const updated = [...prev]
                        updated[updated.length - 1] = { role: 'assistant', content: html }
                        return updated
                    })
                }
            }
        } catch (e) {
            console.error('AI错误：', e)
            setMessages(prev => [
                ...prev.slice(0, -1),
                { role: 'assistant', content: '❌ 网络错误或服务异常。' },
            ])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {!open ? (
                <button onClick={() => setOpen(true)} className="bg-blue-600 text-white p-3 rounded-full shadow-lg">
                    AI助手
                </button>
            ) : (
                <div
                    ref={widgetRef}
                    style={{
                        width: size.width,
                        height: size.height,
                        left: position.x,
                        top: position.y,
                        position: 'fixed',
                        userSelect: isResizing.current ? 'none' : 'auto',
                    }}
                    className="bg-white border rounded-xl shadow-xl flex flex-col"
                >


                    {/* 顶部标题栏 */}
                    <div
                        className="flex justify-between items-center p-2 border-b cursor-move"
                        onMouseDown={onDragStart}
                    >
                        <span className="cursor-pointer font-semibold">AI助手</span>
                        <button onClick={() => setOpen(false)} className="cursor-pointer text-gray-500 hover:text-black">×</button>
                    </div>

                    {/* 内容区域 */}
                    <div className="flex-1 overflow-y-auto p-2 text-sm space-y-2">
                        {messages.map((msg, idx) => (
                            <div key={idx} className="whitespace-pre-wrap">
                                {msg.role === 'user' ? (
                                    <div>🧑‍💻: {msg.content}</div>
                                ) : (
                                    <div className="flex items-start gap-2">
                                        <div className="text-lg">🤖</div>
                                        <div className="markdown" dangerouslySetInnerHTML={{ __html: msg.content }} />
                                    </div>
                                )}
                            </div>
                        ))}
                        {/* {loading && <div className="text-gray-400 text-sm">🤖 正在输入中...</div>} */}
                    </div>

                    {/* 输入框 */}
                    <div className="p-2 border-t flex gap-1">
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && sendMessage()}
                            className="flex-1 px-2 py-1 border rounded"
                            placeholder="请输入问题..."
                        />
                        <button onClick={sendMessage} className="cursor-pointer px-3 bg-blue-600 text-white rounded">发送</button>
                    </div>

                    {/* 拖动区域：四边和四角 */}
                    {['top', 'right', 'bottom', 'left',
                        'top-left', 'top-right', 'bottom-left', 'bottom-right'].map(direction => (
                            <div
                                key={direction}
                                className={`absolute ${getResizeHandleClass(direction)}`}
                            />
                        ))}
                </div>
            )}
        </div>
    )
}

function getResizeHandleClass(direction: string) {
    const base = 'z-50'
    switch (direction) {
        case 'top': return `${base} top-0 left-0 w-full h-1 cursor-n-resize`
        case 'bottom': return `${base} bottom-0 left-0 w-full h-1 cursor-s-resize`
        case 'left': return `${base} top-0 left-0 h-full w-1 cursor-w-resize`
        case 'right': return `${base} top-0 right-0 h-full w-1 cursor-e-resize`
        case 'top-left': return `${base} top-0 left-0 w-3 h-3 cursor-nw-resize`
        case 'top-right': return `${base} top-0 right-0 w-3 h-3 cursor-ne-resize`
        case 'bottom-left': return `${base} bottom-0 left-0 w-3 h-3 cursor-sw-resize`
        case 'bottom-right': return `${base} bottom-0 right-0 w-3 h-3 cursor-se-resize`
        default: return ''
    }
}
