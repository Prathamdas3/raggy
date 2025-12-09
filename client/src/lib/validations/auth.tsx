import { z } from "zod";

// Password validation schema with all criteria
export const passwordSchema = z
	.string()
	.min(8, "Password must be at least 8 characters")
	.regex(/[a-z]/, "Password must contain at least one lowercase letter")
	.regex(/[A-Z]/, "Password must contain at least one uppercase letter")
	.regex(/[0-9]/, "Password must contain at least one number")
	.regex(
		/[^a-zA-Z0-9]/,
		"Password must contain at least one special character",
	);

// Login schema
export const loginSchema = z.object({
	email: z.string().email("Please enter a valid email address"),
	password: z.string().min(1, "Password is required"),
});

// Signup schema
export const signupSchema = z
	.object({
		// name: z.string().min(2, "Name must be at least 2 characters"),
		email: z.email("Please enter a valid email address"),
		password: passwordSchema,
		confirmPassword: z.string(),
	})
	.refine((data) => data.password === data.confirmPassword, {
		message: "Passwords don't match",
		path: ["confirmPassword"],
	});

// Forgot password schema
export const forgotPasswordSchema = z.object({
	email: z.string().email("Please enter a valid email address"),
});

// Export types
export type LoginInput = z.infer<typeof loginSchema>;
export type SignupInput = z.infer<typeof signupSchema>;
export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;
