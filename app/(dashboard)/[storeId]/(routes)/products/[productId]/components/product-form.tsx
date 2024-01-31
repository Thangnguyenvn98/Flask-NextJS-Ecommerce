'use client'

import * as z from "zod"
import Product from "@/app/interface/product"
import Image from "@/app/interface/image"
import { Button } from "@/components/ui/button"
import { Heading } from "@/components/ui/heading"
import { Separator } from "@/components/ui/separator"
import { Trash } from "lucide-react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useState } from "react"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import axios from "axios"
import toast from "react-hot-toast"
import { useUser } from "@auth0/nextjs-auth0/client"
import { useParams, useRouter } from "next/navigation"
import { AlertModal } from "@/components/modals/alert-modal"

import ImageUpload from "@/components/ui/image-upload"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import Category from "@/app/interface/category"
import Color from "@/app/interface/color"
import Size from "@/app/interface/size"
import { Checkbox } from "@/components/ui/checkbox"


    
const formSchema = z.object({
    name: z.string().min(1),
    price: z.coerce.number().min(1),
    images: z.object({url: z.string()}).array(),
    categoryId: z.string().min(1),
    colorId: z.string().min(1),
    sizeId: z.string().min(1),
    isFeatured: z.boolean().default(false).optional(),
    isArchived: z.boolean().default(false).optional()
})

type ProductFormValues = z.infer<typeof formSchema>

interface ProductFormProps {
    initialData: Product & {
        images: Image[]
    }| null
    categories: Category[];
    colors: Color[];
    sizes: Size[]
  }

export const ProductForm: React.FC<ProductFormProps> = ({initialData,categories,colors,sizes}) => {
    const [open, setOpen] = useState(false) //alert model calling different api every time
    const params =useParams()
    const router =useRouter()
    const [loading,setLoading] = useState(false)
    const {user} = useUser()
    const userId = user?.sub?.split('|')[1]

    const title = initialData ? "Edit Product" : "Create Product"
    const description = initialData ? "Edit a Product" : "Add a new Product "
    const toastMessage = initialData ? "Product updated" : "Product created"
    const action = initialData ? "Save changes" : "Create"


    const form = useForm<ProductFormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: initialData ? {...initialData,
        price: parseFloat(String(initialData?.price))
        } : {
            name: '',
            price:0,
            images: [],
            categoryId: '',
            colorId: '',
            sizeId: '',
            isFeatured: false,
            isArchived: false
        }
    })

    const onSubmit = async (data: ProductFormValues) => {
        try {
            setLoading(true)
            const datas = {...data, "user_id":userId}
            if(initialData){
                await axios.patch(`http://127.0.0.1:8080/api/${params.storeId}/products/${params.productId}`,datas)
               
            } else {
                console.log("DATASSSS COMINGS")
                console.log(datas)
                await axios.post(`http://127.0.0.1:8080/api/${params.storeId}/products`,datas)
         
            }
       
            router.push(`/${params.storeId}/products`)
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
            await axios.delete(`http://127.0.0.1:8080/api/${userId}/${params.storeId}/product/${params.productId}`)
            router.push(`/${params.storeId}/products`)
            router.refresh()
            toast.success("Product Deleted.")

        }catch(error){
            toast.error("Make sure you removed all categories usin this Product first.")
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
            <FormField control={form.control} name="images" render={({field}) => (
                        <FormItem>
                            <FormLabel>Images</FormLabel>
                            <FormControl>
                                <ImageUpload
                                disabled={loading}
                                onChange={(url)=>field.onChange([...field.value, {url}])}
                                onRemove={(url)=>field.onChange([...field.value.filter((current) => current.url !== url)])}
                                value={field.value.map((image) => image.url)}/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                
                <div className="grid grid-cols-3 gap-8">
                    <FormField control={form.control} name="name" render={({field}) => (
                        <FormItem>
                            <FormLabel>Name</FormLabel>
                            <FormControl>
                                <Input disabled={loading} placeholder="Product name" {...field}/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                        <FormField control={form.control} name="price" render={({field}) => (
                        <FormItem>
                            <FormLabel>Price</FormLabel>
                            <FormControl>
                                <Input type="number" disabled={loading} placeholder="9.99" {...field}/>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <FormField control={form.control} name="categoryId" render={({field}) => (
                        <FormItem>
                            <FormLabel>Category</FormLabel>
                           <Select disabled={loading} onValueChange={field.onChange} value={field.value} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger >
                                    <SelectValue defaultValue={field.value} placeholder="Select a categorie"/>

                                    
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                {categories.map((categorie) =>(
                                    <SelectItem key={categorie.id}
                                    value={categorie.id}
                                    >
                                            {categorie.name}
                                    </SelectItem>
                                ))}
                                </SelectContent>
                           </Select>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                                <FormField control={form.control} name="sizeId" render={({field}) => (
                        <FormItem>
                            <FormLabel>Size</FormLabel>
                           <Select disabled={loading} onValueChange={field.onChange} value={field.value} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger >
                                    <SelectValue defaultValue={field.value} placeholder="Select a Size"/>

                                    
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                {sizes.map((size) =>(
                                    <SelectItem key={size.id}
                                    value={size.id}
                                    >
                                            {size.name}
                                    </SelectItem>
                                ))}
                                </SelectContent>
                           </Select>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                                <FormField control={form.control} name="colorId" render={({field}) => (
                        <FormItem>
                            <FormLabel>Color</FormLabel>
                           <Select disabled={loading} onValueChange={field.onChange} value={field.value} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger >
                                    <SelectValue defaultValue={field.value} placeholder="Select a color"/>

                                    
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                {colors.map((color) =>(
                                    <SelectItem key={color.id}
                                    value={color.id}
                                    >
                                            {color.name}
                                    </SelectItem>
                                ))}
                                </SelectContent>
                           </Select>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                          <FormField control={form.control} name="isFeatured" render={({field}) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                            <FormControl>
                                <Checkbox checked={field.value} onCheckedChange={field.onChange}/>
                               
                            </FormControl>
                            <div className="space-y-1 leading-none">
                            <FormLabel>
                                    Featured
                                </FormLabel>
                                <FormDescription>
                                    This product will appear on the home page
                                </FormDescription>
                            </div>
                        </FormItem>
                    )}/>
                    <FormField control={form.control} name="isArchived" render={({field}) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                            <FormControl>
                                <Checkbox checked={field.value} onCheckedChange={field.onChange}/>
                               
                            </FormControl>
                            <div className="space-y-1 leading-none">
                            <FormLabel>
                                    Archived
                                </FormLabel>
                                <FormDescription>
                                    This product will not appear anywhere on the home page
                                </FormDescription>
                            </div>
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