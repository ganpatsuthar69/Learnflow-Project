import { Construction } from "lucide-react";
import AppLayout from "./AppLayout";

interface ComingSoonProps {
    title: string;
    description: string;
}

export default function ComingSoon({ title, description }: ComingSoonProps) {
    return (
        <AppLayout>
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
                <div className="bg-primary/10 p-6 rounded-full">
                    <Construction className="h-16 w-16 text-primary" />
                </div>
                <div className="space-y-2 max-w-md">
                    <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
                    <p className="text-muted-foreground text-lg">
                        {description}
                    </p>
                </div>
                <div className="bg-muted px-4 py-2 rounded-lg text-sm text-muted-foreground border border-border">
                    Status: Development in Progress
                </div>
            </div>
        </AppLayout>
    );
}
