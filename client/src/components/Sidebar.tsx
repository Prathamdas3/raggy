import { Link, useNavigate } from "@tanstack/react-router";
import {
	ChevronRight,
	Bookmark,
	FolderPlus,
	MessageSquarePlus,
	User,
	LogOut,
	Settings,
} from "lucide-react";
import ChatsList from "./ChatList";
import { Button } from "./ui/button";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarGroupLabel,
	SidebarHeader,
	SidebarTrigger,
	useSidebar,
} from "./ui/sidebar";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { SearchModalExample } from "./Search";
import { Separator } from "./ui/separator";
import { useSignout } from "@/hooks/auth";

export default function AppSidebar() {
	const { open, setOpen } = useSidebar();
	const { mutate } = useSignout();
	const router = useNavigate();

	const handleSignout = () => {
		mutate(undefined, {
			onSuccess: () => {
				router({ to: "/auth/signin", replace: true });
			},
		});
	};

	return (
		<Sidebar collapsible="icon" className="border-r">
			<SidebarHeader className="border-b px-3 py-3">
				{open ? (
					<div className="flex items-center justify-between">
						<Link
							to="/chats"
							className="flex items-center gap-2 hover:opacity-80 transition-opacity"
						>
							<div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
								<MessageSquarePlus className="h-4 w-4 text-primary-foreground" />
							</div>
							<span className="font-semibold text-lg">ChatApp</span>
						</Link>
						<SidebarTrigger className="h-8 w-8" />
					</div>
				) : (
					<Button
						size="icon"
						variant="ghost"
						onClick={() => setOpen(true)}
						className="h-8 w-8 mx-auto"
					>
						<ChevronRight className="h-4 w-4" />
					</Button>
				)}
			</SidebarHeader>

			<SidebarContent className="px-2 py-3">
				{/* New Chat Button */}
				<SidebarGroup>
					<Link to="/chats" className="no-underline">
						<Button
							variant={open ? "default" : "ghost"}
							className={`w-full h-10 mb-2 ${open ? "justify-start gap-2" : "justify-center"} `}
							size={open ? "default" : "icon"}
						>
							<MessageSquarePlus className="h-4 w-4 flex-shrink-0" />
							{open && <span className="font-medium">New Chat</span>}
						</Button>
					</Link>

					{/* Search */}
					<SearchModalExample sidebarOpen={open} />
				</SidebarGroup>

				<Separator className="my-3" />

				{/* Folders Section */}
				<SidebarGroup>
					{open && (
						<SidebarGroupLabel className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
							Organize
						</SidebarGroupLabel>
					)}

					<div className="space-y-1">
						<Button
							variant="ghost"
							className={`w-full h-9 px-2 ${open ? "justify-start gap-3" : "justify-center"}`}
							size={open ? "default" : "icon"}
						>
							<FolderPlus className="h-4 w-4 flex-shrink-0" />
							{open && <span className="text-sm">Create Folder</span>}
						</Button>

						<Button
							variant="ghost"
							className={`w-full h-9 px-2 ${open ? "justify-start gap-3" : "justify-center"}`}
							size={open ? "default" : "icon"}
						>
							<Bookmark className="h-4 w-4 flex-shrink-0" />
							{open && <span className="text-sm">Bookmarks</span>}
						</Button>
					</div>
				</SidebarGroup>

				<Separator className="my-3" />

				{/* Chats Section */}
				<SidebarGroup className="flex-1 overflow-hidden">
					{open && (
						<SidebarGroupLabel className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
							Recent Chats
						</SidebarGroupLabel>
					)}
					<div className="overflow-y-auto overflow-x-hidden max-h-full pr-1 -mr-1">
						<ChatsList />
					</div>
				</SidebarGroup>
			</SidebarContent>

			<SidebarFooter className="border-t p-2">
				{open ? (
					<DropdownMenu>
						<DropdownMenuTrigger asChild>
							<Button
								variant="ghost"
								className="w-full justify-start gap-3 h-12 px-3 hover:bg-accent"
							>
								<div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center flex-shrink-0">
									<User className="h-4 w-4 text-primary-foreground" />
								</div>
								<div className="flex-1 text-left min-w-0">
									<p className="text-sm font-medium truncate">John Doe</p>
									<p className="text-xs text-muted-foreground truncate">
										john@example.com
									</p>
								</div>
								<ChevronRight className="h-4 w-4 text-muted-foreground" />
							</Button>
						</DropdownMenuTrigger>
						<DropdownMenuContent
							align="end"
							className="w-56"
							side="right"
							sideOffset={8}
						>
							<DropdownMenuItem className="gap-2 cursor-pointer">
								<User className="h-4 w-4" />
								<span>Profile</span>
							</DropdownMenuItem>
							<DropdownMenuItem className="gap-2 cursor-pointer">
								<Settings className="h-4 w-4" />
								<span>Settings</span>
							</DropdownMenuItem>
							<DropdownMenuSeparator />
							<DropdownMenuItem
								className="gap-2 cursor-pointer text-destructive focus:text-destructive"
								onClick={handleSignout}
							>
								<LogOut className="h-4 w-4 text-red-500" />
								<span>Log out</span>
							</DropdownMenuItem>
						</DropdownMenuContent>
					</DropdownMenu>
				) : (
					<DropdownMenu>
						<DropdownMenuTrigger asChild>
							<Button
								size="icon"
								variant="ghost"
								className="h-10 w-10 mx-auto rounded-full"
							>
								<div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
									<User className="h-4 w-4 text-primary-foreground" />
								</div>
							</Button>
						</DropdownMenuTrigger>
						<DropdownMenuContent
							align="end"
							className="w-56"
							side="right"
							sideOffset={8}
						>
							<div className="px-2 py-2 border-b">
								<p className="text-sm font-medium">John Doe</p>
								<p className="text-xs text-muted-foreground">
									john@example.com
								</p>
							</div>
							<DropdownMenuItem className="gap-2 cursor-pointer mt-1">
								<User className="h-4 w-4" />
								<span>Profile</span>
							</DropdownMenuItem>
							<DropdownMenuItem className="gap-2 cursor-pointer">
								<Settings className="h-4 w-4" />
								<span>Settings</span>
							</DropdownMenuItem>
							<DropdownMenuSeparator />
							<DropdownMenuItem
								className="gap-2 cursor-pointer text-destructive focus:text-destructive"
								onClick={handleSignout}
							>
								<LogOut className="h-4 w-4 text-red-500" />
								<span>Log out</span>
							</DropdownMenuItem>
						</DropdownMenuContent>
					</DropdownMenu>
				)}
			</SidebarFooter>
		</Sidebar>
	);
}
