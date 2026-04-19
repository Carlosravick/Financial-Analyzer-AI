import { UploadResponse } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Network response was not ok");
    
    return res.json();
  },

  askQuestion: async (question: string): Promise<{ answer: string }> => {
    const res = await fetch(`${API_BASE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error("Network response was not ok");

    return res.json();
  }
};
