import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import { addDays, iso, mondayOf } from "./dates.js";
import WeekNav from "./components/WeekNav.jsx";
import EntryForm from "./components/EntryForm.jsx";
import EntryList from "./components/EntryList.jsx";
import ProjectManager from "./components/ProjectManager.jsx";
import Summary from "./components/Summary.jsx";

export default function App() {
  const [weekStart, setWeekStart] = useState(() => mondayOf(new Date()));
  const [projects, setProjects] = useState([]);
  const [entries, setEntries] = useState([]);
  const [summary, setSummary] = useState(null);
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");

  const from = iso(weekStart);
  const to = iso(addDays(weekStart, 6));

  const reload = useCallback(async () => {
    try {
      const [p, e, s] = await Promise.all([
        api.listProjects(),
        api.listEntries(from, to),
        api.summary(from, to),
      ]);
      setProjects(p);
      setEntries(e);
      setSummary(s);
      setError("");
    } catch (err) {
      setError(`${err.message} — is the backend running on :8000?`);
    }
  }, [from, to]);

  useEffect(() => {
    reload();
  }, [reload]);

  // Wraps a mutation so every change refreshes state and surfaces errors uniformly.
  const run = (fn) => async (...args) => {
    try {
      await fn(...args);
      await reload();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  const saveEntry = run(async (data) => {
    if (editing) await api.updateEntry(editing.id, data);
    else await api.createEntry(data);
    setEditing(null);
  });

  return (
    <div className="app">
      <header>
        <img src="/logo.svg" alt="" width="32" height="32" />
        <h1>My Timesheet</h1>
      </header>

      {error && <div className="error" onClick={() => setError("")}>{error}</div>}

      <WeekNav weekStart={weekStart} onChange={setWeekStart} />

      <div className="layout">
        <main>
          <EntryForm
            key={editing?.id ?? "new"}
            projects={projects}
            initial={editing}
            defaultDate={iso(new Date())}
            onSave={saveEntry}
            onCancel={() => setEditing(null)}
          />
          <EntryList
            entries={entries}
            projects={projects}
            onEdit={setEditing}
            onDelete={run((id) => api.deleteEntry(id))}
          />
        </main>
        <aside>
          <Summary summary={summary} />
          <ProjectManager
            projects={projects}
            onCreate={run((data) => api.createProject(data))}
            onDelete={run((id) => api.deleteProject(id))}
          />
        </aside>
      </div>
    </div>
  );
}
