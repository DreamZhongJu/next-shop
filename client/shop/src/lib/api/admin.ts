import { baseURL, get, put, del, post } from "./request";

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

export interface Product {
    id: number;
    name: string;
    price: number;
    stock: number;
    category: string;
    description: string;
    image?: string;
}

export async function createProduct(data: Omit<Product, 'id'>) {
    return post(`${baseURL}/api/v1/admin/products`, data);
}

export async function updateProduct(id: number, data: Partial<Product>) {
    return put(`${baseURL}/api/v1/admin/products/${id}`, data);
}

export async function getProductById(id: number): Promise<Product> {
    const response = await get(`${baseURL}/api/v1/admin/products/${id}`);
    return response.data;
}

export async function uploadProductImage(file: File): Promise<{ url: string }> {
    const userStr = localStorage.getItem('user');
    let token = '';

    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            token = user.token;
        } catch {
            throw new Error('用户信息解析失败，请重新登录');
        }
    }

    if (!token) {
        throw new Error('未登录，请先登录');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${baseURL}/api/v1/admin/upload`, {
        method: 'POST',
        body: formData,
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        console.error("上传失败，状态码：", response.status);
        throw new Error('图片上传失败');
    }

    const result = await response.json();

    if (result.error) {
        throw new Error(result.message || '上传接口返回错误');
    }

    if (!result.data?.url) {
        throw new Error('上传成功但返回格式异常');
    }

    return { url: result.data.url };
}
