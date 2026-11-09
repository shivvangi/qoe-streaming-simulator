"""Simulation Engine: Discrete-Time Multi-Client Video Streaming Simulator."""
from typing import Dict, List, Any
import numpy as np
import pandas as pd

from network import NetworkModel
from client import StreamingClient
from abr import get_abr_algorithm
from allocator import get_allocator
from qoe import QoEEvaluator

class SimulationEngine:
    """Coordinates the discrete-time multi-client video streaming simulation."""

    def __init__(
        self,
        num_clients: int = 5,
        trace_type: str = "fluctuating",
        base_bandwidth_kbps: float = 8000.0,
        abr_policy: str = "buffer_based",
        alloc_policy: str = "qoe_aware",
        duration: float = 120.0,
        dt: float = 0.5,
        seed: int = 42
    ):
        self.num_clients = max(1, min(20, num_clients))
        self.trace_type = trace_type
        self.base_bandwidth = float(base_bandwidth_kbps)
        self.abr_policy_name = abr_policy
        self.alloc_policy_name = alloc_policy
        self.duration = float(duration)
        self.dt = float(dt)
        self.seed = seed

        # Initialize core components
        self.network = NetworkModel(
            base_capacity_kbps=self.base_bandwidth,
            trace_type=self.trace_type,
            seed=self.seed
        )
        self.allocator = get_allocator(self.alloc_policy_name)
        self.qoe_eval = QoEEvaluator()

        # Build clients with independent ABR instances and realistic arrival stagger
        self.clients = [
            StreamingClient(
                client_id=i + 1,
                abr_algorithm=get_abr_algorithm(self.abr_policy_name),
                arrival_time=round(i * 1.5, 1)
            )
            for i in range(self.num_clients)
        ]

    def run(self) -> Dict[str, Any]:
        """Runs the complete discrete-time simulation."""
        np.random.seed(self.seed)

        timeline_data: List[Dict[str, Any]] = []
        steps = int(self.duration / self.dt)

        for step in range(steps):
            t = round(step * self.dt, 2)
            capacity = self.network.get_capacity(t)

            # 1. Identify active downloaders at current time t
            active_ids = [c.client_id for c in self.clients if c.is_active_downloader(t)]
            client_states = {
                c.client_id: {
                    "buffer": c.buffer,
                    "current_bitrate": c.current_bitrate,
                    "state": c.state
                }
                for c in self.clients
            }

            # 2. Allocate bandwidth
            allocations = self.allocator.allocate(capacity, active_ids, client_states)

            # 3. Transmit chunk bits & update download progress
            for client in self.clients:
                bw = allocations.get(client.client_id, 0.0)
                client.receive_bandwidth(bw, self.dt)

            # 4. Advance playback & buffer consumption
            for client in self.clients:
                client.update_playback(self.dt)

            # 5. Record telemetry snapshot (sampled every 1 second or at dt)
            if step % 2 == 0:  # Sample every 1.0 second (since dt=0.5s)
                snap: Dict[str, Any] = {
                    "time": t,
                    "link_capacity": round(capacity, 1),
                    "total_allocated": round(sum(allocations.values()), 1),
                    "client_buffers": {c.client_id: round(c.buffer, 2) for c in self.clients},
                    "client_bitrates": {c.client_id: c.current_bitrate for c in self.clients},
                    "client_bandwidths": {c.client_id: round(allocations.get(c.client_id, 0.0), 1) for c in self.clients},
                    "client_states": {c.client_id: c.state for c in self.clients}
                }
                timeline_data.append(snap)

        # 6. Compute end-of-run QoE and aggregate metrics
        client_results: List[Dict[str, Any]] = []
        qoe_scores: List[float] = []
        bitrates: List[float] = []
        stalls: List[float] = []

        for client in self.clients:
            qoe_dict = self.qoe_eval.calculate_client_qoe(
                bitrate_history=client.bitrate_history,
                total_stall_time=client.total_stall_time,
                startup_delay=client.startup_delay
            )
            summary = client.get_summary()
            summary.update(qoe_dict)
            client_results.append(summary)

            qoe_scores.append(qoe_dict["qoe_total"])
            bitrates.append(summary["avg_bitrate_kbps"])
            stalls.append(summary["total_stall_time"])

        jain_fairness_bitrate = self.qoe_eval.jains_fairness_index(bitrates)
        # Shifted QoE for positive Jain calculation
        min_qoe = min(qoe_scores) if qoe_scores else 0.0
        shift = abs(min_qoe) + 1.0 if min_qoe <= 0 else 0.0
        shifted_qoe = [q + shift for q in qoe_scores]
        jain_fairness_qoe = self.qoe_eval.jains_fairness_index(shifted_qoe)

        avg_qoe = round(float(np.mean(qoe_scores)), 2) if qoe_scores else 0.0
        avg_bitrate = round(float(np.mean(bitrates)), 1) if bitrates else 0.0
        total_stall_sec = round(float(np.sum(stalls)), 2) if stalls else 0.0
        avg_stall_per_client = round(float(np.mean(stalls)), 2) if stalls else 0.0

        return {
            "config": {
                "num_clients": self.num_clients,
                "trace_type": self.trace_type,
                "base_bandwidth_kbps": self.base_bandwidth,
                "abr_policy": self.abr_policy_name,
                "alloc_policy": self.alloc_policy_name,
                "duration": self.duration,
                "seed": self.seed
            },
            "summary": {
                "avg_qoe": avg_qoe,
                "avg_bitrate_kbps": avg_bitrate,
                "total_stall_seconds": total_stall_sec,
                "avg_stall_per_client": avg_stall_per_client,
                "jain_fairness_bitrate": jain_fairness_bitrate,
                "jain_fairness_qoe": jain_fairness_qoe
            },
            "client_results": client_results,
            "timeline": timeline_data
        }


