import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Pencil, Sparkles } from "lucide-react";
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
import { useEffect} from "react";

// Validation schema
const renameChatSchema = z.object({
	chatName: z
		.string()
		.min(1, "Chat name is required")
		.min(3, "Chat name must be at least 3 characters")
		.max(50, "Chat name must not exceed 50 characters")
		.regex(
			/^[a-zA-Z0-9\s\-_]+$/,
			"Chat name can only contain letters, numbers, spaces, hyphens, and underscores",
		)
		.transform((val) => val.trim()),
});

type RenameChatFormValues = z.infer<typeof renameChatSchema>;

interface RenameChatModalProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	currentName: string;
	onRename: ( newName: string) => void;
}

export function RenameChatModal({
	open,
	onOpenChange,
	currentName,
	onRename,
}: RenameChatModalProps) {
	const form = useForm<RenameChatFormValues>({
		resolver: zodResolver(renameChatSchema),
		defaultValues: {
			chatName: currentName,
		},
	});

	// Update form when currentName changes
	useEffect(() => {
		if (open) {
			form.reset({ chatName: currentName });
		}
	}, [open, currentName, form]);

	const onSubmit = async (data: RenameChatFormValues) => {
		onRename(data.chatName);
		onOpenChange(false);
		form.reset();
	};

	const handleCancel = () => {
		form.reset();
		onOpenChange(false);
	};

	const charCount = form.watch("chatName")?.length || 0;

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="sm:max-w-[500px]">
				<DialogHeader>
					<div className="flex items-center gap-3 mb-2">
						<div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
							<Pencil className="h-5 w-5 text-primary" />
						</div>
						<div>
							<DialogTitle className="text-xl">Rename Chat</DialogTitle>
							<DialogDescription className="text-sm mt-1">
								Give your conversation a memorable name
							</DialogDescription>
						</div>
					</div>
				</DialogHeader>

				<Form {...form}>
					<form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
						<FormField
							control={form.control}
							name="chatName"
							render={({ field }) => (
								<FormItem>
									<FormLabel className="text-base font-medium">
										Chat Name
									</FormLabel>
									<FormControl>
										<div className="relative">
											<Input
												placeholder="Enter chat name..."
												className="pr-16"
												autoFocus
												{...field}
											/>
											<div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
												{charCount}/50
											</div>
										</div>
									</FormControl>
									<FormDescription className="text-xs">
										Use a descriptive name to easily find this chat later
									</FormDescription>
									<FormMessage />
								</FormItem>
							)}
						/>

						<div className="bg-muted/50 rounded-lg p-4 border border-border/50">
							<div className="flex items-start gap-3">
								<Sparkles className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
								<div>
									<p className="text-sm font-medium mb-1">Pro Tip</p>
									<p className="text-xs text-muted-foreground">
										Choose a name that reflects the main topic or purpose of
										this conversation for easy reference.
									</p>
								</div>
							</div>
						</div>

						<DialogFooter className="gap-3 ">
							<Button
								type="button"
								variant="outline"
								onClick={handleCancel}
								disabled={form.formState.isSubmitting}
							>
								Cancel
							</Button>
							<Button type="submit" disabled={form.formState.isSubmitting}>
								{form.formState.isSubmitting ? "Renaming..." : "Rename"}
							</Button>
						</DialogFooter>
					</form>
				</Form>
			</DialogContent>
		</Dialog>
	);
}
