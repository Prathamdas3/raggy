import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import AudioPlayer from "./AudioPlayer";

function SystemMessage({ children }: { children: React.ReactNode }) {
	return (
		<div className="flex justify-center py-4">
			<div className="bg-muted border rounded-lg px-4 py-2 flex items-center gap-2 text-sm text-muted-foreground">
				{children}
			</div>
		</div>
	);
}

export default function MessageBubble({
	message,
	role = "assistant",
	audio_url,
}: {
	message: string;
	audio_url?: string | null;
	role: string;
}) {
	const isUser = role === "user";

	if (role === "system") {
		return <SystemMessage>{message}</SystemMessage>;
	}

	return (
		<div
			className={cn(
				"flex gap-3 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-500",
				isUser ? "flex-row-reverse" : "flex-row",
			)}
		>
			{/* Avatar */}
			<div
				className={cn(
					"h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold",
					isUser
						? "bg-primary text-primary-foreground"
						: "bg-muted text-muted-foreground",
				)}
			>
				{isUser ? "You" : "AI"}
			</div>

			{/* Message Content */}
			<div
				className={cn(
					"rounded-2xl px-4 py-3 max-w-[80%]",
					isUser
						? "bg-primary text-primary-foreground"
						: "bg-muted text-foreground",
				)}
			>
				{isUser ? (
					<p className="text-sm whitespace-pre-wrap">{message}</p>
				) : (
					<div className="prose prose-sm dark:prose-invert max-w-none">
						<ReactMarkdown remarkPlugins={[remarkGfm]}>{message}</ReactMarkdown>
						{audio_url && <AudioPlayer src={audio_url} />}
					</div>
				)}
			</div>
		</div>
	);
}
