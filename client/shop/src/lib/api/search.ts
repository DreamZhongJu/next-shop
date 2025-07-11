import { postForm, get } from './request'

const baseURL = 'http://localhost:8080'

interface SearchOptions {
    signal?: AbortSignal
}

export const search = (name: string, options?: SearchOptions) =>
    postForm(`${baseURL}/api/v1/search`, { name }, options)

export const searchAll = () =>
    get(`${baseURL}/api/v1/search/all`)

export const getProductDetail = (id: number) =>
    get(`${baseURL}/api/v1/search/detail/${id}`)
