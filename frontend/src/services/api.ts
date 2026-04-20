import { UploadResponse } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
      });
      
      if (!res.ok) {
        const errorData = await res.text();
        throw new Error(`Upload failed: ${res.status} ${res.statusText} - ${errorData}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error("Error uploading file:", error);
      throw error;
    }
  },

  askQuestion: async (question: string): Promise<{ answer: string }> => {
    try {
      const res = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      
      if (!res.ok) {
        const errorData = await res.text();
        throw new Error(`Failed to ask question: ${res.status} ${res.statusText} - ${errorData}`);
      }

      return await res.json();
    } catch (error) {
      console.error("Error asking question:", error);
      throw error;
    }
  }
};
