"""Tests for ABR Algorithms: Throughput, Buffer-Based, and Hybrid."""
from abr import ThroughputABR, BufferBasedABR, HybridABR, BITRATE_LADDER

def test_throughput_abr_initial():
    abr = ThroughputABR()
    # Empty history defaults to minimum ladder rate
    rate = abr.select_bitrate(current_buffer=10.0, throughput_history=[])
    assert rate == BITRATE_LADDER[0]

def test_throughput_abr_selection():
    abr = ThroughputABR(safety_margin=0.85)
    # Average throughput of 2000 kbps * 0.85 = 1700 kbps -> should pick 1200 kbps (1850 is > 1700)
    history = [2000.0, 2000.0, 2000.0]
    rate = abr.select_bitrate(current_buffer=10.0, throughput_history=history)
    assert rate == 1200

def test_buffer_based_abr_thresholds():
    bba = BufferBasedABR(reservoir=4.0, cushion=16.0)
    # Below reservoir -> lowest rate
    assert bba.select_bitrate(current_buffer=2.0, throughput_history=[]) == BITRATE_LADDER[0]
    # Above cushion -> highest rate
    assert bba.select_bitrate(current_buffer=20.0, throughput_history=[]) == BITRATE_LADDER[-1]
    # In between -> intermediate rate
    intermediate = bba.select_bitrate(current_buffer=10.0, throughput_history=[])
    assert BITRATE_LADDER[0] <= intermediate <= BITRATE_LADDER[-1]

def test_hybrid_abr_buffer_protection():
    hybrid = HybridABR(low_buf_thresh=6.0, high_buf_thresh=18.0)
    # High throughput (5000 kbps), but critically low buffer (3.0s) -> should step down
    rate_normal = hybrid.throughput_abr.select_bitrate(10.0, [5000.0, 5000.0])
    rate_low_buf = hybrid.select_bitrate(current_buffer=3.0, throughput_history=[5000.0, 5000.0])
    assert BITRATE_LADDER.index(rate_low_buf) <= BITRATE_LADDER.index(rate_normal)
