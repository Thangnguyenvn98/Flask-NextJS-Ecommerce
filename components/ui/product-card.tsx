'use client'

import { Product } from "@/types"
import Image from "next/image"
import IconButton from "./icon-button"
import { Expand, ShoppingCart } from "lucide-react"
import Currency from "./currency"
import { useRouter } from "next/navigation"
import { MouseEventHandler } from "react"
import usePreviewModal from "@/hooks/use-preview-modal"
import useCart from "@/hooks/use-cart"

interface ProductCard {
    data: Product
}


const ProductCard:React.FC<ProductCard> = ({data}) => {

  const router =useRouter();

  const handleClick = () => {
    router.push(`/product/${data?.id}`);
  }
  const cart = useCart()
  const previewModal = usePreviewModal()

  const onPreview:MouseEventHandler<HTMLButtonElement> = (event) => {
    event.stopPropagation()
    //override the maindiv onClick
    previewModal.onOpen(data)
  }

  const onAddToCart:MouseEventHandler<HTMLButtonElement> = (event) => {
    event.stopPropagation()
    //override the maindiv onClick
    cart.addItem(data)
  }

  return (
    <div onClick={handleClick} className="cursor-pointer bg-white group rounded-xl border p-3 space-y-4">
        {/* Images and Actions */}
    <div className="aspect-square rounded-xl bg-gray-100 relative">
    <Image alt="image" src={data?.images?.[0]?.url} fill className="aspect-square object-cover rounded-md"/>
          {/* group here allow you to show objects when hover so preview of it for instance */}
    <div className="opacity-0 group-hover:opacity-100 transition absolute w-full px-6 bottom-5">
      <div className="flex gap-x-6 justify-center">
        <IconButton onClick={onPreview} icon={<Expand size={20} className="text-gray-600"/>}/>
        <IconButton onClick={onAddToCart} icon={<ShoppingCart  size={20} className="text-gray-600"/>}/>
      </div>
    </div>
    
    </div>
    {/* Description */}
    <div>
      <p className="font-semibold text-lg">
        {data.name}
      </p>
      <p className="text-sm text-gray-500">
        {data.category?.name}
      </p>
    </div>
        {/* Price */}
        <div className="flex items-center justify-between">
          <Currency value={data?.price}/>
        </div>

    </div>
  )
}

export default ProductCard