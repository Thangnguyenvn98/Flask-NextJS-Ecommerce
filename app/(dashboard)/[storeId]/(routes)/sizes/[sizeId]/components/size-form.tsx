'use client'

import * as z from "zod"
import Size from "@/app/interface/size"
import { Button } from "@/components/ui/button"
import { Heading } from "@/components/ui/heading"
import { Separator } from "@/components/ui/separator"
import { Trash } from "lucide-react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useState } from "react"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import axios from "axios"
import toast from "react-hot-toast"
import { useUser } from "@auth0/nextjs-auth0/client"
import { useParams, useRouter } from "next/navigation"
import { AlertModal } from "@/components/modals/alert-modal"



    
const formSchema = z.object({
    name: z.string().min(1),
    value: z.string().min(1)
})

type SizeFormValues = z.infer<typeof formSchema>

interface SizeFormProps {
    initialData: Size | null
  }

export const SizeForm: React.FC<SizeFormProps> = ({initialData}) => {
    const [open, setOpen] = useState(false) //alert model calling different api every time
    const params =useParams()
    const router =useRouter()
    const [loading,setLoading] = useState(false)
    const {user} = useUser()
    const userId = user?.sub?.split('|')[1]

    const title = initialData ? "Edit Size" : "Create Size"
    const description = initialData ? "Edit a Size" : "Add a new Size "
    const toastMessage = initialData ? "Size updated" : "Size created"
    const action = initialData ? "Save changes" : "Create"


    const form = useForm<SizeFormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: initialData || {
            name: '',
            value: ''
        }
    })

    const onSubmit = async (data: SizeFormValues) => {
        try {
            setLoading(true)
            const datas = {...data, "user_id":userId}
            if(initialData){
                await axios.patch(`http://127.0.0.1:8080/api/${params.storeId}/sizes/${params.sizeId}`,datas)
               
            } else {
                await axios.post(`http://127.0.0.1:8080/api/${params.storeId}/sizes`,datas)
         
            }
       
            router.push(`/${params.storeId}/sizes`)
            router.refresh()
            toast.success(toastMessage)
        }catch (error){
            toast.error("Something went wrong.")
        }finally {
            setLoading(false)
        }
    }

    const onDelete = async () => {
        try {
            setLoading(true)
            await axios.delete(`http://127.0.0.1:8080/api/${userId}/${params.storeId}/size/${params.sizeId}`)
            router.push(`/${params.storeId}/sizes`)
            router.refresh()
            toast.success("Size Deleted.")

        }catch(error){
            toast.error("Make sure you removed all categories using this size first.")
        }finally {
            setLoading(false)
            setOpen(false)
        }
    }

    return (
        <>
        <AlertModal isOpen={open}
        onClose={()=>setOpen(false)}
        onConfirm={onDelete}
        loading={loading}
        />
        <div className="flex items-center justify-between">
            <Heading title={title} description={description}/>
            {initialData && (
                 <Button variant="destructive" disabled={loading} size="sm" onClick={()=>setOpen(true)}>
          
            
                 <Trash className="h-4 w-4"/>
                 </Button>
            )}
           
        </div>
        <Separator/>
        {/* The form */}
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 w-full">
      
                <div className="grid grid-cols-3 gap-8">
                    <FormField control={form.control} name="name" render={({field}) => (
                        <FormItem>
                            <FormLabel>Name</FormLabel>
                            <FormControl>
                                <Input disabled={loading} placeholder="Size Name" {...field}/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                          <FormField control={form.control} name="value" render={({field}) => (
                        <FormItem>
                            <FormLabel>Value</FormLabel>
                            <FormControl>
                                <Input disabled={loading} placeholder="Size Value" {...field}/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                </div>

            <Button disabled={loading} className="ml-auto" type="submit">
{action}
            </Button>

            </form>
        </Form>
        <Separator/>
        </>
   
    )
}