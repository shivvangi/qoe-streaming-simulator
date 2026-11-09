import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ConfigPanel from './components/ConfigPanel';
import MetricsSummary from './components/MetricsSummary';
import CompareTable from './components/CompareTable';
import BandwidthChart from './charts/BandwidthChart';
import BufferChart from './charts/BufferChart';
import BitrateChart from './charts/BitrateChart';
import { Activity, GitCompare, BookOpen } from 'lucide-react';

export default function App() {
  const [config, setConfig] = useState({
    num_clients: 5,
    trace_type: 'fluctuating',
    base_bandwidth_kbps: 8000,
    abr_policy: 'buffer_based',
    alloc_policy: 'qoe_aware',
    duration: 120,
    seed: 42
  });

  const [activeTab, setActiveTab] = useState('telemetry'); // 'telemetry' | 'compare' | 'viva'
  const [loading, setLoading] = useState(false);
  const [singleResult, setSingleResult] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Initial simulation run on component mount
  useEffect(() => {
    runSimulate();
  }, []);

  const runSimulate = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setSingleResult(data);
      setActiveTab('telemetry');
    } catch (err) {
      console.error(err);
      setErrorMsg('Failed to run simulation. Ensure backend server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const runCompare = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setComparisonResult(data);
      setSingleResult(data.qoe_aware);
      setActiveTab('compare');
    } catch (err) {
      console.error(err);
      setErrorMsg('Failed to run comparison. Ensure backend server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportCsv = () => {
    window.open('/api/export-csv', '_blank');
  };

  return (
    <div className="app-container">
      <Header onExportCsv={handleExportCsv} />

      {errorMsg && (
        <div style={{ background: '#7f1d1d', color: '#fecaca', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px' }}>
          {errorMsg}
        </div>
      )}

      <div className="dashboard-grid">
        {/* Left Column: Simulation Controls */}
        <div>
          <ConfigPanel
            config={config}
            setConfig={setConfig}
            onRunSimulate={runSimulate}
            onRunCompare={runCompare}
            loading={loading}
          />
        </div>

        {/* Right Column: Visualizations & Analytics */}
        <div>
          {/* KPI Metrics Banner */}
          {singleResult && (
            <MetricsSummary
              summary={singleResult.summary}
              policyName={singleResult.config.alloc_policy}
            />
          )}

          {/* Navigation Tabs */}
          <div className="tabs-header">
            <button
              className={`tab-btn ${activeTab === 'telemetry' ? 'active' : ''}`}
              onClick={() => setActiveTab('telemetry')}
            >
              <Activity size={15} style={{ display: 'inline', marginRight: '6px' }} />
              Live Simulation Telemetry
            </button>
            <button
              className={`tab-btn ${activeTab === 'compare' ? 'active' : ''}`}
              onClick={() => setActiveTab('compare')}
            >
              <GitCompare size={15} style={{ display: 'inline', marginRight: '6px' }} />
              Equal vs. QoE-Aware Comparison
            </button>
            <button
              className={`tab-btn ${activeTab === 'viva' ? 'active' : ''}`}
              onClick={() => setActiveTab('viva')}
            >
              <BookOpen size={15} style={{ display: 'inline', marginRight: '6px' }} />
              Formula References
            </button>
          </div>

          {/* Tab 1: Time-series Telemetry */}
          {activeTab === 'telemetry' && singleResult && (
            <div className="charts-stack">
              <BandwidthChart timeline={singleResult.timeline} />
              <BufferChart timeline={singleResult.timeline} />
              <BitrateChart timeline={singleResult.timeline} />
            </div>
          )}

          {/* Tab 2: Side-by-Side Comparison */}
          {activeTab === 'compare' && (
            <div>
              {comparisonResult ? (
                <CompareTable comparisonData={comparisonResult} />
              ) : (
                <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                  <p style={{ color: '#94a3b8', marginBottom: '16px' }}>
                    Click "Compare Equal vs. QoE-Aware" in the configuration panel to run controlled experiments under identical network conditions.
                  </p>
                  <button className="btn btn-primary" style={{ width: 'auto' }} onClick={runCompare} disabled={loading}>
                    Run Comparison Now
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Tab 3: Formula References & Mathematical Explanations */}
          {activeTab === 'viva' && (
            <div className="card">
              <div className="card-title">
                <span>Mathematical Foundation &amp; Formula References</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', color: '#cbd5e1', fontSize: '0.9rem' }}>
                <div className="reference-box">
                  <strong>1. Video Ladder &amp; Chunk Formulation:</strong>
                  <p style={{ marginTop: '4px' }}>
                    Bitrates R ∈ [300, 750, 1200, 1850, 2850, 4300] kbps. Chunks are 4.0 seconds long.
                    Chunk size S(R) = R × 4.0s bits.
                  </p>
                </div>

                <div className="reference-box">
                  <strong>2. Proposed QoE-Aware Dynamic Bandwidth Allocation:</strong>
                  <p style={{ marginTop: '4px' }}>
                    B_i(t) = C(t) · [w_i(t) / Σ w_j(t)], where client weight:
                    <br />
                    w_i = clamp(α · Urgency_i + (1 - α) · Gain_i, 0.10, 1.0)
                    <br />
                    • Buffer Urgency: Prioritizes clients with buffer &lt; 16.0s (maximum weight if buffer ≤ 4.0s).
                    <br />
                    • Marginal Gain: Estimates perceptual utility step-up [q(R_m+1) - q(R_m)] / [q(R_max) - q(R_min)].
                    <br />
                    • Capacity Invariant: Σ B_i(t) ≤ C(t) strictly preserved at every time tick Δt = 0.5s.
                  </p>
                </div>

                <div className="reference-box">
                  <strong>3. Quality of Experience (QoE) Objective Function:</strong>
                  <p style={{ marginTop: '4px' }}>
                    QoE_i = Σ ln(R_k / 300) - 1.0 · Σ |Δq| - 4.3 · T_rebuf - 1.0 · T_startup
                    <br />
                    • Quality utility q(R) = ln(R / 300) models human logarithmic perception (Weber-Fechner law).
                    <br />
                    • Penalty μ = 4.3 reflects research showing 1s of rebuffering stall is 4.3x more detrimental than 1 tier of lower resolution.
                  </p>
                </div>

                <div className="reference-box">
                  <strong>4. Jain's Fairness Index:</strong>
                  <p style={{ marginTop: '4px' }}>
                    J(R) = (Σ R_i)² / [N · Σ (R_i)²] ∈ [1/N, 1.0].
                    A value of 1.0 indicates perfect fairness where all clients receive balanced bitrate allocations.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
