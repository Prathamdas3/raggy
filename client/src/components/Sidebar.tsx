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
import { ArrowBigRightDash, User } from "lucide-react";

export default function AppSidebar() {
	const { open, setOpen } = useSidebar();

	return (
		<Sidebar collapsible="icon">
			<SidebarHeader>
				{open ? (
					<div className="flex justify-between">
						<Link to="/chats">Logo</Link>
						<SidebarTrigger />
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
				<SidebarGroup></SidebarGroup>
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
