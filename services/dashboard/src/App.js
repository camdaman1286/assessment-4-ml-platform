import React, { useState, useEffect } from 'react';
import axios from 'axios';

const GATEWAY_URL = process.env.REACT_APP_GATEWAY_URL || '';

const styles = {
  container: { fontFamily: 'monospace', maxWidth: '900px', margin: '0 auto', padding: '2rem' },
  header: { borderBottom: '2px solid #333', paddingBottom: '1rem', marginBottom: '2rem' },
  title: { fontSize: '1.5rem', fontWeight: 'bold' },
  section: { marginBottom: '2rem' },
  sectionTitle: { fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '1rem' },
  pod: { display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' },
  dot: (status) => ({
    width: '10px', height: '10px', borderRadius: '50%',
    backgroundColor: status === 'Running' ? '#22c55e' : '#ef4444'
  }),
  input: { padding: '0.5rem', width: '100%', marginBottom: '0.5rem', fontFamily: 'monospace' },
  button: { padding: '0.5rem 1rem', cursor: 'pointer', fontFamily: 'monospace' },
  response: { background: '#f4f4f4', padding: '1rem', marginTop: '1rem', whiteSpace: 'pre-wrap' },
  error: { color: '#ef4444' }
};

// Mock pod data — replace with real k8s metrics API when available
const MOCK_PODS = [
  { name: 'model-service', namespace: 'default', status: 'Running' },
  { name: 'data-service', namespace: 'ml-platform', status: 'Running' },
  { name: 'gateway-service', namespace: 'ml-platform', status: 'Running' },
];

function PodStatus() {
  return (
    <div style={styles.section}>
      <div style={styles.sectionTitle}>Service Status</div>
      {MOCK_PODS.map(pod => (
        <div key={pod.name} style={styles.pod}>
          <div style={styles.dot(pod.status)} />
          <span>{pod.name}</span>
          <span style={{ color: '#888' }}>({pod.namespace})</span>
          <span>{pod.status}</span>
        </div>
      ))}
    </div>
  );
}

function PredictForm() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setError(null);
    setResponse(null);
    try {
      const res = await axios.post(`${GATEWAY_URL}/predict`, { input });
      setResponse(JSON.stringify(res.data, null, 2));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div style={styles.section}>
      <div style={styles.sectionTitle}>Predict</div>
      <input
        style={styles.input}
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Enter input for model..."
      />
      <button style={styles.button} onClick={handleSubmit}>Run Predict</button>
      {response && <div style={styles.response}>{response}</div>}
      {error && <div style={styles.error}>{error}</div>}
    </div>
  );
}

function IngestForm() {
  const [payload, setPayload] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setError(null);
    setResponse(null);
    try {
      const res = await axios.post(`${GATEWAY_URL}/ingest`, { payload });
      setResponse(JSON.stringify(res.data, null, 2));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div style={styles.section}>
      <div style={styles.sectionTitle}>Ingest</div>
      <input
        style={styles.input}
        value={payload}
        onChange={e => setPayload(e.target.value)}
        placeholder="Enter payload to ingest..."
      />
      <button style={styles.button} onClick={handleSubmit}>Run Ingest</button>
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
        <div style={{ color: '#888', fontSize: '0.85rem' }}>assessment-4 | dev</div>
      </div>
      <PodStatus />
      <PredictForm />
      <IngestForm />
    </div>
  );
}
