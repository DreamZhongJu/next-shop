// lib/api/request.ts

interface RequestOptions {
    signal?: AbortSignal;
    [key: string]: any;
}

export const baseURL = 'http://192.168.1.15:8080'

// 获取本地存储的 token
function getAuthToken() {
    if (typeof window === 'undefined') return '';
    try {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        return user?.token || '';
    } catch {
        return '';
    }
}

function handleAuthHeader(headers: HeadersInit = {}): HeadersInit {
    const token = getAuthToken();
    if (token) {
        return { ...headers, Authorization: `Bearer ${token}` };
    }
    return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
    if (res.status === 401) {
        localStorage.removeItem('user');
        alert('登录状态已过期，请重新登录');
        window.location.href = '/';
        throw new Error('Unauthorized');
    }

    if (!res.ok) {
        let errorMsg = `HTTP error! status: ${res.status}`;
        try {
            const errorBody = await res.json();
            errorMsg = errorBody.msg || errorBody.message || errorMsg;
        } catch { }
        throw new Error(errorMsg);
    }

    return res.json();
}

export async function postForm<T = any>(
    url: string,
    data: Record<string, string>,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'POST',
        headers: handleAuthHeader({ 'Content-Type': 'application/x-www-form-urlencoded' }),
        body: new URLSearchParams(data).toString(),
        ...options,
    };

    const res = await fetch(url, fetchOptions);
    return handleResponse(res);
}

export async function post<T = any>(
    url: string,
    data: Record<string, any>,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'POST',
        headers: handleAuthHeader({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(data),
        ...options,
    };

    const res = await fetch(url, fetchOptions);
    return handleResponse(res);
}

export async function putForm<T = any>(
    url: string,
    data: Record<string, string>,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'PUT',
        headers: handleAuthHeader({ 'Content-Type': 'application/x-www-form-urlencoded' }),
        body: new URLSearchParams(data).toString(),
        ...options,
    };

    const res = await fetch(url, fetchOptions);
    return handleResponse(res);
}

export async function get<T = any>(
    url: string,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'GET',
        headers: handleAuthHeader(),
        ...options,
    };

    const res = await fetch(url, fetchOptions);
    return handleResponse(res);
}

export async function put<T = any>(
    url: string,
    data: Record<string, any>,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'PUT',
        headers: handleAuthHeader({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(data),
        ...options,
    };

    const res = await fetch(url, fetchOptions);
    return handleResponse(res);
}

export async function del<T = any>(
    url: string,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'DELETE',
        headers: handleAuthHeader(),
        ...options,
    };

    const res = await fetch(url, fetchOptions);
    return handleResponse(res);
}
