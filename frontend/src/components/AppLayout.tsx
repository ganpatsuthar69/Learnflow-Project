import React, { useState } from "react";
import { Sidebar } from "./Sidebar";
import { Menu, Bell } from "lucide-react";

interface AppLayoutProps {
    children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Sidebar */}
            <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Mobile Header */}
                <header className="md:hidden sticky top-0 z-30 bg-background/80 backdrop-blur-md border-b border-border p-4 flex items-center justify-between">
                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="p-2 -ml-2 hover:bg-accent rounded-lg text-foreground"
                    >
                        <Menu size={24} />
                    </button>
                    <span className="font-bold text-lg text-primary">LEARNFLOW</span>
                    <button className="p-2 -mr-2 hover:bg-accent rounded-lg text-foreground">
                        <Bell size={20} />
                    </button>
                </header>

                {/* Content Area */}
                <main className="flex-1 p-4 md:p-8 overflow-y-auto">
                    <div className="max-w-7xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
