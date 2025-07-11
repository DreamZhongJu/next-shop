"use client";

import useImageFallback from '@/hooks/useImageFallback';
import ProductBuy from './ProductBuy';

export default function ProductView({ product }: { product: any }) {
    if (!product) return <div className="text-center text-gray-600 py-20">商品未找到</div>;

    const normalizedProduct = {
        ...product,
        image_url: product.Image_url || ''
    };

    const { currentImage, handleError } = useImageFallback(normalizedProduct.image_url);

    return (
        <div className="p-4">
            <div className="flex bg-white rounded-xl shadow-lg mx-auto max-w-7xl min-h-[600px] overflow-hidden">
                {/* 左侧 商品图片+信息区域 */}
                <div className="flex flex-col md:flex-row flex-[2] items-center justify-center bg-gray-50 p-8">
                    <img
                        src={currentImage}
                        onError={handleError}
                        alt={product.Name}
                        className="w-[400px] h-[400px] object-cover rounded-md shadow-md"
                    />
                    <div className="ml-8 max-w-md">
                        <h1 className="text-3xl font-bold mb-4">{product.Name}</h1>
                        <p className="text-gray-600 mb-4 leading-relaxed">{product.Description}</p>
                        <div className="text-xl font-bold text-primary-600">¥{product.Price}</div>
                        <div className="text-sm text-gray-500 mt-2">库存: {product.Stock}</div>
                    </div>
                </div>

                {/* 右侧 购买组件区域 */}
                <div className="flex-[1] p-6 bg-white flex flex-col justify-center">
                    <ProductBuy product={product} />
                </div>
            </div>
        </div>
    );
}