
import { format } from 'date-fns';
import { ColorsClient } from './components/client'
import { ColorColumn } from './components/columns';


async function getColors(params:string){
  const res = await fetch(`http://127.0.0.1:8080/api/${params}/colors`, { next: { revalidate: 0 } });
  return res.json()
}

const ColorsPage = async ({params}:{params:{storeId:string}}) => {


  const colors = await getColors(params.storeId)
  
 

  const formattedColors: ColorColumn[] = colors.map((item:any) => ({
    id: item.id,
    name: item.name,
    value:item.value,
    created_at: format(item.created_at, "MMMM do, yyyy")
  }))
  console.log(formattedColors)
  console.log("data")

  return (
    <div className="flex-col ">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <ColorsClient data={formattedColors}/>
        </div>
    </div>
  )
}

export default ColorsPage