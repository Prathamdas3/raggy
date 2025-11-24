import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/components/ui/form";
import { signupSchema, type SignupInput } from "@/lib/validations/auth";
import { PasswordRequirements } from "./password";

export function SignupForm() {
	const form = useForm<SignupInput>({
		resolver: zodResolver(signupSchema),
		defaultValues: {
			name: "",
			email: "",
			password: "",
		},
	});

	const password = form.watch("password");

	const onSubmit = async (data: SignupInput) => {
		// Simulate API call
		await new Promise((resolve) => setTimeout(resolve, 1000));
		console.log("Signup attempt:", data);
	};

	return (
		<div className="space-y-6">
			<div className="space-y-2 text-center">
				<h1 className="text-3xl font-semibold tracking-tight">
					Create an account
				</h1>
				<p className="text-sm text-muted-foreground">
					Enter your information to get started
				</p>
			</div>

			<Form {...form}>
				<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
					<FormField
						control={form.control}
						name="name"
						render={({ field }) => (
							<FormItem>
								<FormLabel>Full Name</FormLabel>
								<FormControl>
									<Input
										type="text"
										placeholder="John Doe"
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
								<FormLabel>Password</FormLabel>
								<FormControl>
									<Input
										type="password"
										placeholder="Create a password"
										disabled={form.formState.isSubmitting}
										{...field}
									/>
								</FormControl>
								<FormMessage />
								<PasswordRequirements password={password} />
							</FormItem>
						)}
					/>

					<Button
						type="submit"
						className="w-full"
						disabled={form.formState.isSubmitting}
					>
						{form.formState.isSubmitting
							? "Creating account..."
							: "Create account"}
					</Button>
				</form>
			</Form>

			<div className="text-center text-sm">
				<span className="text-muted-foreground">Already have an account? </span>
				<Link
					to="/auth/signin"
					className="font-medium hover:underline underline-offset-4"
				>
					Sign in
				</Link>
			</div>
		</div>
	);
}
