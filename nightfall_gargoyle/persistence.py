"""Guardado/carga de partidas en JSON."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .settings import user_data_dir

SAVE_SCHEMA_VERSION = 1
MAX_HEALTH = 5
STARTING_LIVES = 3


def save_file() -> Path:
    return user_data_dir() / "savegame.json"


@dataclass(slots=True)
class SaveState:
    schema_version: int = SAVE_SCHEMA_VERSION
    profile_name: str = "Jugador"
    current_level: int = 0
    checkpoint: tuple[float, float] = (120.0, 660.0)
    health: int = MAX_HEALTH
    lives: int = STARTING_LIVES
    collected_shards: list[str] = field(default_factory=list)
    defeated_enemies: list[str] = field(default_factory=list)
    reached_checkpoints: list[str] = field(default_factory=list)
    unlocked_levels: int = 1
    play_time_seconds: float = 0.0
    last_saved: str = ""

    @property
    def total_shards(self) -> int:
        return len(self.collected_shards)


def new_save(profile_name: str = "Jugador", checkpoint: tuple[float, float] = (120.0, 660.0)) -> SaveState:
    return SaveState(profile_name=profile_name, checkpoint=checkpoint)


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _from_dict(data: dict[str, Any]) -> SaveState:
    checkpoint_raw = data.get("checkpoint", (120.0, 660.0))
    if isinstance(checkpoint_raw, (list, tuple)) and len(checkpoint_raw) == 2:
        try:
            checkpoint = (float(checkpoint_raw[0]), float(checkpoint_raw[1]))
        except (TypeError, ValueError):
            checkpoint = (120.0, 660.0)
    else:
        checkpoint = (120.0, 660.0)

    try:
        current_level = max(0, int(data.get("current_level", 0)))
    except (TypeError, ValueError):
        current_level = 0

    try:
        unlocked_levels = max(1, int(data.get("unlocked_levels", 1)))
    except (TypeError, ValueError):
        unlocked_levels = 1

    try:
        play_time_seconds = max(0.0, float(data.get("play_time_seconds", 0.0)))
    except (TypeError, ValueError):
        play_time_seconds = 0.0

    try:
        health = max(1, min(MAX_HEALTH, int(data.get("health", MAX_HEALTH))))
    except (TypeError, ValueError):
        health = MAX_HEALTH

    try:
        lives = max(0, int(data.get("lives", STARTING_LIVES)))
    except (TypeError, ValueError):
        lives = STARTING_LIVES

    return SaveState(
        schema_version=SAVE_SCHEMA_VERSION,
        profile_name=str(data.get("profile_name", "Jugador")),
        current_level=current_level,
        checkpoint=checkpoint,
        health=health,
        lives=lives,
        collected_shards=_as_string_list(data.get("collected_shards")),
        defeated_enemies=_as_string_list(data.get("defeated_enemies")),
        reached_checkpoints=_as_string_list(data.get("reached_checkpoints")),
        unlocked_levels=unlocked_levels,
        play_time_seconds=play_time_seconds,
        last_saved=str(data.get("last_saved", "")),
    )


def load_save(path: Path | None = None) -> SaveState | None:
    path = path or save_file()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return _from_dict(data)


def write_save(state: SaveState, path: Path | None = None) -> None:
    path = path or save_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    state.last_saved = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(asdict(state), indent=2, ensure_ascii=False), encoding="utf-8")


def reset_save(path: Path | None = None) -> None:
    path = path or save_file()
    try:
        path.unlink()
    except FileNotFoundError:
        return
