'use client'

import * as z from "zod"
import { useForm } from "react-hook-form"
import { zodResolver} from "@hookform/resolvers/zod"


import { useStoreModal } from "@/hooks/use-store-modal"


import { Modal } from "../ui/modal"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "../ui/form"
import { Input } from "../ui/input"
import { Button } from "../ui/button"
import { useState } from "react"
import axios from "axios"
import {toast} from "react-hot-toast"
import { useUser } from "@auth0/nextjs-auth0/client"


//zod is required from shadcn for forms
const formSchema = z.object({
    name: z.string().min(1) //at least 1 character required
})

export const StoreModal = () => {
    const storeModal = useStoreModal()
    const [loading,setLoading] = useState(false)

    const {user} = useUser()

    //form here is used below in Form component of ShadCN
    const form = useForm<z.infer<typeof formSchema>>(
        {
            resolver: zodResolver(formSchema),
            defaultValues: {
                name:""
            }
        }
    )

    const onSubmit = async (values: z.infer<typeof formSchema>) => {
            try {
                setLoading(true)
                const data = {...values,'userId': user?.sid}
                const response = await axios.post('/api/stores',data)

                toast.success("Store created")
            }catch(e) {
                toast.error("Something went wrong")

            }finally {
                setLoading(false)
            }
            //CREATE STORE: TODO LATER
    }

    return (
        <Modal title="Create Store" description="Add a new store"
        isOpen={storeModal.isOpen} 
        onClose={storeModal.onClose}>
        <div>
            <div className="space-y-4 py-2 pb-4">
        <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
            <FormField
            control={form.control}
            name="name"
            render={({field})=>(
                <FormItem>
                    <FormLabel>
                        Name
                    </FormLabel>
                    <FormControl>
                        <Input disabled={loading} placeholder="Ecommerce" {...field}/>
                    </FormControl>
                    <FormMessage/>   {/* This condition defined in form constant of zod above in formSchema*/}
                </FormItem>
            )}
            />
        <div className='pt-6 space-x-2 flex items-center justify-end w-full'>
                    <Button variant="outline" disabled={loading} onClick={storeModal.onClose}>Cancel</Button>
                    <Button disabled={loading} type="submit">Continue</Button> 
                    {/* call the obSubmit defined above*/}

        </div>
            
        </form>
        </Form>
            </div>
        </div>
       
        </Modal>
    )
   
}

