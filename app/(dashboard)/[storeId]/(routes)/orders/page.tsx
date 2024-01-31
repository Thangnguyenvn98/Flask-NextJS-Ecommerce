
import { format } from 'date-fns';
import { OrderClient } from './components/client'
import { OrderColumn } from './components/columns';
import { formatter } from '@/lib/utils';



const OrdersPage = async ({params}:{params:{storeId:string}}) => {

  const response = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/orders`, { cache: 'no-store' });

  const orders = await response.json()
  
 
  //reduce function taking the total item reduce it starting at 9

  const formattedOrders: OrderColumn[] = orders.map((item:any) => ({
    id: item.id,
    phone: item.phone,
    address: item.address,
    products: item.orderItems.map((orderItem:any)=> orderItem.product.name).join(', '),
    totalPrice: formatter.format(item.orderItems.reduce((total :any , item:any) => {
      return total + Number(item.product.price)
    },0)),
    isPaid: item.is_paid,
    created_at: format(item.created_at, "MMMM do, yyyy")
  }))
  console.log(formattedOrders)
  console.log("data")

  return (
    <div className="flex-col ">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <OrderClient data={formattedOrders}/>
        </div>
    </div>
  )
}

export default OrdersPage