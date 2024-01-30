
import { format } from 'date-fns';
import { CategoryClient } from './components/client'
import { CategoryColumn } from './components/columns';
import { useEffect, useState } from 'react';




const CategoriesPage = async ({params}:{params:{storeId:string}}) => {

  const response = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/categories`, { cache: 'no-store' });
  const categories = await response.json();
  

  const formattedCategories: CategoryColumn[] = categories.map((item:any) => ({
    id: item.id,
    name: item.name,
    billboardLabel: item.billboard.label,
    created_at: format(item.created_at, "MMMM do, yyyy")
  }))
  console.log(formattedCategories)
  console.log("data")

  return (
    <div className="flex-col ">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <CategoryClient data={formattedCategories}/>
        </div>
    </div>
  )
}

export default CategoriesPage