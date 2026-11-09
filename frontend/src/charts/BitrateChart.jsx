import React from 'react';
import Plot from 'react-plotly.js';

export default function BitrateChart({ timeline }) {
  if (!timeline || timeline.length === 0) return null;

  const times = timeline.map(d => d.time);
  const clientIds = Object.keys(timeline[0].client_bitrates || {});
  const colors = ['#38bdf8', '#22c55e', '#a855f7', '#ec4899', '#f97316', '#eab308', '#06b6d4', '#64748b'];

  const traces = [];

  clientIds.forEach((cid, idx) => {
    traces.push({
      x: times,
      y: timeline.map(d => d.client_bitrates[cid] || 300),
      type: 'scatter',
      mode: 'lines',
      line: { shape: 'hv', color: colors[idx % colors.length], width: 1.8 },
      name: `Client ${cid}`
    });
  });

  return (
    <div className="chart-card">
      <div className="chart-header">
        <span className="chart-title">Client Video Bitrate Selection Timeline (kbps)</span>
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
            title: { text: 'Bitrate (kbps)', font: { color: '#94a3b8', size: 11 } },
            tickvals: [300, 750, 1200, 1850, 2850, 4300],
            ticktext: ['300k', '750k', '1.2M', '1.85M', '2.85M', '4.3M'],
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
