export default function ProductView({ product }: { product: any }) {
    if (!product) return <div>商品未找到</div>

    return (
        <div className="p-4">
            <div className="flex flex-col md:flex-row bg-white border rounded-xl shadow-lg p-4 mx-[10%]">
                <img
                    src={product.Image_url}
                    alt={product.Name}
                    className="w-96 h-96 object-cover rounded-md"
                />
                <div className="ml-8 mt-4 md:mt-0">
                    <h1 className="text-3xl font-bold">{product.Name}</h1>
                    <p className="text-gray-600 mt-2">{product.Description}</p>
                    <div className="mt-4">
                        <span className="text-xl font-bold">¥{product.Price}</span>
                    </div>
                    <div className="mt-2">
                        <span className="text-sm text-gray-500">库存: {product.Stock}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
