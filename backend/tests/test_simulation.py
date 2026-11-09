"""Integration tests for Simulation Engine."""
from simulation import SimulationEngine, run_comparison

def test_simulation_run_basic():
    engine = SimulationEngine(
        num_clients=3,
        trace_type="fixed",
        base_bandwidth_kbps=6000.0,
        abr_policy="buffer_based",
        alloc_policy="qoe_aware",
        duration=30.0,
        dt=0.5,
        seed=42
    )
    res = engine.run()

    assert "summary" in res
    assert "client_results" in res
    assert len(res["client_results"]) == 3
    assert len(res["timeline"]) > 0

    # Ensure all clients downloaded chunks and maintained non-negative buffers
    for c in res["client_results"]:
        assert c["chunks_downloaded"] > 0
        assert c["buffer"] >= 0.0
        assert c["startup_delay"] >= 0.0

def test_simulation_reproducibility():
    """Verify that identical random seeds yield identical simulation results."""
    sim1 = SimulationEngine(num_clients=4, duration=20.0, seed=123)
    res1 = sim1.run()

    sim2 = SimulationEngine(num_clients=4, duration=20.0, seed=123)
    res2 = sim2.run()

    assert res1["summary"]["avg_qoe"] == res2["summary"]["avg_qoe"]
    assert res1["summary"]["avg_bitrate_kbps"] == res2["summary"]["avg_bitrate_kbps"]
    assert res1["summary"]["total_stall_seconds"] == res2["summary"]["total_stall_seconds"]

def test_run_comparison_output():
    comp = run_comparison(
        num_clients=4,
        trace_type="fluctuating",
        base_bandwidth_kbps=6000.0,
        abr_policy="buffer_based",
        duration=30.0,
        seed=42
    )

    assert "equal_share" in comp
    assert "qoe_aware" in comp
    assert "comparison" in comp
    assert "qoe_gain" in comp["comparison"]
    assert "stall_reduction_pct" in comp["comparison"]
