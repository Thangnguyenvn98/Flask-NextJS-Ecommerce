import React from 'react'
import { ColorForm } from './components/color-form'
import { getSession } from '@auth0/nextjs-auth0'
import { redirect } from 'next/navigation'

const ColorPage = async ({params}:{params: {colorId : string}}) => {
    const session = await getSession()
    const user = session?.user
    const userId = user?.sub.split('|')[1]
    if(!userId) {
        redirect('/auth/login')
    }
    
    const response = await fetch(`http://127.0.0.1:8080/api/color/${params.colorId}`,{
        cache: "no-store"
    })
    let color = null; // Initialize with null
    if (response.ok) {
        color = await response.json();
    }
    
  
    return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <ColorForm initialData={color}/>
        </div>
    </div> 
  )
}

export default ColorPage