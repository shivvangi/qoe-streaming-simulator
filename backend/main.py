"""FastAPI Application: REST endpoints for Video Streaming Simulation & Comparison."""
import os
import io
import pandas as pd
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from simulation import SimulationEngine, run_comparison

app = FastAPI(
    title="QoE-Aware Adaptive Video Streaming Simulator API",
    description="REST backend for simulating multi-client ABR streaming over a bottleneck link with dynamic bandwidth allocation.",
    version="1.0.0"
)

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure results directory exists
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
os.makedirs(RESULTS_DIR, exist_ok=True)

# Store last simulation result in memory for quick CSV export
LAST_RUN_RESULT = None


class SimulationRequest(BaseModel):
    num_clients: int = Field(default=5, ge=1, le=20, description="Number of simultaneous clients (3-10 recommended)")
    trace_type: str = Field(default="fluctuating", description="'fixed', 'fluctuating', or 'step_drop'")
    base_bandwidth_kbps: float = Field(default=8000.0, ge=500.0, le=50000.0, description="Bottleneck link capacity in kbps")
    abr_policy: str = Field(default="buffer_based", description="'throughput_based', 'buffer_based', or 'hybrid'")
    alloc_policy: str = Field(default="qoe_aware", description="'equal_share' or 'qoe_aware'")
    duration: float = Field(default=120.0, ge=10.0, le=300.0, description="Simulation duration in seconds")
    seed: int = Field(default=42, description="Random seed for reproducibility")


class CompareRequest(BaseModel):
    num_clients: int = Field(default=5, ge=1, le=20)
    trace_type: str = Field(default="fluctuating")
    base_bandwidth_kbps: float = Field(default=8000.0, ge=500.0, le=50000.0)
    abr_policy: str = Field(default="buffer_based")
    duration: float = Field(default=120.0, ge=10.0, le=300.0)
    seed: int = Field(default=42)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "QoE Video Streaming Simulator",
        "supported_clients": "1-20",
        "bitrate_ladder_kbps": [300, 750, 1200, 1850, 2850, 4300],
        "allocators": ["equal_share", "qoe_aware"],
        "abr_algorithms": ["throughput_based", "buffer_based", "hybrid"]
    }


@app.post("/api/simulate")
def simulate(req: SimulationRequest):
    global LAST_RUN_RESULT
    try:
        engine = SimulationEngine(
            num_clients=req.num_clients,
            trace_type=req.trace_type,
            base_bandwidth_kbps=req.base_bandwidth_kbps,
            abr_policy=req.abr_policy,
            alloc_policy=req.alloc_policy,
            duration=req.duration,
            dt=0.5,
            seed=req.seed
        )
        result = engine.run()
        LAST_RUN_RESULT = result

        # Also persist to results/last_run.csv
        df_clients = pd.DataFrame(result["client_results"])
        csv_path = os.path.join(RESULTS_DIR, "last_simulation_clients.csv")
        df_clients.to_csv(csv_path, index=False)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compare")
def compare(req: CompareRequest):
    global LAST_RUN_RESULT
    try:
        result = run_comparison(
            num_clients=req.num_clients,
            trace_type=req.trace_type,
            base_bandwidth_kbps=req.base_bandwidth_kbps,
            abr_policy=req.abr_policy,
            duration=req.duration,
            seed=req.seed
        )
        LAST_RUN_RESULT = result["qoe_aware"]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export-csv")
def export_csv():
    global LAST_RUN_RESULT
    if not LAST_RUN_RESULT or "client_results" not in LAST_RUN_RESULT:
        # Run a quick default simulation if none exists
        engine = SimulationEngine(num_clients=5, duration=60.0)
        LAST_RUN_RESULT = engine.run()

    df = pd.DataFrame(LAST_RUN_RESULT["client_results"])
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=simulation_results.csv"
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
