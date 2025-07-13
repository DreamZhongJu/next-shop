import { baseURL, get } from './request';

export interface DashboardData {
    productCount: number;
    totalStock: number;
    userCount: number;
}

export async function getDashboardData(): Promise<DashboardData> {
    const response = await get(`${baseURL}/api/v1/admin/dashboard`);
    return response.data;
}
