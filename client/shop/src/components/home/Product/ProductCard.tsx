import React from 'react';
import Link from 'next/link';  // 使用 Next.js 的 Link 组件进行页面跳转

interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    image_url: string;
    stock: number;
}

const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
    return (
        <Link
            href='/product/[id]'
            as={'/product/1'}
            target="_blank"
            className="p-4 border border-gray-200 rounded-md shadow-md"
        >
            <img src={product.image_url} alt={product.name} className="w-full h-48 object-cover rounded-md" />
            <h3 className="mt-2 text-lg font-semibold">{product.name}</h3>
            <p className="text-gray-600">{product.description}</p>
            <div className="flex justify-between items-center mt-2">
                <span className="text-xl font-bold">¥{product.price}</span>
                <span className="text-sm text-gray-500">剩余库存: {product.stock}</span>
            </div>
        </Link>
    );
};

export default ProductCard;
