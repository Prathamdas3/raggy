import { useState, useMemo } from "react";
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
	Search,
	MessageSquare,
	Bookmark,
	Clock,
	X,
	SidebarOpen,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { Button } from "@/components/ui/button";
import type { Chat } from "@/hooks/chats";

interface SearchModalProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	chats: Chat[];
	onSelectChat: (chatId: string) => void;
}

export function SearchModal({
	open,
	onOpenChange,
	chats,
	onSelectChat,
}: SearchModalProps) {
	const [searchQuery, setSearchQuery] = useState("");

	// Filter chats based on search query
	const filteredChats = useMemo(() => {
		if (!searchQuery.trim()) return chats;

		const query = searchQuery.toLowerCase();
		return chats.filter((chat) => chat.chat_name.toLowerCase().includes(query));
	}, [chats, searchQuery]);

	const handleSelectChat = (chatId: string) => {
		onSelectChat(chatId);
		onOpenChange(false);
		setSearchQuery("");
	};

	const handleClearSearch = () => {
		setSearchQuery("");
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="max-w-2xl p-0 gap-0">
				<DialogHeader className="px-6 pt-6 pb-4 border-b">
					<DialogTitle className="text-xl">Search Chats</DialogTitle>
				</DialogHeader>

				{/* Search Input */}
				<div className="px-6 py-4 border-b">
					<div className="relative">
						<Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
						<Input
							placeholder="Search by chat name..."
							value={searchQuery}
							onChange={(e) => setSearchQuery(e.target.value)}
							className="pl-10 pr-10"
							autoFocus
						/>
						{searchQuery && (
							<button
								onClick={handleClearSearch}
								className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
								type="button"
							>
								<X className="h-4 w-4" />
							</button>
						)}
					</div>
				</div>

				{/* Results */}
				<div className="max-h-[400px] overflow-y-auto">
					{filteredChats.length === 0 ? (
						<div className="flex flex-col items-center justify-center py-12 px-6 text-center">
							<div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-3">
								<Search className="h-6 w-6 text-muted-foreground" />
							</div>
							<h3 className="text-sm font-medium mb-1">No chats found</h3>
							<p className="text-xs text-muted-foreground">
								{searchQuery
									? `No results for "${searchQuery}"`
									: "Start typing to search"}
							</p>
						</div>
					) : (
						<ul className="py-2">
							{filteredChats.map((chat) => (
								<li key={chat.id}>
									<button
										onClick={() => handleSelectChat(chat.id)}
										className="w-full px-6 py-3 hover:bg-accent transition-colors text-left group"
										type="button"
									>
										<div className="flex items-start gap-3">
											{/* Icon */}
											<div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
												<MessageSquare className="h-5 w-5 text-primary" />
											</div>

											{/* Chat Info */}
											<div className="flex-1 min-w-0">
												<div className="flex items-center gap-2 mb-1">
													<h4 className="text-sm font-medium truncate">
														{chat.chat_name}
													</h4>
													{chat.is_bookmarked && (
														<Bookmark className="h-3 w-3 text-yellow-500 fill-yellow-500 flex-shrink-0" />
													)}
												</div>
												<div className="flex items-center gap-2 text-xs text-muted-foreground">
													<Clock className="h-3 w-3" />
													<span>
														{formatDistanceToNow(new Date(chat.updated_at), {
															addSuffix: true,
														})}
													</span>
												</div>
											</div>
										</div>
									</button>
								</li>
							))}
						</ul>
					)}
				</div>

				{/* Footer with count */}
				{filteredChats.length > 0 && (
					<div className="px-6 py-3 border-t bg-muted/50">
						<p className="text-xs text-muted-foreground text-center">
							{filteredChats.length}{" "}
							{filteredChats.length === 1 ? "chat" : "chats"} found
						</p>
					</div>
				)}
			</DialogContent>
		</Dialog>
	);
}

// Example usage component
export function SearchModalExample({ sidebarOpen }: { sidebarOpen: boolean }) {
	const [open, setOpen] = useState(false);

	// Dummy data
	const dummyChats: Chat[] = [
		{
			id: "1",
			chat_name: "Machine Learning Basics",
			is_bookmarked: true,
			created_at: "2024-01-15T10:00:00Z",
			updated_at: "2024-01-20T15:30:00Z",
		},
		{
			id: "2",
			chat_name: "React Best Practices",
			is_bookmarked: false,
			created_at: "2024-01-16T11:00:00Z",
			updated_at: "2024-01-21T09:15:00Z",
		},
		{
			id: "3",
			chat_name: "TypeScript Advanced Topics",
			is_bookmarked: true,
			created_at: "2024-01-17T14:00:00Z",
			updated_at: "2024-01-22T16:45:00Z",
		},
		{
			id: "4",
			chat_name: "Database Design Patterns",
			is_bookmarked: false,
			created_at: "2024-01-18T09:00:00Z",
			updated_at: "2024-01-23T11:20:00Z",
		},
		{
			id: "5",
			chat_name: "API Development Guide",
			is_bookmarked: false,
			created_at: "2024-01-19T13:00:00Z",
			updated_at: "2024-01-24T14:10:00Z",
		},
	];

	const handleSelectChat = (chatId: string) => {
		console.log("Selected chat:", chatId);
		// Navigate to chat or perform action
	};

	return (
		<div className="flex gap-2 h-10 items-center cursor-pointer">
			<Button
				size="icon"
				variant="ghost"
				onClick={() => setOpen(true)}
				className="h-12"
			>
				<Search className="h-8 w-8" />
			</Button>
			{sidebarOpen && <span>Search Chats</span>}

			<SearchModal
				open={open}
				onOpenChange={setOpen}
				chats={dummyChats}
				onSelectChat={handleSelectChat}
			/>
		</div>
	);
}
