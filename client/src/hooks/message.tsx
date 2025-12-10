import { apiClient } from "@/lib/axios";
import { tryCatch } from "@/lib/trycatch";
import {  useQuery } from "@tanstack/react-query";


interface SummaryResult {
	message: string;
	status: string;
	data: {
		summary_text: string;
		audio_url: string;
	};
}

export function useGetSummary({
	chatId,
	shouldRun,
}: {
	chatId: string;
	shouldRun: boolean;
}) {
	return useQuery({
		queryKey: ["getSummary",chatId],
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
