import { useChatCreate } from '@/store/chat'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/chat/$id')({
  component: RouteComponent,
})

function RouteComponent() {
  const { id } = Route.useParams()
  const getContent = useChatCreate((s) => s.getContent)
  const { content } = getContent(id) ?? {}
  
  return <div>Hello "/chat/$id"!</div>
}
