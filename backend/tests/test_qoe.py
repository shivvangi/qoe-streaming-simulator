"""Tests for QoE Evaluator and Jain's Fairness Index."""
import pytest
from qoe import QoEEvaluator
from abr import BITRATE_LADDER

def test_logarithmic_utility():
    evaluator = QoEEvaluator()
    # At 300 kbps, ln(300/300) = ln(1) = 0.0
    assert evaluator.utility(300.0) == pytest.approx(0.0)
    # At 1200 kbps, ln(1200/300) = ln(4) approx 1.3863
    assert evaluator.utility(1200.0) == pytest.approx(1.38629, rel=1e-3)

def test_qoe_components():
    evaluator = QoEEvaluator(lambda_switch=1.0, mu_stall=4.3, tau_startup=1.0)
    rates = [300, 750, 750]  # 1 switch: ln(2.5) - ln(1) = 0.9163
    qoe = evaluator.calculate_client_qoe(
        bitrate_history=rates,
        total_stall_time=2.0,  # stall penalty: 4.3 * 2 = 8.6
        startup_delay=1.5      # startup penalty: 1.0 * 1.5 = 1.5
    )
    assert qoe["stall_penalty"] == pytest.approx(8.6, rel=1e-2)
    assert qoe["startup_penalty"] == pytest.approx(1.5, rel=1e-2)
    assert qoe["num_switches"] == 1
    assert qoe["avg_bitrate_kbps"] == pytest.approx(600.0, rel=1e-2)

def test_jains_fairness_identical():
    # If all clients receive identical bitrates, fairness must be exactly 1.0
    vals = [1200.0, 1200.0, 1200.0, 1200.0]
    assert QoEEvaluator.jains_fairness_index(vals) == pytest.approx(1.0)

def test_jains_fairness_unfair():
    # 1 client gets 10000, 3 clients get 0 -> fairness is 1/N = 0.25
    vals = [10000.0, 0.0, 0.0, 0.0]
    assert QoEEvaluator.jains_fairness_index(vals) == pytest.approx(0.25)
