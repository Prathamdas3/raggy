import type { LucideIcon } from "lucide-react";
import { Button } from "./ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";

type btnType =
	| "link"
	| "default"
	| "destructive"
	| "outline"
	| "secondary"
	| "ghost"
	| null
	| undefined;

interface Props {
	Icon: LucideIcon;
	content: string;
	type?: btnType;
	side?: "top" | "bottom" | "left" | "right";
	action?: <T>(arg?: T) => void;
}

export default function TooltipIcon({
	Icon,
	content,
	action,
	type = "outline",
	side = "bottom",
}: Props) {
	return (
		<Tooltip>
			<TooltipTrigger asChild>
				<Button
					onClick={action}
					className="w-8 h-8 p-1"
					size="icon"
					variant={type}
				>
					<Icon className="w-4 h-4" />
				</Button>
			</TooltipTrigger>
			<TooltipContent side={side}>{content}</TooltipContent>
		</Tooltip>
	);
}
