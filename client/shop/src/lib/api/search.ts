import { postForm, get, baseURL } from './request'

interface SearchOptions {
    signal?: AbortSignal
}

export const search = (name: string, options?: SearchOptions) =>
    postForm(`${baseURL}/api/v1/search`, { name }, options)

export const searchAll = () =>
    get(`${baseURL}/api/v1/search/all`)

export const getProductDetail = (id: number) =>
    get(`${baseURL}/api/v1/search/detail/${id}`)
