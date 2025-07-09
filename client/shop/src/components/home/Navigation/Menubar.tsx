'use client'

import Link from 'next/link'

import AuthModal from './AuthModal'
import Login from './Login'

export default function Menubar() {

    return (
        <>
            <nav className="w-full bg-white shadow-md px-6 py-4 flex justify-between items-center">
                <div className="text-xl font-bold text-gray-800">
                    <Link href="/">NextShop</Link>
                </div>

                <div className="space-x-6 hidden md:flex">
                    <Link href="/products" className="text-gray-700 hover:text-blue-600 cursor-pointer">商品</Link>
                </div>
                <Login />
            </nav>

        </>
    )
}
