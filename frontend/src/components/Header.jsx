import React from 'react';
import { Activity, Download, PlayCircle } from 'lucide-react';

export default function Header({ onExportCsv }) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <h1>
          <Activity size={26} color="#38bdf8" />
          QoE-Aware Adaptive Video Streaming Simulator
        </h1>
        <p className="subtitle">
          Dynamic Bandwidth Allocation &amp; Buffer-Aware QoE Optimization over Shared Bottleneck Links
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span className="badge badge-info">BTech Subject Project</span>
        <span className="badge badge-success">Discrete Time (Δt=0.5s)</span>
        <button className="btn btn-outline" onClick={onExportCsv} title="Download CSV of simulation results">
          <Download size={14} />
          Export CSV
        </button>
      </div>
    </header>
  );
}
