import { apiClient } from "@/lib/axios";
import { tryCatch } from "@/lib/trycatch";
import { useMutation, useQuery } from "@tanstack/react-query";

interface SummaryResult {
	message: string;
	status: string;
	data: {
		summary_text: string;
		audio_url: string;
	};
}
interface AskQuestion {
	status: string;
	message: string;
	data: {
		question_id: string;
		task_id: string;
	};
}

export type ChatMessageEntity = {
	id: string; // UUID
	chat_id: string; // UUID
	user_id: string; // UUID
	question_id: string | null;
	sender: "user" | "llm";
	content: string;
	audio_url: string;
	created_at: string; // ISO datetime
	updated_at: string; // ISO datetime
};

export type QuestionWithResponses = {
	question: ChatMessageEntity;
	responses: ChatMessageEntity[];
};

export type GetChatMessagesResponse = {
	status: "success" | "error";
	message: string;
	data: QuestionWithResponses[];
	error: string | null;
};

export type AnswerItem = {
	answer_id: string; // UUID
	question_id: string; // UUID
	answer: string; // Markdown text
	audio_url: string; // Signed URL (may be empty if no audio)
};

export type GetAnswerResponse = {
	status: "success" | "error";
	message: string;
	data: AnswerItem[];
	error: string | null;
};

export function useGetSummary({
	chatId,
	shouldRun,
}: {
	chatId: string;
	shouldRun: boolean;
}) {
	return useQuery({
		queryKey: ["getSummary", chatId],
		queryFn: async () => {
			const { data, error } = await tryCatch(
				apiClient.get<SummaryResult>(`/chats/${chatId}/summary`),
			);
			if (error) {
				throw error;
			}
			return data?.data?.data;
		},
		gcTime: 10 * 60 * 1000,
		retry: false,
		enabled: shouldRun,
	});
}

export function useAskQuerstion() {
	return useMutation({
		mutationKey: ["askQuestion"],
		mutationFn: async ({
			chatId,
			question,
		}: {
			chatId: string;
			question: string;
		}) => {
			const { data, error } = await tryCatch(
				apiClient.post<AskQuestion>(`/messages/${chatId}/query`, { question }),
			);
			if (error) {
				throw error;
			}
			return data?.data?.data;
		},
		gcTime: 30 * 60 * 1000,
		retry: false,
	});
}

export function useGetAnser({
	chatId,
	querstionId,
	shouldFetch,
}: {
	chatId: string;
	querstionId?: string;
	shouldFetch: boolean;
}) {
	return useQuery({
		queryKey: ["getAnser", querstionId],
		queryFn: async () => {
			const { data } = await apiClient.get<GetAnswerResponse>(
				`/messages/${chatId}/query/${querstionId}`,
			);
			return data?.data;
		},
		gcTime: 10 * 60 * 1000,
		enabled: shouldFetch,
		retry: false,
	});
}

export function useGetAllMessages({ chatId }: { chatId: string }) {
	return useQuery({
		queryKey: ["getAllAnswers", chatId],
		enabled: Boolean(chatId?.trim),
		retry: false,
		gcTime: 2 * 60 * 1000,
		queryFn: async () => {
			const { data } = await apiClient.get<GetChatMessagesResponse>(
				`/chats/${chatId}/messages`,
			);
			return data?.data;
		},
	});
}
