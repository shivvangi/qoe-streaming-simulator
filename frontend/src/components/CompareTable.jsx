import React from 'react';
import { CheckCircle2, TrendingUp, AlertTriangle } from 'lucide-react';

export default function CompareTable({ comparisonData }) {
  if (!comparisonData) return null;

  const { equal_share, qoe_aware, comparison } = comparisonData;
  const eqSummary = equal_share.summary;
  const qoeSummary = qoe_aware.summary;

  const isQoEBetter = comparison.qoe_gain >= 0;
  const isStallBetter = comparison.stall_reduction_pct > 0;

  return (
    <div className="compare-container">
      <div className="card">
        <div className="card-title">
          <span>Side-by-Side Policy Comparison (Identical Trace &amp; Seed)</span>
          <span className="badge badge-success">Controlled Evaluation</span>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Evaluation Metric</th>
                <th>Equal-Share (Baseline)</th>
                <th>QoE-Aware (Proposed)</th>
                <th>Relative Improvement</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Average QoE Score</strong></td>
                <td>{eqSummary.avg_qoe}</td>
                <td><strong>{qoeSummary.avg_qoe}</strong></td>
                <td>
                  <span className={isQoEBetter ? 'win-badge' : 'loss-badge'}>
                    {comparison.qoe_gain > 0 ? `+${comparison.qoe_gain}` : comparison.qoe_gain} pts
                  </span>
                </td>
              </tr>
              <tr>
                <td><strong>Total Rebuffering Stall Time</strong></td>
                <td>{comparison.equal_stall_total} s</td>
                <td><strong>{comparison.qoe_stall_total} s</strong></td>
                <td>
                  <span className={isStallBetter ? 'win-badge' : ''}>
                    {comparison.stall_reduction_pct > 0 ? `-${comparison.stall_reduction_pct}% stalls` : '0% (No stalls)'}
                  </span>
                </td>
              </tr>
              <tr>
                <td><strong>Average Video Bitrate</strong></td>
                <td>{eqSummary.avg_bitrate_kbps} kbps</td>
                <td><strong>{qoeSummary.avg_bitrate_kbps} kbps</strong></td>
                <td>
                  <span className="win-badge">
                    {comparison.bitrate_gain_kbps >= 0 ? `+${comparison.bitrate_gain_kbps}` : comparison.bitrate_gain_kbps} kbps
                  </span>
                </td>
              </tr>
              <tr>
                <td><strong>Jain's Fairness Index</strong></td>
                <td>{comparison.equal_fairness.toFixed(3)}</td>
                <td><strong>{comparison.qoe_fairness.toFixed(3)}</strong></td>
                <td>
                  <span>
                    {(comparison.qoe_fairness - comparison.equal_fairness) >= 0 ? '+' : ''}
                    {(comparison.qoe_fairness - comparison.equal_fairness).toFixed(3)}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="reference-box" style={{ marginTop: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: '#f8fafc', fontWeight: 600 }}>
            <TrendingUp size={16} color="#22c55e" />
            Key Research Takeaway
          </div>
          Under identical bottleneck conditions, the <strong>QoE-Aware Allocator</strong> dynamically shifts spare bandwidth from clients with full buffers to clients with near-empty buffers.
          This dramatically reduces playback stalls (the heaviest QoE penalty, μ = 4.3), resulting in a higher overall user experience without starving healthy clients.
        </div>
      </div>

      {/* Per-Client Comparison Table */}
      <div className="card">
        <div className="card-title">
          <span>Client Breakdown (Equal-Share vs. QoE-Aware)</span>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Client</th>
                <th>Equal QoE</th>
                <th>QoE-Aware QoE</th>
                <th>Equal Stalls (s)</th>
                <th>QoE Stalls (s)</th>
                <th>Equal Avg Bitrate</th>
                <th>QoE Avg Bitrate</th>
              </tr>
            </thead>
            <tbody>
              {equal_share.client_results.map((eqClient, idx) => {
                const qoeClient = qoe_aware.client_results[idx];
                return (
                  <tr key={eqClient.client_id}>
                    <td><strong>Client {eqClient.client_id}</strong></td>
                    <td>{eqClient.qoe_total}</td>
                    <td style={{ color: '#22c55e', fontWeight: 600 }}>{qoeClient.qoe_total}</td>
                    <td>{eqClient.total_stall_time}s</td>
                    <td style={{ color: qoeClient.total_stall_time === 0 ? '#22c55e' : '#ef4444' }}>
                      {qoeClient.total_stall_time}s
                    </td>
                    <td>{eqClient.avg_bitrate_kbps} kbps</td>
                    <td>{qoeClient.avg_bitrate_kbps} kbps</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
