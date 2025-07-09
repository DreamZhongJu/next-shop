// lib/api/request.ts

export async function postForm<T = any>(url: string, data: Record<string, string>): Promise<T> {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(data).toString(),
    })

    if (!res.ok) {
        let errorMsg = `HTTP error! status: ${res.status}`
        try {
            // 尝试解析错误响应中的JSON
            const errorBody = await res.json()
            if (errorBody.msg) {
                errorMsg = errorBody.msg
            } else if (errorBody.message) {
                errorMsg = errorBody.message
            }
        } catch (e) {
            // 如果无法解析JSON，使用默认错误信息
        }
        throw new Error(errorMsg)
    }

    return res.json()
}
