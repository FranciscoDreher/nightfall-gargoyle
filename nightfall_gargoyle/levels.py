"""Capa de compatibilidad para los niveles del juego.

La definición real de los niveles vive en level_data.py, y la validación en
level_validation.py. Este archivo conserva la API pública existente para no
romper imports del resto del proyecto mientras mantiene cada responsabilidad
separada y más legible.
"""

from __future__ import annotations

from .level_data import CheckpointDef, EnemyDef, LevelData, RectDef, ShardDef, LEVELS
from .level_validation import validate_level, validate_levels

validate_levels(LEVELS)

__all__ = [
    "CheckpointDef",
    "EnemyDef",
    "LevelData",
    "LEVELS",
    "RectDef",
    "ShardDef",
    "validate_level",
    "validate_levels",
]
