
import { useState } from "react";
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
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import {
	forgotPasswordSchema,
	type ForgotPasswordInput,
} from "@/lib/validations/auth";

export function ForgotPasswordForm() {
	const [isSubmitted, setIsSubmitted] = useState(false);
	const [submittedEmail, setSubmittedEmail] = useState("");

	const form = useForm<ForgotPasswordInput>({
		resolver: zodResolver(forgotPasswordSchema),
		defaultValues: {
			email: "",
		},
	});

	const onSubmit = async (data: ForgotPasswordInput) => {
		// Simulate API call
		await new Promise((resolve) => setTimeout(resolve, 1000));
		console.log("Password reset request:", data);
		setSubmittedEmail(data.email);
		setIsSubmitted(true);
	};

	if (isSubmitted) {
		return (
			<div className="space-y-6 text-center">
				<div className="flex justify-center">
					<div className="rounded-full bg-primary/10 p-3">
						<CheckCircle2 className="h-6 w-6 text-primary" />
					</div>
				</div>

				<div className="space-y-2">
					<h1 className="text-2xl font-semibold tracking-tight">
						Check your email
					</h1>
					<p className="text-sm text-muted-foreground leading-relaxed">
						We've sent a password reset link to{" "}
						<strong>{submittedEmail}</strong>. Click the link in the email to
						reset your password.
					</p>
				</div>

				<div className="pt-4">
					<Link to="/auth/signin">
						<Button variant="outline" className="w-full bg-transparent">
							<ArrowLeft className="mr-2 h-4 w-4" />
							Back to sign in
						</Button>
					</Link>
				</div>
			</div>
		);
	}

	return (
		<div className="space-y-6">
			<div className="space-y-2 text-center">
				<h1 className="text-3xl font-semibold tracking-tight">
					Reset password
				</h1>
				<p className="text-sm text-muted-foreground">
					Enter your email and we'll send you a reset link
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

					<Button
						type="submit"
						className="w-full"
						disabled={form.formState.isSubmitting}
					>
						{form.formState.isSubmitting ? "Sending..." : "Send reset link"}
					</Button>
				</form>
			</Form>

			<div className="text-center">
				<Link
					to="/auth/signin"
					className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-2 transition-colors"
				>
					<ArrowLeft className="h-4 w-4" />
					Back to sign in
				</Link>
			</div>
		</div>
	);
}
