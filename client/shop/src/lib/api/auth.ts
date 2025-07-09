import { postForm } from './request'

const baseURL = 'http://localhost:8080'

export const login = (username: string, password: string) =>
    postForm(`${baseURL}/api/v1/login`, { username, password })

export const signup = (username: string, password: string) =>
    postForm(`${baseURL}/api/v1/sign`, { username, password })
