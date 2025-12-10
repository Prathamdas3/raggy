import { Download, Forward, Trash } from "lucide-react";
import TooltipIcon from "./TooltipIcons";
import { useDeleteChat } from "@/hooks/chats";
import { useLocation, useNavigate } from "@tanstack/react-router";
interface Props {
	tools: boolean;
}

export default function Header({ tools }: Props) {
	const { mutate: deleteChat } = useDeleteChat();
	const router = useNavigate();
	const params = useLocation().pathname.split("/").reverse()[0];

	const onDelete = () => {
		deleteChat(params, {
			onSuccess: () => {
				router({ to: "/chats", replace: true });
			},
		});
	};

	return (
		<header className="flex justify-between border-b py-3 items-center px-3  w-full">
			<h3 className="text-xl font-semibold">App Name</h3>
			{tools && (
				<nav className="flex justify-evenly gap-2">
					<TooltipIcon Icon={Download} content="Download chat" />
					<TooltipIcon Icon={Forward} content="Share chat" />
					<TooltipIcon Icon={Trash} content="Delete chat" action={onDelete} />
				</nav>
			)}
		</header>
	);
}
