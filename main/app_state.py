from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class AppState:
    source_type: str = "webcam"
    source_value: Optional[str] = None
    roi_rect: Optional[Tuple[int, int, int, int]] = None
    recording: bool = False
