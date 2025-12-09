import { env } from "@/env";
import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

// Type for queued requests
interface QueueItem {
	resolve: (value?: any) => void;
	reject: (reason?: any) => void;
}

// Base axios instance for authenticated requests (with cookies)
const apiClient = axios.create({
	baseURL: env.VITE_API_URL,
	withCredentials: true,
	headers: {
		"Content-Type": "application/json",
	},
});

const authClient = axios.create({
	baseURL: env.VITE_API_URL,
	withCredentials: false,
	headers: {
		"Content-Type": "application/json",
	},
});

// Flag to prevent multiple simultaneous refresh requests
let isRefreshing = false;
let failedQueue: QueueItem[] = [];

// Extend the AxiosRequestConfig to include our custom _retry flag
declare module "axios" {
	export interface InternalAxiosRequestConfig {
		_retry?: boolean;
	}
}

const processQueue = (
	error: AxiosError | null,
	token: string | null = null,
): void => {
	failedQueue.forEach((prom) => {
		if (error) {
			prom.reject(error);
		} else {
			prom.resolve(token);
		}
	});
	failedQueue = [];
};

// Response interceptor for handling 401 errors
apiClient.interceptors.response.use(
	(response) => response,
	async (error: AxiosError) => {
		const originalRequest = error.config as InternalAxiosRequestConfig;

		// If error is 401 and we haven't retried yet
		if (error.response?.status === 401 && !originalRequest._retry) {
			if (isRefreshing) {
				// If already refreshing, queue this request
				return new Promise((resolve, reject) => {
					failedQueue.push({ resolve, reject });
				})
					.then(() => apiClient(originalRequest))
					.catch((err) => Promise.reject(err));
			}

			originalRequest._retry = true;
			isRefreshing = true;

			try {
				// Hit the refresh endpoint
				await apiClient.get("/auth/refresh");

				// If refresh succeeds, process queued requests
				processQueue(null);
				isRefreshing = false;

				// Retry the original request
				return apiClient(originalRequest);
			} catch (refreshError) {
				// If refresh fails, reject all queued requests
				processQueue(refreshError as AxiosError);
				isRefreshing = false;

				// Optionally redirect to login or clear user state
				window.location.href = "/auth/signin";

				return Promise.reject(refreshError);
			}
		}

		return Promise.reject(error);
	},
);

// Optional: Request interceptor for logging or adding custom headers
apiClient.interceptors.request.use(
	(config: InternalAxiosRequestConfig) => {
		// You can add custom headers here if needed
		return config;
	},
	(error: AxiosError) => Promise.reject(error),
);

export { apiClient, authClient };
