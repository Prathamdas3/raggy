import { createFileRoute } from "@tanstack/react-router";
import { SidebarProvider } from "@/components/ui/sidebar";
import AppSidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import UploadDocs from "@/components/UploadDoc";

export const Route = createFileRoute("/chats/")({
	component: App,
});

function App() {
	
	return (
		<SidebarProvider>
			<AppSidebar />
			<div className="max-h-dvh w-full">
				<Header />
				<main className="w-full h-[calc(100dvh-3.5rem)] flex justify-center items-center">
					<div>
					<h3 className="text-center font-semibold text-3xl text-gray-600 mb-4">Wellcome, how can I help you today...</h3>
					<UploadDocs />
					</div>
				</main>
			</div>
		</SidebarProvider>
	);
}
