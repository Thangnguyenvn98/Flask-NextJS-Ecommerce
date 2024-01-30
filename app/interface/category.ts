interface Category {
    id: string;
    name: string;
    created_at: string; 
    updated_at: string | null;
    store_id: string;
    billboard_id:string
}

export default Category;