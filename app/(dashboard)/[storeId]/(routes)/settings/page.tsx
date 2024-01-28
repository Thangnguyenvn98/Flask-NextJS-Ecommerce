import { redirect } from 'next/navigation';
import { SettingsForm } from './components/settings-form';
import { fetchStore } from '@/hooks/fetchStore';


interface SettingsPageProps {
    params: { 
        storeId: string;
    }
}

const SettingsPage: React.FC<SettingsPageProps>= async ({params}) => {
    const response = await fetch(`http://127.0.0.1:8080/api/store/${params.storeId}`)
    const store = await response.json()
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