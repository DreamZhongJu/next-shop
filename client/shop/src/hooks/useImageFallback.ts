"use client";
import { useState } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";

const useImageFallback = (initialUrl: string, fallbackUrl: string = "/default-product.png") => {
    const fullInitialUrl = initialUrl?.startsWith("http") ? initialUrl : BASE_URL + initialUrl;
    // console.log(fullInitialUrl)
    const [currentImage, setCurrentImage] = useState(fullInitialUrl || fallbackUrl);

    const handleError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
        console.error("图片加载失败:", e);
        console.log("切换到默认图片:", fallbackUrl);
        setCurrentImage(fallbackUrl);
    };

    return {
        currentImage,
        handleError
    };
};

export default useImageFallback;
