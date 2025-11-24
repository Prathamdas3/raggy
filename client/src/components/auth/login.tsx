import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { loginSchema, type LoginInput } from "@/lib/validations/auth";
import { Link } from "@tanstack/react-router";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "../ui/form";

export function LoginForm() {
	const form = useForm<LoginInput>({
		resolver: zodResolver(loginSchema),
		defaultValues: {
			email: "",
			password: "",
		},
	});
	const onSubmit = async (data: LoginInput) => {
		// Simulate API call
		await new Promise((resolve) => setTimeout(resolve, 1000));
		console.log("Login attempt:", data);
	};

	return (
		<div className="space-y-6">
			<div className="space-y-2 text-center">
				<h1 className="text-3xl font-semibold tracking-tight">Welcome back</h1>
				<p className="text-sm text-muted-foreground">
					Enter your credentials to access your account
				</p>
			</div>

			<Form {...form}>
				<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
					<FormField
						control={form.control}
						name="email"
						render={({ field }) => (
							<FormItem>
								<FormLabel>Email</FormLabel>
								<FormControl>
									<Input
										type="email"
										placeholder="name@example.com"
										disabled={form.formState.isSubmitting}
										{...field}
									/>
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>

					<FormField
						control={form.control}
						name="password"
						render={({ field }) => (
							<FormItem>
								<div className="flex items-center justify-between">
									<FormLabel>Password</FormLabel>
									<Link
										to="/auth/reset-password"
										className="text-sm text-muted-foreground hover:text-foreground transition-colors"
									>
										Forgot password?
									</Link>
								</div>
								<FormControl>
									<Input
										type="password"
										placeholder="Enter your password"
										disabled={form.formState.isSubmitting}
										{...field}
									/>
								</FormControl>
								<FormMessage />
							</FormItem>
						)}
					/>

					<Button
						type="submit"
						className="w-full"
						disabled={form.formState.isSubmitting}
					>
						{form.formState.isSubmitting ? "Signing in..." : "Sign in"}
					</Button>
				</form>
			</Form>

			<div className="text-center text-sm">
				<span className="text-muted-foreground">Don't have an account? </span>
				<Link
					to="/auth/signup"
					className="font-medium hover:underline underline-offset-4"
				>
					Sign up
				</Link>
			</div>
		</div>
	);
}
