'use client'
import { Button } from "@/components/ui/button";
import { navigate } from "../actions";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
    const { push } = useRouter();
    const routing = () => {
        push('/api/login')
    }

  return (
 
    <div className="p-4">
        <Button onClick={routing}>Click me</Button>
    </div>
  )
}
