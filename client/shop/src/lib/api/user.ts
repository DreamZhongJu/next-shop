import { baseURL, get } from "./request";

export const getUserCount = () =>
    get(`${baseURL}/api/v1/user/count/`)