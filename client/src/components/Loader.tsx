import { Skeleton } from "@/components/ui/skeleton";

type MessageSkeletonProps = { isUser?: boolean };

function MessageSkeleton({ isUser = false }: MessageSkeletonProps) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} px-4 py-2`}>
      <div className={`max-w-[80%] ${isUser ? "text-right" : "text-left"}`}>
        <div className="flex items-end gap-3">
          {/* avatar */}
          {!isUser && <Skeleton className="h-9 w-9 rounded-full" />}
          {/* bubble */}
          <div className={`space-y-2 ${isUser ? "items-end" : "items-start"}`}>
            <Skeleton className={`h-4 w-32 rounded-md ${isUser ? "ml-auto" : ""}`} />
            <div className="space-y-2">
              <Skeleton className="h-3 w-[90%] rounded-md" />
              <Skeleton className="h-3 w-[70%] rounded-md" />
              <Skeleton className="h-3 w-[60%] rounded-md" />
            </div>
          </div>
          {/* small avatar for user if desired */}
          {isUser && <Skeleton className="h-7 w-7 rounded-full" />}
        </div>
      </div>
    </div>
  );
}

function SidebarSkeleton() {
  return (
    <aside className="w-64 min-w-[16rem] border-r px-4 py-6">
      <div className="mb-6">
        <Skeleton className="h-10 w-full rounded-md" />
      </div>

      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i.toString()} className="flex items-center gap-3">
            <Skeleton className="h-8 w-8 rounded-md" />
            <div className="flex-1">
              <Skeleton className="h-4 w-3/4 rounded-md mb-2" />
              <Skeleton className="h-3 w-1/2 rounded-md" />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6">
        <Skeleton className="h-9 w-full rounded-md" />
      </div>
    </aside>
  );
}

function ComposerSkeleton() {
  return (
    <div className="border-t px-4 py-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-full" />
        <div className="flex-1">
          <Skeleton className="h-10 w-full rounded-lg" />
        </div>
        <Skeleton className="h-10 w-28 rounded-lg" />
      </div>
    </div>
  );
}

export default function ChatSkeleton() {
  return (
    <div className="h-screen flex bg-surface-50">
      {/* Sidebar */}
      <SidebarSkeleton />

      {/* Main chat area */}
      <main className="flex-1 flex flex-col">
        {/* header */}
        <div className="border-b px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Skeleton className="h-8 w-8 rounded-full" />
            <Skeleton className="h-6 w-48 rounded-md" />
          </div>
          <div className="flex items-center gap-3">
            <Skeleton className="h-6 w-24 rounded-md" />
            <Skeleton className="h-8 w-8 rounded-md" />
          </div>
        </div>

        {/* messages scroll area */}
        <div className="flex-1 overflow-y-auto space-y-2 py-4">
          <div className="px-4">
            {/* multiple message skeletons to simulate conversation */}
            <MessageSkeleton />
            <MessageSkeleton isUser />
            <MessageSkeleton />
            <MessageSkeleton isUser />
            <MessageSkeleton />
          </div>
        </div>

        {/* composer */}
        <ComposerSkeleton />
      </main>

      {/* optional right panel - recommended or context */}
      <div className="w-80 min-w-[20rem] border-l px-4 py-6 hidden lg:block">
        <Skeleton className="h-6 w-40 rounded-md mb-4" />
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i.toString()}>
              <Skeleton className="h-4 w-full rounded-md mb-2" />
              <Skeleton className="h-3 w-3/4 rounded-md" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
