import Layout from '@/components/common/Layout'
import { Input } from '@/components/ui/input'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/quiz/')({
    component: RouteComponent,
})

function RouteComponent() {
    return <Layout>
        <section className='max-w-5xl space-y-4 mx-auto container'>
            <Input />
        </section>
    </Layout>
}
