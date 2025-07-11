import { postForm, baseURL } from './request'



export const login = (username: string, password: string) =>
    postForm(`${baseURL}/api/v1/login`, { username, password })

export const signup = (username: string, password: string) =>
    postForm(`${baseURL}/api/v1/sign`, { username, password })
