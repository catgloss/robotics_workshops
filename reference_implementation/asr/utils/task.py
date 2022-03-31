"""Task data class."""

from dataclasses import dataclass, field


@dataclass
class Task:  # pylint: disable=too-many-instance-attributes
    """Task."""

    audio_file: str
    object_id: str
    priority: str
    language: str
    mp3_filename: str
    wav_filename: str
    results: dict = field(default_factory=dict)
    domain: str = "n/a"
    complete: bool = False

    def mark_complete(self, results) -> None:
        """Set results and complete flag for task."""
        self.complete = True
        self.results = results
