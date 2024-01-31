import React from 'react'
import { ProductForm } from './components/product-form'
import { getSession } from '@auth0/nextjs-auth0'
import { redirect } from 'next/navigation'

const ProductPage = async ({params}:{params: {productId : string,storeId: string}}) => {
    const session = await getSession()
    const user = session?.user
    const userId = user?.sub.split('|')[1]
    if(!userId) {
        redirect('/auth/login')
    }
    
    const response = await fetch(`http://127.0.0.1:8080/api/product/${params.productId}`,{
        cache: "no-store"
    })
    let product = null; // Initialize with null
    if (response.ok) {
        product = await response.json();
    }
    const categoriesResponse = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/categories`, { cache: 'no-store' });
    const categories = await categoriesResponse.json();
    
    const sizesResponse = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/sizes`, { cache: 'no-store' });
    const sizes = await sizesResponse.json();
    
    const colorsResponse = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/colors`, { cache: 'no-store' });
    const colors = await colorsResponse.json();
    

    return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <ProductForm initialData={product} categories={categories} sizes={sizes} colors={colors}/>
        </div>
    </div> 
  )
}

export default ProductPage