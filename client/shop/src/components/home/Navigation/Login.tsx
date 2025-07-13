import { useEffect, useState } from 'react'
import Link from 'next/link'
import AuthModal from './AuthModal'
import Button from '@/components/common/Button'

export default function Login() {
    const [modalType, setModalType] = useState<'login' | 'signup' | null>(null)
    const [user, setUser] = useState<{ Username: string; Role?: string } | null>(null)

    useEffect(() => {
        const storedUser = localStorage.getItem('user')
        if (storedUser) {
            const userData = JSON.parse(storedUser)
            console.log('Loaded user from localStorage:', userData)
            setUser(userData)
        }
    }, [])

    console.log('Current user state:', user)

    const handleLogout = () => {
        localStorage.removeItem('user') // 清除本地存储
        setUser(null)                   // 重置前端状态
        alert('已成功登出')             // 提示
    }
    return (
        <>

            {user ? (
                <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600">你好，{user.Username}</span>
                    {user.Role === 'admin' && (
                        <Link href="/admin" className="text-sm text-gray-600 hover:text-blue-600">
                            后台管理
                        </Link>
                    )}
                    <Button
                        onClick={handleLogout}
                        className="text-sm text-red-600 hover:text-red-800 cursor-pointer"
                    >
                        登出
                    </Button>
                </div>
            ) : (
                <div className="space-x-4 md:flex">
                    <Button
                        onClick={() => setModalType('login')}
                        className="cursor-pointer text-sm text-gray-600 hover:text-blue-600 hover:font-semibold"
                    >
                        登录
                    </Button>
                    <Button
                        onClick={() => setModalType('signup')}
                        className="cursor-pointer text-sm text-gray-600 hover:text-blue-600 hover:font-semibold"
                    >
                        注册
                    </Button>
                </div>
            )}
            {modalType && (
                <AuthModal
                    type={modalType}
                    onClose={() => {
                        setModalType(null)

                        // 尝试登录/注册成功后更新状态
                        const storedUser = localStorage.getItem('user')
                        if (storedUser) {
                            setUser(JSON.parse(storedUser))
                        }
                    }}
                />
            )}
        </>
    )


}
