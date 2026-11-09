import React from 'react';
import { Play, GitCompare, Settings, Info } from 'lucide-react';

export default function ConfigPanel({ config, setConfig, onRunSimulate, onRunCompare, loading }) {
  const handleChange = (field, val) => {
    setConfig(prev => ({ ...prev, [field]: val }));
  };

  return (
    <div className="card">
      <div className="card-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Settings size={18} color="#38bdf8" />
          Simulation Parameters
        </span>
      </div>

      {/* Number of Clients */}
      <div className="form-group">
        <label>Simultaneous Streaming Clients (N)</label>
        <div className="range-wrap">
          <input
            type="range"
            min="3"
            max="10"
            step="1"
            value={config.num_clients}
            onChange={e => handleChange('num_clients', parseInt(e.target.value))}
          />
          <span className="range-val">{config.num_clients} Clients</span>
        </div>
      </div>

      {/* Bottleneck Bandwidth */}
      <div className="form-group">
        <label>Shared Link Capacity C(t)</label>
        <div className="range-wrap">
          <input
            type="range"
            min="4000"
            max="20000"
            step="1000"
            value={config.base_bandwidth_kbps}
            onChange={e => handleChange('base_bandwidth_kbps', parseFloat(e.target.value))}
          />
          <span className="range-val">{(config.base_bandwidth_kbps / 1000).toFixed(1)} Mbps</span>
        </div>
      </div>

      {/* Network Trace Type */}
      <div className="form-group">
        <label>Network Capacity Profile</label>
        <select
          value={config.trace_type}
          onChange={e => handleChange('trace_type', e.target.value)}
        >
          <option value="fluctuating">Fluctuating (Wave + Congestion Dip)</option>
          <option value="fixed">Fixed Bottleneck (Constant Bandwidth)</option>
          <option value="step_drop">Step Drop (Severe Congestion at t=30s)</option>
        </select>
      </div>

      {/* ABR Algorithm */}
      <div className="form-group">
        <label>Client ABR Algorithm</label>
        <select
          value={config.abr_policy}
          onChange={e => handleChange('abr_policy', e.target.value)}
        >
          <option value="buffer_based">Buffer-Based ABR (BBA)</option>
          <option value="throughput_based">Throughput-Based ABR (Harmonic)</option>
          <option value="hybrid">Hybrid ABR (Throughput + Buffer Guard)</option>
        </select>
      </div>

      {/* Allocation Policy */}
      <div className="form-group">
        <label>Bandwidth Allocation Policy</label>
        <select
          value={config.alloc_policy}
          onChange={e => handleChange('alloc_policy', e.target.value)}
        >
          <option value="qoe_aware">Proposed QoE-Aware Allocator</option>
          <option value="equal_share">Equal-Share Allocator (Baseline)</option>
        </select>
      </div>

      {/* Duration */}
      <div className="form-group">
        <label>Simulation Duration</label>
        <select
          value={config.duration}
          onChange={e => handleChange('duration', parseFloat(e.target.value))}
        >
          <option value="60">60 Seconds (Fast Demo)</option>
          <option value="120">120 Seconds (Standard 30 Chunks)</option>
          <option value="180">180 Seconds (Extended)</option>
        </select>
      </div>

      {/* Action Buttons */}
      <button
        className="btn btn-primary"
        onClick={onRunSimulate}
        disabled={loading}
      >
        <Play size={16} />
        {loading ? 'Simulating...' : 'Run Simulation'}
      </button>

      <button
        className="btn btn-secondary"
        onClick={onRunCompare}
        disabled={loading}
      >
        <GitCompare size={16} />
        Compare Equal vs. QoE-Aware
      </button>

      <div className="reference-box">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: '#f8fafc', fontWeight: 600 }}>
          <Info size={14} color="#38bdf8" />
          Key Concept
        </div>
        QoE-Aware allocator dynamically evaluates client buffer deficit and marginal quality gain:
        <code> B_i = C(t) · (w_i / Σw_j)</code>, giving temporary bandwidth boosts to clients approaching stalls.
      </div>
    </div>
  );
}
