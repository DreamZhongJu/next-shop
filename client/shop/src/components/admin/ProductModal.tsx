"use client";

import { useState, useEffect, useRef } from "react";
import { createProduct, updateProduct, getProductById, uploadProductImage } from "@/lib/api/admin";
import Button from "@/components/common/Button";

interface ProductFormData {
    id?: number;
    name: string;
    price: number;
    stock: number;
    category: string;
    description: string;
    image?: string;
    imageFile?: File | null;
    imageUrl?: string;
}

interface ProductModalProps {
    isOpen: boolean;
    onClose: () => void;
    productId?: number;
    onSuccess: () => void;
}

export default function ProductModal({ isOpen, onClose, productId, onSuccess }: ProductModalProps) {
    const [formData, setFormData] = useState<ProductFormData>({
        name: "",
        price: 0,
        stock: 0,
        category: "",
        description: "",
        imageFile: null,
        imageUrl: ""
    });
    const [loading, setLoading] = useState(false);
    const [previewImage, setPreviewImage] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (productId) {
            const fetchProduct = async () => {
                try {
                    setLoading(true);
                    const product = await getProductById(productId);
                    if (product) {
                        setFormData(product);
                        if (product.image) {
                            setPreviewImage(product.image);
                        }
                    }
                } catch (e) {
                    console.error("获取商品详情失败", e);
                } finally {
                    setLoading(false);
                }
            };
            fetchProduct();
        } else {
            setFormData({
                name: "",
                price: 0,
                stock: 0,
                category: "",
                description: "",
                imageFile: null,
                imageUrl: ""
            });
            setPreviewImage(null);
        }
    }, [productId]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === "price" || name === "stock" ? Number(value) : value
        }));
    };

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setFormData(prev => ({ ...prev, imageFile: file, imageUrl: "" }));

            const reader = new FileReader();
            reader.onload = (event) => {
                setPreviewImage(event.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleImageUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const url = e.target.value;
        setFormData(prev => ({ ...prev, imageUrl: url, imageFile: null }));
        setPreviewImage(url);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setLoading(true);

            let imageUrl = formData.imageUrl;

            if (formData.imageFile) {
                console.log("准备上传图片...");
                const uploadedImage = await uploadProductImage(formData.imageFile);
                imageUrl = uploadedImage.url;
                console.log("图片上传成功：", imageUrl);
            }

            const productData = {
                name: formData.name,
                description: formData.description,
                price: formData.price,
                stock: formData.stock,
                category: formData.category,
                image_url: imageUrl || ""
            };

            console.log("准备提交商品信息：", productData);

            if (productId) {
                await updateProduct(productId, productData);
            } else {
                await createProduct(productData);
            }

            onSuccess();
            onClose();
        } catch (e) {
            console.error("保存商品失败", e);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold">
                        {productId ? "编辑商品" : "添加商品"}
                    </h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        &times;
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        {/* 图片上传区域 */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                商品图片
                            </label>
                            <div className="flex space-x-4">
                                <div className="flex-1">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        上传图片
                                    </label>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        accept="image/*"
                                        onChange={handleImageUpload}
                                        className="block w-full text-sm text-gray-500
                                        file:mr-4 file:py-2 file:px-4
                                        file:rounded-md file:border-0
                                        file:text-sm file:font-semibold
                                        file:bg-blue-50 file:text-blue-700
                                        hover:file:bg-blue-100"
                                    />
                                </div>
                                <div className="flex-1">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        或输入图片URL
                                    </label>
                                    <input
                                        type="text"
                                        name="imageUrl"
                                        value={formData.imageUrl}
                                        onChange={handleImageUrlChange}
                                        placeholder="https://example.com/image.jpg"
                                        className="w-full px-3 py-2 border rounded-md"
                                    />
                                </div>
                            </div>
                            {/* 图片预览 */}
                            {previewImage && (
                                <div className="mt-4">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        图片预览
                                    </label>
                                    <img
                                        src={previewImage}
                                        alt="商品预览"
                                        className="h-40 object-contain border rounded"
                                    />
                                </div>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                商品名称
                            </label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border rounded-md"
                                required
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    价格
                                </label>
                                <input
                                    type="number"
                                    name="price"
                                    value={formData.price}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border rounded-md"
                                    min="0"
                                    step="0.01"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    库存
                                </label>
                                <input
                                    type="number"
                                    name="stock"
                                    value={formData.stock}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border rounded-md"
                                    min="0"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                分类
                            </label>
                            <input
                                type="text"
                                name="category"
                                value={formData.category}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border rounded-md"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                描述
                            </label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border rounded-md"
                                rows={3}
                                required
                            />
                        </div>

                        <div className="flex justify-end space-x-2 pt-4">
                            <Button
                                variant="outline"
                                onClick={onClose}
                                disabled={loading}
                            >
                                取消
                            </Button>
                            <Button
                                type="submit"
                                variant="primary"
                                loading={loading}
                            >
                                {productId ? "保存" : "添加"}
                            </Button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}
