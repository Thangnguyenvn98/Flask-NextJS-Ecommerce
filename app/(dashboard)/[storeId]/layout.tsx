import Navbar from '@/components/navbar';
import { fetchStore } from '@/hooks/fetchStore';
import { redirect } from "next/navigation";

export default async function DashboardLayout({children,params}:{
    children: React.ReactNode;
    params: {storeId: string}
}) {
    const store = await fetchStore();
    
    if (!store || !store.name) {
        redirect('/')
    }
    return (
        <>
        <div>
            <Navbar/>
        </div>
        {children}
        </>
    )
}