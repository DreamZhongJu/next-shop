"use client"
import { useState } from 'react';

const useImageFallback = (initialUrl: string, fallbackUrl: string = '/default-product.png') => {
    const [currentImage, setCurrentImage] = useState(initialUrl || fallbackUrl);

    const handleError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
        console.error('图片加载失败:', e);
        console.log('切换到默认图片:', fallbackUrl);
        setCurrentImage(fallbackUrl);
    };

    return {
        currentImage,
        handleError
    };
};

export default useImageFallback;
