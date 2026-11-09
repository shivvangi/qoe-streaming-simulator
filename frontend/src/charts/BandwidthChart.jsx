import React from 'react';
import Plot from 'react-plotly.js';

export default function BandwidthChart({ timeline }) {
  if (!timeline || timeline.length === 0) return null;

  const times = timeline.map(d => d.time);
  const capacities = timeline.map(d => d.link_capacity);
  const totalAlloc = timeline.map(d => d.total_allocated);

  // Extract client IDs
  const clientIds = Object.keys(timeline[0].client_bandwidths || {});

  const traces = [
    {
      x: times,
      y: capacities,
      type: 'scatter',
      mode: 'lines',
      name: 'Link Capacity C(t)',
      line: { color: '#f59e0b', width: 2.5, dash: 'dash' }
    },
    {
      x: times,
      y: totalAlloc,
      type: 'scatter',
      mode: 'lines',
      name: 'Total Allocated',
      line: { color: '#38bdf8', width: 2 }
    }
  ];

  const colors = ['#22c55e', '#a855f7', '#ec4899', '#06b6d4', '#eab308', '#f97316', '#64748b', '#84cc16'];

  clientIds.forEach((cid, idx) => {
    traces.push({
      x: times,
      y: timeline.map(d => d.client_bandwidths[cid] || 0),
      type: 'scatter',
      mode: 'lines',
      name: `Client ${cid}`,
      line: { color: colors[idx % colors.length], width: 1.5 }
    });
  });

  return (
    <div className="chart-card">
      <div className="chart-header">
        <span className="chart-title">Dynamic Bandwidth Allocation over Shared Bottleneck</span>
      </div>
      <Plot
        data={traces}
        layout={{
          autosize: true,
          height: 320,
          margin: { l: 50, r: 20, t: 10, b: 40 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: {
            title: { text: 'Simulation Time (seconds)', font: { color: '#94a3b8', size: 11 } },
            gridcolor: '#334155',
            tickfont: { color: '#94a3b8' }
          },
          yaxis: {
            title: { text: 'Bandwidth (kbps)', font: { color: '#94a3b8', size: 11 } },
            gridcolor: '#334155',
            tickfont: { color: '#94a3b8' }
          },
          legend: {
            font: { color: '#f8fafc', size: 10 },
            orientation: 'h',
            y: 1.15
          }
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
}
