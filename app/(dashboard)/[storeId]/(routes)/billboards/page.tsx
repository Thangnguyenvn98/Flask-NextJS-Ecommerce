
import { format } from 'date-fns';
import { BillboardClient } from './components/client'
import { BillboardColumn } from './components/columns';
import { useEffect, useState } from 'react';


async function getBillboards(params:string){
  const res = await fetch(`http://127.0.0.1:8080/api/${params}/billboards`, { cache: "no-store" });
  return res.json()
}

const BillboardsPage = async ({params}:{params:{storeId:string}}) => {

  // const response = await fetch(`http://127.0.0.1:8080/api/${params.storeId}/billboards`, { cache: 'no-store' });

  const billboards = await getBillboards(params.storeId)
  
 
  

  const formattedBillboards: BillboardColumn[] = billboards.map((item:any) => ({
    id: item.id,
    label: item.label,
    created_at: format(item.created_at, "MMMM do, yyyy")
  }))
  console.log(formattedBillboards)
  console.log("data")

  return (
    <div className="flex-col ">
        <div className="flex-1 space-y-4 p-8 pt-6">
            <BillboardClient data={formattedBillboards}/>
        </div>
    </div>
  )
}

export default BillboardsPage