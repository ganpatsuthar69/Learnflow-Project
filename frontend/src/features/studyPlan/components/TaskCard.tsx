import { type Task, updateTask } from "../services/studyPlanApi";
import { Card, CardContent } from "../../../components/Profile/ui/card";
import { Checkbox } from "../../../components/Profile/ui/checkbox";
import { Badge } from "../../../components/Profile/ui/badge";
import { Clock, AlertCircle, ArrowRight, Calendar } from "lucide-react";
import { format } from "date-fns";
import { cn } from "../../../lib/utils";
import { toast } from "sonner";

interface TaskCardProps {
    task: Task;
    onUpdate: () => void;
}

export function TaskCard({ task, onUpdate }: TaskCardProps) {
    const handleStatusChange = async (checked: boolean) => {
        try {
            await updateTask(task.id, { status: checked ? "completed" : "pending" });
            toast.success(checked ? "Task completed!" : "Task marked as pending");
            onUpdate();
        } catch (error) {
            console.error(error);
            toast.error("Failed to update task");
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case "high": return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300";
            case "medium": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300";
            case "low": return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
            default: return "bg-gray-100 text-gray-800";
        }
    };

    const handleCarryForward = async () => {
        try {
            const today = new Date().toISOString().split('T')[0];
            await updateTask(task.id, {
                planned_date: today,
                status: "pending"
            });
            toast.success("Task carried forward to today");
            onUpdate();
        } catch (error) {
            console.error(error);
            toast.error("Failed to update task");
        }
    };

    const isMissed = task.status === "missed";
    const isCompleted = task.status === "completed";

    return (
        <Card className={cn("transition-all", isCompleted ? "opacity-60" : "", isMissed ? "border-red-200 bg-red-50/50 dark:bg-red-900/10" : "")}>
            <CardContent className="p-4 flex items-start gap-4">
                <Checkbox
                    checked={isCompleted}
                    onCheckedChange={handleStatusChange}
                    className="mt-1"
                />

                <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                        <h4 className={cn("font-medium leading-none", isCompleted && "line-through text-muted-foreground")}>
                            {task.title}
                        </h4>
                        <div className="flex items-center gap-2">
                            {isMissed && (
                                <button
                                    onClick={handleCarryForward}
                                    className="text-xs flex items-center gap-1 text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded-md transition-colors"
                                    title="Move to Today"
                                >
                                    <ArrowRight size={12} />
                                    Carry Forward
                                </button>
                            )}
                            <Badge variant="outline" className={getPriorityColor(task.priority)}>
                                {task.priority}
                            </Badge>
                        </div>
                    </div>

                    <p className="text-sm text-muted-foreground">{task.subject} {task.topic && `• ${task.topic}`}</p>

                    <div className="flex items-center gap-4 text-xs text-muted-foreground mt-2">
                        {task.estimated_time && (
                            <div className="flex items-center gap-1">
                                <Clock size={12} />
                                <span>{task.estimated_time}h</span>
                            </div>
                        )}
                        <div className="flex items-center gap-1">
                            <Calendar size={12} />
                            <span>{format(new Date(task.planned_date), "MMM d")}</span>
                        </div>
                        {isMissed && (
                            <div className="flex items-center gap-1 text-red-500 font-medium">
                                <AlertCircle size={12} />
                                <span>Missed</span>
                            </div>
                        )}
                        {task.is_carried_forward && (
                            <Badge variant="secondary" className="text-xs">Carried Forward</Badge>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
