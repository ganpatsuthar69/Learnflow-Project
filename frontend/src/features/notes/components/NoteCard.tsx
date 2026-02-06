import { Card, CardContent, CardHeader, CardTitle } from "../../../components/Profile/ui/card";
import type { Note } from "../services/noteApi";
import { FileText, Image as ImageIcon, File, FileType, Download } from "lucide-react";
import { format } from "date-fns";
import { Button } from "../../../components/Profile/ui/button";

interface NoteCardProps {
    note: Note;
}

export function NoteCard({ note }: NoteCardProps) {
    const getIcon = (type: string) => {
        switch (type) {
            case "pdf":
                return <FileText className="h-10 w-10 text-red-500" />;
            case "word":
                return <FileText className="h-10 w-10 text-blue-500" />;
            case "ppt":
                return <FileType className="h-10 w-10 text-orange-500" />;
            case "image":
                return <ImageIcon className="h-10 w-10 text-green-500" />;
            default:
                return <File className="h-10 w-10 text-gray-500" />;
        }
    };

    return (
        <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-lg font-bold truncate">{note.title}</CardTitle>
                {getIcon(note.file_type)}
            </CardHeader>
            <CardContent>
                {note.description && (
                    <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                        {note.description}
                    </p>
                )}
                <div className="flex items-center justify-between text-xs text-muted-foreground mt-4">
                    <span>{format(new Date(note.created_at), "PPP")}</span>
                    <Button variant="outline" size="sm" asChild>
                        <a href={note.file_url} target="_blank" rel="noopener noreferrer">
                            <Download className="mr-2 h-4 w-4" />
                            Open
                        </a>
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
