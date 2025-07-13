// lib/api/request.ts

interface RequestOptions {
    signal?: AbortSignal;
    [key: string]: any;
}

export const baseURL = 'http://localhost:8080'

export async function postForm<T = any>(
    url: string,
    data: Record<string, string>,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(data).toString(),
        ...options
    };

    const res = await fetch(url, fetchOptions);

    if (!res.ok) {
        let errorMsg = `HTTP error! status: ${res.status}`
        try {
            const errorBody = await res.json()
            if (errorBody.msg) {
                errorMsg = errorBody.msg
            } else if (errorBody.message) {
                errorMsg = errorBody.message
            }
        } catch (e) { }
        throw new Error(errorMsg)
    }

    return res.json()
}

export async function putForm<T = any>(
    url: string,
    data: Record<string, string>,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'PUT',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(data).toString(),
        ...options
    };

    const res = await fetch(url, fetchOptions);

    if (!res.ok) {
        let errorMsg = `HTTP error! status: ${res.status}`;
        try {
            const errorBody = await res.json();
            if (errorBody.msg) {
                errorMsg = errorBody.msg;
            } else if (errorBody.message) {
                errorMsg = errorBody.message;
            }
        } catch (e) { }
        throw new Error(errorMsg);
    }

    return res.json();
}

export async function get<T = any>(
    url: string,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'GET',
        ...options
    };

    const res = await fetch(url, fetchOptions);

    if (!res.ok) {
        let errorMsg = `HTTP error! status: ${res.status}`;
        try {
            const errorBody = await res.json();
            if (errorBody.msg) {
                errorMsg = errorBody.msg;
            } else if (errorBody.message) {
                errorMsg = errorBody.message;
            }
        } catch (e) { }
        throw new Error(errorMsg);
    }

    return res.json();
}

export async function put<T = any>(
    url: string,
    data: Record<string, any>,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        ...options
    };

    const res = await fetch(url, fetchOptions);

    if (!res.ok) {
        let errorMsg = `HTTP error! status: ${res.status}`;
        try {
            const errorBody = await res.json();
            if (errorBody.msg) {
                errorMsg = errorBody.msg;
            } else if (errorBody.message) {
                errorMsg = errorBody.message;
            }
        } catch (e) { }
        throw new Error(errorMsg);
    }

    return res.json();
}

export async function del<T = any>(
    url: string,
    options?: RequestOptions
): Promise<T> {
    const fetchOptions: RequestInit = {
        method: 'DELETE',
        ...options
    };

    const res = await fetch(url, fetchOptions);

    if (!res.ok) {
        let errorMsg = `HTTP error! status: ${res.status}`;
        try {
            const errorBody = await res.json();
            if (errorBody.msg) {
                errorMsg = errorBody.msg;
            } else if (errorBody.message) {
                errorMsg = errorBody.message;
            }
        } catch (e) { }
        throw new Error(errorMsg);
    }

    return res.json();
}
