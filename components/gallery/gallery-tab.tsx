import { Image as ImageType } from '@/types'
import React from 'react'
import { cn } from '@/lib/utils'
import Image from 'next/image'
import { Tab } from '@headlessui/react'

interface GalleryTabProps{
    image: ImageType
}

const GalleryTab:React.FC<GalleryTabProps> = ({image}) => {
  return (
    <Tab className="relative flex aspect-square cursor-pointer items-center justify-center rounded-md bg-white">

    </Tab>
  )
}

export default GalleryTab