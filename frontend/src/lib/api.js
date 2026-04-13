const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch (_err) {
      // Ignore parse failures and return generic message.
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  getSubjects: () => request("/subjects"),
  getChapters: (subjectId) => request(`/chapters?subject_id=${subjectId}`),
  getTopics: (chapterId) => request(`/topics?chapter_id=${chapterId}`),
  getQuestions: (params) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, String(value));
      }
    });
    return request(`/questions?${query.toString()}`);
  },
  getQuestionsCount: (params) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, String(value));
      }
    });
    return request(`/questions/count?${query.toString()}`);
  },
  updateQuestion: (questionId, payload) =>
    request(`/questions/${questionId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }),
  deleteQuestion: (questionId) =>
    request(`/questions/${questionId}`, {
      method: "DELETE"
    }),
  submitAttempt: (payload) =>
    request("/attempt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }),
  getStats: () => request("/stats"),
  getAttempts: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, String(value));
      }
    });
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return request(`/attempts${suffix}`);
  },
  importCsv: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/import/csv", {
      method: "POST",
      body: formData
    });
  },
  importJson: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/import/json", {
      method: "POST",
      body: formData
    });
  },
  validateCsv: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/import/validate/csv", {
      method: "POST",
      body: formData
    });
  },
  validateJson: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/import/validate/json", {
      method: "POST",
      body: formData
    });
  }
};
