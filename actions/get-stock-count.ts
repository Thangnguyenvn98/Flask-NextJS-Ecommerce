
import Product from "@/app/interface/product"

export const getStockCount = async (storeId: string) => {
    console.log("Store ID")
    console.log(`http://127.0.0.1:8080/api/${storeId}/orders/paid`)
    const response = await fetch(`http://127.0.0.1:8080/api/store/${storeId}/products`,{
        next : {revalidate : 300}
    })
    const products = await response.json()
    let count = 0
    products.forEach((product:Product) => {
        if (product.isFeatured){
            count += 1
        }
    })
    return count
}