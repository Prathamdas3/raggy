import { SignupForm } from "@/components/auth/signup";
import { AuthLayout } from "@/layouts/auth-layout";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/auth/signup")({
	component: RouteComponent,
});

function RouteComponent() {
	return (
		<AuthLayout>
			<SignupForm />
		</AuthLayout>
	);
}
