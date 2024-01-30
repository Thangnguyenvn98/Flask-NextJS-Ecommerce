"use client"

import { ColumnDef } from "@tanstack/react-table"
import { CellAction } from "./cell-action"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type SizeColumn = {
  id: string ;
  name: string ;
  value:string;
  created_at: string;
}
//Rows object below in actions used these properties above, id,label,created_at

export const columns: ColumnDef<SizeColumn>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "value",
    header: "Value",
  },
  {
    accessorKey: "created_at",
    header: "Date",
  },
  {
    id:"actions",
    cell: ({row}) => <CellAction data={row.original}/>
    // This is something from tanstack query table
  }
  
]
