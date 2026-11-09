"""Network bottleneck link model with synthetic capacity traces."""
import math
from typing import Dict, Any, List

class NetworkModel:
    """Simulates a shared bottleneck link capacity C(t) in kbps."""

    def __init__(
        self,
        base_capacity_kbps: float = 8000.0,
        trace_type: str = "fluctuating",
        seed: int = 42
    ):
        self.base_capacity = float(base_capacity_kbps)
        self.trace_type = trace_type
        self.seed = seed

    def get_capacity(self, t: float) -> float:
        """Returns instantaneous network capacity C(t) in kbps."""
        if self.trace_type == "fixed":
            return max(500.0, self.base_capacity)

        elif self.trace_type == "fluctuating":
            # Realistic diurnal/sinusoidal fluctuation with periodic dips
            # C(t) = base * [1.0 + 0.35 * sin(2*pi*t/30) + 0.15 * cos(2*pi*t/12)]
            wave1 = 0.35 * math.sin(2.0 * math.pi * t / 30.0)
            wave2 = 0.15 * math.cos(2.0 * math.pi * t / 12.0)
            cap = self.base_capacity * (1.0 + wave1 + wave2)
            # Add a temporary congestion dip between t=40s and t=60s
            if 40.0 <= t <= 60.0:
                cap *= 0.60
            return max(600.0, cap)

        elif self.trace_type == "step_drop":
            # Step down at t=30s, step up at t=70s
            if 30.0 <= t < 70.0:
                return max(500.0, self.base_capacity * 0.45)
            return max(500.0, self.base_capacity)

        else:
            return max(500.0, self.base_capacity)

    def get_timeline(self, duration: float, dt: float = 0.5) -> List[Dict[str, float]]:
        """Generates a discrete timeline of network capacities."""
        steps = int(duration / dt)
        return [{"time": round(i * dt, 2), "capacity": round(self.get_capacity(i * dt), 2)} for i in range(steps)]
