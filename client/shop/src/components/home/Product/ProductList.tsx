"use client";

import React, { useState, useEffect } from 'react';
import ProductCard from './ProductCard';
import { searchAll } from '@/lib/api/search';
import Button from '@/components/common/Button';

interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    image_url: string;
    stock: number;
}

interface Pagination {
    currentPage: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
}

const ProductList: React.FC = () => {
    const [productList, setProductList] = useState<Product[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [pagination, setPagination] = useState<Pagination>({
        currentPage: 1,
        pageSize: 10,
        totalItems: 0,
        totalPages: 1
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const res = await searchAll(pagination.currentPage, pagination.pageSize);
                const productsData = res?.data?.data || [];
                const paginationData = res?.data?.pagination;

                setProductList(productsData);
                if (paginationData) {
                    setPagination({
                        currentPage: paginationData.currentPage,
                        pageSize: paginationData.pageSize,
                        totalItems: paginationData.totalItems,
                        totalPages: paginationData.totalPages
                    });
                }
            } catch (error) {
                console.error('Error fetching products:', error);
                setError("加载商品数据失败");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [pagination.currentPage, pagination.pageSize]);

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= pagination.totalPages) {
            setPagination(prev => ({ ...prev, currentPage: newPage }));
        }
    };

    // 如果正在加载，显示加载提示
    if (loading) {
        return <div>加载中...</div>;
    }

    // 如果发生错误，显示错误提示
    if (error) {
        return <div>{error}</div>;
    }

    return (
        <>
            <div className="grid grid-cols-5 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {productList.length > 0 ? (
                    productList.map((product) => (
                        <ProductCard key={product.id} product={product} />
                    ))
                ) : (
                    <div>没有商品可展示</div>
                )}
            </div>

            {/* Pagination Controls */}
            {pagination.totalPages > 1 && (
                <div className="flex justify-center items-center mt-8">
                    <div className="flex space-x-2">
                        <Button
                            variant="outline"
                            onClick={() => handlePageChange(pagination.currentPage - 1)}
                            disabled={pagination.currentPage === 1}
                            className='cursor-pointer '
                        >
                            上一页
                        </Button>
                        <div className="px-4 py-2 text-sm text-gray-600">
                            第 {pagination.currentPage} 页，共 {pagination.totalPages} 页
                        </div>
                        <Button
                            variant="outline"
                            onClick={() => handlePageChange(pagination.currentPage + 1)}
                            disabled={pagination.currentPage === pagination.totalPages}
                            className='cursor-pointer '
                        >
                            下一页
                        </Button>
                    </div>
                </div>
            )}
        </>
    );
};

export default ProductList;
