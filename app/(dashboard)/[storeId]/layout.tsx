import { useUser } from "@auth0/nextjs-auth0/client";
import axios from "axios";
import { redirect } from "next/navigation";

export default async function DashboardLayout({children,params}:{
    children: React.ReactNode;
    params: {storeId: string}
}) {
    const {user} = useUser()
    const userId = user?.sid
    if(!userId){
        redirect('/api/auth/login')
    }

    const store = await axios.get('/api/store').then((response) => {
        console.log(response.data)
    })
    return (
        <>
        <div>
            This will be a Navbar
        </div>
        {children}
        </>
    )
}