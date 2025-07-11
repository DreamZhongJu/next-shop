import Navigation from "@/components/home/Navigation";
import ProductList from "@/components/home/Product/ProductList";
import Search from "@/components/home/Search";
import Image from "next/image";

export default function Home() {
  return (
    <div>
      <Navigation />
      <Search />
      <ProductList />
    </div>
  );
}
