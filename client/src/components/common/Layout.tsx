import Header from "./Header";
import AppSidebar from "./Sidebar";


export default function Layout({ children }: { children: React.ReactNode }) {
    return <>
        <AppSidebar />
        <div className="min-h-dvh  w-full flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-auto">
                {children}
            </main>
        </div>
    </>
}