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
import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";

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
	const { mutate: deleteChat } = useDeleteChat();
	const { mutate: updateChat } = useUpdateChat();

	return (
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
				<DropdownMenuItem className="gap-2 cursor-pointer">
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
					onClick={() => deleteChat(chat.id)}
				>
					<Trash className="h-4 w-4 text-red-500" />
					<span>Delete</span>
				</DropdownMenuItem>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}

function ChatItem({ chat }: { chat: Chat }) {
	const [isHovered, setIsHovered] = useState(false);
	const router = useNavigate();

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
