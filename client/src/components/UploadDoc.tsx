import { CloudUpload, Link as LinkIcon, X, FileText } from "lucide-react";
import {
	Empty,
	EmptyContent,
	EmptyDescription,
	EmptyHeader,
	EmptyMedia,
	EmptyTitle,
} from "./ui/empty";
import { Input } from "./ui/input";
import { useDropzone } from "react-dropzone";
import { useCallback, useState } from "react";
import { Button } from "./ui/button";
import TooltipIcon from "./TooltipIcons";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "./ui/form";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { useCreateChat } from "@/hooks/chats";
import { useNavigate } from "@tanstack/react-router";
import { useTasksIdStore } from "@/store/task";

// Validation schema for link
const linkSchema = z.object({
	url: z.url({ message: "Please enter a valid URL" }).refine(
		(url) => {
			try {
				const parsedUrl = new URL(url);
				return ["http:", "https:"].includes(parsedUrl.protocol);
			} catch {
				return false;
			}
		},
		{ message: "URL must start with http:// or https://" },
	),
});

type LinkFormValues = z.infer<typeof linkSchema>;

export default function UploadDocs() {
	const [activeTab, setActiveTab] = useState<"file" | "link">("file");
	const [selectedFile, setSelectedFile] = useState<File | null>(null);
	const [submittedLink, setSubmittedLink] = useState<string | null>(null);
	const setTaskId = useTasksIdStore((s) => s.setTaskId);

	const form = useForm<LinkFormValues>({
		resolver: zodResolver(linkSchema),
		defaultValues: {
			url: "",
		},
	});
	const { mutate } = useCreateChat();
	const router = useNavigate();

	const onDrop = useCallback((files: any) => {
		setSelectedFile(files || null);
	}, []);

	const {
		acceptedFiles: files,
		getRootProps,
		getInputProps,
		isDragActive,
	} = useDropzone({
		onDrop,
		maxSize: 10 * 1024 * 1024,
		autoFocus: true,
		maxFiles: 1,
		accept: {
			"image/*": [],
			"application/pdf": [],
		},
	});

	const onLinkSubmit = (data: LinkFormValues) => {
		setSubmittedLink(data.url);
	};

	const handleRemoveFile = () => {
		setSelectedFile(null);
	};

	const handleRemoveLink = () => {
		setSubmittedLink(null);
		form.reset();
	};

	const handleFinalSubmit = () => {
		if (activeTab === "file" && files.length > 0) {
			console.log("Submitting file:", selectedFile);
			// Handle file submission
		} else if (activeTab === "link" && submittedLink) {
			mutate(
				{ link: submittedLink },
				{
					onSuccess: (data) => {
						setSubmittedLink(null);
						setTaskId(data?.task_id);
						form.reset();
						router({ to: `/chats/${data?.chat_id}`, from: "/chats" });
					},
				},
			);
		}
	};

	const hasContent =
		(activeTab === "file" && files.length > 0) ||
		(activeTab === "link" && submittedLink);

	return (
		<section className="space-y-4">
			<Tabs
				value={activeTab}
				onValueChange={(v) => setActiveTab(v as "file" | "link")}
			>
				<TabsList className="grid w-full grid-cols-2">
					<TabsTrigger value="file" className="gap-2">
						<FileText className="h-4 w-4" />
						File Upload
					</TabsTrigger>
					<TabsTrigger value="link" className="gap-2">
						<LinkIcon className="h-4 w-4" />
						Link
					</TabsTrigger>
				</TabsList>

				{/* File Upload Tab */}
				<TabsContent value="file" className="space-y-4">
					<Empty
						{...getRootProps({
							className:
								"dropzone border-2 border-dashed cursor-pointer transition-colors hover:border-primary/50",
						})}
					>
						<EmptyHeader>
							<EmptyMedia variant="icon">
								<CloudUpload />
							</EmptyMedia>
						</EmptyHeader>
						<EmptyTitle>Start your learning journey</EmptyTitle>
						<EmptyDescription>
							Upload your desired topic file to load and start your learning
							journey
						</EmptyDescription>
						<EmptyContent>
							<Input {...getInputProps()} />
							{isDragActive ? (
								<p className="text-muted-foreground">Drop the files here ...</p>
							) : (
								<p className="text-muted-foreground">
									Drag 'n' drop some files here, or click to select files
								</p>
							)}
						</EmptyContent>
					</Empty>

					{files.length > 0 && (
						<div className="border rounded-lg p-4 flex items-center justify-between bg-accent/50">
							<div className="flex items-center gap-3 flex-1 min-w-0">
								{selectedFile?.type.startsWith("image/") ? (
									<img
										src={URL.createObjectURL(selectedFile)}
										alt={selectedFile?.name}
										className="h-16 w-16 object-cover rounded"
									/>
								) : (
									<div className="h-16 w-16 bg-primary/10 rounded flex items-center justify-center flex-shrink-0">
										<FileText className="h-8 w-8 text-primary" />
									</div>
								)}
								<div className="flex-1 min-w-0">
									<p className="text-sm font-medium truncate">
										{files[0].name}
									</p>
									<p className="text-xs text-muted-foreground">
										{(files[0].size / 1024).toFixed(1)} KB
									</p>
								</div>
							</div>
							<TooltipIcon
								Icon={X}
								content="Remove file"
								type="destructive"
								side="left"
								action={handleRemoveFile}
							/>
						</div>
					)}
				</TabsContent>

				{/* Link Tab */}
				<TabsContent value="link" className="space-y-4">
					{!submittedLink ? (
						<div className="border-2 border-dashed rounded-lg p-6">
							<div className="flex flex-col items-center mb-6">
								<div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-3">
									<LinkIcon className="h-6 w-6 text-primary" />
								</div>
								<h3 className="text-lg font-semibold">Add a link</h3>
								<p className="text-sm text-muted-foreground text-center mt-1">
									Paste a URL to a youtube video you'd like to learn from
								</p>
							</div>

							<Form {...form}>
								<form
									onSubmit={form.handleSubmit(onLinkSubmit)}
									className="space-y-4"
								>
									<FormField
										control={form.control}
										name="url"
										render={({ field }) => (
											<FormItem>
												<FormLabel>URL</FormLabel>
												<FormControl>
													<Input
														placeholder="https://example.com/document"
														{...field}
													/>
												</FormControl>
												<FormMessage />
											</FormItem>
										)}
									/>
									<Button type="submit" className="w-full">
										Add Link
									</Button>
								</form>
							</Form>
						</div>
					) : (
						<div className="border rounded-lg p-4 flex items-center justify-between bg-accent/50">
							<div className="flex items-center gap-3 flex-1 min-w-0">
								<div className="h-16 w-16 bg-primary/10 rounded flex items-center justify-center flex-shrink-0">
									<LinkIcon className="h-8 w-8 text-primary" />
								</div>
								<div className="flex-1 min-w-0">
									<p className="text-sm font-medium">Link Added</p>
									<p className="text-xs text-muted-foreground truncate">
										{submittedLink}
									</p>
								</div>
							</div>
							<TooltipIcon
								Icon={X}
								content="Remove link"
								type="destructive"
								side="left"
								action={handleRemoveLink}
							/>
						</div>
					)}
				</TabsContent>
			</Tabs>

			{hasContent && (
				<Button className="w-full" onClick={handleFinalSubmit}>
					Submit
				</Button>
			)}
		</section>
	);
}
