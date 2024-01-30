import React from 'react'
import { SizeForm } from './components/size-form'
import { getSession } from '@auth0/nextjs-auth0'
import { redirect } from 'next/navigation'

const SizePage = async ({params}:{params: {sizeId : string}}) => {
    const session = await getSession()
    const user = session?.user
    const userId = user?.sub.split('|')[1]
    if(!userId) {
        redirect('/auth/login')
    }
    
    const response = await fetch(`http://127.0.0.1:8080/api/size/${params.sizeId}`,{
        cache: "no-store"
    })
    let size = null; // Initialize with null
    if (response.ok) {
        size = await response.json();
    }
    
  
    return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <SizeForm initialData={size}/>
        </div>
    </div> 
  )
}

export default SizePage