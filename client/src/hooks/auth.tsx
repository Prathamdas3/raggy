import { useMutation, useQuery } from "@tanstack/react-query";
import { tryCatch } from "@/lib/trycatch";
import type { SignupInput, LoginInput } from "@/lib/validations/auth";
import { apiClient, authClient } from "@/lib/axios";
import { toast } from "sonner";
import type { AxiosError } from "axios";

type CurrentUser = {
	message: string;
	status: string;
	data: {
		user_id: string;
		email: string;
	};
};

export function useSignup() {
	return useMutation({
		mutationKey: ["signup"],
		mutationFn: async (payload: SignupInput) => {
			const { data, error } = await tryCatch(
				authClient.post("/auth/sign-up", payload),
			);
			if (error) {
				throw error;
			}
			return data?.data;
		},
		retry: false,
		gcTime: 10 * 60 * 1000,
		onSuccess: () => {
			toast.success("successfully created the user");
		},
		onError: (error: AxiosError) => {
			if (error?.response?.status === 409) {
				toast.error("Email already exists, Please use another email");
			} else {
				toast.error("Signup failed");
			}
		},
	});
}

export function useSignin() {
	return useMutation({
		mutationKey: ["signin"],
		mutationFn: async (payload: LoginInput) => {
			const { data, error } = await tryCatch(
				authClient.post("/auth/sign-in", payload),
			);
			if (error) {
				throw error;
			}
			return data?.data;
		},
		retry: false,
		gcTime: 10 * 60 * 1000,
		onSuccess: () => {
			toast.success("Successfully logged in");
		},
		onError: () => {
			toast.error("Failed to login in");
		},
	});
}

export function useSignout() {
	return useMutation({
		mutationKey: ["signout"],
		mutationFn: async () => {
			const { data, error } = await tryCatch(
				apiClient.delete("/auth/sign-out"),
			);
			if (error) {
				throw error;
			}
			return data?.data;
		},
		retry: false,
		gcTime: 5 * 10 * 1000,
		onSuccess: () => {
			toast.success("Successfully logged out ");
		},
		onError: () => {
			toast.error("Failed to log out");
		},
	});
}

export function useGetCurrentUser() {
	return useQuery({
		queryKey: ["getCurrentUser"],
		retry: false,
		gcTime: 10 * 60 * 1000,
		queryFn: async () => {
			const { data } = await apiClient.get<CurrentUser>("/auth/me");
			return data?.data;
		},
	});
}
