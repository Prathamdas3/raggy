import { CloudUpload, X } from "lucide-react";
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
import { useCallback } from "react";
import { Button } from "./ui/button";
import TooltipIcon from "./TooltipIcons";

export default function UploadDocs() {
	const onDrop = useCallback((files: any) => {
		console.log(files);
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

	return (
		<section>
			<Empty {...getRootProps({ className: "dropzone border border-dashed" })}>
				<EmptyHeader>
					<EmptyMedia variant="icon">
						<CloudUpload />
					</EmptyMedia>
				</EmptyHeader>
				<EmptyTitle>Start your learning journey</EmptyTitle>
				<EmptyDescription>
					Upload your desired topic file to load and start your learning journey
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
				<div className="mt-4 border rounded-lg p-4 flex  items-center justify-between">
					{files[0].type.startsWith("image/") ? (
						<img
							src={(files[0] as any).preview}
							alt={files[0].name}
							className="max-h-60 object-contain"
						/>
					) : (
						<p className="text-sm text-muted-foreground">
							{files[0].name} ({(files[0].size / 1024).toFixed(1)} KB)
						</p>
					)}
					<TooltipIcon Icon={X} content="Remove docs" type="destructive" side="right"/>
				</div>
			)}
			<Button
				className={`w-full mt-4 ${files.length > 0 ? "block" : "hidden"}`}
			>
				Submit
			</Button>
		</section>
	);
}
