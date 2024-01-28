import { fetchStore } from '@/hooks/fetchStore';
import { redirect } from "next/navigation";

export default async function SetupLayout({children}:{children:React.ReactNode}){
   
    const store = await fetchStore();
    if(store && store.id && store.name ) {
        redirect(`/${store.id}`)
    }
    
    return (
        <>
        {children}
        </>
    )
}