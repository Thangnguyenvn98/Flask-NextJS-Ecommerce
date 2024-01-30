"use client"

import { ColumnDef } from "@tanstack/react-table"
import { CellAction } from "./cell-action"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type CategoryColumn = {
  id: string ;
  name: string ;
  billboardLabel: string ;
  created_at: string;
}
//Rows object below in actions used these properties above, id,label,created_at

export const columns: ColumnDef<CategoryColumn>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "billboard",
    header: "Billboard",
    cell: ({row}) => row.original.billboardLabel,
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
