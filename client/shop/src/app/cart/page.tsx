'use client'

import { useEffect, useState } from 'react'
import { cartList, cartDelete } from '@/lib/api/cart'
import { getProductDetail } from '@/lib/api/search'

interface CartItem {
    id: number
    user_id: string
    product_id: string
    quantity: number
    updated_at: string
    name: string
    image_url: string
    image_fallback_url: string
    price: number
}

export default function CartPage() {
    const [cart, setCart] = useState<CartItem[]>([])
    const [selectedItems, setSelectedItems] = useState<number[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchCartWithDetails = async () => {
            setLoading(true)
            const userStr = localStorage.getItem('user')
            if (!userStr) return

            const user = JSON.parse(userStr)
            const uid = user.ID || user.UserID || user.id
            if (!uid) return

            const res = await cartList(uid)
            if (res?.data) {
                const detailedCart = await Promise.all(
                    res.data.map(async (item: any) => {
                        const detail = await getProductDetail(Number(item.product_id))
                        return {
                            ...item,
                            name: detail?.data?.Name,
                            image_url: detail?.data?.ImageURL,
                            image_fallback_url: detail?.data?.ImageURL,
                            price: detail?.data?.Price,
                        }
                    })
                )
                setCart(detailedCart)
                // setSelectedItems(detailedCart.map(i => i.id)) // 默认全选
            }
            setLoading(false)
        }

        fetchCartWithDetails()
    }, [])

    const handleToggleSelect = (id: number) => {
        setSelectedItems(prev =>
            prev.includes(id) ? prev.filter(itemId => itemId !== id) : [...prev, id]
        )
    }

    const handleSelectAll = () => {
        if (selectedItems.length === cart.length) {
            setSelectedItems([])
        } else {
            setSelectedItems(cart.map(i => i.id))
        }
    }

    const handleDeleteSelected = async () => {
        const userStr = localStorage.getItem('user')
        const user = JSON.parse(userStr || '{}')
        const uid = user.ID || user.UserID || user.id

        for (const id of selectedItems) {
            const item = cart.find(i => i.id === id)
            if (item) {
                await cartDelete(uid, item.product_id)
            }
        }

        setCart(prev => prev.filter(item => !selectedItems.includes(item.id)))
        setSelectedItems([])
        alert('删除成功')
    }

    const totalPrice = cart
        .filter(item => selectedItems.includes(item.id))
        .reduce((sum, item) => sum + (item.price || 0) * (item.quantity || 0), 0)

    if (loading) return <div>加载中...</div>

    return (
        <div className="container mx-auto p-4">
            <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={selectedItems.length === cart.length}
                        onChange={handleSelectAll}
                    />
                    <span>全选</span>
                    <button onClick={handleDeleteSelected} className="ml-4 text-red-600">
                        删除
                    </button>
                </div>
                <div>已选 {selectedItems.length} 件</div>
            </div>

            {cart.map(item => (
                <div key={item.id} className="flex items-center gap-4 border-b pb-2">
                    <input
                        type="checkbox"
                        checked={selectedItems.includes(item.id)}
                        onChange={() => handleToggleSelect(item.id)}
                    />
                    <img
                        src={item.image_fallback_url}
                        alt={item.name}
                        className="w-24 h-24 object-cover rounded"
                        onError={e =>
                            (e.currentTarget.src = '/default-product.png')
                        }
                    />
                    <div className="flex-1">
                        <h2 className="text-lg font-semibold">{item.name}</h2>
                        <p>单价：¥{item.price.toFixed(2)}</p>
                        <p>数量：{item.quantity}</p>
                        <p>小计：¥{(item.price * item.quantity).toFixed(2)}</p>
                    </div>
                </div>
            ))}

            <div className="text-right font-bold text-xl mt-4">
                总价：¥{totalPrice.toFixed(2)}
            </div>
        </div>
    )
}
