
import { format } from 'date-fns';
import { SizesClient } from './components/client'
import { SizeColumn } from './components/columns';


const SizesPage = async ({params}:{params:{storeId:string}}) => {

  const response = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/sizes`, { cache: 'no-store' });

  const sizes = await response.json();
  
 
  

  const formattedSizes: SizeColumn[] = sizes.map((item:any) => ({
    id: item.id,
    name: item.name,
    value:item.value,
    created_at: format(item.created_at, "MMMM do, yyyy")
  }))
  console.log(formattedSizes)
  console.log("data")

  return (
    <div className="flex-col ">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <SizesClient data={formattedSizes}/>
        </div>
    </div>
  )
}

export default SizesPage