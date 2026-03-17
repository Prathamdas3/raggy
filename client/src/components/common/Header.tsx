// import { useDeleteChat, useExportChat } from "@/hooks/chats";
// import { useLocation, useNavigate } from "@tanstack/react-router";
// import { useGetTaskDetails } from "@/hooks/task";
// import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import axios from "axios";
import { useSidebar } from "../ui/sidebar";
async function downloadPdf(url: string) {
    try {
        const toastId = toast.loading("Preparing download...");
        // Correct axios call
        const response = await axios.get(url, {
            withCredentials: true,
            responseType: "blob",
        });
        // Create blob URL
        const blobUrl = URL.createObjectURL(response.data);
        const urlPath = new URL(url).pathname;
        const filename = urlPath.split("/").pop() || "chat-export.pdf";
        // Trigger download
        const link = document.createElement("a");
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setTimeout(() => URL.revokeObjectURL(blobUrl), 200);
        toast.success("Download started!", { id: toastId });
    } catch (error) {
        console.error("Download failed:", error);
        toast.error("Failed to download. Opening in new tab instead...");
        window.open(url, "_blank", "noopener,noreferrer");
    }
}

// const { mutate: deleteChat } = useDeleteChat();
// const { mutate: exportChat, isPending } = useExportChat();
// const router = useNavigate();
// const params = useLocation().pathname.split("/").reverse()[0];
// const [taskId, setTaskId] = useState<string | undefined>();
// const { data: task } = useGetTaskDetails(taskId);
// const hasHandledResult = useRef(false);
// useEffect(() => {
//     if (!task) return;
//     if (task.status !== "SUCCESS") return;
//     if (!task.result) return;
//     if (hasHandledResult.current) return;
//     hasHandledResult.current = true;
//     downloadPdf(task.result as string);
// }, [task]);
// const onDelete = () => {
//     deleteChat(params, {
//         onSuccess: () => {
//             router({ to: "/", replace: true });
//         },
//     });
// };
// const onExport = () => {
//     hasHandledResult.current = false; // reset for new export
//     exportChat(params, {
//         onSuccess: (res) => {
//             setTaskId(res.task_id);
//         },
//     });
// };


export default function Header({ tools }: { tools?: React.ReactNode }) {
  const { open } = useSidebar()

  return (
    <header className="flex justify-between border-b h-14 items-center px-3 w-full">
      <h3 className={`text-xl font-semibold ${open ? "invisible" : "visible"}`}>Raggy</h3>
      {tools && <nav className="flex gap-2">{tools}</nav>}
    </header>
  )
}