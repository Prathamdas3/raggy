import Layout from '@/components/common/Layout'
import { useSidebar } from '@/components/ui/sidebar'
import { createFileRoute } from '@tanstack/react-router'
import { useEffect } from 'react'

export const Route = createFileRoute('/quiz/$id')({
    component: RouteComponent,
})

function RouteComponent() {
    const { setOpen } = useSidebar()
    useEffect(() => {
        setOpen(false)
    }, [])
    return <Layout header>
        <section className='h-full max-w-5xl mx-auto container '>
        </section>
    </Layout>
}
