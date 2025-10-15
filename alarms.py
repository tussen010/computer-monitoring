from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Literal
import json

@dataclass
class ThresholdAlarm:
    type: Literal["cpu", "mem", "disk"]
    threshold: float

    def to_dict(self) -> dict:
        return asdict(self)

class AlarmStore:
    """
    Sköter läsning/skrivning av tröskellarm till en JSON-fil.
    Format i filen: [{"type": "cpu", "threshold": 80.0}, ...]
    """
    def __init__(self, json_path: Path | str = "alarms.json") -> None:
        self.path = Path(json_path)
        self.alarms: List[ThresholdAlarm] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.alarms = []
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("no expected file in alarms.json")
            self.alarms = [ThresholdAlarm(type=a["type"], threshold=float(a["threshold"])) for a in raw]
        except Exception as e:
            raise RuntimeError(f"could not read '{self.path}': {e}") from e

    def save(self) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps([a.to_dict() for a in self.alarms], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        tmp.replace(self.path)  # atomisk ersättning

    # ---- Publika hjälpare ----
    def list(self) -> List[dict]:
        return [a.to_dict() for a in self.alarms]

    def add(self, alarm_type: Literal["cpu", "mem", "disk"], threshold: float) -> ThresholdAlarm:
        a = ThresholdAlarm(type=alarm_type, threshold=float(threshold))
        self.alarms.append(a)
        self.save()
        return a

    def remove_index(self, idx_zero_based: int) -> ThresholdAlarm:
        a = self.alarms.pop(idx_zero_based)
        self.save()
        return a

    def is_empty(self) -> bool:
        return len(self.alarms) == 0
