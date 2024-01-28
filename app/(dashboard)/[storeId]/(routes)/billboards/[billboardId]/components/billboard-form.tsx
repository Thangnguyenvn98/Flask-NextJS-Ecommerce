'use client'

import * as z from "zod"
import Billboard from "@/app/interface/billboard"
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
import { ApiAlert } from "@/components/ui/api-alert"
import { useOrigin } from "@/hooks/use-origin"
import ImageUpload from "@/components/ui/image-upload"


    
const formSchema = z.object({
    label: z.string().min(1),
    imageUrl: z.string().min(1)
})

type BillboardFormValues = z.infer<typeof formSchema>

interface BillboardFormProps {
    initialData: Billboard | null
  }

export const BillboardForm: React.FC<BillboardFormProps> = ({initialData}) => {
    const [open, setOpen] = useState(false) //alert model calling different api every time
    const params =useParams()
    const router =useRouter()
    const [loading,setLoading] = useState(false)
    const origin = useOrigin()
    const {user} = useUser()
    const userId = user?.sub?.split('|')[1]

    const title = initialData ? "Edit billboard" : "Create billboard"
    const description = initialData ? "Edit a billboard" : "Add a new billboard "
    const toastMessage = initialData ? "Billboard updated" : "Billboard created"
    const action = initialData ? "Save changes" : "Create"


    const form = useForm<BillboardFormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: initialData || {
            label: '',
            imageUrl: ''
        }
    })

    const onSubmit = async (data: BillboardFormValues) => {
        try {
            setLoading(true)
            await axios.patch(`http://127.0.0.1:8080/api/store/${params.storeId}/${userId}`,data)
            router.refresh()
            toast.success("Store name updated.")
        }catch (error){
            toast.error("Something went wrong.")
        }finally {
            setLoading(false)
        }
    }

    const onDelete = async () => {
        try {
            setLoading(true)
            await axios.delete(`http://127.0.0.1:8080/api/store/${params.storeId}/${userId}`)
            router.refresh()
            router.push('/')
            toast.success("Store Deleted.")

        }catch(error){
            toast.error("Something went wrong.")
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
            <FormField control={form.control} name="imageUrl" render={({field}) => (
                        <FormItem>
                            <FormLabel>Background Image</FormLabel>
                            <FormControl>
                                <ImageUpload
                                disabled={loading}
                                onChange={(url)=>field.onChange(url)}
                                onRemove={()=>field.onChange("")}
                                value={field.value ? [field.value] : []}/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                
                <div className="grid grid-cols-3 gap-8">
                    <FormField control={form.control} name="label" render={({field}) => (
                        <FormItem>
                            <FormLabel>Label</FormLabel>
                            <FormControl>
                                <Input disabled={loading} placeholder="Billboard label" {...field}/>
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