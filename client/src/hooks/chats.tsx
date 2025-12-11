import { apiClient } from "@/lib/axios";
import { tryCatch } from "@/lib/trycatch";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

interface Chats {
	data: {
		id: string;
		chat_name: string;
		is_bookmarked: boolean;
		created_at: string;
		updated_at: string;
	}[];
	message: string;
	status: string;
}
export type Chat = Chats["data"][0];

type UpdateChatInput = {
	chat_id: string;
	chat_name?: string;
	is_bookmarked?: boolean;
};

type CreateChatInput = {
	link?: string;
	file?: File;
};

type SingleChat = {
	message: string;
	status: string;
	data: {
		task_id: string;
		chat_id: string;
	};
};

interface ExportChat {
	data: {
		task_id: string;
	};
	message: string;
	status: string;
}

export function useGetAllChats() {
	return useQuery({
		queryKey: ["getAllChats"],
		queryFn: async () => {
			const { data } = await apiClient.get<Chats>("/chats");
			return data?.data;
		},
		retry: false,
		staleTime: 10 * 60 * 1000,
		gcTime: 10 * 60 * 1000,
	});
}

export function useCreateChat() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationKey: ["createChat"],
		mutationFn: async ({ link, file }: CreateChatInput) => {
			if (link && file) {
				throw new Error("Provide either link or file, not both");
			}

			if (!link && !file) {
				throw new Error("Either link or file is required");
			}

			if (link) {
				const { data, error } = await tryCatch(
					apiClient.post<SingleChat>("/chats/links", {
						link,
					}),
				);
				if (error) {
					throw error;
				}
				return data?.data?.data;
			}

			if (file) {
				const formData = new FormData();
				formData.append("file", file);

				const { data, error } = await tryCatch(
					apiClient.post<SingleChat>("/chats/file", formData, {
						headers: {
							"Content-Type": "multipart/form-data",
						},
					}),
				);

				if (error) {
					throw error;
				}

				return data?.data?.data;
			}
		},
		retry: false,
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["getAllChats"],
			});
			toast.success("Successfully created the chat");
		},
		onError: () => {
			toast.error("Failed to create the chat");
		},
	});
}

export function useDeleteChat() {
	const queryclient = useQueryClient();

	return useMutation({
		mutationKey: ["deleteChat"],
		mutationFn: async (chat_id: string) => {
			const { data, error } = await tryCatch(
				apiClient.delete(`/chats/${chat_id}`),
			);
			if (error) {
				throw error;
			}
			return data?.data;
		},
		retry: false,
		gcTime: 10 * 60 * 1000,
		onSuccess: () => {
			queryclient.invalidateQueries({ queryKey: ["getAllChats"] });
			toast.success("Successfully deleted the chat");
		},
		onError: () => {
			toast.error("Failed to delete the chat");
		},
	});
}

export function useUpdateChat() {
	const queryclient = useQueryClient();

	return useMutation({
		mutationKey: ["updateChat"],
		mutationFn: async ({
			chat_id,
			chat_name,
			is_bookmarked,
		}: UpdateChatInput) => {
			if (chat_name === undefined && is_bookmarked === undefined) {
				throw new Error("Nothing to update");
			}

			const payload: Partial<
				Pick<UpdateChatInput, "chat_name" | "is_bookmarked">
			> = {};

			if (chat_name !== undefined) {
				payload.chat_name = chat_name;
			}
			if (is_bookmarked !== undefined) {
				payload.is_bookmarked = is_bookmarked;
			}

			const { data } = await apiClient.patch(`/chats/${chat_id}`, payload);

			return data.data;
		},
		retry: false,
		gcTime: 10 * 60 * 1000,
		onSuccess: () => {
			queryclient.invalidateQueries({ queryKey: ["getAllChats"] });
			toast.success("Successfully updated the chat");
		},
		onError: () => {
			toast.error("Failed to update the chat");
		},
	});
}

export function useExportChat() {
	return useMutation({
		mutationKey: ["exportChat"],
		mutationFn: async (chatId: string) => {
			const { data, error } = await tryCatch(
				apiClient.get<ExportChat>(`/chats/${chatId}/export`),
			);
			if (error) {
				throw error;
			}
			return data?.data?.data;
		},
		gcTime: 10 * 60 * 1000,
		retry: false,
		onError: () => {
			toast.error("Failed to Export your chat");
		},
		onSuccess: () => {
			toast.success("Successfully started exporting your chat");
		},
	});
}
