# QoE-Aware Adaptive Video Streaming Simulator with Dynamic Bandwidth Allocation

A discrete-time multi-client video streaming simulation system and research dashboard developed for a **BTech Subject Project**.

---

## 1. Project Overview & Objective

In multi-client HTTP Adaptive Video Streaming (DASH/HLS) over a shared network bottleneck link, clients independently make bitrate decisions using Adaptive Bitrate (ABR) logic. When network capacity fluctuates or becomes congested, standard equal sharing can cause client playback buffers to starve, triggering **annoying video rebuffering stalls**.

This project implements:
1. A **mathematically correct, discrete-time multi-client video streaming simulator** ($\Delta t = 0.5\text{ s}$).
2. A **QoE-Aware Dynamic Bandwidth Allocator** that balances client buffer urgency with marginal quality gains:
   $$B_i(t) = C(t) \cdot \frac{w_i(t)}{\sum_{j \in \mathcal{A}(t)} w_j(t)}$$
3. A **head-to-head comparison engine** pitting Equal-Share allocation against the proposed QoE-Aware allocation under identical network traces and random seeds.
4. A **modern React + Plotly.js research dashboard** connected to a **FastAPI** simulation backend.

---

## 2. Mathematical Foundation (Viva-Ready)

### A. Video Ladder & Chunk Formulation
- Video chunk duration: $\Delta_{\text{chunk}} = 4.0\text{ seconds}$.
- Bitrate ladder: $\mathcal{R} \in [300, 750, 1200, 1850, 2850, 4300]\text{ kbps}$.
- Chunk size: $S(R) = R \times 4.0\text{ s}$ bits.

### B. Adaptive Bitrate (ABR) Algorithms
1. **Throughput-Based ABR**:
   Uses harmonic mean of past 5 chunk download speeds with a safety margin $\gamma = 0.85$: selects highest ladder tier $\le 0.85 \times \hat{T}$.
2. **Buffer-Based ABR (BBA)**:
   Maps buffer occupancy between Reservoir ($4.0\text{ s}$) and Cushion ($16.0\text{ s}$) to the bitrate ladder.
3. **Hybrid ABR**:
   Calculates throughput baseline, then steps down 1 tier if buffer $< 6.0\text{ s}$ (stall protection) or steps up 1 tier if buffer $> 18.0\text{ s}$.

### C. Proposed QoE-Aware Bandwidth Allocation
Each active client receives an allocation weight:
$$w_i(t) = \text{clamp}\Big( \alpha \cdot \text{Urgency}_i(t) + (1 - \alpha) \cdot \text{Gain}_i(t), \; w_{\min}, \; w_{\max} \Big)$$
- **Buffer Urgency ($\text{Urgency}_i$)**:
  - If buffer $B_i \le 4.0\text{ s}$ (critical): $\text{Urgency} = 1.0$.
  - If buffer $B_i \ge 16.0\text{ s}$ (safe target): $\text{Urgency} = 0.0$.
  - Otherwise: linear interpolation $\frac{16.0 - B_i}{12.0}$.
- **Marginal QoE Gain ($\text{Gain}_i$)**:
  Estimates perceptual step-up utility $\frac{q(R_{m+1}) - q(R_m)}{q(R_{\max}) - q(R_{\min})}$.
- **Starvation Bounds**: $w_{\min} = 0.10, w_{\max} = 1.0, \alpha = 0.60$.
- **Strict Capacity Invariant**: $\sum_{i \in \mathcal{A}(t)} B_i(t) \le C(t)$ strictly holds at every time tick.

### D. Quality of Experience (QoE) Model
Perceptual quality uses logarithmic utility (Weber-Fechner law):
$$q(R_k) = \ln\left(\frac{R_k}{300\text{ kbps}}\right)$$
Total QoE across $K_i$ downloaded chunks:
$$QoE_i = \sum_{k=1}^{K_i} q(R_k) - \lambda \sum_{k=1}^{K_i - 1} |q(R_{k+1}) - q(R_k)| - \mu \cdot T_{\text{rebuf}, i} - \tau \cdot T_{\text{startup}, i}$$
- $\lambda = 1.0$ (Quality switching penalty)
- $\mu = 4.3\text{ s}^{-1}$ (Rebuffering stall penalty: 1 second freeze is 4.3x worse than 1 tier lower quality)
- $\tau = 1.0\text{ s}^{-1}$ (Initial startup delay penalty)

### E. Jain's Fairness Index
Evaluates bitrate distribution fairness across all $N$ clients:
$$J(\mathbf{\bar{R}}) = \frac{\left(\sum_{i=1}^N \bar{R}_i\right)^2}{N \sum_{i=1}^N \bar{R}_i^2} \in \left[\frac{1}{N}, 1.0\right]$$

---

## 3. Directory Structure

```
qoe_streaming_simulator/
├── backend/
│   ├── main.py              # FastAPI REST API endpoints (/simulate, /compare, /export-csv)
│   ├── simulation.py        # Discrete time-stepped simulation coordinator
│   ├── network.py           # Shared bottleneck traces (Fixed, Fluctuating, Step-Drop)
│   ├── client.py            # Client buffer dynamics, playback states, stalls
│   ├── abr.py               # Throughput, Buffer-Based (BBA), and Hybrid ABR
│   ├── allocator.py         # Equal-Share and Proposed QoE-Aware allocators
│   ├── qoe.py               # QoE metrics & Jain's Fairness Index
│   ├── pytest.ini           # Pytest configuration
│   ├── requirements.txt     # Python dependencies
│   └── tests/
│       ├── test_allocator.py
│       ├── test_abr.py
│       ├── test_qoe.py
│       └── test_simulation.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main application & state manager
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── ConfigPanel.jsx
│   │   │   ├── MetricsSummary.jsx
│   │   │   └── CompareTable.jsx
│   │   ├── charts/
│   │   │   ├── BandwidthChart.jsx
│   │   │   ├── BufferChart.jsx
│   │   │   └── BitrateChart.jsx
│   │   └── styles/
│   │       └── index.css
│   ├── package.json
│   └── vite.config.js
│
└── results/                 # Exported simulation CSV outputs
```

---

## 4. Running the Project

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Step 1: Run Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### Step 2: Run Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at: `http://127.0.0.1:5173/`

### Step 3: Run Automated Test Suite
```bash
cd backend
source venv/bin/activate
pytest -v
```

---

## 5. Viva Preparation: Key Questions & Answers

1. **Why does Equal Sharing cause rebuffering stalls under congestion?**
   *Answer*: Equal sharing ignores application-layer buffer levels. A client with 20 seconds of buffer receives the same bandwidth as a client with only 0.5 seconds of buffer about to freeze. The QoE-Aware allocator temporarily prioritizes clients with buffer deficits to avert stalls.

2. **Why is the quality utility logarithmic rather than linear?**
   *Answer*: Human perceptual acuity follows the Weber-Fechner law of diminishing marginal returns: upgrading from 300 kbps to 750 kbps produces a much higher noticeable improvement in video clarity than upgrading from 2850 kbps to 4300 kbps.

3. **How is the capacity constraint preserved?**
   *Answer*: Allocated bandwidths are calculated via normalized weights $B_i = C(t) \cdot \frac{w_i}{\sum w_j}$, mathematically guaranteeing that $\sum B_i(t) \le C(t)$ at every discrete simulation tick.

4. **Why is startup delay separated from rebuffering?**
   *Answer*: Startup delay is the initial waiting time before the first frame renders and is expected by users. Rebuffering stalls occur mid-playback and cause much greater user dissatisfaction (penalized at $\mu = 4.3\text{ s}^{-1}$).
