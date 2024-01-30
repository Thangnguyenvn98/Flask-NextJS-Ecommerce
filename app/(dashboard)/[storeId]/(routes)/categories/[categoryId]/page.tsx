import React from 'react'
import { CategoryForm } from './components/category-form'
import { getSession } from '@auth0/nextjs-auth0'
import { redirect } from 'next/navigation'

const CategoryPage = async ({params}:{params: {categoryId : string, storeId: string}}) => {
    const session = await getSession()
    const user = session?.user
    const userId = user?.sub.split('|')[1]
    if(!userId) {
        redirect('/auth/login')
    }
    
    const categoryResponse = await fetch(`http://127.0.0.1:8080/api/category/${params.categoryId}`,{
        cache: "no-store"
    })
    let category = null; // Initialize with null
    if (categoryResponse.ok) {
        category = await categoryResponse.json();
    }
    
    
    const billboardResponse = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/billboards`,{
        cache: "no-store"
    })
     
    const billboards = await billboardResponse.json();
  
    
  
    return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <CategoryForm billboards={billboards} initialData={category}/>
        </div>
    </div> 
  )
}

export default CategoryPage