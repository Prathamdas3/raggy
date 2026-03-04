import Layout from '@/components/common/Layout'
import { useChatCreate } from '@/store/chat'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/chat/$id')({
  component: RouteComponent,
})

function RouteComponent() {
  const { id } = Route.useParams()
  const getContent = useChatCreate((s) => s.getContent)
  const { content } = getContent(id) ?? {}

  return <Layout>
    <section className='h-full max-w-5xl mx-auto container py-2'>

    </section>
  </Layout>
}
