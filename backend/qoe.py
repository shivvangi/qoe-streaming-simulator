"""Quality of Experience (QoE) and Fairness Calculation Module."""
import math
from typing import List, Dict, Any

class QoEEvaluator:
    """Calculates standardized QoE metrics and Jain's fairness index."""

    def __init__(self, lambda_switch: float = 1.0, mu_stall: float = 4.3, tau_startup: float = 1.0):
        self.lambda_switch = lambda_switch
        self.mu_stall = mu_stall
        self.tau_startup = tau_startup

    @staticmethod
    def utility(bitrate_kbps: float) -> float:
        """Logarithmic perceptual quality utility q(R) = ln(R / R_min)."""
        r = max(300.0, float(bitrate_kbps))
        return math.log(r / 300.0)

    def calculate_client_qoe(
        self,
        bitrate_history: List[int],
        total_stall_time: float,
        startup_delay: float
    ) -> Dict[str, float]:
        """Calculates QoE components for a single client."""
        if not bitrate_history:
            return {
                "qoe_total": 0.0,
                "quality_utility": 0.0,
                "switching_penalty": 0.0,
                "stall_penalty": round(self.mu_stall * total_stall_time, 3),
                "startup_penalty": round(self.tau_startup * startup_delay, 3),
                "avg_bitrate_kbps": 0.0,
                "num_switches": 0
            }

        utilities = [self.utility(r) for r in bitrate_history]
        quality_sum = sum(utilities)

        switching_penalty = 0.0
        num_switches = 0
        for k in range(len(utilities) - 1):
            diff = abs(utilities[k + 1] - utilities[k])
            switching_penalty += diff
            if bitrate_history[k + 1] != bitrate_history[k]:
                num_switches += 1

        stall_penalty = self.mu_stall * total_stall_time
        startup_penalty = self.tau_startup * startup_delay

        qoe_total = quality_sum - (self.lambda_switch * switching_penalty) - stall_penalty - startup_penalty
        avg_bitrate = sum(bitrate_history) / len(bitrate_history)

        return {
            "qoe_total": round(qoe_total, 3),
            "quality_utility": round(quality_sum, 3),
            "switching_penalty": round(self.lambda_switch * switching_penalty, 3),
            "stall_penalty": round(stall_penalty, 3),
            "startup_penalty": round(startup_penalty, 3),
            "avg_bitrate_kbps": round(avg_bitrate, 1),
            "num_switches": num_switches
        }

    @staticmethod
    def jains_fairness_index(values: List[float]) -> float:
        """Calculates Jain's fairness index: J(x) = (sum x)^2 / (N * sum x^2)."""
        if not values:
            return 1.0

        n = len(values)
        val_sum = sum(values)
        sum_sq = sum(v * v for v in values)

        if sum_sq <= 1e-9:
            return 1.0

        fairness = (val_sum * val_sum) / (n * sum_sq)
        # Numerical safeguard to ensure fairness is within [1/n, 1.0]
        return round(min(1.0, max(1.0 / n, fairness)), 4)
