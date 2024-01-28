import { getSession } from '@auth0/nextjs-auth0';
import axios from 'axios';
import { redirect } from 'next/navigation';
import { SettingsForm } from './components/settings-form';


interface SettingsPageProps {
    params: { 
        storeId: string;
    }
}

const SettingsPage: React.FC<SettingsPageProps>= async ({params}) => {
    const session = await getSession();
    const user = session?.user;
    if (!user) {
        redirect('/api/auth/login')
    }
    let store
    const response = await axios.get(`http://127.0.0.1:8080/api/store/${params.storeId}`)
    store = response.data
    if (!store || !store.id){
        redirect('/')
    }
  return (
    <div className="flex-col">
        <div className="flex-1 space-y-4 p-8 pt-6"> 
        <SettingsForm initialData={store} />
        </div>
     
    </div>
  )
}

export default SettingsPage