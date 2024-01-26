import { useUser } from "@auth0/nextjs-auth0/client";
import axios from "axios";
import { redirect } from "next/navigation";

export default async function SetupLayout({children}:{children:React.ReactNode}){
    // const {user} = useUser()
    // const userId = user?.sid
    // if (!userId) {
    //     redirect('/api/auth/login')
    // }

    // const store = await axios.get(`/api/store/${userId}`).then((response) =>
    // {
    //     console.log(response.data)
    // })
    
    return (
        <>
        {children}
        </>
    )
}