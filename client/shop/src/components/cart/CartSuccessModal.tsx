'use client';

import Link from 'next/link';
import { useEffect } from 'react';

export default function CartSuccessModal({
    onClose,
}: {
    onClose: () => void;
}) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 2000); // 2 秒后自动关闭
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/20">
            <div className="bg-white rounded-xl shadow-xl p-6 w-[260px] text-center">
                <div className="flex flex-col items-center justify-center gap-2">
                    <div className="w-14 h-14 bg-green-500 rounded-full flex items-center justify-center text-white text-3xl">
                        ✓
                    </div>
                    <div className="text-lg font-bold">成功加入购物车</div>
                    <Link href="/cart">
                        <button
                            onClick={onClose}
                            className="cursor-pointer mt-4 w-full py-2 rounded bg-orange-500 text-white font-semibold hover:bg-orange-600"
                        >
                            去购物车
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    );
}
