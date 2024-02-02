import OrderItem from "./orderitem";

interface Order {
    id:string;
    address:string;
    phone:string;
    is_paid:boolean;
    orderitems: OrderItem
    created_at:string;

}

export default Order