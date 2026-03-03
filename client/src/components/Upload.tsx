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
import TooltipIcon from "./Tooltip";
import { useForm } from "@tanstack/react-form"
import { z } from "zod";
import {
    Field,
    FieldDescription,
    FieldError,
    FieldGroup,
    FieldLabel,
} from "@/components/ui/field"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { useNavigate } from "@tanstack/react-router";
import { useChatCreate } from "@/store/chat"

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


export default function UploadDocs() {
    const [activeTab, setActiveTab] = useState<"file" | "link">("file");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [submittedLink, setSubmittedLink] = useState<string | null>(null);
    const setTaskId = useChatCreate((s) => s.setContent);

    const appform = useForm({
        validators: {
            onSubmit: linkSchema
        },
        defaultValues: {
            url: "",
        },
        onSubmit: async ({ value }) => setSubmittedLink(value.url)
    });
    // const { mutate } = useCreateChat();
    const router = useNavigate();

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles && acceptedFiles.length > 0) {
            setSelectedFile(acceptedFiles[0]);
        }
    }, []);

    const {
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


    const handleRemoveFile = () => {
        setSelectedFile(null);
    };

    const handleRemoveLink = () => {
        setSubmittedLink(null);
        appform.reset();
    };

    const handleFinalSubmit = () => {
        const newChatId = crypto.randomUUID()
        setTaskId({ id: newChatId, content: selectedFile || submittedLink })
        router({
            to: "/chat/$id", from: "/", params: { id: newChatId },
            replace: true
        })
    };

    const hasContent =
        (activeTab === "file" && selectedFile !== null) ||
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

                    {selectedFile && (
                        <div className="border rounded-lg p-4 flex items-center justify-between bg-accent/50">
                            <div className="flex items-center gap-3 flex-1 min-w-0">
                                {selectedFile.type.startsWith("image/") ? (
                                    <img
                                        src={URL.createObjectURL(selectedFile)}
                                        alt={selectedFile.name}
                                        className="h-16 w-16 object-cover rounded"
                                    />
                                ) : (
                                    <div className="h-16 w-16 bg-primary/10 rounded flex items-center justify-center shrink-0">
                                        <FileText className="h-8 w-8 text-primary" />
                                    </div>
                                )}
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium truncate">
                                        {selectedFile.name}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        {(selectedFile.size / 1024).toFixed(1)} KB
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


                            <form
                                id="yt_link_form"
                                onSubmit={(e) => {
                                    e.preventDefault()
                                    appform.handleSubmit()
                                }}
                                className="space-y-4"
                            >
                                <FieldGroup>
                                    <appform.Field
                                        name="url"
                                        children={(field) => {
                                            const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid
                                            return (
                                                <Field data-invalid={isInvalid}>
                                                    <FieldLabel htmlFor={field.name}>Url</FieldLabel>
                                                    <Input
                                                        id={field.name}
                                                        name={field.name}
                                                        value={field.state.value}
                                                        onBlur={field.handleBlur}
                                                        onChange={(e) => field.handleChange(e.target.value)}
                                                        aria-invalid={isInvalid}
                                                        placeholder="https://example.com/document"
                                                        autoComplete="off"

                                                    />
                                                    <FieldDescription>
                                                        Provide a valid youtube url.
                                                    </FieldDescription>
                                                    {isInvalid && <FieldError errors={field.state.meta.errors} />}
                                                </Field>
                                            )
                                        }}
                                    >

                                    </appform.Field>
                                </FieldGroup>

                                <Button type="submit" className="w-full">
                                    Add Link
                                </Button>
                            </form>

                        </div>
                    ) : (
                        <div className="border rounded-lg p-4 flex items-center justify-between bg-accent/50">
                            <div className="flex items-center gap-3 flex-1 min-w-0">
                                <div className="h-16 w-16 bg-primary/10 rounded flex items-center justify-center shrink-0">
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