import { Link, useLocation, useNavigate } from "react-router-dom";
import {
    BookOpen,
    Brain,
    Calendar,
    FileText,
    BarChart3,
    LogOut,
    UserRoundPen,
    X,
    ChevronRight
} from "lucide-react";

interface SidebarProps {
    isOpen: boolean;
    onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        navigate("/login", { replace: true });
    };

    const menuItems = [
        { icon: BarChart3, label: "Dashboard", path: "/dashboard" },
        { icon: BookOpen, label: "Roadmap", path: "/roadmap" },
        { icon: FileText, label: "Notes", path: "/notes" },
        { icon: Brain, label: "AI Notes", path: "/ai-notes" },
        { icon: Calendar, label: "Study Plan", path: "/study-plan" },
        { icon: FileText, label: "Quiz", path: "/quiz" },
        { icon: UserRoundPen, label: "Profile", path: "/profile" },
    ];

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm transition-opacity"
                    onClick={onClose}
                />
            )}

            {/* Sidebar Container */}
            <aside
                className={`
          fixed top-0 left-0 z-50 h-full w-72 bg-card border-r border-border
          transform transition-transform duration-300 ease-in-out
          md:translate-x-0 md:static md:h-screen shadow-2xl md:shadow-none
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
            >
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="p-6 border-b border-border flex items-center justify-between">
                        <div className="flex items-center gap-2 font-bold text-2xl text-primary tracking-tight">
                            <span className="bg-primary text-primary-foreground p-1 rounded-lg">LF</span>
                            LEARNFLOW
                        </div>
                        <button onClick={onClose} className="md:hidden p-1 hover:bg-accent rounded-md">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                        {menuItems.map((item) => {
                            const isActive = location.pathname === item.path;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => onClose()} // Close on mobile click
                                    className={`
                    group flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200
                    ${isActive
                                            ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                                            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                                        }
                  `}
                                >
                                    <div className="flex items-center gap-3">
                                        <item.icon size={20} className={isActive ? "text-primary-foreground" : "text-muted-foreground group-hover:text-primary"} />
                                        <span className="font-medium">{item.label}</span>
                                    </div>
                                    {isActive && <ChevronRight size={16} className="opacity-50" />}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User / Logout */}
                    <div className="p-4 border-t border-border bg-muted/20 space-y-2">
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-3 w-full px-4 py-3 text-destructive hover:bg-destructive/10 rounded-xl transition-colors"
                        >
                            <LogOut size={20} />
                            <span className="font-medium">Logout</span>
                        </button>
                    </div>
                </div>
            </aside>
        </>
    );
}
