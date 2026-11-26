import { formatMinutes } from "../dates.js";

export default function Summary({ summary }) {
  if (!summary) return null;
  const projects = Object.entries(summary.by_project).sort((a, b) => b[1] - a[1]);

  return (
    <section className="card">
      <h2>This week: {formatMinutes(summary.total_minutes)}</h2>
      {projects.length === 0 ? (
        <p className="muted">Nothing logged.</p>
      ) : (
        <ul className="summary">
          {projects.map(([name, minutes]) => (
            <li key={name}>
              <span>{name}</span>
              <span>{formatMinutes(minutes)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
