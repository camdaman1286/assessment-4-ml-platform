import React, { useState } from "react";
import axios from "axios";

const styles = {
  container: { fontFamily: "monospace", maxWidth: "900px", margin: "0 auto", padding: "2rem" },
  header: { borderBottom: "2px solid #333", paddingBottom: "1rem", marginBottom: "2rem" },
  title: { fontSize: "1.5rem", fontWeight: "bold" },
  section: { marginBottom: "2rem", border: "1px solid #ddd", padding: "1rem", borderRadius: "4px" },
  sectionTitle: { fontSize: "1.1rem", fontWeight: "bold", marginBottom: "1rem" },
  pod: { display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" },
  dot: (status) => ({ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: status === "Running" ? "#22c55e" : "#ef4444" }),
  input: { padding: "0.5rem", width: "100%", marginBottom: "0.5rem", fontFamily: "monospace", boxSizing: "border-box" },
  button: { padding: "0.5rem 1rem", cursor: "pointer", fontFamily: "monospace", backgroundColor: "#333", color: "#fff", border: "none", borderRadius: "4px" },
  response: { background: "#f4f4f4", padding: "1rem", marginTop: "1rem", whiteSpace: "pre-wrap", borderRadius: "4px" },
  error: { color: "#ef4444", marginTop: "0.5rem" },
  grid: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" },
  tag: (color) => ({ display: "inline-block", padding: "2px 8px", borderRadius: "4px", backgroundColor: color, color: "#fff", fontSize: "0.75rem", marginLeft: "0.5rem" })
};

const SERVICES = [
  { name: "fraud-service", namespace: "ml-platform", status: "Running" },
  { name: "recommendations-service", namespace: "ml-platform", status: "Running" },
  { name: "forecasting-service", namespace: "ml-platform", status: "Running" },
  { name: "gateway-service", namespace: "ml-platform", status: "Running" },
  { name: "data-service", namespace: "ml-platform", status: "Running" },
  { name: "model-service", namespace: "default", status: "Running" },
  { name: "dashboard", namespace: "ml-platform", status: "Running" },
];

function ServiceStatus() {
  return (
    <div style={styles.section}>
      <div style={styles.sectionTitle}>Service Status</div>
      {SERVICES.map(svc => (
        <div key={svc.name} style={styles.pod}>
          <div style={styles.dot(svc.status)} />
          <span>{svc.name}</span>
          <span style={{ color: "#888" }}>({svc.namespace})</span>
          <span style={styles.tag("#6366f1")}>{svc.status}</span>
        </div>
      ))}
    </div>
  );
}

function ApiForm({ title, endpoint, fields, buildPayload, tag, tagColor }) {
  const [values, setValues] = useState({});
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError(null);
    setResponse(null);
    setLoading(true);
    try {
      const res = await axios.post(endpoint, buildPayload(values), { timeout: 15000 });
      setResponse(JSON.stringify(res.data, null, 2));
    } catch (e) {
      setError(e.response ? JSON.stringify(e.response.data) : e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.section}>
      <div style={styles.sectionTitle}>
        {title}
        <span style={styles.tag(tagColor)}>{tag}</span>
      </div>
      {fields.map(f => (
        <div key={f.key}>
          <label style={{ fontSize: "0.8rem", color: "#555" }}>{f.label}</label>
          <input
            style={styles.input}
            value={values[f.key] || ""}
            onChange={e => setValues({ ...values, [f.key]: e.target.value })}
            placeholder={f.placeholder}
          />
        </div>
      ))}
      <button style={styles.button} onClick={handleSubmit} disabled={loading}>
        {loading ? "Running..." : "Submit"}
      </button>
      {response && <div style={styles.response}>{response}</div>}
      {error && <div style={styles.error}>{error}</div>}
    </div>
  );
}

export default function App() {
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.title}>ML Platform Dashboard</div>
        <div style={{ color: "#888", fontSize: "0.85rem" }}>assessment-4 | dev | SageMaker endpoints active</div>
      </div>

      <ServiceStatus />

      <div style={styles.grid}>
        <ApiForm
          title="Fraud Detection"
          endpoint="/fraud"
          tag="XGBoost"
          tagColor="#dc2626"
          fields={[{ key: "features", label: "CSV Features", placeholder: "0.5,1.2,0.3,..." }]}
          buildPayload={v => ({ features: v.features })}
        />

        <ApiForm
          title="Recommendations"
          endpoint="/recommend"
          tag="Factorization Machines"
          tagColor="#2563eb"
          fields={[
            { key: "user_id", label: "User ID (0-99)", placeholder: "5" },
            { key: "item_id", label: "Item ID (0-49)", placeholder: "10" }
          ]}
          buildPayload={v => ({ user_id: parseInt(v.user_id), item_id: parseInt(v.item_id) })}
        />

        <ApiForm
          title="Forecasting"
          endpoint="/forecast"
          tag="DeepAR"
          tagColor="#16a34a"
          fields={[
            { key: "start", label: "Start Date", placeholder: "2024-01-01" },
            { key: "target", label: "Historical Values (min 14, comma separated)", placeholder: "10.9,11.3,14.6,..." }
          ]}
          buildPayload={v => ({ start: v.start, target: v.target.split(",").map(Number) })}
        />
      </div>
    </div>
  );
}
