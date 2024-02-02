import { getSession } from "@auth0/nextjs-auth0";
import { redirect } from "next/navigation";

export async function fetchStore() {
    const session = await getSession();
    const user = session?.user;
    
    const userId = user?.sub.split('|')[1]
    console.log(userId)
    if (!userId) {
        redirect('/api/auth/login')
    }

    const store = await fetch(`http://127.0.0.1:8080/api/user/${userId}/store`,{
        next : {revalidate : 120}
    })
    return store.json()
}