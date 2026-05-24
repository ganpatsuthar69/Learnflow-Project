import apiClient from "../../../services/apiClient";

export interface Task {
    id: string;
    title: string;
    description?: string;
    subject: string;
    topic?: string;
    status: "pending" | "completed" | "missed";
    priority: "high" | "medium" | "low";
    planned_date: string;
    estimated_time?: number;
    is_carried_forward: boolean;
    created_at: string;
}

export interface TaskCreate {
    title: string;
    description?: string;
    subject: string;
    topic?: string;
    priority?: string;
    planned_date: string;
    estimated_time?: number;
}

export interface TaskUpdate {
    title?: string;
    description?: string;
    subject?: string;
    topic?: string;
    status?: string;
    priority?: string;
    planned_date?: string;
    estimated_time?: number;
}

export interface TaskSummary {
    total: number;
    completed: number;
    pending: number;
    missed: number;
}

export const getTasks = async (date?: string, status?: string): Promise<Task[]> => {
    const params = new URLSearchParams();
    if (date) params.append("date", date);
    if (status) params.append("status", status);

    const response = await apiClient.get<Task[]>(`/api/tasks/?${params.toString()}`);
    return response.data;
};

export const createTask = async (data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>("/api/tasks/", data);
    return response.data;
};

export const updateTask = async (id: string, data: TaskUpdate): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/api/tasks/${id}`, data);
    return response.data;
};

export const getSummary = async (): Promise<TaskSummary> => {
    const response = await apiClient.get<TaskSummary>("/api/tasks/summary");
    return response.data;
};