def run_comparison(
    num_clients: int = 5,
    trace_type: str = "fluctuating",
    base_bandwidth_kbps: float = 8000.0,
    abr_policy: str = "buffer_based",
    duration: float = 120.0,
    seed: int = 42
) -> Dict[str, Any]:
    """Runs identical configuration under Equal-Share and QoE-Aware policies."""
    # 1. Run Equal-Share
    sim_equal = SimulationEngine(
        num_clients=num_clients,
        trace_type=trace_type,
        base_bandwidth_kbps=base_bandwidth_kbps,
        abr_policy=abr_policy,
        alloc_policy="equal_share",
        duration=duration,
        seed=seed
    )
    res_equal = sim_equal.run()

    # 2. Run Proposed QoE-Aware
    sim_qoe = SimulationEngine(
        num_clients=num_clients,
        trace_type=trace_type,
        base_bandwidth_kbps=base_bandwidth_kbps,
        abr_policy=abr_policy,
        alloc_policy="qoe_aware",
        duration=duration,
        seed=seed
    )
    res_qoe = sim_qoe.run()

    eq_summary = res_equal["summary"]
    qoe_summary = res_qoe["summary"]

    # Calculate improvements
    qoe_gain = round(qoe_summary["avg_qoe"] - eq_summary["avg_qoe"], 2)

    stall_reduction = 0.0
    if eq_summary["total_stall_seconds"] > 0:
        stall_reduction = round(
            ((eq_summary["total_stall_seconds"] - qoe_summary["total_stall_seconds"]) / eq_summary["total_stall_seconds"]) * 100.0,
            1
        )

    bitrate_gain = round(qoe_summary["avg_bitrate_kbps"] - eq_summary["avg_bitrate_kbps"], 1)

    return {
        "equal_share": res_equal,
        "qoe_aware": res_qoe,
        "comparison": {
            "qoe_gain": qoe_gain,
            "stall_reduction_pct": stall_reduction,
            "bitrate_gain_kbps": bitrate_gain,
            "equal_stall_total": eq_summary["total_stall_seconds"],
            "qoe_stall_total": qoe_summary["total_stall_seconds"],
            "equal_fairness": eq_summary["jain_fairness_bitrate"],
            "qoe_fairness": qoe_summary["jain_fairness_bitrate"]
        }
    }
