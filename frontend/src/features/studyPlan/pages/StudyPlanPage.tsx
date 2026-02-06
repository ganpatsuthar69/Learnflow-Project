import { useEffect, useState } from "react";
import { getTasks, getSummary, type Task, type TaskSummary } from "../services/studyPlanApi";
import { TaskCard } from "../components/TaskCard";
import { AddTaskDialog } from "../components/AddTaskDialog";
import AppLayout from "../../../components/AppLayout";
import { Loader2, CheckCircle2, Clock, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/Profile/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../../components/Profile/ui/tabs";
import { isToday, parseISO, isFuture } from "date-fns";

export default function StudyPlanPage() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [summary, setSummary] = useState<TaskSummary | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [tasksData, summaryData] = await Promise.all([
                getTasks(),
                getSummary()
            ]);
            setTasks(tasksData);
            setSummary(summaryData);
        } catch (error) {
            console.error("Failed to fetch study plan data", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleTaskUpdate = () => {
        getTasks().then(setTasks);
        getSummary().then(setSummary);
    };

    useEffect(() => {
        fetchData();
    }, []);

    const todayTasks = tasks.filter(t => isToday(parseISO(t.planned_date)) && t.status !== "completed" && t.status !== "missed");
    const upcomingTasks = tasks.filter(t => isFuture(parseISO(t.planned_date)) && t.status !== "completed");
    const missedTasks = tasks.filter(t => t.status === "missed");
    const completedTasks = tasks.filter(t => t.status === "completed");

    return (
        <AppLayout>
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Study Plan</h1>
                        <p className="text-muted-foreground mt-2">
                            Organize your learning schedule.
                        </p>
                    </div>
                    <AddTaskDialog onTaskAdded={fetchData} />
                </div>

                {/* Summary Stats */}
                <div className="grid gap-4 md:grid-cols-3">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Pending</CardTitle>
                            <Clock className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{summary?.pending || 0}</div>
                            <p className="text-xs text-muted-foreground">Today & Upcoming</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Completed</CardTitle>
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{summary?.completed || 0}</div>
                            <p className="text-xs text-muted-foreground">Tasks finished</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Missed</CardTitle>
                            <AlertTriangle className="h-4 w-4 text-red-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{summary?.missed || 0}</div>
                            <p className="text-xs text-muted-foreground text-red-500">Action required</p>
                        </CardContent>
                    </Card>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-10">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    </div>
                ) : (
                    <Tabs defaultValue="today" className="space-y-4">
                        <TabsList>
                            <TabsTrigger value="today" className="gap-2">
                                Today <span className="bg-primary/10 text-primary px-1.5 rounded-full text-xs">{todayTasks.length}</span>
                            </TabsTrigger>
                            <TabsTrigger value="upcoming" className="gap-2">
                                Upcoming <span className="bg-primary/10 text-primary px-1.5 rounded-full text-xs">{upcomingTasks.length}</span>
                            </TabsTrigger>
                            <TabsTrigger value="missed" className="gap-2">
                                Missed <span className="bg-red-100 text-red-600 px-1.5 rounded-full text-xs">{missedTasks.length}</span>
                            </TabsTrigger>
                            <TabsTrigger value="completed">Completed</TabsTrigger>
                        </TabsList>

                        <TabsContent value="today" className="space-y-4">
                            {todayTasks.length > 0 ? todayTasks.map(task => (
                                <TaskCard key={task.id} task={task} onUpdate={handleTaskUpdate} />
                            )) : (
                                <p className="text-center text-muted-foreground py-10">No tasks for today.</p>
                            )}
                        </TabsContent>

                        <TabsContent value="upcoming" className="space-y-4">
                            {upcomingTasks.length > 0 ? upcomingTasks.map(task => (
                                <TaskCard key={task.id} task={task} onUpdate={handleTaskUpdate} />
                            )) : (
                                <p className="text-center text-muted-foreground py-10">No upcoming tasks.</p>
                            )}
                        </TabsContent>

                        <TabsContent value="missed" className="space-y-4">
                            {missedTasks.length > 0 ? missedTasks.map(task => (
                                <TaskCard key={task.id} task={task} onUpdate={handleTaskUpdate} />
                            )) : (
                                <p className="text-center text-muted-foreground py-10">No missed tasks! Great job.</p>
                            )}
                        </TabsContent>

                        <TabsContent value="completed" className="space-y-4">
                            {completedTasks.length > 0 ? completedTasks.map(task => (
                                <TaskCard key={task.id} task={task} onUpdate={handleTaskUpdate} />
                            )) : (
                                <p className="text-center text-muted-foreground py-10">No completed tasks yet.</p>
                            )}
                        </TabsContent>
                    </Tabs>
                )}
            </div>
        </AppLayout>
    );
}
