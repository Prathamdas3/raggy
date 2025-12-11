import { createContext, useContext } from "react";
import ChatSkeleton from "@/components/Loader";
import { useGetCurrentUser } from "@/hooks/auth";
import { Navigate } from "@tanstack/react-router";
import type React from "react";

type childT = {
	children: React.ReactNode;
};
type ApiType = {
	data?: { email: string; user_id: string };
	isLoading: boolean;
	isError: boolean;
};
const apiContext = createContext<ApiType | null>(null);

export const ContextProvider = ({ children }: childT) => {
	const { data, isLoading, isError } = useGetCurrentUser();
	const value = { data, isLoading, isError };
	return <apiContext.Provider value={value}>{children}</apiContext.Provider>;
};

export const useAuth = () => {
	const contextData = useContext(apiContext);
	if (!contextData) {
		throw new Error("context must be used inside the provider");
	}
	return contextData;
};

function ProtectedChild({ children }: { children: React.ReactNode }) {
	const { isLoading, isError, data } = useAuth();

	if (isLoading) {
		return <ChatSkeleton />;
	}
	if (isError || !data?.user_id) {
		return <Navigate to="/auth/signin" />;
	}
	return children;
}

export default function Protected({ children }: { children: React.ReactNode }) {
	return (
		<ContextProvider>
			<ProtectedChild>{children}</ProtectedChild>
		</ContextProvider>
	);
}
