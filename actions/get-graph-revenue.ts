
import Order from "@/app/interface/order"

interface GraphData {
    name:string;
    total:number;
}

export const getGraphRevenue = async (storeId: string) => {
    console.log("Store ID")
    console.log(`http://127.0.0.1:8080/api/${storeId}/orders/paid`)
    const response = await fetch(`http://127.0.0.1:8080/api/${storeId}/orders/paid`,{
        next: {revalidate: 120}
    })
    const paidOrders = await response.json()
 

    const monthlyRevenue: { [key:number] :number} = {}

    for (const order of paidOrders){
        let month= order.created_at.slice(5,7)
        if (month.substring(0,1) == '0'){
            month = month.slice(1) 
        }
        console.log(month)
        let revenueForOrder = 0
        for (const item of order.orderitems){
            revenueForOrder += item.products.price
        }
        monthlyRevenue[month] = (monthlyRevenue[month] || 0) + revenueForOrder
    }
    const graphData: GraphData[] = [
        { name: "Jan", total: 0},
        { name: "Feb", total: 0},
        { name: "Mar", total: 0},
        { name: "Apr", total: 0},
        { name: "May", total: 0},
        { name: "Jun", total: 0},
        { name: "Jul", total: 0},
        { name: "Aug", total: 0},
        { name: "Sep", total: 0},
        { name: "Oct", total: 0},
        { name: "Nov", total: 0},
        { name: "Dec", total: 0},
    ]
    for (const month in monthlyRevenue){
        graphData[parseInt(month)].total = monthlyRevenue[parseInt(month)]
    }
    console.log(graphData)
    return graphData
}