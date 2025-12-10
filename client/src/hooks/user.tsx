import { apiClient } from "@/lib/axios";
import { tryCatch } from "@/lib/trycatch";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

interface UserDetails {
	message: string;
	status: string;
	data: {
		id: string;
		user_name: string;
		first_name: string;
		last_name: string;
		email: string;
	};
}

export function useGetUserDetails(fetch: boolean) {
	return useQuery({
		queryKey: ["getUserDetails"],
		gcTime: 30 * 60 * 1000,
		queryFn: async () => {
			const { data } = await apiClient.get<UserDetails>("/user");
			return data;
		},
		retry: false,
		enabled: fetch,
		staleTime: 10 * 60 * 1000,
	});
}

export function useUpdateUserDetails() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationKey: ["updateUserdetails"],
		gcTime: 10 * 60 * 1000,
		retry: false,
		mutationFn: async (payload: {
			user_name: string;
			first_name: string;
			last_name: string;
		}) => {
			const { data, error } = await tryCatch(
				apiClient.patch("/user/update-details", payload),
			);

			if (error) {
				throw error;
			}
			return data?.data;
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["getUserDetails"] });
			toast.success("Successfully updated the your details");
		},
		onError: () => {
			toast.error("Failed to update your details");
		},
	});
}
