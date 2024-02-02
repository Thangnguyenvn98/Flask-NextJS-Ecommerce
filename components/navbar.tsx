import { MainNav } from "@/components/main-nav"
import StoreSwitcher from "@/components/store-switcher"
import { getSession } from '@auth0/nextjs-auth0';
import axios from "axios";
import { redirect } from "next/navigation"

const Navbar = async () => {
  const session = await getSession();
  const user = session?.user;
  
  const userId = user?.sub.split('|')[1]
  if (!userId) {
      redirect('/api/auth/login')
  }

  let stores
  try {
    const response = await fetch(`http://127.0.0.1:8080/api/user/${userId}/stores`, {
      next : {revalidate : 300}
    })

    stores = await response.json()
    console.log(stores)
  }catch (error){
    console.log(error)
  }


  return (
    <div className="border-b">
        <div className="flex h-16 items-center px-4">
            <StoreSwitcher items={stores}/>
            <MainNav className="mx-6"/>
            <div className="ml-auto flex items-center space-x-4">
              <a href="/api/auth/logout">Logout</a>
            </div>
        </div>
    </div>
  )
}

export default Navbar