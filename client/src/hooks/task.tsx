import { apiClient } from "@/lib/axios";
import { useQuery } from "@tanstack/react-query";

interface TaskResult {
	message?: string;
	error?: Error;
	status: "PENDING" | "FAILURE" | "SUCCESS" | "STARTED";
	result?: unknown;
	task_id: string;
}

export function useGetTaskDetails(taskId?: string) {
	return useQuery({
		queryKey: ["taskDetails", taskId],
		queryFn: async () => {
			const { data } = await apiClient.get<TaskResult>(`/tasks/${taskId}`);
			return data;
		},
		enabled:Boolean(taskId?.trim()),
		gcTime: 2 * 60 * 1000,
		refetchInterval: ({ state }) => {
			const data = state.data;
			if (!data) return false;

			if (data.status === "PENDING" || data.status === "STARTED") {
				return 2000; // poll every 2 seconds
			}

			return false; // stop polling
		},
		refetchIntervalInBackground: false,
	});
}
