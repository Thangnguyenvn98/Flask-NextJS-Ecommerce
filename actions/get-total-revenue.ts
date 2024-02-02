

export const getTotalRevenue = async (storeId: string) => {
    console.log("Store ID")
    console.log(`http://127.0.0.1:8080/api/${storeId}/orders/paid`)
    const response = await fetch(`http://127.0.0.1:8080/api/${storeId}/orders/paid`,{
        next : {revalidate : 300}
    })
    const paidOrders = await response.json()
    const totalRevenue = paidOrders.reduce((total: any,order: { orderitems: any[] })=>{
        const orderTotal = order.orderitems.reduce((orderSum,item)=>{
            return orderSum + item.products.price
        },0)
        return total + orderTotal
    },0)
   
    return totalRevenue
}