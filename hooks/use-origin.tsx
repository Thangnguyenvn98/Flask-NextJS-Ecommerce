import { useState, useEffect } from "react"




export const useOrigin = () => {
    const [mounted,setMounted] = useState(false);
    let origin = typeof window !== "undefined" && window.location.origin ? window.location.origin : ""

    if (origin.includes(':3000')) {
        origin = origin.replace(':3000', ':8080');
    }
    useEffect(() => {
        setMounted(true)

    },[])

    if(!mounted) {
        return ''
    }

    return origin
}