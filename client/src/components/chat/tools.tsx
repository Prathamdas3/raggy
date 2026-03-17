import { Download, Forward, Network, StickyNote, Trash } from "lucide-react"
import { useChatOptions } from "./store"
import TooltipIcon from "../common/Tooltip"

// components/chat/ChatTools.tsx
export function ChatTools() {
    const { setDocTree, setNotes } = useChatOptions(s => s)
    return <>
        <TooltipIcon Icon={Network} content="Document tree" action={setDocTree} />
        <TooltipIcon Icon={StickyNote} content="Notes" action={setNotes} />
        <TooltipIcon Icon={Download} content="Download chat" />
        <TooltipIcon Icon={Forward} content="Share chat" />
        <TooltipIcon Icon={Trash} content="Delete chat" />
    </>
}