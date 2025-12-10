import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { User, Mail, UserCircle, Loader2, CheckCircle2 } from "lucide-react";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogFooter,
} from "@/components/ui/dialog";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
	FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useGetUserDetails, useUpdateUserDetails } from "@/hooks/user";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useEffect } from "react";

// Validation schema
const userDetailsSchema = z.object({
	user_name: z
		.string()
		.min(3, "Username must be at least 3 characters")
		.max(30, "Username must not exceed 30 characters")
		.regex(
			/^[a-zA-Z0-9_-]+$/,
			"Username can only contain letters, numbers, hyphens, and underscores",
		),
	first_name: z
		.string()
		.min(1, "First name is required")
		.max(50, "First name must not exceed 50 characters")
		.regex(/^[a-zA-Z\s]+$/, "First name can only contain letters and spaces"),
	last_name: z
		.string()
		.min(1, "Last name is required")
		.max(50, "Last name must not exceed 50 characters")
		.regex(/^[a-zA-Z\s]+$/, "Last name can only contain letters and spaces"),
});

type UserDetailsFormValues = z.infer<typeof userDetailsSchema>;

interface UserDetailsModalProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
}

export function UserDetailsModal({
	open,
	onOpenChange,
}: UserDetailsModalProps) {
	const {
		data: userData,
		isLoading,
		isError,
		refetch,
	} = useGetUserDetails(open);
	const { mutate: updateUser, isPending } = useUpdateUserDetails();

	const form = useForm<UserDetailsFormValues>({
		resolver: zodResolver(userDetailsSchema),
		defaultValues: {
			user_name: "",
			first_name: "",
			last_name: "",
		},
	});

	// Update form when user data is loaded
	useEffect(() => {
		if (userData?.data) {
			form.reset({
				user_name: userData.data.user_name,
				first_name: userData.data.first_name,
				last_name: userData.data.last_name,
			});
		}
	}, [userData, form]);

	const onSubmit = async (data: UserDetailsFormValues) => {
		updateUser(data, {
			onSuccess: () => {
				refetch();
			},
		});
	};

	const handleCancel = () => {
		if (userData?.data) {
			form.reset({
				user_name: userData.data.user_name,
				first_name: userData.data.first_name,
				last_name: userData.data.last_name,
			});
		}
		onOpenChange(false);
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-[550px]">
				<DialogHeader>
					<div className="flex items-center gap-3 mb-2">
						<div className="h-12 w-12 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
							<UserCircle className="h-6 w-6 text-primary-foreground" />
						</div>
						<div>
							<DialogTitle className="text-xl">Profile Settings</DialogTitle>
							<DialogDescription className="text-sm mt-1">
								Update your personal information
							</DialogDescription>
						</div>
					</div>
				</DialogHeader>

				{isLoading ? (
					<div className="space-y-6 py-4">
						<div className="space-y-4">
							<Skeleton className="h-10 w-full" />
							<Skeleton className="h-10 w-full" />
							<Skeleton className="h-10 w-full" />
						</div>
						<Skeleton className="h-16 w-full" />
					</div>
				) : isError ? (
					<div className="py-8 text-center">
						<div className="h-12 w-12 rounded-full bg-destructive/10 flex items-center justify-center mx-auto mb-3">
							<User className="h-6 w-6 text-destructive" />
						</div>
						<p className="text-sm text-destructive font-medium">
							Failed to load user details
						</p>
						<Button
							variant="outline"
							size="sm"
							onClick={() => refetch()}
							className="mt-4"
						>
							Try Again
						</Button>
					</div>
				) : (
					<>
						{/* Email Display (Read-only) */}
						<div className="bg-muted/50 rounded-lg p-4 border border-border/50">
							<div className="flex items-center gap-3">
								<div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
									<Mail className="h-5 w-5 text-primary" />
								</div>
								<div className="flex-1 min-w-0">
									<p className="text-xs text-muted-foreground mb-1">
										Email Address
									</p>
									<p className="text-sm font-medium truncate">
										{userData?.data.email}
									</p>
								</div>
								<Badge variant="secondary" className="text-xs">
									Verified
								</Badge>
							</div>
						</div>

						<Form {...form}>
							<form
								onSubmit={form.handleSubmit(onSubmit)}
								className="space-y-4"
							>
								<FormField
									control={form.control}
									name="user_name"
									render={({ field }) => (
										<FormItem>
											<FormLabel>Username</FormLabel>
											<FormControl>
												<div className="relative">
													<User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
													<Input
														placeholder="johndoe"
														className="pl-10"
														disabled={isPending}
														{...field}
													/>
												</div>
											</FormControl>
											<FormDescription className="text-xs">
												This is your public display name
											</FormDescription>
											<FormMessage />
										</FormItem>
									)}
								/>

								<div className="grid grid-cols-2 gap-4">
									<FormField
										control={form.control}
										name="first_name"
										render={({ field }) => (
											<FormItem>
												<FormLabel>First Name</FormLabel>
												<FormControl>
													<Input
														placeholder="John"
														disabled={isPending}
														{...field}
													/>
												</FormControl>
												<FormMessage />
											</FormItem>
										)}
									/>

									<FormField
										control={form.control}
										name="last_name"
										render={({ field }) => (
											<FormItem>
												<FormLabel>Last Name</FormLabel>
												<FormControl>
													<Input
														placeholder="Doe"
														disabled={isPending}
														{...field}
													/>
												</FormControl>
												<FormMessage />
											</FormItem>
										)}
									/>
								</div>

								{form.formState.isDirty && (
									<div className="bg-blue-50 dark:bg-blue-950/20 rounded-lg p-3 border border-blue-200 dark:border-blue-900">
										<div className="flex items-start gap-2">
											<CheckCircle2 className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
											<p className="text-xs text-blue-700 dark:text-blue-300">
												You have unsaved changes
											</p>
										</div>
									</div>
								)}

								<DialogFooter className="gap-2 ">
									<Button
										type="button"
										variant="outline"
										onClick={handleCancel}
										disabled={isPending}
									>
										Cancel
									</Button>
									<Button
										type="submit"
										disabled={isPending || !form.formState.isDirty}
									>
										{isPending ? (
											<>
												<Loader2 className="mr-2 h-4 w-4 animate-spin" />
												Saving...
											</>
										) : (
											"Save"
										)}
									</Button>
								</DialogFooter>
							</form>
						</Form>
					</>
				)}
			</DialogContent>
		</Dialog>
	);
}
