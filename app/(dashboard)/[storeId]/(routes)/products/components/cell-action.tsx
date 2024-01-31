'use client'

import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ProductColumn } from "./columns"
import { Button } from "@/components/ui/button"
import { Copy, Edit, MoreHorizontal, Trash } from "lucide-react"
import toast from "react-hot-toast"
import { useRouter, useParams } from "next/navigation"
import { useState } from "react"
import axios from "axios"
import { AlertModal } from "@/components/modals/alert-modal"
import { useUser } from "@auth0/nextjs-auth0/client"

interface CellActionProps {
    data: ProductColumn
}

export const CellAction:React.FC<CellActionProps>= ({data}) => {
    const [loading, setLoading] = useState(false)
    const [open,setOpen] = useState(false)
    const router = useRouter()
    const {user} = useUser()
    const userId = user?.sub?.split('|')[1]
 
    const onCopy = (id:string) => {
        navigator.clipboard.writeText(id) //Description from the props that was passed
        toast.success("Copied to clipboard.")
    }
    const params = useParams()

    const onDelete = async () => {
        try {
            setLoading(true)
            await axios.delete(`http://127.0.0.1:8080/api/${userId}/${params.storeId}/product/${data.id}`)
            router.refresh()
            toast.success("Product Deleted.")

        }catch(error){
            toast.error("Make sure you removed all categories usin this Product first.")
        }finally {
            setLoading(false)
            setOpen(false)
        }
    }

    //Copy from the api alert model to get the text
    return (
        <>
        <AlertModal 
            isOpen={open}
            onClose={()=>setOpen(false)}
            onConfirm={onDelete}
            loading={loading}
        />
         <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                    <span className="sr-only">Open menu</span>
                    <MoreHorizontal className="h-4 w-4"/>
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
            <DropdownMenuLabel>
                Actions
            </DropdownMenuLabel>
            <DropdownMenuItem onClick={()=>onCopy(data.id)}>
                <Copy className="h-4 w-4 mr-2"/>
                Copy Id
            </DropdownMenuItem>
            <DropdownMenuItem onClick={()=> router.push(`/${params.storeId}/products/${data.id}`)}>
                <Edit className="h-4 w-4 mr-2"/>
                Update
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setOpen(true)}>
                <Trash className="h-4 w-4 mr-2"/>
                Delete
            </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
        </>
       
    )
}