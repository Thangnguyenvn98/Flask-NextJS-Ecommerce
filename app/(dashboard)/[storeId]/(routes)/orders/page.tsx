
import { format } from 'date-fns';
import { OrderClient } from './components/client'
import { OrderColumn } from './components/columns';
import { formatter } from '@/lib/utils';



const OrdersPage = async ({params}:{params:{storeId:string}}) => {

  const response = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/orders`, { cache: 'no-store' });

  const orders = await response.json()
  
  console.log(orders)
  //reduce function taking the total item reduce it starting at 9

  const formattedOrders: OrderColumn[] = orders.map((item:any) => ({
    id: item.id,
    phone: item.phone,
    address: item.address,
    products: item.orderitems.map((orderItem:any)=> orderItem.products.name).join(', '),
    totalPrice: formatter.format(item.orderitems.reduce((total :any , item:any) => {
      return total + Number(item.products.price)
    },0)),
    isPaid: item.is_paid,
    
  }))
 

  return (
    <div className="flex-col ">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <OrderClient data={formattedOrders}/>
        </div>
    </div>
  )
}

export default OrdersPage