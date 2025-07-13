// app/admin/layout.tsx

import AdminSidebar from "@/components/admin/SideBar";
import { ReactNode } from "react";

export default function AdminLayout({ children }: { children: ReactNode }) {
    return (
        <div className="flex h-screen">
            <AdminSidebar />
            <main className="flex-1 overflow-auto bg-gray-50 p-6">
                {children}
            </main>
        </div>
    );
}
