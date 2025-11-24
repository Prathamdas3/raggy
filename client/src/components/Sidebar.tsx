import { Link } from "@tanstack/react-router";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarHeader,
	SidebarTrigger,
	useSidebar,
} from "./ui/sidebar";
import { Button } from "./ui/button";
import { ArrowBigRightDash, FolderPlus, User } from "lucide-react";
import { SquarePen, Search, Bookmark } from "lucide-react";

export default function AppSidebar() {
	const { open, setOpen } = useSidebar();

	return (
		<Sidebar collapsible="icon">
			<SidebarHeader>
				{open ? (
					<div className="flex justify-between">
						<Link to="/chats">Logo</Link>
						<SidebarTrigger size="sm" />
					</div>
				) : (
					<Button
						size="icon"
						variant="outline"
						onClick={() => setOpen(true)}
						className="w-8 h-8 p-1"
					>
						<ArrowBigRightDash className="h-4 w-4" />
					</Button>
				)}
			</SidebarHeader>
			<SidebarContent>
				<SidebarGroup>
					<div className="flex gap-2 h-10 items-center">
						<Button size="icon" variant="ghost">
							<SquarePen className="h-8 w-8" />
						</Button>
						{open && "New Chat"}
					</div>
					<div className="flex gap-2 h-10 items-center">
						<Button size="icon" variant="ghost" className="h-12">
							<Search className="h-12 w-12" />
						</Button>
						{open && "Search Chat"}
					</div>
				</SidebarGroup>
				<SidebarGroup>
					{open && (
						<>
							<h4>Folders</h4>
							<div className="flex gap-2 h-12 items-center">
								<Button size="icon" variant="ghost" className="h-12">
									<FolderPlus className="h-12 w-12" />
								</Button>
								{open && "Create Folder"}
							</div>
							<div className="px-2 flex gap-2 items-center ">
								<Bookmark className="h-4 w-4" />
								{open && "Bookmarks"}
							</div>
						</>
					)}
				</SidebarGroup>
				<SidebarGroup>
					{open&&<>
					<h4>Your chats</h4>
					<div className=""></div>
					</>}
				</SidebarGroup>
			</SidebarContent>
			<SidebarFooter className={`${open && "border-t"}`}>
				{open ? (
					<div className="flex gap-2 items-center p-1">
						<Button
							size="icon"
							variant="outline"
							className="w-8 h-8  rounded-full"
						>
							<User className="h-4 w-4" />
						</Button>
						<h3 className="text-md">User</h3>
					</div>
				) : (
					<Button size="icon" variant="outline" className="w-8 h-8 p-1">
						<User className="h-4 w-4" />
					</Button>
				)}
			</SidebarFooter>
		</Sidebar>
	);
}
