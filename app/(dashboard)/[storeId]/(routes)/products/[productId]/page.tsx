import React from 'react'
import { ProductForm } from './components/product-form'
import { getSession } from '@auth0/nextjs-auth0'
import { redirect } from 'next/navigation'

const ProductPage = async ({params}:{params: {productId : string}}) => {
    const session = await getSession()
    const user = session?.user
    const userId = user?.sub.split('|')[1]
    if(!userId) {
        redirect('/auth/login')
    }
    
    const response = await fetch(`http://127.0.0.1:8080/api/Product/${params.productId}`,{
        cache: "no-store"
    })
    let product = null; // Initialize with null
    if (response.ok) {
        product = await response.json();
    }
    
  
    return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <ProductForm initialData={product}/>
        </div>
    </div> 
  )
}

export default ProductPage