import { postForm, get, putForm, baseURL } from './request'

export const cartAdd = (uid: string, pid: string, quantity: string) =>
    postForm(`${baseURL}/api/v1/cart/add`, { uid, pid, quantity })

export const cartUpdate = (uid: string, pid: string, quantity: string) =>
    putForm(`${baseURL}/api/v1/cart/update`, { uid, pid, quantity })

export const cartDelete = (uid: string, pid: string) =>
    postForm(`${baseURL}/api/v1/cart/delete`, { uid, pid })

export const cartList = (uid: string) =>
    get(`${baseURL}/api/v1/cart/list/${uid}`)