// Thin wrapper over the backend REST API. All network calls go through here.
async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = Array.isArray(body.detail)
      ? body.detail.map((d) => d.msg).join("; ")
      : body.detail;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  listProjects: () => request("/projects"),
  createProject: (data) => request("/projects", { method: "POST", body: JSON.stringify(data) }),
  deleteProject: (id) => request(`/projects/${id}`, { method: "DELETE" }),

  listEntries: (from, to) => request(`/entries?from=${from}&to=${to}`),
  createEntry: (data) => request("/entries", { method: "POST", body: JSON.stringify(data) }),
  updateEntry: (id, data) => request(`/entries/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteEntry: (id) => request(`/entries/${id}`, { method: "DELETE" }),

  summary: (from, to) => request(`/summary?from=${from}&to=${to}`),
};
