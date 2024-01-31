interface Product {
    id: string;
    name: string;
    price: number;
    created_at: string; 
    updated_at: string | null;
    store_id: string;
}

export default Product;