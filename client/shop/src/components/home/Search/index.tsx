"use client";

import { useState, useEffect, useRef } from "react";
import { search, getSuggestions } from "@/lib/api/search";

export default function Search() {
    const [keyword, setKeyword] = useState("");
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [open, setOpen] = useState(false);             // ✅ 单独控制下拉是否展示
    const [results, setResults] = useState<any[]>([]);   // ✅ 搜索结果独立于联想

    const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const abortController = useRef<AbortController | null>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);

    useEffect(() => {
        return () => {
            if (debounceTimer.current) clearTimeout(debounceTimer.current);
            if (abortController.current) abortController.current.abort();
        };
    }, []);

    // ---- 搜索按钮：只更新搜索结果，不要动 suggestions ----
    const handleSearch = async () => {
        const q = keyword.trim();
        if (!q) return;
        try {
            setIsLoading(true);
            const response = await search(q);
            // 假设返回是 { data: [{ name: 'xxx' }, ...] }
            const payload = (response as any)?.data ?? response;
            const list = Array.isArray(payload) ? payload : payload?.data ?? [];
            setResults(list);
            setOpen(false); // 收起联想
        } catch (e) {
            console.error("Search error:", e);
        } finally {
            setIsLoading(false);
        }
    };

    // ---- 取联想：正确取 data.Suggestions，打开下拉 ----
    const fetchSuggestions = async (value: string) => {
        if (abortController.current) abortController.current.abort();
        abortController.current = new AbortController();

        try {
            setIsLoading(true);
            const resp = await getSuggestions(value, 8, { signal: abortController.current.signal });
            const payload = (resp && (resp as any).data) ? (resp as any).data : resp;
            const list: string[] = payload?.data?.Suggestions ?? payload?.Suggestions ?? [];
            setSuggestions(Array.isArray(list) ? list : []);
            setOpen((Array.isArray(list) && list.length > 0));
        } catch (error: any) {
            if (error?.name !== "AbortError") {
                console.error("Suggest error:", error);
                setSuggestions([]);
                setOpen(false);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setKeyword(value);

        if (debounceTimer.current) clearTimeout(debounceTimer.current);

        if (value.trim().length >= 2) {
            debounceTimer.current = setTimeout(() => fetchSuggestions(value.trim()), 300);
        } else {
            setSuggestions([]);
            setOpen(false);
        }
    };

    const handlePick = (s: string) => {
        setKeyword(s);
        setOpen(false);
        // 选中后你也可以直接触发搜索：
        // handleSearch();
    };

    return (
        <div className="p-4">
            <div className="flex items-center gap-0">
                {/* ✅ 给输入框外面包一层“定位容器”，只让下拉跟着输入框宽度走 */}
                <div className="relative w-full">
                    <input
                        ref={inputRef}
                        type="text"
                        className="border p-2 rounded-l w-full"
                        placeholder="搜索商品..."
                        value={keyword}
                        onChange={handleInputChange}
                        onFocus={() => suggestions.length > 0 && setOpen(true)}
                        onBlur={() => setTimeout(() => setOpen(false), 120)} // 给 li 的 onMouseDown->onClick 留时间
                    />

                    {/* ✅ 下拉定位在输入框下方：top-full + left-0 + right-0；提高 z-index */}
                    {open && suggestions.length > 0 && (
                        <ul className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md max-h-60 overflow-auto z-50 shadow-lg">
                            {suggestions.map((suggestion, index) => (
                                <li
                                    key={`${suggestion}-${index}`}
                                    className="px-3 py-2 hover:bg-gray-100 cursor-pointer select-none"
                                    onMouseDown={(e) => e.preventDefault()} // ✅ 防止 input 失焦导致列表瞬间消失
                                    onClick={() => handlePick(suggestion)}
                                    title={suggestion}
                                >
                                    {suggestion}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                <button
                    onMouseDown={(e) => e.preventDefault()} // 防止点击按钮时 input 先 blur
                    onClick={handleSearch}
                    className="cursor-pointer bg-blue-500 text-white p-2 rounded-r flex items-center justify-center min-w-[80px]"
                    disabled={isLoading}
                >
                    {isLoading ? "…" : "搜索"}
                </button>
            </div>

            {/* 可选：展示搜索结果，和联想互不干扰 */}
            {results.length > 0 && (
                <div className="mt-4 text-sm text-gray-600">
                    共 {results.length} 条结果
                </div>
            )}
        </div>
    );
}
