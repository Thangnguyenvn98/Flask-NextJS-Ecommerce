import React from 'react'
import { BillboardForm } from './components/billboard-form'
import { getSession } from '@auth0/nextjs-auth0'
import { redirect } from 'next/navigation'

const BillboardPage = async ({params}:{params: {billboardId : string}}) => {
    const session = await getSession()
    const user = session?.user
    const userId = user?.sub.split('|')[1]
    if(!userId) {
        redirect('/auth/login')
    }
    
    const response = await fetch(`http://127.0.0.1:8080/api/billboard/${params.billboardId}`,{
        cache: "no-store"
    })
    let billboard = null; // Initialize with null
    if (response.ok) {
        billboard = await response.json();
    }
    
  
    return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <BillboardForm initialData={billboard}/>
        </div>
    </div> 
  )
}

export default BillboardPage