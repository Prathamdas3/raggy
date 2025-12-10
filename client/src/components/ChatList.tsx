import {
	Bookmark,
	Ellipsis,
	MessageSquare,
	Pencil,
	Share,
	Trash,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import {
	useDeleteChat,
	useGetAllChats,
	useUpdateChat,
	type Chat,
} from "@/hooks/chats";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { useEffect, useState } from "react";
import {
	useLocation,
	useNavigate,
} from "@tanstack/react-router";
import { useChatStore } from "@/store/chats";
import { RenameChatModal } from "./RenameModal";

function ListSkeleton({ rows = 6 }: { rows?: number }) {
	return (
		<div className="space-y-2 p-2">
			{Array.from({ length: rows }).map((_, i) => (
				<div
					key={i.toString()}
					className="flex items-center gap-3 rounded-lg p-3 border border-border/50"
				>
					<Skeleton className="h-10 w-10 rounded-lg flex-shrink-0" />
					<div className="flex flex-1 flex-col gap-2">
						<Skeleton className="h-4 w-3/5" />
						<Skeleton className="h-3 w-2/5" />
					</div>
					<Skeleton className="h-8 w-8 rounded-md" />
				</div>
			))}
		</div>
	);
}

function Dropdown({ chat }: { chat: Chat }) {
	const [open, setOpen] = useState<boolean>(false);
	const params = useLocation().pathname.split("/").reverse()[0];
	const { mutate: deleteChat } = useDeleteChat();
	const { mutate: updateChat } = useUpdateChat();
	const router = useNavigate();

	const onRename = (chat_name: string) => {
		updateChat({ chat_id: chat.id, chat_name: chat_name });
	};

	const onDelete = () => {
		deleteChat(chat.id, {
			onSuccess: () => {
				if (chat.id === params) {
					router({ to: "/chats", replace: true });
				}
			},
		});
	};

	return (
		<>
			<DropdownMenu>
				<DropdownMenuTrigger asChild>
					<button
						className="h-8 w-8 rounded-md hover:bg-accent flex items-center justify-center transition-colors"
						onClick={(e) => e.stopPropagation()}
						type="button"
					>
						<Ellipsis className="h-4 w-4" />
					</button>
				</DropdownMenuTrigger>
				<DropdownMenuContent align="end" className="w-48" side="right">
					<DropdownMenuItem
						className="gap-2 cursor-pointer"
						onClick={() => {
							setOpen(true);
						}}
					>
						<Pencil className="h-4 w-4" />
						<span>Rename</span>
					</DropdownMenuItem>
					<DropdownMenuItem
						className="gap-2 cursor-pointer"
						onClick={() =>
							updateChat({
								chat_id: chat.id,
								is_bookmarked: !chat.is_bookmarked,
							})
						}
					>
						<Bookmark className="h-4 w-4" />
						<span>Bookmark</span>
					</DropdownMenuItem>
					<DropdownMenuItem className="gap-2 cursor-pointer">
						<Share className="h-4 w-4" />
						<span>Share</span>
					</DropdownMenuItem>
					<DropdownMenuSeparator />
					<DropdownMenuItem
						className="gap-2 cursor-pointer text-destructive focus:text-destructive"
						onClick={onDelete}
					>
						<Trash className="h-4 w-4 text-red-500" />
						<span>Delete</span>
					</DropdownMenuItem>
				</DropdownMenuContent>
			</DropdownMenu>
			<RenameChatModal
				open={open}
				onOpenChange={setOpen}
				currentName={chat.chat_name}
				onRename={onRename}
			/>
		</>
	);
}

function ChatItem({ chat }: { chat: Chat }) {
	const [isHovered, setIsHovered] = useState(false);
	const router = useNavigate();
	const { mutate: updateChat } = useUpdateChat();
	return (
		<li
			key={chat.id}
			className="relative rounded-lg border border-transparent hover:border-border hover:bg-accent/50 transition-all duration-200 cursor-pointer"
			onMouseEnter={() => setIsHovered(true)}
			onMouseLeave={() => setIsHovered(false)}
			onClick={() => router({ to: `/chats/${chat.id}` })}
			onKeyDown={(e) => {
				if (e.key === "Enter") {
					router({ to: `/chats/${chat.id}` });
				}
			}}
		>
			<div className="flex items-center gap-3 p-1 px-2">
				{/* Chat Info */}
				<Bookmark
					className={`${
						chat.is_bookmarked ? "text-primary" : "text-muted-foreground"
					} h-4 w-4 ${!chat.is_bookmarked && "hidden"} `}
					fill={chat.is_bookmarked ? "currentColor" : "none"}
					stroke="currentColor"
					onClick={() => {
						updateChat({
							chat_id: chat.id,
							is_bookmarked: !chat.is_bookmarked,
						});
					}}
				/>
				<div className="flex-1 min-w-0">
					<h3 className="text-sm font-medium text-foreground truncate">
						{chat.chat_name}
					</h3>
				</div>
				{/* Dropdown Menu */}
				<div
					className="transition-opacity duration-200"
					style={{ opacity: isHovered ? 1 : 0 }}
				>
					<Dropdown chat={chat} />
				</div>
			</div>
		</li>
	);
}

export default function ChatsList() {
	const { data, isLoading, isError } = useGetAllChats();
	const updateChats = useChatStore((s) => s.updateChat);

	useEffect(() => {
		if (data && data.length > 0) {
			updateChats(data);
		}
	}, [data, updateChats]);

	if (isLoading) {
		return <ListSkeleton />;
	}

	if (isError) {
		return (
			<div className="p-4 mx-2 rounded-lg border border-destructive/50 bg-destructive/10">
				<h4 className="text-sm font-medium text-destructive">
					Failed to load the chats
				</h4>
				<p className="text-xs text-muted-foreground mt-1">
					Please try reloading the page
				</p>
			</div>
		);
	}

	if (!data || data.length === 0) {
		return (
			<div className="flex flex-col items-center justify-center p-8 text-center">
				<MessageSquare className="h-12 w-12 text-muted-foreground/50 mb-3" />
				<h4 className="text-sm font-medium text-foreground">No chats yet</h4>
				<p className="text-xs text-muted-foreground mt-1">
					Start a new conversation to get started
				</p>
			</div>
		);
	}

	return (
		<ul className="space-y-1 p-2">
			{data.map((chat) => (
				<ChatItem key={chat.id} chat={chat} />
			))}
		</ul>
	);
}
