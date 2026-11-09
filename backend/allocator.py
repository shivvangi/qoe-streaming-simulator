"""Bandwidth Allocation Policies: Equal-Share and Proposed QoE-Aware Allocator."""
from typing import Dict, List, Any
import math
from abr import BITRATE_LADDER
from qoe import QoEEvaluator

class BaseAllocator:
    """Base class for bottleneck bandwidth allocation."""
    def allocate(
        self,
        capacity_kbps: float,
        active_client_ids: List[int],
        client_states: Dict[int, Dict[str, Any]]
    ) -> Dict[int, float]:
        raise NotImplementedError


class EqualShareAllocator(BaseAllocator):
    """Evenly distributes bottleneck capacity among all active downloaders."""
    def allocate(
        self,
        capacity_kbps: float,
        active_client_ids: List[int],
        client_states: Dict[int, Dict[str, Any]]
    ) -> Dict[int, float]:
        if not active_client_ids or capacity_kbps <= 0:
            return {cid: 0.0 for cid in active_client_ids}

        share = float(capacity_kbps) / len(active_client_ids)
        return {cid: share for cid in active_client_ids}


class QoEAwareAllocator(BaseAllocator):
    """
    Proposed QoE-Aware Allocator:
    Weights bandwidth based on buffer urgency (stall avoidance)
    and marginal quality utility gain.
    """
    def __init__(
        self,
        alpha: float = 0.60,
        w_min: float = 0.10,
        w_max: float = 1.0,
        target_buffer: float = 16.0,
        critical_buffer: float = 4.0
    ):
        self.alpha = alpha
        self.w_min = w_min
        self.w_max = w_max
        self.target_buffer = target_buffer
        self.critical_buffer = critical_buffer
        self.qoe_eval = QoEEvaluator()
        self.max_utility = self.qoe_eval.utility(BITRATE_LADDER[-1])

    def allocate(
        self,
        capacity_kbps: float,
        active_client_ids: List[int],
        client_states: Dict[int, Dict[str, Any]]
    ) -> Dict[int, float]:
        if not active_client_ids or capacity_kbps <= 0:
            return {cid: 0.0 for cid in active_client_ids}

        weights: Dict[int, float] = {}

        for cid in active_client_ids:
            state = client_states[cid]
            buf = state.get("buffer", 0.0)
            curr_rate = state.get("current_bitrate", BITRATE_LADDER[0])

            # 1. Buffer Urgency component in [0, 1]
            if buf <= self.critical_buffer:
                urgency = 1.0
            elif buf >= self.target_buffer:
                urgency = 0.0
            else:
                urgency = (self.target_buffer - buf) / (self.target_buffer - self.critical_buffer)

            # 2. Marginal QoE gain component in [0, 1]
            curr_idx = BITRATE_LADDER.index(curr_rate) if curr_rate in BITRATE_LADDER else 0
            if curr_idx < len(BITRATE_LADDER) - 1:
                next_rate = BITRATE_LADDER[curr_idx + 1]
                q_diff = self.qoe_eval.utility(next_rate) - self.qoe_eval.utility(curr_rate)
                # Normalize against maximum ladder step
                gain = min(1.0, max(0.0, q_diff / self.max_utility))
            else:
                gain = 0.05  # Already at max rate, nominal maintenance weight

            # Combined weight with starvation prevention clamp
            w = self.alpha * urgency + (1.0 - self.alpha) * gain
            w = max(self.w_min, min(self.w_max, w))
            weights[cid] = w

        total_weight = sum(weights.values())
        if total_weight <= 0:
            total_weight = 1.0

        # Allocate bandwidth strictly preserving total capacity
        allocations: Dict[int, float] = {}
        for cid in active_client_ids:
            allocations[cid] = (weights[cid] / total_weight) * capacity_kbps

        # Sanity check: sum <= capacity
        sum_allocated = sum(allocations.values())
        if sum_allocated > capacity_kbps and capacity_kbps > 0:
            scale = capacity_kbps / sum_allocated
            for cid in allocations:
                allocations[cid] *= scale

        return allocations


def get_allocator(name: str) -> BaseAllocator:
    name = name.lower()
    if name in ["equal", "equal_share", "fair"]:
        return EqualShareAllocator()
    elif name in ["qoe", "qoe_aware", "proposed"]:
        return QoEAwareAllocator()
    else:
        return EqualShareAllocator()
