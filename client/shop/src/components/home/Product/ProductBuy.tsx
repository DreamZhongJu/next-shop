'use client'

import { useState } from 'react'
import { AiOutlineStar, AiFillStar } from 'react-icons/ai'
import { cartAdd } from '@/lib/api/cart'
import CartSuccessModal from '@/components/cart/CartSuccessModal'

export default function ProductBuy({ product }: { product: any }) {
    const [quantity, setQuantity] = useState(1)
    const [isFavorite, setIsFavorite] = useState(false)
    const [showSuccess, setShowSuccess] = useState(false)

    const getUid = () => {
        const userStr = localStorage.getItem('user')
        console.log(userStr)
        if (!userStr) return null
        const user = JSON.parse(userStr)
        return user.ID || user.UserID || user.id
    }

    const handleAddToCart = async () => {
        const uid = getUid()
        if (!uid) {
            alert('请先登录')
            return
        }
        try {
            const res = await cartAdd(uid, product.ID, String(quantity))

            if (res?.Code === 0) {
                setShowSuccess(true)
            } else {
                alert(res?.msg || '加入购物车失败')
            }
        } catch (error) {
            console.error('加入购物车失败：', error)
            alert('网络错误，请稍后重试')
        }
    }

    const handleBuyNow = () => {
        console.log('立即购买', { productId: product.ID, quantity })
        alert(`准备购买：${product.Name} × ${quantity}`)
    }

    const handleToggleFavorite = () => {
        setIsFavorite(!isFavorite)
        alert(isFavorite ? '已取消收藏' : '已收藏')
    }

    return (
        <>
            <div className="flex flex-col gap-4 p-4 w-full">
                <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-500">数量</span>
                    <div className="flex items-center border rounded overflow-hidden">
                        <button
                            onClick={() => setQuantity(Math.max(1, quantity - 1))}
                            className="cursor-pointer px-3 py-1 text-gray-600 hover:bg-gray-100"
                        >-</button>
                        <input
                            type="number"
                            value={quantity}
                            onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                            className="w-12 text-center border-l border-r outline-none"
                            min={1}
                        />
                        <button
                            onClick={() => setQuantity(quantity + 1)}
                            className="cursor-pointer px-3 py-1 text-gray-600 hover:bg-gray-100"
                        >+</button>
                    </div>
                    <span className="text-sm text-gray-500">有货</span>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex flex-1">
                        <button
                            onClick={handleAddToCart}
                            className="cursor-pointer flex-1 py-3 text-white font-semibold rounded-l-full"
                            style={{ background: 'linear-gradient(to right, #facc15, #f97316)' }}
                        >加入购物车</button>
                        <button
                            onClick={handleBuyNow}
                            className="cursor-pointer flex-1 py-3 text-white font-semibold rounded-r-full"
                            style={{ background: 'linear-gradient(to right, #f97316, #ef4444)' }}
                        >立即购买</button>
                    </div>
                    <button
                        onClick={handleToggleFavorite}
                        className="cursor-pointer flex flex-col items-center justify-center text-gray-500"
                    >
                        {isFavorite ? <AiFillStar className="text-xl text-yellow-400" /> : <AiOutlineStar className="text-xl" />}
                        <span className="text-xs">收藏</span>
                    </button>
                </div>
            </div>

            {showSuccess && <CartSuccessModal onClose={() => setShowSuccess(false)} />}
        </>
    )
}
