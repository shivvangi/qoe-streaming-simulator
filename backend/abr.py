"""Adaptive Bitrate (ABR) Algorithms: Throughput, Buffer-Based, and Hybrid."""
from typing import List

BITRATE_LADDER = [300, 750, 1200, 1850, 2850, 4300]  # in kbps
CHUNK_DURATION = 4.0  # in seconds

class BaseABR:
    """Base class for ABR algorithms."""
    def select_bitrate(self, current_buffer: float, throughput_history: List[float]) -> int:
        raise NotImplementedError


class ThroughputABR(BaseABR):
    """Throughput-based ABR with harmonic mean estimation and safety margin."""
    def __init__(self, safety_margin: float = 0.85):
        self.safety_margin = safety_margin

    def select_bitrate(self, current_buffer: float, throughput_history: List[float]) -> int:
        if not throughput_history:
            return BITRATE_LADDER[0]

        # Use recent 5 chunk throughputs (harmonic mean gives robustness to spikes)
        recent = throughput_history[-5:]
        if any(t <= 0 for t in recent):
            est_throughput = sum(recent) / len(recent)
        else:
            est_throughput = len(recent) / sum(1.0 / t for t in recent)

        safe_throughput = est_throughput * self.safety_margin

        # Select highest bitrate <= safe_throughput
        selected = BITRATE_LADDER[0]
        for rate in BITRATE_LADDER:
            if rate <= safe_throughput:
                selected = rate
            else:
                break
        return selected


class BufferBasedABR(BaseABR):
    """Buffer-based ABR (BBA) with reservoir and cushion thresholds."""
    def __init__(self, reservoir: float = 4.0, cushion: float = 16.0):
        self.reservoir = reservoir
        self.cushion = cushion

    def select_bitrate(self, current_buffer: float, throughput_history: List[float]) -> int:
        if current_buffer <= self.reservoir:
            return BITRATE_LADDER[0]
        elif current_buffer >= self.cushion:
            return BITRATE_LADDER[-1]
        else:
            # Linear interpolation between reservoir and cushion
            fraction = (current_buffer - self.reservoir) / (self.cushion - self.reservoir)
            idx = int(fraction * (len(BITRATE_LADDER) - 1))
            idx = min(max(0, idx), len(BITRATE_LADDER) - 1)
            return BITRATE_LADDER[idx]


class HybridABR(BaseABR):
    """Hybrid ABR combining throughput estimation with buffer urgency adjustment."""
    def __init__(self, low_buf_thresh: float = 6.0, high_buf_thresh: float = 18.0):
        self.throughput_abr = ThroughputABR(safety_margin=0.90)
        self.low_buf = low_buf_thresh
        self.high_buf = high_buf_thresh

    def select_bitrate(self, current_buffer: float, throughput_history: List[float]) -> int:
        # Base selection from throughput
        base_rate = self.throughput_abr.select_bitrate(current_buffer, throughput_history)
        base_idx = BITRATE_LADDER.index(base_rate)

        # Buffer urgency guard: step down if buffer dangerously low
        if current_buffer < self.low_buf:
            base_idx = max(0, base_idx - 1)
        # Buffer cushion bonus: step up if buffer is rich
        elif current_buffer > self.high_buf:
            base_idx = min(len(BITRATE_LADDER) - 1, base_idx + 1)

        return BITRATE_LADDER[base_idx]


def get_abr_algorithm(name: str) -> BaseABR:
    name = name.lower()
    if name in ["throughput", "throughput_based"]:
        return ThroughputABR()
    elif name in ["buffer", "buffer_based", "bba"]:
        return BufferBasedABR()
    elif name in ["hybrid", "hybrid_qoe"]:
        return HybridABR()
    else:
        return BufferBasedABR()
