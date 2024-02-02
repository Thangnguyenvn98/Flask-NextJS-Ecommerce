

export const getSalesCount = async (storeId: string) => {
    console.log("Store ID")
    console.log(`http://127.0.0.1:8080/api/${storeId}/orders/paid`)
    const response = await fetch(`http://127.0.0.1:8080/api/${storeId}/orders/paid`,{
        next : {revalidate : 300}
    })
    const paidOrders = await response.json()
    const salesCount = paidOrders.reduce((total: any,order: { orderitems: any[] })=>{
        const orderTotal = order.orderitems.length
        return total + orderTotal
    },0)
   
    return salesCount
}