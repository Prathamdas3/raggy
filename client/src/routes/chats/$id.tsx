import { useState, useRef, useEffect } from "react";
import Header from "@/components/Header";
import AppSidebar from "@/components/Sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
import { createFileRoute } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Send, Loader2, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const Route = createFileRoute("/chats/$id")({
	component: RouteComponent,
});

type Message = {
	id: string;
	role: "user" | "assistant" | "system";
	content: string;
	timestamp: Date;
};

function SystemMessage({ children }: { children: React.ReactNode }) {
	return (
		<div className="flex justify-center py-4">
			<div className="bg-muted border rounded-lg px-4 py-2 flex items-center gap-2 text-sm text-muted-foreground">
				{children}
			</div>
		</div>
	);
}

function ChatSkeleton() {
	return (
		<div className="flex gap-3 mb-4 px-4">
			<Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
			<div className="flex-1 space-y-2 max-w-[80%]">
				<Skeleton className="h-4 w-full" />
				<Skeleton className="h-4 w-5/6" />
				<Skeleton className="h-4 w-4/6" />
				<Skeleton className="h-4 w-full" />
				<Skeleton className="h-4 w-3/6" />
			</div>
		</div>
	);
}

function MessageBubble({ message }: { message: Message }) {
	const isUser = message.role === "user";

	if (message.role === "system") {
		return <SystemMessage>{message.content}</SystemMessage>;
	}

	return (
		<div
			className={cn(
				"flex gap-3 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-500",
				isUser ? "flex-row-reverse" : "flex-row"
			)}
		>
			{/* Avatar */}
			<div
				className={cn(
					"h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold",
					isUser
						? "bg-primary text-primary-foreground"
						: "bg-muted text-muted-foreground"
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
						: "bg-muted text-foreground"
				)}
			>
				{isUser ? (
					<p className="text-sm whitespace-pre-wrap">{message.content}</p>
				) : (
					<div className="prose prose-sm dark:prose-invert max-w-none">
						<ReactMarkdown remarkPlugins={[remarkGfm]}>
							{message.content}
						</ReactMarkdown>
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

function ChatView() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [input, setInput] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [isProcessing, setIsProcessing] = useState(true);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const textareaRef = useRef<HTMLTextAreaElement>(null);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages, isLoading, isProcessing]);

	// Simulate initial summary generation
	useEffect(() => {
		// Simulate API call to generate summary
		const timer = setTimeout(() => {
			const summaryMessage: Message = {
				id: "summary-1",
				role: "assistant",
				content: `# Document Summary

I've analyzed your document and here are the key insights:

## Main Topics
- **Introduction to Machine Learning**: Overview of supervised and unsupervised learning approaches
- **Neural Networks**: Deep dive into architecture and training methods
- **Practical Applications**: Real-world use cases in healthcare, finance, and technology

## Key Takeaways
1. Machine learning models require quality training data
2. Overfitting can be prevented through regularization techniques
3. Cross-validation is essential for model evaluation

## Statistics
- Total Pages: 45
- Key Concepts Identified: 23
- Code Examples: 12

Feel free to ask me any questions about the content!`,
				timestamp: new Date(),
			};
			setMessages([summaryMessage]);
			setIsProcessing(false);
		}, 3000); // Simulate 3 seconds processing time

		return () => clearTimeout(timer);
	}, []);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!input.trim() || isLoading || isProcessing) return;

		const userMessage: Message = {
			id: Date.now().toString(),
			role: "user",
			content: input.trim(),
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInput("");
		setIsLoading(true);

		// Simulate AI response
		setTimeout(() => {
			const aiMessage: Message = {
				id: (Date.now() + 1).toString(),
				role: "assistant",
				content: `That's a great question! Based on the document, here's what I found:

**Answer**: ${userMessage.content}

The document mentions several related points:
- First key point about your question
- Second important consideration
- Third relevant detail

Would you like me to elaborate on any of these points?`,
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, aiMessage]);
			setIsLoading(false);
		}, 1500);
	};

	const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(e);
		}
	};

	return (
		<div className="flex flex-col h-full">
			{/* Messages Area */}
			<div className="flex-1 overflow-y-auto px-4 py-6">
				<div className="max-w-3xl mx-auto">
					{isProcessing ? (
						<>
							<SystemMessage>
								<Clock className="h-4 w-4" />
								<span>We're processing your content. This may take a minute.</span>
							</SystemMessage>
							<ChatSkeleton />
							<ChatSkeleton />
						</>
					) : (
						<>
							{messages.map((message) => (
								<MessageBubble key={message.id} message={message} />
							))}
							{isLoading && <TypingIndicator />}
						</>
					)}
					<div ref={messagesEndRef} />
				</div>
			</div>

			{/* Input Area */}
			<div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
				<div className="max-w-3xl mx-auto px-4 py-4">
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
		</div>
	);
}

function RouteComponent() {
	const { id } = Route.useParams();

	return (
		<SidebarProvider>
			<AppSidebar />
			<div className="max-h-dvh w-full">
				<Header />
				<main className="w-full h-[calc(100dvh-3.5rem)]">
					<ChatView />
				</main>
			</div>
		</SidebarProvider>
	);
}