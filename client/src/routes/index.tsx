import Protected, { useAuth } from "@/layouts/protected-layout";
import { createFileRoute, Navigate } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
	component: RouteComponent,
});

function RouteComponent() {
	return (
		<Protected>
			<Child />
		</Protected>
	);
}

function Child() {
	const { data } = useAuth();
	const isAllowed = !!data?.email;
	return isAllowed ? <Navigate to="/chats" /> : <Navigate to="/auth/signin" />;
}
