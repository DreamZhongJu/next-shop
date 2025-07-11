// client/shop/src/app/product/[id]/page.tsx
import { getProductDetail } from '@/lib/api/search'
import ProductView from '@/components/home/Product/ProductView'
import { notFound } from 'next/navigation'

interface Product {
    id: number
    name: string
    description: string
    price: number
    image_url: string
    stock: number
}

export default async function ProductPage({ params }: { params: { id: string } }) {
    params = await params
    const id = Number(params.id)

    if (isNaN(id)) return notFound()

    try {
        const res = await getProductDetail(id)
        // console.log(res)
        if (res?.Code !== 0 || !res.data) {
            return notFound()
        }

        return <ProductView product={res.data as Product} />
    } catch (error) {
        console.error('Error fetching product:', error)
        return notFound()
    }
}
