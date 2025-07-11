import ProductList from "@/components/home/Product/ProductList";
import Search from "@/components/home/Search";

export default function Home() {
  return (
    <div className="flex flex-col items-center">
      <div className="w-full max-w-7xl px-4">
        <Search />
      </div>
      <div className="w-full max-w-7xl px-4">
        <ProductList />
      </div>
    </div>
  );
}
