import { Download, Forward, Trash } from "lucide-react";
import TooltipIcon from "./TooltipIcons";

export default function Header() {
	return (
		<header className="flex justify-between border-b h-14 items-center px-3  w-full">
			<h3 className="text-xl font-semibold">App Name</h3>
			<nav className="flex justify-evenly gap-2">
				<TooltipIcon Icon={Download} content="Download chat" />
				<TooltipIcon Icon={Forward} content="Share chat" />
				<TooltipIcon Icon={Trash} content="Delete chat" />
			</nav>
		</header>
	);
}
