import Header from "./Header";
import AppSidebar from "./Sidebar";

interface Props {
    children: React.ReactNode,
    tools?: React.ReactNode
    header?: boolean
}


export default function Layout({ children, tools, header }: Props) {
    return <>
        <AppSidebar />
        <div className="min-h-dvh  w-full flex flex-col overflow-hidden">
            {header && <Header tools={tools} />}
            <main className="flex-1 overflow-auto">
                {children}
            </main>
        </div>
    </>
}