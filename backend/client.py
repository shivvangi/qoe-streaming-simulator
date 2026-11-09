"""Streaming Client Model: Buffer, Playback State Machine, and Chunk Downloads."""
from typing import List, Dict, Any
from abr import BaseABR, BITRATE_LADDER, CHUNK_DURATION

class StreamingClient:
    """Simulates an individual DASH video streaming client."""

    def __init__(
        self,
        client_id: int,
        abr_algorithm: BaseABR,
        arrival_time: float = 0.0,
        buffer_cap: float = 30.0,
        startup_threshold: float = 4.0,
        resume_threshold: float = 2.0
    ):
        self.client_id = client_id
        self.abr = abr_algorithm
        self.arrival_time = arrival_time
        self.buffer_cap = buffer_cap
        self.startup_threshold = startup_threshold
        self.resume_threshold = resume_threshold

        # Playback states: 'NOT_ARRIVED', 'STARTUP', 'PLAYING', 'REBUFFERING', 'IDLE_BUFFER_FULL'
        self.state = "NOT_ARRIVED" if arrival_time > 0.0 else "STARTUP"
        self.buffer = 0.0

        # Chunk download tracking
        self.current_chunk_idx = 0
        self.current_bitrate = BITRATE_LADDER[0]
        self.chunk_bits_downloaded = 0.0
        self.chunk_bits_total = float(self.current_bitrate * CHUNK_DURATION)  # in kbits
        self.chunk_download_time = 0.0

        # Historical metrics
        self.bitrate_history: List[int] = []
        self.throughput_history: List[float] = []  # in kbps

        self.startup_delay = 0.0
        self.total_stall_time = 0.0
        self.stall_count = 0
        self.total_play_time = 0.0

        if self.state == "STARTUP":
            self._init_chunk()

    def _init_chunk(self):
        """Initializes the download of the next chunk using ABR choice."""
        if self.current_chunk_idx == 0:
            self.current_bitrate = BITRATE_LADDER[0]
        else:
            self.current_bitrate = self.abr.select_bitrate(self.buffer, self.throughput_history)

        self.chunk_bits_downloaded = 0.0
        self.chunk_bits_total = float(self.current_bitrate * CHUNK_DURATION)  # in kbits
        self.chunk_download_time = 0.0

    def is_active_downloader(self, current_time: float = 0.0) -> bool:
        """Returns True if client is present and demanding bandwidth."""
        if self.state == "NOT_ARRIVED":
            if current_time >= self.arrival_time:
                self.state = "STARTUP"
                self._init_chunk()
                return True
            return False
        return self.state != "IDLE_BUFFER_FULL"

    def receive_bandwidth(self, bandwidth_kbps: float, dt: float) -> bool:
        """
        Transmits bits over duration dt at assigned bandwidth.
        Returns True if chunk download was completed in this tick.
        """
        if self.state in ["NOT_ARRIVED", "IDLE_BUFFER_FULL"] or bandwidth_kbps <= 0:
            return False

        bits_received = bandwidth_kbps * dt  # in kbits
        self.chunk_bits_downloaded += bits_received
        self.chunk_download_time += dt

        if self.chunk_bits_downloaded >= self.chunk_bits_total:
            # Chunk completed!
            self.bitrate_history.append(self.current_bitrate)

            # Record estimated chunk throughput: total kbits / download duration in seconds
            if self.chunk_download_time > 0:
                est_tp = self.chunk_bits_total / self.chunk_download_time
                self.throughput_history.append(est_tp)

            # Add chunk duration to playback buffer
            self.buffer += CHUNK_DURATION
            self.current_chunk_idx += 1

            # Buffer capping check
            if self.buffer >= self.buffer_cap:
                self.state = "IDLE_BUFFER_FULL"
            else:
                self._init_chunk()

            return True

        return False

    def update_playback(self, dt: float):
        """Advances playback and buffer drainage by dt seconds."""
        if self.state == "NOT_ARRIVED":
            return

        elif self.state == "STARTUP":
            self.startup_delay += dt
            if self.buffer >= self.startup_threshold:
                self.state = "PLAYING"

        elif self.state == "PLAYING":
            if self.buffer > 0:
                drain = min(self.buffer, dt)
                self.buffer -= drain
                self.total_play_time += drain

                if self.buffer <= 0.001:
                    self.buffer = 0.0
                    self.state = "REBUFFERING"
                    self.stall_count += 1
            else:
                self.state = "REBUFFERING"
                self.stall_count += 1
                self.total_stall_time += dt

        elif self.state == "REBUFFERING":
            self.total_stall_time += dt
            if self.buffer >= self.resume_threshold:
                self.state = "PLAYING"

        elif self.state == "IDLE_BUFFER_FULL":
            drain = min(self.buffer, dt)
            self.buffer -= drain
            self.total_play_time += drain

            if self.buffer < (self.buffer_cap - CHUNK_DURATION):
                self.state = "PLAYING"
                self._init_chunk()

    def get_summary(self) -> Dict[str, Any]:
        """Returns client summary metrics."""
        avg_rate = (sum(self.bitrate_history) / len(self.bitrate_history)) if self.bitrate_history else 0.0
        return {
            "client_id": self.client_id,
            "arrival_time": self.arrival_time,
            "buffer": round(self.buffer, 2),
            "state": self.state,
            "chunks_downloaded": len(self.bitrate_history),
            "avg_bitrate_kbps": round(avg_rate, 1),
            "startup_delay": round(self.startup_delay, 2),
            "total_stall_time": round(self.total_stall_time, 2),
            "stall_count": self.stall_count,
            "total_play_time": round(self.total_play_time, 2)
        }
