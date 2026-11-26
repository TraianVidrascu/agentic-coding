import { useState } from "react";

const blank = (date) => ({
  date,
  start_time: "09:00",
  end_time: "10:00",
  project_id: "",
  description: "",
});

export default function EntryForm({ projects, initial, defaultDate, onSave, onCancel }) {
  const [form, setForm] = useState(() =>
    initial ? { ...initial, project_id: initial.project_id ?? "" } : blank(defaultDate)
  );

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    const ok = await onSave({
      date: form.date,
      start_time: form.start_time,
      end_time: form.end_time,
      project_id: form.project_id === "" ? null : Number(form.project_id),
      description: form.description,
    });
    if (ok && !initial) setForm(blank(form.date));
  };

  return (
    <form className="card entry-form" onSubmit={submit}>
      <h2>{initial ? "Edit entry" : "Log time"}</h2>
      <div className="row">
        <input type="date" value={form.date} onChange={set("date")} required />
        <input type="time" value={form.start_time} onChange={set("start_time")} required />
        <input type="time" value={form.end_time} onChange={set("end_time")} required />
        <select value={form.project_id} onChange={set("project_id")}>
          <option value="">(no project)</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>
      <input
        className="wide"
        placeholder="What did you work on?"
        value={form.description}
        onChange={set("description")}
      />
      <div className="row">
        <button type="submit">{initial ? "Save" : "Add"}</button>
        {initial && <button type="button" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  );
}
