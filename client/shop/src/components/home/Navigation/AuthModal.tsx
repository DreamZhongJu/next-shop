import { login, signup } from '@/lib/api/auth'
import { postForm } from '@/lib/api/request'
import { useState } from 'react'


export default function AuthModal({ type, onClose }: { type: 'login' | 'signup', onClose: () => void }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')

    const handleSubmit = async () => {
        try {
            const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080'}/api/v1/${type}`
            console.log(`Sending ${type} request to:`, apiUrl, 'with data:', { username, password })

            const res = type === 'login'
                ? await login(username, password)
                : await signup(username, password)

            console.log('Response:', res)

            if (res.Code === 0 && res.data) {
                const name = res.data.Username
                localStorage.setItem('user', JSON.stringify(res.data))
                alert(`欢迎你，${name}`)
                onClose()
            } else {
                alert(`失败：${res.msg || '操作失败，请重试'}`)
            }
        } catch (err) {
            console.error(err)
            alert('请求失败，请检查网络或后端接口')
        }
    }


    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[rgba(0,0,0,0.05)]">
            <div className="bg-white rounded-xl shadow-xl w-[320px] p-6 relative">
                <h2 className="text-xl font-semibold mb-4 text-center">{type === 'login' ? '登录' : '注册'}</h2>
                <input
                    type="text"
                    placeholder="用户名"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-3 py-2 border rounded mb-3"
                />
                <input
                    type="password"
                    placeholder="密码"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3 py-2 border rounded mb-4"
                />
                <button onClick={handleSubmit} className="cursor-pointer w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                    {type === 'login' ? '登录' : '注册'}
                </button>
                <button onClick={onClose} className="cursor-pointer absolute top-2 right-3 text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
        </div>
    )
}
