"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { IconType } from "react-icons";
import { FaBox, FaUser, FaHome } from "react-icons/fa";

type NavItem = {
    label: string;
    href: string;
    icon: IconType;
    exact?: boolean; // Add exact property
};

const navItems: NavItem[] = [
    {
        label: "仪表盘",
        href: "/admin",
        icon: FaHome,
        exact: true // Requires exact match
    },
    {
        label: "商品管理",
        href: "/admin/products",
        icon: FaBox,
        exact: false
    },
    {
        label: "用户管理",
        href: "/admin/users",
        icon: FaUser,
        exact: false
    },
];

export default function AdminSidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-60 h-screen bg-gray-800 text-white flex flex-col">
            <div className="p-4 text-lg font-bold border-b border-gray-700">
                管理后台
            </div>
            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => {
                    // Use exact match for dashboard, prefix match for others
                    const isActive = item.exact
                        ? pathname === item.href
                        : pathname.startsWith(item.href);
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-2 p-2 rounded-md transition ${isActive
                                ? "bg-gray-700 font-semibold"
                                : "hover:bg-gray-700 text-gray-300"
                                }`}
                        >
                            <item.icon className="text-lg" />
                            {item.label}
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
}
