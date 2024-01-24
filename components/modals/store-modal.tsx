"use client"

import * as z from "zod"
import { useForm } from "react-hook-form"
import { zodResolver} from "@hookform/resolvers/zod"



import { useStoreModal } from "@/hooks/use-store-modal"

import { Modal } from "../ui/modal"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "../ui/form"
import { Input } from "../ui/input"
import { Button } from "../ui/button"


//zod is required from shadcn for forms
const formSchema = z.object({
    name: z.string().min(1) //at least 1 character required
})

export const StoreModal = () => {
    const storeModal = useStoreModal()

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
            console.log(values)
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
                        <Input placeholder="Ecommerce" {...field}/>
                    </FormControl>
                    <FormMessage/>   {/* This condition defined in form constant of zod above in formSchema*/}
                </FormItem>
            )}
            />
        <div className='pt-6 space-x-2 flex items-center justify-end w-full'>
                    <Button variant="outline" onClick={storeModal.onClose}>Cancel</Button>
                    <Button type="submit">Continue</Button> 
                    {/* call the obSubmit defined above*/}

        </div>
            
        </form>
        </Form>
            </div>
        </div>
       
        </Modal>
    )
   
}

