"use client"

import { ColumnDef } from "@tanstack/react-table"
import { CellAction } from "./cell-action"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type ProductColumn = {
  id: string ;
  price: number;
  name: string ;
  size:string;
  category:string;
  color:string;
  isFeatured: boolean;
  isArchived: boolean;
  createdAt: string;
}
//Rows object below in actions used these properties above, id,label,created_at

export const columns: ColumnDef<ProductColumn>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "isArchived",
    header: "Archived",
  },
  {
    accessorKey: "isFeatured",
    header: "Featured",
  },  
  {
    accessorKey: "price",
    header: "Price",
  },  {
    accessorKey: "category",
    header: "Category",
  },  {
    accessorKey: "size",
    header: "Size",
  },  {
    accessorKey: "color",
    header: "Color",
    cell: ({row})=> (
      <div className="flex items-center gap-x-2">
        {/* it said .color here instead .value because that what it map from as key in page.tsx */}
        {row.original.color}
        <div className="h-6 w-6 rounded-full border" style={{backgroundColor:row.original.color}}/>
      </div>
    )
  },
  {
    accessorKey: "createdAt",
    header: "Date",
  },
  {
    id:"actions",
    cell: ({row}) => <CellAction data={row.original}/>
    // This is something from tanstack query table
  }
  
]
