import { createFileRoute } from '@tanstack/react-router'
import UploadDocs from '@/components/Upload'


export const Route = createFileRoute('/')({ component: App })

function App() {

  return (
    <div>
      <UploadDocs />
    </div>
  )
}
