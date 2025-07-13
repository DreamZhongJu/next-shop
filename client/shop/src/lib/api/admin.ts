import { baseURL, get, put, del } from "./request";

export interface User {
    UserID: number;
    Username: string;
    Role: string;
    CreatedAt: string;
}

export interface UserListResponse {
    users: User[];
    totalPages: number;
}

export async function getUsers(page: number, pageSize: number): Promise<UserListResponse> {
    const response = await get(`${baseURL}/api/v1/admin/users?page=${page}&pageSize=${pageSize}`);
    return response.data;
}

export async function deleteUser(id: number) {
    return del(`${baseURL}/api/v1/admin/users/${id}`);
}

export async function updateUser(id: number, data: { role: string }) {
    return put(`${baseURL}/api/v1/admin/users/${id}`, data);
}
