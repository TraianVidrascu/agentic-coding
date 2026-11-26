import { useState } from "react";

export default function ProjectManager({ projects, onCreate, onDelete }) {
  const [name, setName] = useState("");
  const [color, setColor] = useState("#2563eb");

  const submit = async (e) => {
    e.preventDefault();
    if (await onCreate({ name: name.trim(), color })) setName("");
  };

  return (
    <section className="card">
      <h2>Projects</h2>
      <form className="row" onSubmit={submit}>
        <input placeholder="New project" value={name} onChange={(e) => setName(e.target.value)} required />
        <input type="color" value={color} onChange={(e) => setColor(e.target.value)} />
        <button type="submit">Add</button>
      </form>
      <ul className="projects">
        {projects.map((p) => (
          <li key={p.id}>
            <span className="tag" style={{ background: p.color }}>{p.name}</span>
            <button onClick={() => onDelete(p.id)}>×</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
