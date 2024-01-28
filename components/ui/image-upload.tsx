'use client'

import { useEffect, useState } from "react";

interface ImageUploadProps {
    disabled?: boolean;
    onChange: (value: string) => void;
    onRemove: (value: string) => void;
    value: string[];
}


const ImageUpload:React.FC<ImageUploadProps> = ({
    disabled,onChange,onRemove,value
}) => {
    const [mounted,setMounted] = useState(false);

    useEffect(() => {
        setMounted(true)

    },[])

    if(!mounted) {
        return null
    }
    return (
        <div>ImageUpload</div>
    )
}

export default ImageUpload
