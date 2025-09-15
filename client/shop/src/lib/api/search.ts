import { postForm, get, baseURL } from './request'

interface SearchOptions {
    signal?: AbortSignal
}

export const search = (name: string, options?: SearchOptions) =>
    postForm(`${baseURL}/api/v1/search`, { name }, options)

export const searchAll = (page: number = 1, pageSize: number = 10) =>
    get(`${baseURL}/api/v1/search/all?page=${page}&pageSize=${pageSize}`)

export const getProductDetail = (id: number) =>
    get(`${baseURL}/api/v1/search/detail/${id}`)

export const getSuggestions = (query: string, n: number = 8, options?: SearchOptions) =>
    get(`${baseURL}/api/v1/suggest?q=${encodeURIComponent(query)}&n=${n}`, options)
