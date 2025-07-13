"use client";

import { useState, useEffect } from "react";
import { User, getUsers, deleteUser, updateUser } from "@/lib/api/admin";
import { Pagination } from "@/components/admin/Pagination";

export default function UserManagement() {
    const [users, setUsers] = useState<User[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [loading, setLoading] = useState(true);
    const [editingUser, setEditingUser] = useState<User | null>(null);
    const [editForm, setEditForm] = useState({ role: "" });
    const pageSize = 10;

    useEffect(() => {
        fetchUsers();
    }, [currentPage]);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const data = await getUsers(currentPage, pageSize);
            setUsers(data.users);
            setTotalPages(data.totalPages);
        } catch (error) {
            console.error("Failed to fetch users:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (confirm("确定要删除这个用户吗？")) {
            try {
                await deleteUser(id);
                fetchUsers();
            } catch (error) {
                console.error("删除用户失败:", error);
            }
        }
    };

    const handleEdit = (user: User) => {
        setEditingUser(user);
        setEditForm({ role: user.Role });
    };

    const handleUpdate = async () => {
        if (editingUser) {
            try {
                await updateUser(editingUser.UserID, { role: editForm.role });
                setEditingUser(null);
                fetchUsers();
            } catch (error) {
                console.error("更新用户失败:", error);
            }
        }
    };

    return (
        <div className="container mx-auto p-6">
            <h1 className="text-2xl font-semibold mb-6">用户管理</h1>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            ) : (
                <>
                    <div className="bg-white shadow-md rounded-lg overflow-hidden">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {users.map((user) => (
                                    <tr key={user.UserID}>
                                        <td className="px-6 py-4 whitespace-nowrap">{user.UserID}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">{user.Username}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">{user.Role}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {new Date(user.CreatedAt).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <button
                                                onClick={() => handleEdit(user)}
                                                className="text-indigo-600 hover:text-indigo-900 mr-4"
                                            >
                                                编辑
                                            </button>
                                            <button
                                                onClick={() => handleDelete(user.UserID)}
                                                className="text-red-600 hover:text-red-900"
                                            >
                                                删除
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setCurrentPage}
                    />
                </>
            )}

            {/* Edit Modal */}
            {editingUser && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
                        <h2 className="text-xl font-semibold mb-4">编辑用户</h2>
                        <div className="mb-4">
                            <label className="block text-gray-700 mb-2">用户名</label>
                            <input
                                type="text"
                                value={editingUser.Username}
                                disabled
                                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            />
                        </div>
                        <div className="mb-4">
                            <label className="block text-gray-700 mb-2">角色</label>
                            <select
                                value={editForm.role}
                                onChange={(e) => setEditForm({ role: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            >
                                <option value="admin">管理员</option>
                                <option value="common">普通用户</option>
                            </select>
                        </div>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={() => setEditingUser(null)}
                                className="px-4 py-2 text-gray-600 hover:text-gray-800"
                            >
                                取消
                            </button>
                            <button
                                onClick={handleUpdate}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                            >
                                保存
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
