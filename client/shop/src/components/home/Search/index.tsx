"use client";

import { useState, useEffect, useRef } from 'react';
import { search } from '@/lib/api/search';

export default function Search() {
    const [keyword, setKeyword] = useState('');
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const debounceTimer = useRef<NodeJS.Timeout | null>(null);
    const abortController = useRef<AbortController | null>(null);

    const handleSearch = async () => {
        if (keyword.trim()) {
            console.log("Searching for:", keyword);  // 调试日志，查看是否有触发
            try {
                // 调用后端接口获取搜索结果
                const response = await search(keyword);
                console.log("Search results:", response);
                setSuggestions(response?.data?.map((item: { name: string }) => item.name) || []);
            } catch (error) {
                console.error("Error fetching search results:", error);
            }
        }
    };

    useEffect(() => {
        return () => {
            if (debounceTimer.current) {
                clearTimeout(debounceTimer.current);
            }
            if (abortController.current) {
                abortController.current.abort();
            }
        };
    }, []);

    const fetchSuggestions = async (value: string) => {
        if (abortController.current) {
            abortController.current.abort();
        }
        abortController.current = new AbortController();

        try {
            setIsLoading(true);
            const response = await search(value, { signal: abortController.current.signal });
            setSuggestions(response?.data.map((item: { name: string }) => item.name) || []);
        } catch (error) {
            if (error instanceof Error && error.name !== 'AbortError') {
                console.error("Error fetching search suggestions:", error);
                setSuggestions([]);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setKeyword(value);

        if (debounceTimer.current) {
            clearTimeout(debounceTimer.current);
        }

        if (value.trim()) {
            debounceTimer.current = setTimeout(() => {
                fetchSuggestions(value);
            }, 300);
        } else {
            setSuggestions([]);
        }
    };

    return (
        <div className="flex items-center p-4 relative">
            <input
                type="text"
                className="border p-2 rounded-l w-full"
                placeholder="搜索商品..."
                value={keyword}
                onChange={handleInputChange}
            />
            <button
                onClick={handleSearch}
                className="cursor-pointer bg-blue-500 text-white p-2 rounded-r flex items-center justify-center min-w-[80px]"
                disabled={isLoading}
            >
                {isLoading ? (
                    <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        搜索中...
                    </>
                ) : (
                    "搜索"
                )}
            </button>

            {/* Suggestions dropdown */}
            {suggestions.length > 0 && (
                <ul className="absolute left-0 right-0 mt-2 bg-white border border-gray-300 rounded-md max-h-60 overflow-auto z-10">
                    {suggestions.map((suggestion, index) => (
                        <li
                            key={index}
                            className="p-2 hover:bg-gray-200 cursor-pointer"
                            onClick={() => {
                                setKeyword(suggestion);
                                setSuggestions([]); // 清空建议列表
                            }}
                        >
                            {suggestion}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
