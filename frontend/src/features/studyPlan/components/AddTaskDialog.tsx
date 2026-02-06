import { useState } from "react";
import { useForm } from "react-hook-form";
import { createTask, type TaskCreate } from "../services/studyPlanApi";
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/Profile/ui/select";
import { toast } from "sonner";
import { Loader2, Plus } from "lucide-react";

interface AddTaskDialogProps {
    onTaskAdded: () => void;
}

export function AddTaskDialog({ onTaskAdded }: AddTaskDialogProps) {
    const [open, setOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const { register, handleSubmit, reset, setValue } = useForm<TaskCreate>();

    const onSubmit = async (data: TaskCreate) => {
        setIsLoading(true);
        try {
            await createTask(data);
            toast.success("Task added successfully");
            setOpen(false);
            reset();
            onTaskAdded();
        } catch (error) {
            console.error(error);
            toast.error("Failed to add task");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Task
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Add Study Task</DialogTitle>
                    <DialogDescription>
                        Create a new task for your daily study plan.
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
                            <Label htmlFor="subject" className="text-right">
                                Subject
                            </Label>
                            <Input
                                id="subject"
                                className="col-span-3"
                                {...register("subject", { required: true })}
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="topic" className="text-right">
                                Topic
                            </Label>
                            <Input
                                id="topic"
                                className="col-span-3"
                                {...register("topic")}
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="priority" className="text-right">
                                Priority
                            </Label>
                            <Select onValueChange={(val) => setValue("priority", val)} defaultValue="medium">
                                <SelectTrigger className="col-span-3">
                                    <SelectValue placeholder="Select priority" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="high">High</SelectItem>
                                    <SelectItem value="medium">Medium</SelectItem>
                                    <SelectItem value="low">Low</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="planned_date" className="text-right">
                                Date
                            </Label>
                            <Input
                                id="planned_date"
                                type="date"
                                className="col-span-3"
                                {...register("planned_date", { required: true })}
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="estimated_time" className="text-right">
                                Est. Time (h)
                            </Label>
                            <Input
                                id="estimated_time"
                                type="number"
                                step="0.5"
                                className="col-span-3"
                                {...register("estimated_time", { valueAsNumber: true })}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isLoading}>
                            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Add Task
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
