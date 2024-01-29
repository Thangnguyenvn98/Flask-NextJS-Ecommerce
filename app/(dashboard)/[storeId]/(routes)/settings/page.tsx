import { redirect } from 'next/navigation';
import { SettingsForm } from './components/settings-form';
import { getSession } from '@auth0/nextjs-auth0';

interface SettingsPageProps {
    params: { 
        storeId: string;
    }
}

const SettingsPage: React.FC<SettingsPageProps>= async ({params}) => {
    const session = await getSession()
    const user = session?.user
    const userId = user?.sub.split('|')[1]
    if(!userId) {
        redirect('/auth/login')
    }
 
    const response = await fetch(`http://127.0.0.1:8080/api/store/${params.storeId}/${userId}`,{
        cache: "no-cache"
    })
    console.log("helo")
  
    const store = await response.json()


  return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6"> 
        <SettingsForm initialData={store} />
        </div>
     
    </div>
  )
}

export default SettingsPage