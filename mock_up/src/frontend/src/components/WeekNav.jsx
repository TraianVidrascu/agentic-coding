import { addDays, iso, mondayOf } from "../dates.js";

export default function WeekNav({ weekStart, onChange }) {
  const end = addDays(weekStart, 6);
  return (
    <nav className="week-nav">
      <button onClick={() => onChange(addDays(weekStart, -7))}>← Prev</button>
      <strong>{iso(weekStart)} → {iso(end)}</strong>
      <button onClick={() => onChange(addDays(weekStart, 7))}>Next →</button>
      <button onClick={() => onChange(mondayOf(new Date()))}>This week</button>
    </nav>
  );
}
