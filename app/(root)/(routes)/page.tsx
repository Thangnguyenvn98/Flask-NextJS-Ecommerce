"use client"

import { useEffect, useState } from "react"

import { useStoreModal } from "@/hooks/use-store-modal"
import { useUser } from "@auth0/nextjs-auth0/client"
import axios from "axios"

const SetupPage = () => {
  const onOpen = useStoreModal((state)=> state.onOpen)
  const isOpen = useStoreModal((state)=> state.isOpen)
  const [isDataSet, setIsDataSet] = useState(false)
  const {user, isLoading, error} = useUser()

useEffect(() =>{
  
    const sendUserInfo = async () => {
      if(!isLoading && !isDataSet && user ) {

        try {
          const response = await axios.post('/api/user', user);
          console.log(response.data);
          // Set isUserDataSent to true after sending user data
          setIsDataSet(true);
        } catch (error) {
          console.error(error);
        }
      }
   } 
   sendUserInfo()
   
  
  

  if (!isOpen) {
    onOpen()
  }
},[isOpen,onOpen,isLoading,user,isDataSet])

  return null;
  

}

export default SetupPage