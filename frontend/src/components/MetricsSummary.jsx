import React from 'react';
import { Award, Zap, PauseCircle, Users, BarChart3 } from 'lucide-react';

export default function MetricsSummary({ summary, policyName }) {
  if (!summary) return null;

  return (
    <div className="metrics-row">
      {/* Average QoE */}
      <div className="metric-card green">
        <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Award size={14} color="#22c55e" />
          Average QoE Score
        </div>
        <div className="metric-value" style={{ color: '#22c55e' }}>
          {summary.avg_qoe > 0 ? `+${summary.avg_qoe}` : summary.avg_qoe}
        </div>
        <div className="metric-sub">
          {policyName === 'qoe_aware' ? 'Proposed Policy' : 'Equal-Share Baseline'}
        </div>
      </div>

      {/* Average Bitrate */}
      <div className="metric-card">
        <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={14} color="#38bdf8" />
          Average Bitrate
        </div>
        <div className="metric-value">
          {summary.avg_bitrate_kbps} <span style={{ fontSize: '0.85rem' }}>kbps</span>
        </div>
        <div className="metric-sub">
          {(summary.avg_bitrate_kbps / 1000).toFixed(2)} Mbps delivered
        </div>
      </div>

      {/* Total Rebuffering Stall Time */}
      <div className="metric-card red">
        <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <PauseCircle size={14} color="#ef4444" />
          Total Stall Time
        </div>
        <div className="metric-value" style={{ color: summary.total_stall_seconds > 0 ? '#ef4444' : '#22c55e' }}>
          {summary.total_stall_seconds} <span style={{ fontSize: '0.85rem' }}>s</span>
        </div>
        <div className="metric-sub">
          Avg {summary.avg_stall_per_client}s / client
        </div>
      </div>

      {/* Jain's Fairness Index */}
      <div className="metric-card purple">
        <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <BarChart3 size={14} color="#a855f7" />
          Jain's Fairness Index
        </div>
        <div className="metric-value" style={{ color: '#a855f7' }}>
          {summary.jain_fairness_bitrate.toFixed(3)}
        </div>
        <div className="metric-sub">
          Range [1/N, 1.0] (1.0 = Ideal)
        </div>
      </div>
    </div>
  );
}
