import { Skeleton } from "../ui/skeleton";

export default function ChatSkeleton() {
	return (
		<div className="flex gap-3 mb-4 px-4">
			<Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
			<div className="flex-1 space-y-2 max-w-[80%]">
				<Skeleton className="h-4 w-full" />
				<Skeleton className="h-4 w-5/6" />
				<Skeleton className="h-4 w-4/6" />
				<Skeleton className="h-4 w-full" />
				<Skeleton className="h-4 w-3/6" />
			</div>
		</div>
	);
}
