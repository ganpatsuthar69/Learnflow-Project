import { useState } from "react";
import { useForm } from "react-hook-form";
import { uploadNote } from "../services/noteApi";
import { Button } from "../../../components/Profile/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "../../../components/Profile/ui/dialog";
import { Input } from "../../../components/Profile/ui/input";
import { Label } from "../../../components/Profile/ui/label";
import { Textarea } from "../../../components/Profile/ui/textarea";
import { toast } from "sonner";
import { Loader2, Upload } from "lucide-react";

interface UploadNoteDialogProps {
    onUploadSuccess: () => void;
}

export function UploadNoteDialog({ onUploadSuccess }: UploadNoteDialogProps) {
    const [open, setOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const { register, handleSubmit, reset } = useForm();

    const onSubmit = async (data: any) => {
        setIsLoading(true);
        try {
            const formData = new FormData();
            formData.append("title", data.title);
            if (data.description) formData.append("description", data.description);
            formData.append("file", data.file[0]);

            await uploadNote(formData);
            toast.success("Note uploaded successfully");
            setOpen(false);
            reset();
            onUploadSuccess();
        } catch (error) {
            console.error(error);
            toast.error("Failed to upload note");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Note
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Upload Note</DialogTitle>
                    <DialogDescription>
                        Upload PDF, Word, PowerPoint, or Image files.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="title" className="text-right">
                                Title
                            </Label>
                            <Input
                                id="title"
                                className="col-span-3"
                                {...register("title", { required: true })}
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="description" className="text-right">
                                Description
                            </Label>
                            <Textarea
                                id="description"
                                className="col-span-3"
                                {...register("description")}
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="file" className="text-right">
                                File
                            </Label>
                            <Input
                                id="file"
                                type="file"
                                className="col-span-3"
                                {...register("file", { required: true })}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isLoading}>
                            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Upload
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
