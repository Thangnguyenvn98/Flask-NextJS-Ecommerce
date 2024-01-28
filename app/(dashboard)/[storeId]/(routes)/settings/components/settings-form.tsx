'use client'

import * as z from "zod"
import Store from "@/app/interface/store"
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

interface SettingsFormProps {
    initialData: Store
}

const formSchema = z.object({
    name: z.string().min(1)
})

type SettingsFormValues = z.infer<typeof formSchema>

export const SettingsForm: React.FC<SettingsFormProps> = ({initialData}) => {
    const [open, setOpen] = useState(false) //alert model calling different api every time
    const params =useParams()
    const router =useRouter()
    const [loading,setLoading] = useState(false)
    const origin = useOrigin()
    const {user} = useUser()
    const userId = user?.sub?.split('|')[1]
    const form = useForm<SettingsFormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: initialData
    })

    const onSubmit = async (data: SettingsFormValues) => {
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
            <Heading title="Settings" description="Manage store preferences"/>
            <Button variant="destructive" disabled={loading} size="sm" onClick={()=>setOpen(true)}>
            <Trash className="h-4 w-4"/>
            </Button>
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
                                <Input disabled={loading} placeholder="Store Name" {...field}/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                </div>

            <Button disabled={loading} className="ml-auto" type="submit">
                Save changes
            </Button>

            </form>
        </Form>
        <Separator/>
        <ApiAlert title="NEXT_PUBLIC_API_URL" description={`${origin}/api/${params.storeId}`} variant="public"/>
        </>
   
    )
}