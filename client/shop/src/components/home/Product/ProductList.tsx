"use client";

import React, { useState, useEffect } from 'react';
import ProductCard from './ProductCard';
import { searchAll } from '@/lib/api/search'; // 引入获取商品数据的函数

interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    image_url: string;
    stock: number;
}

const ProductList: React.FC = () => {
    const [productList, setProductList] = useState<Product[]>([]);  // 存储商品数据
    const [loading, setLoading] = useState<boolean>(true);  // 加载状态
    const [error, setError] = useState<string | null>(null);  // 错误信息

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await searchAll();  // 获取所有商品数据
                console.log(data);
                if (Array.isArray(data.data)) {
                    setProductList(data.data);  // 将商品数据存储到状态中
                } else {
                    setProductList([]);  // 如果返回的不是数组，设置为空数组
                    setError("返回的数据格式不正确");
                }
            } catch (error) {
                console.error('Error fetching products:', error);
                setError("加载商品数据失败");
            } finally {
                setLoading(false);  // 设置加载完成
            }
        };

        fetchData();
    }, []);  // 组件加载时调用一次 fetchData

    // 如果正在加载，显示加载提示
    if (loading) {
        return <div>加载中...</div>;
    }

    // 如果发生错误，显示错误提示
    if (error) {
        return <div>{error}</div>;
    }

    return (
        <div className="grid grid-cols-6 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {productList.length > 0 ? (
                productList.map((product) => (
                    <ProductCard key={product.id} product={product} />
                ))
            ) : (
                <div>没有商品可展示</div>  // 如果没有商品，显示提示
            )}
        </div>
    );
};

export default ProductList;
