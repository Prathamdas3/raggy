import { LoginForm } from "@/components/auth/login";
import { AuthLayout } from "@/layouts/auth-layout";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/auth/signin")({
	component: RouteComponent,
});

function RouteComponent() {
	return (
		<AuthLayout>
			<LoginForm />
		</AuthLayout>
	);
}
