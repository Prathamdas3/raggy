import { useGetSummary } from "@/hooks/message";
import { useGetTaskDetails } from "@/hooks/task";
import { useTasksIdStore } from "@/store/task";
import { useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import AudioPlayer from "./AudioPlayer";
import ChatSkeleton from "./ChatSkeleton";
import { cn } from "@/lib/utils";

export default function SummarySection({ chatId }: { chatId: string }) {
	const taskId = useTasksIdStore((s) => s.taskId);
	const clearTaskId = useTasksIdStore((s) => s.setTaskId);

	const { data: task } = useGetTaskDetails(taskId);

	const isTaskSuccess = task?.status === "SUCCESS";
	const isTaskFailed = task?.status === "FAILURE";
	const shouldFetchSummary =
		Boolean(chatId) && (taskId == null || isTaskSuccess);

	const {
		data: summaryData,
		isLoading,
		isError,
	} = useGetSummary({ chatId: chatId, shouldRun: shouldFetchSummary });

	// clear taskId AFTER success (single responsibility)
	useEffect(() => {
		if (isTaskSuccess) {
			clearTaskId(undefined);
		}
	}, [isTaskSuccess, clearTaskId]);

	// -------- UI STATE NORMALIZATION --------
	const summaryText = summaryData?.summary_text?.trim() || null;
	const audioUrl = summaryData?.audio_url?.trim() || null;

	// -------- RENDER --------
	if (taskId && !isTaskSuccess) {
		return <ChatSkeleton />;
	}

	if (isLoading) {
		return <ChatSkeleton />;
	}

	if (isError) {
		return <div>Failed to prepare your summary</div>;
	}

	if (!summaryText && !audioUrl) {
		return (
			<div className="text-muted-foreground italic">
				Summary not available yet.
			</div>
		);
	}

	if (isTaskFailed) {
		return (
			<div className="text-red-500 bg-red-500/10 p-3 rounded-lg flex items-center gap-3 animate-in fade-in slide-in-from-bottom-1">
				<span className="font-medium">
					Something went wrong while preparing your summary.
				</span>
				<button
					type="button"
					className="underline text-sm"
					onClick={() => {
						clearTaskId(undefined); // reset
					}}
				>
					Try again
				</button>
			</div>
		);
	}

	return (
		<section className="space-y-4">
			<div
				className={cn(
					"flex gap-3 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-500 flex-row",
				)}
			>
				{/* Avatar */}
				<div
					className={cn(
						"h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold bg-muted text-muted-foreground",
					)}
				>
					AI
				</div>
				<div
					className={cn(
						"rounded-2xl px-4 py-3 max-w-[80%] bg-muted text-foreground",
					)}
				>
					{summaryText && (
						<div className="prose prose-sm dark:prose-invert max-w-none">
							<ReactMarkdown remarkPlugins={[remarkGfm]}>
								{summaryText}
							</ReactMarkdown>
						</div>
					)}

					{audioUrl && <AudioPlayer src={audioUrl} />}
				</div>
			</div>
		</section>
	);
}
