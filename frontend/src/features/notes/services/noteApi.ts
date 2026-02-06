import apiClient from "../../../services/apiClient";

export interface Note {
    id: string;
    title: string;
    description: string | null;
    file_url: string;
    file_type: string;
    created_at: string;
}

export const getNotes = async (): Promise<Note[]> => {
    const response = await apiClient.get("/api/notes/");
    return response.data;
};

export const uploadNote = async (formData: FormData): Promise<Note> => {
    const response = await apiClient.post("/api/notes/upload", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
    return response.data;
};
