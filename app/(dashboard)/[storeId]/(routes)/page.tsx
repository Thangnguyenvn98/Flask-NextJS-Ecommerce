import axios from "axios"

interface DashboardProps {
    params: {storeId: string}
}
const DashboardPage: React.FC<DashboardProps> = async ({params}) => {
    //params is the params of url, storeId is the app router name [storeId]
   
    const response = await fetch(`http://127.0.0.1:8080/api/store/${params.storeId}`)
    const store = await response.json()
    return (
        <div>Active Store: {store?.name}</div>
    )
}

export default DashboardPage