
import { format } from 'date-fns';
import { ProductClient } from './components/client'
import { ProductColumn } from './components/columns';
import { formatter } from '@/lib/utils';


async function getProducts(params:string){
  const res = await fetch(`http://127.0.0.1:8080/api/store/${params}/products`, { next: { revalidate: 0 } });
  return res.json()
}

const ProductsPage = async ({params}:{params:{storeId:string}}) => {


  const products = await getProducts(params.storeId)
  
 
  

  const formattedProducts: ProductColumn[] = products.map((item:any) => ({
    id: item.id,
    name: item.name,
    price: formatter.format(item.price),
    category: item.category.name,
    size: item.category.name,
    color:item.color.value,
    isFeatured: item.is_featured,
    isArchived: item.is_archived,
    createdAt: format(item.created_at, "MMMM do, yyyy")
  }))
  console.log(formattedProducts)
  console.log("data")

  return (
    <div className="flex-col ">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <ProductClient data={formattedProducts}/>
        </div>
    </div>
  )
}

export default ProductsPage