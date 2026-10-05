"""Configuración persistente y rutas de datos multiplataforma."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sys
from typing import Any

APP_NAME = "Nightfall Gargoyle"
APP_DIR_NAME = "nightfall_gargoyle"

LOGICAL_WIDTH = 960
LOGICAL_HEIGHT = 540
LOGICAL_SIZE = (LOGICAL_WIDTH, LOGICAL_HEIGHT)
FPS = 60

RESOLUTION_PRESETS: tuple[tuple[int, int], ...] = (
    (960, 540),
    (1280, 720),
    (1600, 900),
    (1920, 1080),
)


def user_data_dir() -> Path:
    """Devuelve una carpeta de usuario adecuada para Linux, Windows y macOS."""

    override = os.environ.get("NIGHTFALL_GARGOYLE_HOME")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))

    return base / APP_DIR_NAME


def config_file() -> Path:
    return user_data_dir() / "config.json"


@dataclass(slots=True)
class GameConfig:
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    master_volume: float = 0.7
    vsync: bool = True

    @property
    def window_size(self) -> tuple[int, int]:
        return self.width, self.height


def _clean_config(data: dict[str, Any]) -> GameConfig:
    defaults = asdict(GameConfig())
    clean: dict[str, Any] = {}
    for key, default in defaults.items():
        value = data.get(key, default)
        if key in {"width", "height"}:
            try:
                clean[key] = max(320, int(value))
            except (TypeError, ValueError):
                clean[key] = default
        elif key == "fullscreen":
            clean[key] = bool(value)
        elif key == "vsync":
            clean[key] = bool(value)
        elif key == "master_volume":
            try:
                clean[key] = min(1.0, max(0.0, float(value)))
            except (TypeError, ValueError):
                clean[key] = default
        else:
            clean[key] = value
    return GameConfig(**clean)


def load_config(path: Path | None = None) -> GameConfig:
    path = path or config_file()
    if not path.exists():
        return GameConfig()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return GameConfig()

    if not isinstance(data, dict):
        return GameConfig()
    return _clean_config(data)


def save_config(config: GameConfig, path: Path | None = None) -> None:
    path = path or config_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(config), indent=2, ensure_ascii=False), encoding="utf-8")
