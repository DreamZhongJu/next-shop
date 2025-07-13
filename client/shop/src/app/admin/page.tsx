import AdminDashboard from "@/components/admin/Dashboard";
import AdminSidebar from "@/components/admin/SideBar";

export default function AdminPage() {
    return (
        <div className="flex h-screen">
            <main className="flex-1 overflow-auto p-6 bg-gray-50">
                <AdminDashboard />
            </main>
        </div>
    );
}
