"use client";

import Link from 'next/link';
import { AiOutlineCustomerService, AiOutlineShoppingCart, AiOutlineQrcode, AiOutlineUser, AiOutlineEllipsis } from "react-icons/ai";
import { TbAppWindow } from "react-icons/tb";

export default function SidebarLayout() {
    return (
        <div className="flex">
            {/* 右侧悬浮侧边栏 */}
            <aside className="fixed top-1/4 right-0 z-50 bg-white rounded-l-xl shadow-xl flex flex-col items-center py-4 gap-4">
                {/* <button className="flex flex-col items-center justify-center text-xs text-gray-800">
                    <TbAppWindow className="text-2xl mb-1" />
                    桌面版
                </button> */}
                {/* <button className="flex flex-col items-center justify-center text-xs text-gray-800">
                    <AiOutlineCustomerService className="text-2xl mb-1" />
                    联系客服
                </button> */}
                <Link href="/cart" target="_blank">
                    <button className="cursor-pointer flex flex-col items-center justify-center text-xs text-gray-800">
                        <AiOutlineShoppingCart className="text-2xl mb-1" />
                        购物车
                    </button>
                </Link>
                {/* <button className="flex flex-col items-center justify-center text-xs text-gray-800">
                    <AiOutlineQrcode className="text-2xl mb-1" />
                    商品码
                </button> */}
                {/* <button className="flex flex-col items-center justify-center text-xs text-gray-800">
                    <AiOutlineUser className="text-2xl mb-1" />
                    用户调研
                </button> */}
                {/* <button className="flex flex-col items-center justify-center text-xs text-gray-800">
                    <AiOutlineEllipsis className="text-2xl mb-1" />
                    更多
                </button> */}
            </aside>
        </div>
    );
}
