import { getSession } from '@auth0/nextjs-auth0';
import axios from "axios";
import { redirect } from "next/navigation";

export default async function SetupLayout({children}:{children:React.ReactNode}){
    const session = await getSession();
    const user = session?.user;
    
    const userId = user?.sid
    if (!userId) {
        redirect('/api/auth/login')
    }

    let store;
    try {
        const response = await axios.get(`http://127.0.0.1:8080/api/user/${userId}/store`) 
        
        if (response.status === 200) {
            store = response.data
        }
  
    }catch (error) {
        console.error(error);
    }
    if(store && store.id ) {
        redirect(`/${store.id}`)
    }
    
    return (
        <>
        {children}
        </>
    )
}