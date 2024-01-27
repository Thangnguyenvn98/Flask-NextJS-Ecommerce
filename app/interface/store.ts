interface Store {
    id: string;
    name: string;
    created_at: string; 
    updated_at: string | null;
    user_id: string;
}

export default Store;