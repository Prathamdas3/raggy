import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/chats/$id')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/$id"!</div>
}
