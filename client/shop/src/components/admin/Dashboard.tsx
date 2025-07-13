"use client";

import { useEffect, useState } from "react";
import { getDashboardData } from "@/lib/api/dashboard";

// Create a new file for dashboard API in lib/api/dashboard.ts
export default function AdminDashboard() {
    const [metrics, setMetrics] = useState({
        productCount: 0,
        totalStock: 0,
        userCount: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const data = await getDashboardData();
                // console.log(data)
                setMetrics({
                    productCount: data.productCount,
                    totalStock: data.totalStock,
                    userCount: data.userCount
                });
            } catch (e) {
                console.error("获取仪表盘数据失败", e);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="p-6 bg-white rounded-lg shadow">
                        <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
                        <div className="h-12 bg-gray-200 rounded w-1/2"></div>
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <DashboardCard
                title="商品总数"
                value={metrics.productCount}
                icon="🛒"
                color="bg-blue-100"
            />
            <DashboardCard
                title="总库存"
                value={metrics.totalStock}
                icon="📦"
                color="bg-green-100"
            />
            <DashboardCard
                title="用户总数"
                value={metrics.userCount}
                icon="👥"
                color="bg-purple-100"
            />
        </div>
    );
}

function DashboardCard({
    title,
    value,
    icon = "",
    color = "bg-gray-100"
}: {
    title: string;
    value: number;
    icon?: string;
    color?: string;
}) {
    return (
        <div className={`p-6 ${color} rounded-lg shadow-lg flex flex-col items-center transition-all hover:scale-105`}>
            <div className="text-4xl mb-2">{icon}</div>
            <div className="text-gray-600 text-lg">{title}</div>
            <div className="text-4xl font-bold mt-2 text-gray-800">{value.toLocaleString()}</div>
        </div>
    );
}
