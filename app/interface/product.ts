import Image from "./image";

interface Product {
    id: string;
    name: string;
    price: number;
    createdAt: string; 
    size: string;
    category:string;
    color:string;
    isFeatured: boolean;
    isArchived: boolean;
    images:Image[];
}

export default Product;