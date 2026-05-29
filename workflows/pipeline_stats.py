from dataclasses import dataclass


@dataclass
class PipelineStats:
    videos_processed: int = 0
    new_videos_discovered: int = 0
    video_errors: int = 0
    discovery_errors: int = 0
    status: str = "success"

    def mark_partial_success(self):
        if self.status != "failed":
            self.status = "partial_success"

    def mark_failed(self):
        self.status = "failed"
