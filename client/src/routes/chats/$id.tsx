import Header from "@/components/Header";
import AppSidebar from "@/components/Sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
import { createFileRoute } from "@tanstack/react-router";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SummarySection from "@/components/chats/SummarySection";
import { Textarea } from "@/components/ui/textarea";
import { useRef, useState } from "react";
import { Loader2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/chats/$id")({
	component: RouteComponent,
});

function SystemMessage({ children }: { children: React.ReactNode }) {
	return (
		<div className="flex justify-center py-4">
			<div className="bg-muted border rounded-lg px-4 py-2 flex items-center gap-2 text-sm text-muted-foreground">
				{children}
			</div>
		</div>
	);
}

function MessageBubble({
	message,
	role = "assistant",
}: {
	message: string;
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
					</div>
				)}
			</div>
		</div>
	);
}

function TypingIndicator() {
	return (
		<div className="flex gap-3 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
			<div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0 text-xs font-semibold text-muted-foreground">
				AI
			</div>
			<div className="bg-muted rounded-2xl px-4 py-3">
				<div className="flex gap-1">
					<div className="h-2 w-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:-0.3s]" />
					<div className="h-2 w-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:-0.15s]" />
					<div className="h-2 w-2 bg-muted-foreground/50 rounded-full animate-bounce" />
				</div>
			</div>
		</div>
	);
}

function RouteComponent() {
	const { id } = Route.useParams();
	const [input, setInput] = useState("");
	const [isLoading, _setIsLoading] = useState(false);
	const [isProcessing, _setIsProcessing] = useState(true);
	const textareaRef = useRef<HTMLTextAreaElement>(null);

	const handleKeyDown = () => {};

	const handleSubmit = () => {};

	return (
		<SidebarProvider>
			<AppSidebar />
			<div className="max-h-dvh w-full">
				<Header tools />
				<main className="h-[calc(100dvh-3.5rem)] flex flex-col">
					{/* SCROLLABLE CONTENT */}
					<div className="flex-1 overflow-y-auto">
						<div className="mx-auto max-w-3xl px-4 py-8 space-y-6">
							<SummarySection chatId={id} />
						</div>
					</div>

					{/* INPUT BAR */}
					<div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
						<div className="mx-auto max-w-3xl px-4 py-4">
							<form onSubmit={handleSubmit} className="relative">
								<Textarea
									ref={textareaRef}
									value={input}
									onChange={(e) => setInput(e.target.value)}
									onKeyDown={handleKeyDown}
									placeholder={
										isProcessing
											? "Processing…"
											: "Ask me anything about your document..."
									}
									className="min-h-[60px] max-h-[200px] pr-12 resize-none"
									disabled={isLoading || isProcessing}
								/>

								<Button
									type="submit"
									size="icon"
									className="absolute right-2 bottom-2 h-8 w-8"
									disabled={!input.trim() || isLoading || isProcessing}
								>
									{isLoading ? (
										<Loader2 className="h-4 w-4 animate-spin" />
									) : (
										<Send className="h-4 w-4" />
									)}
								</Button>
							</form>

							<p className="text-xs text-muted-foreground mt-2 text-center">
								{isProcessing
									? "Please wait while we process your content"
									: "Press Enter to send, Shift+Enter for new line"}
							</p>
						</div>
					</div>
				</main>
			</div>
		</SidebarProvider>
	);
}
