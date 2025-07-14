// app/admin/products/page.tsx

"use client";

import { useEffect, useState } from "react";
import Button from "@/components/common/Button";
import { searchAll } from "@/lib/api/search";
import ProductModal from "@/components/admin/ProductModal";

interface Product {
    id: number;
    name: string;
    price: number;
    stock: number;
    category: string;
}

interface Pagination {
    currentPage: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
}

export default function AdminProductPage() {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [pagination, setPagination] = useState<Pagination>({
        currentPage: 1,
        pageSize: 10,
        totalItems: 0,
        totalPages: 1
    });
    const [modalOpen, setModalOpen] = useState(false);
    const [editingProductId, setEditingProductId] = useState<number | null>(null);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                setLoading(true);
                const res = await searchAll(pagination.currentPage, pagination.pageSize);
                // Backend returns { data: products, pagination: metadata }
                const productsData = res?.data?.data || [];
                const paginationData = res?.data?.pagination;

                setProducts(productsData);
                if (paginationData) {
                    setPagination({
                        currentPage: paginationData.currentPage,
                        pageSize: paginationData.pageSize,
                        totalItems: paginationData.totalItems,
                        totalPages: paginationData.totalPages
                    });
                }
            } catch (e) {
                console.error("获取商品失败", e);
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, [pagination.currentPage, pagination.pageSize]);

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= pagination.totalPages) {
            setPagination(prev => ({ ...prev, currentPage: newPage }));
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-xl font-semibold">商品管理</h1>
                <Button
                    variant="primary"
                    onClick={() => {
                        setEditingProductId(null);
                        setModalOpen(true);
                    }}
                >
                    添加商品
                </Button>
            </div>

            {loading ? (
                <div>加载中...</div>
            ) : products.length === 0 ? (
                <div>暂无商品</div>
            ) : (
                <>
                    <table className="w-full border-collapse">
                        <thead>
                            <tr className="bg-gray-100">
                                <th className="p-2 border">ID</th>
                                <th className="p-2 border">名称</th>
                                <th className="p-2 border">价格</th>
                                <th className="p-2 border">库存</th>
                                <th className="p-2 border">分类</th>
                                <th className="p-2 border">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map((item) => (
                                <tr key={item.id}>
                                    <td className="p-2 border">{item.id}</td>
                                    <td className="p-2 border">{item.name}</td>
                                    <td className="p-2 border">¥{item.price}</td>
                                    <td className="p-2 border">{item.stock}</td>
                                    <td className="p-2 border">{item.category}</td>
                                    <td className="p-2 border">
                                        <Button
                                            variant="outline"
                                            className="mr-2 text-sm"
                                            onClick={() => {
                                                setEditingProductId(item.id);
                                                setModalOpen(true);
                                            }}
                                        >
                                            编辑
                                        </Button>
                                        <Button variant="text" className="text-sm text-red-500">
                                            删除
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {/* Pagination Controls */}
                    <div className="flex justify-between items-center mt-4">
                        <div className="text-sm text-gray-600">
                            显示第 {pagination.currentPage} 页，共 {pagination.totalPages} 页
                            ({pagination.totalItems} 条记录)
                        </div>
                        <div className="flex space-x-2">
                            <Button
                                variant="outline"
                                onClick={() => handlePageChange(pagination.currentPage - 1)}
                                disabled={pagination.currentPage === 1}
                                className="cursor-pointer "
                            >
                                上一页
                            </Button>
                            <Button
                                variant="outline"
                                onClick={() => handlePageChange(pagination.currentPage + 1)}
                                disabled={pagination.currentPage === pagination.totalPages}
                                className="cursor-pointer "
                            >
                                下一页
                            </Button>
                        </div>
                    </div>
                </>
            )}

            <ProductModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                productId={editingProductId || undefined}
                onSuccess={() => {
                    setPagination(prev => ({ ...prev, currentPage: 1 }));
                    setModalOpen(false);
                }}
            />
        </div>
    );
}
