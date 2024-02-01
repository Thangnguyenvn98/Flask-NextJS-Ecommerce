import { Product } from "@/types";
import qs from "query-string"
const URL = `${process.env.NEXT_PUBLIC_API_URL}/products`

//Filter string for the query ?= for website
interface Query {
    categoryId?: string;
    colorId?: string;
    sizeId?: string;
    isFeatured?: boolean;
}


const getProducts = async (query:Query):Promise<Product[]> => {
    const url = qs.stringifyUrl({
        url:URL,
        query:{
            colorId: query.colorId,
            sizeId: query.sizeId,
            categoryId:query.categoryId,
            isFeatured: query.isFeatured,
        }
    })
    //this will add ?colorId=numberhjkashd to the existing URL 
      
    const res = await fetch(url, {cache: "no-store"})

    return res.json()
}

export default getProducts