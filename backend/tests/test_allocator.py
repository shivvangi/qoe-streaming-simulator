"""Tests for Bandwidth Allocators: Equal-Share and QoE-Aware."""
import pytest
from allocator import EqualShareAllocator, QoEAwareAllocator
from abr import BITRATE_LADDER

def test_equal_share_allocation():
    alloc = EqualShareAllocator()
    capacity = 10000.0
    active_clients = [1, 2, 3, 4]
    states = {cid: {"buffer": 10.0, "current_bitrate": 1200} for cid in active_clients}

    res = alloc.allocate(capacity, active_clients, states)
    assert len(res) == 4
    for cid in active_clients:
        assert res[cid] == pytest.approx(2500.0)
    assert sum(res.values()) == pytest.approx(capacity)

def test_allocator_empty_clients():
    alloc = QoEAwareAllocator()
    res = alloc.allocate(10000.0, [], {})
    assert res == {}

def test_allocator_zero_capacity():
    alloc = QoEAwareAllocator()
    res = alloc.allocate(0.0, [1, 2], {1: {"buffer": 2.0}, 2: {"buffer": 15.0}})
    assert res[1] == 0.0 and res[2] == 0.0

def test_qoe_aware_prioritizes_low_buffer():
    """Client with low buffer (in danger of stall) should get significantly more bandwidth than a client with high buffer."""
    alloc = QoEAwareAllocator(alpha=0.8, w_min=0.1, w_max=1.0)
    capacity = 6000.0
    active = [1, 2]
    # Client 1 is near stall (buffer=1.0s), Client 2 has healthy buffer (buffer=20.0s)
    states = {
        1: {"buffer": 1.0, "current_bitrate": 750},
        2: {"buffer": 20.0, "current_bitrate": 750}
    }

    res = alloc.allocate(capacity, active, states)
    assert sum(res.values()) <= capacity + 1e-5
    # Client 1 must receive strictly higher bandwidth than Client 2
    assert res[1] > res[2]
    # Client 2 should not be completely starved (due to w_min)
    assert res[2] > 0.0

def test_capacity_conservation_invariant():
    """Verify sum of allocations never exceeds bottleneck capacity for random conditions."""
    alloc = QoEAwareAllocator()
    for cap in [1000.0, 5000.0, 15000.0]:
        active = [1, 2, 3, 4, 5]
        states = {
            cid: {"buffer": cid * 3.0, "current_bitrate": BITRATE_LADDER[cid % len(BITRATE_LADDER)]}
            for cid in active
        }
        res = alloc.allocate(cap, active, states)
        assert sum(res.values()) <= cap + 1e-4
