import { Download, Forward, Trash } from "lucide-react";
import TooltipIcon from "./TooltipIcons";
import { useDeleteChat, useExportChat } from "@/hooks/chats";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { useGetTaskDetails } from "@/hooks/task";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { apiClient } from "@/lib/axios";

interface Props {
	tools: boolean;
}

async function downloadPdf(url: string) {
	try {
		const toastId = toast.loading("Preparing download...");

		// Correct axios call
		const response = await apiClient.get(url, {
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

export default function Header({ tools }: Props) {
	const { mutate: deleteChat } = useDeleteChat();
	const { mutate: exportChat, isPending } = useExportChat();

	const router = useNavigate();
	const params = useLocation().pathname.split("/").reverse()[0];

	const [taskId, setTaskId] = useState<string | undefined>();
	const { data: task } = useGetTaskDetails(taskId);

	const hasHandledResult = useRef(false);

	useEffect(() => {
		if (!task) return;
		if (task.status !== "SUCCESS") return;
		if (!task.result) return;
		if (hasHandledResult.current) return;

		hasHandledResult.current = true;
		downloadPdf(task.result as string);
	}, [task]);

	const onDelete = () => {
		deleteChat(params, {
			onSuccess: () => {
				router({ to: "/chats", replace: true });
			},
		});
	};

	const onExport = () => {
		hasHandledResult.current = false; // reset for new export

		exportChat(params, {
			onSuccess: (res) => {
				setTaskId(res.task_id);
			},
		});
	};

	return (
		<header className="flex justify-between border-b py-3 items-center px-3 w-full">
			<h3 className="text-xl font-semibold">App Name</h3>

			{tools && (
				<nav className="flex gap-2">
					<TooltipIcon
						Icon={Download}
						content="Download chat"
						action={onExport}
						disabled={isPending}
					/>
					<TooltipIcon Icon={Forward} content="Share chat" />
					<TooltipIcon Icon={Trash} content="Delete chat" action={onDelete} />
				</nav>
			)}
		</header>
	);
}
