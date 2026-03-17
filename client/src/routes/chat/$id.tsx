import Layout from '@/components/common/Layout'
import { useChatCreate, useChatOptions } from '@/components/chat/store'
import { createFileRoute } from '@tanstack/react-router'
import DocTreeViewer from '@/components/chat/id/DocTreeView'
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@/components/ui/resizable'
import ChatUI from '@/components/chat/id/ChatUi'
import { ChatTools } from '@/components/chat/tools'

export const Route = createFileRoute('/chat/$id')({
  component: RouteComponent,
})

function RouteComponent() {
  const { id } = Route.useParams()
  const getContent = useChatCreate((s) => s.getContent)
  const { content } = getContent(id) ?? {}
  const { doctree, notes } = useChatOptions((s) => s)

  const hasRight = doctree || notes

  return (
    <Layout tools={<ChatTools />} header>
      <ResizablePanelGroup orientation="horizontal" className="h-full w-full">

        {/* Left - Chat */}
        <ResizablePanel defaultSize={hasRight ? 60 : 100}>
          <ChatUI />
        </ResizablePanel>

        {/* Right column - only mounts when at least one panel is open */}
        {hasRight && (
          <>
            <ResizableHandle />
            <ResizablePanel defaultSize={40}>
              <ResizablePanelGroup orientation="vertical">

                {doctree && (
                  <>
                    <ResizablePanel defaultSize={notes ? 50 : 100}>
                      <div className="h-full overflow-auto">
                        <DocTreeViewer />
                      </div>
                    </ResizablePanel>
                    {notes && <ResizableHandle />}
                  </>
                )}

                {notes && (
                  <ResizablePanel defaultSize={doctree ? 50 : 100}>
                    <div className="h-full overflow-auto p-4 text-muted-foreground text-sm">
                      Notes panel
                    </div>
                  </ResizablePanel>
                )}

              </ResizablePanelGroup>
            </ResizablePanel>
          </>
        )}

      </ResizablePanelGroup>
    </Layout>
  )
}