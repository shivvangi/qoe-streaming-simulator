import React from 'react';
import Plot from 'react-plotly.js';

export default function BufferChart({ timeline }) {
  if (!timeline || timeline.length === 0) return null;

  const times = timeline.map(d => d.time);
  const clientIds = Object.keys(timeline[0].client_buffers || {});
  const colors = ['#38bdf8', '#22c55e', '#a855f7', '#ec4899', '#f97316', '#eab308', '#06b6d4', '#64748b'];

  const traces = [];

  // Per client buffer levels
  clientIds.forEach((cid, idx) => {
    traces.push({
      x: times,
      y: timeline.map(d => d.client_buffers[cid] || 0),
      type: 'scatter',
      mode: 'lines',
      name: `Client ${cid}`,
      line: { color: colors[idx % colors.length], width: 1.8 }
    });
  });

  // Reference line: Critical Buffer Hazard (4.0s)
  traces.push({
    x: [times[0], times[times.length - 1]],
    y: [4.0, 4.0],
    type: 'scatter',
    mode: 'lines',
    name: 'Critical Buffer (4.0s)',
    line: { color: '#ef4444', width: 2, dash: 'dot' }
  });

  // Reference line: Target Buffer (16.0s)
  traces.push({
    x: [times[0], times[times.length - 1]],
    y: [16.0, 16.0],
    type: 'scatter',
    mode: 'lines',
    name: 'Target Buffer (16.0s)',
    line: { color: '#22c55e', width: 1.5, dash: 'dot' }
  });

  return (
    <div className="chart-card">
      <div className="chart-header">
        <span className="chart-title">Client Playback Buffer Occupancy (seconds)</span>
      </div>
      <Plot
        data={traces}
        layout={{
          autosize: true,
          height: 300,
          margin: { l: 50, r: 20, t: 10, b: 40 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: {
            title: { text: 'Simulation Time (seconds)', font: { color: '#94a3b8', size: 11 } },
            gridcolor: '#334155',
            tickfont: { color: '#94a3b8' }
          },
          yaxis: {
            title: { text: 'Buffer Level (seconds)', font: { color: '#94a3b8', size: 11 } },
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
