import Header from "@/components/Header";
import AppSidebar from "@/components/Sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
import { createFileRoute } from "@tanstack/react-router";
import SummarySection from "@/components/chats/SummarySection";
import { Textarea } from "@/components/ui/textarea";
import { useEffect, useRef, useState } from "react";
import { Loader2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
	useGetAllMessages,
	useAskQuerstion,
	useGetAnser,
	type AnswerItem,
} from "@/hooks/message";
import { useGetTaskDetails } from "@/hooks/task";
import MessageBubble from "@/components/chats/MessageBubble";
import Protected from "@/layouts/protected-layout";

export const Route = createFileRoute("/chats/$id")({
	component: RouteComponent,
});

/* -------------------- TYPES -------------------- */

type ChatMessage = {
	id: string;
	role: "user" | "assistant";
	content: string;
	audio_url?: string | null;
	created_at: string;
	status?: "pending";
};

/* -------------------- COMPONENT -------------------- */

function RouteComponent() {
	const { id: chatId } = Route.useParams();

	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const [input, setInput] = useState("");

	// chat timeline
	const [messages, setMessages] = useState<ChatMessage[]>([]);

	// in-flight state
	const [taskId, setTaskId] = useState<string>();
	const [questionId, setQuestionId] = useState<string>();

	/* -------------------- API -------------------- */

	const { data: history } = useGetAllMessages({ chatId });
	const { mutate: askQuestion, isPending: isAsking } = useAskQuerstion();
	const { data: task } = useGetTaskDetails(taskId);
	const isTaskRunning =
		task?.status === "PENDING" || task?.status === "STARTED";
	const isTaskSuccess = task?.status === "SUCCESS";
	const { data: answer } = useGetAnser({
		chatId,
		querstionId: questionId,
		shouldFetch: isTaskSuccess,
	});

	/* -------------------- INITIAL LOAD (FLATTEN) -------------------- */

	useEffect(() => {
		if (!history) return;

		const flat: ChatMessage[] = history.flatMap(
			({ question, responses }: any) => [
				{
					id: question.id,
					role: "user",
					content: question.content,
					audio_url: question.audio_url || null,
					created_at: question.created_at,
				},
				...responses.map((r: any) => ({
					id: r.id,
					role: "assistant",
					content: r.content,
					audio_url: r.audio_url || null,
					created_at: r.created_at,
				})),
			],
		);

		flat.sort(
			(a, b) =>
				new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
		);

		setMessages(flat);
	}, [history]);

	/* -------------------- ANSWER ARRIVED -------------------- */

	useEffect(() => {
		if (!answer) return;

		setMessages((prev) => {
			// remove pending assistant message
			const withoutPending = prev.filter((m) => m.status !== "pending");

			return [
				...withoutPending,
				...answer.map((r: AnswerItem) => ({
					id: r.answer_id,
					role: "assistant" as const,
					content: r.answer,
					audio_url: r.audio_url || null,
					created_at: Date.now().toLocaleString(),
				})),
			];
		});

		setTaskId(undefined);
		setQuestionId(undefined);
	}, [answer]);

	/* -------------------- SEND QUESTION -------------------- */

	const handleSubmit = () => {
		if (!input.trim() || isTaskRunning) return;

		const questionText = input;
		setInput("");
		textareaRef.current?.focus();

		// append USER message
		const userMessage: ChatMessage = {
			id: crypto.randomUUID(),
			role: "user",
			content: questionText,
			created_at: new Date().toISOString(),
		};

		// append PENDING assistant message
		const pendingAssistant: ChatMessage = {
			id: crypto.randomUUID(),
			role: "assistant",
			content: "Thinking…",
			created_at: new Date().toISOString(),
			status: "pending",
		};

		setMessages((prev) => [...prev, userMessage, pendingAssistant]);

		askQuestion(
			{ chatId, question: questionText },
			{
				onSuccess: (res) => {
					setTaskId(res.task_id);
					setQuestionId(res.question_id);
				},
			},
		);
	};

	const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSubmit();
		}
	};

	/* -------------------- RENDER -------------------- */

	return (
		<Protected>
			<SidebarProvider>
				<AppSidebar />
				<div className="max-h-dvh w-full">
					<Header tools />
					<main className="h-[calc(100dvh-3.5rem)] flex flex-col">
						{/* SCROLL AREA */}
						<div className="flex-1 overflow-y-auto">
							<div className="mx-auto max-w-3xl px-4 py-8 space-y-6">
								<SummarySection chatId={chatId} />

								{messages.map((msg) => (
									<MessageBubble
										key={msg.id}
										message={msg.content}
										role={msg.role}
										audio_url={msg.audio_url}
									/>
								))}
							</div>
						</div>

						{/* INPUT BAR */}
						<div className="border-t bg-background/95 backdrop-blur">
							<div className="mx-auto max-w-3xl px-4 py-4">
								<form
									onSubmit={(e) => {
										e.preventDefault();
										handleSubmit();
									}}
									className="relative"
								>
									<Textarea
										ref={textareaRef}
										value={input}
										onChange={(e) => setInput(e.target.value)}
										onKeyDown={handleKeyDown}
										placeholder={
											isTaskRunning
												? "Waiting for response…"
												: "Ask me anything…"
										}
										className="min-h-[60px] pr-12 resize-none"
										disabled={isTaskRunning || isAsking}
									/>

									<Button
										type="submit"
										size="icon"
										className="absolute right-2 bottom-2 h-8 w-8"
										disabled={!input.trim() || isTaskRunning || isAsking}
									>
										{isAsking || isTaskRunning ? (
											<Loader2 className="h-4 w-4 animate-spin" />
										) : (
											<Send className="h-4 w-4" />
										)}
									</Button>
								</form>
							</div>
						</div>
					</main>
				</div>
			</SidebarProvider>
		</Protected>
	);
}
