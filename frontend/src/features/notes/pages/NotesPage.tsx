import { useEffect, useState } from "react";
import { getNotes, type Note } from "../services/noteApi";
import { NoteCard } from "../components/NoteCard";
import { UploadNoteDialog } from "../components/UploadNoteDialog";
import AppLayout from "../../../components/AppLayout";
import { Loader2 } from "lucide-react";

export default function NotesPage() {
    const [notes, setNotes] = useState<Note[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchNotes = async () => {
        setIsLoading(true);
        try {
            const data = await getNotes();
            setNotes(data);
        } catch (error) {
            console.error("Failed to fetch notes", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchNotes();
    }, []);

    return (
        <AppLayout>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">My Notes</h1>
                        <p className="text-muted-foreground mt-2">
                            Manage and view your uploaded study materials.
                        </p>
                    </div>
                    <UploadNoteDialog onUploadSuccess={fetchNotes} />
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    </div>
                ) : notes.length > 0 ? (
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {notes.map((note) => (
                            <NoteCard key={note.id} note={note} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-20 bg-muted/20 rounded-xl border border-dashed border-border">
                        <p className="text-muted-foreground">No notes found. Upload your first note!</p>
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
