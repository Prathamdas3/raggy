import UploadDocs from '@/components/chat/new/Upload';
import Layout from '@/components/common/Layout';
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/chat/')({
    component: RouteComponent,
})
function getPrompt(): string {
    const currentTime = new Date().getHours();

    if (currentTime > 0 && currentTime <= 12) {
        return "Good morning, what are we learning today?";
    } else if (currentTime > 12 && currentTime <= 16) {
        return "Afternoon grind, let's get it.";
    } else if (currentTime > 16 && currentTime <= 21) {
        return "Evening session, you've got this.";
    } else {
        return "Late night learner, respect.";
    }
}
function RouteComponent() {
    return (
        <Layout>
            <section className='flex flex-col items-center justify-center h-full'>

                <h3 className="text-center font-semibold text-3xl text-gray-600 mb-4">
                    {getPrompt()}
                </h3>

                <UploadDocs />
            </section>
        </Layout>
    )
}
