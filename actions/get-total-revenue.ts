

export const getTotalRevenue = async (storeId: string) => {
    const response = await fetch(`http://127.0.0.1:8080/api/${storeId}/orders/paid`)
    const paidOrders = await response.json()
    return paidOrders.amount
}