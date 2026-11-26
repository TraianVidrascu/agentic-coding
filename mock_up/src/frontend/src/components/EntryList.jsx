import { formatMinutes } from "../dates.js";

export default function EntryList({ entries, projects, onEdit, onDelete }) {
  const byId = Object.fromEntries(projects.map((p) => [p.id, p]));

  if (entries.length === 0) {
    return <p className="card muted">No entries this week yet.</p>;
  }

  return (
    <table className="card entries">
      <thead>
        <tr>
          <th>Date</th><th>Time</th><th>Project</th><th>Description</th><th>Duration</th><th></th>
        </tr>
      </thead>
      <tbody>
        {entries.map((e) => {
          const project = byId[e.project_id];
          return (
            <tr key={e.id}>
              <td>{e.date}</td>
              <td>{e.start_time}–{e.end_time}</td>
              <td>
                {project ? (
                  <span className="tag" style={{ background: project.color }}>{project.name}</span>
                ) : (
                  <span className="muted">—</span>
                )}
              </td>
              <td>{e.description}</td>
              <td>{formatMinutes(e.minutes)}</td>
              <td className="actions">
                <button onClick={() => onEdit(e)}>Edit</button>
                <button onClick={() => onDelete(e.id)}>Delete</button>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
