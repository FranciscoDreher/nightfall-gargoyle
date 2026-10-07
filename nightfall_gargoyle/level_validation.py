"""Validación de invariantes de diseño para los niveles del juego."""

from __future__ import annotations

from .level_data import LevelData, RectDef


def _ensure_rect(rect: RectDef, *, level_id: str, name: str) -> None:
    if len(rect) != 4:
        raise ValueError(f"{level_id}: {name} tiene un rectángulo inválido: {rect!r}")
    x, y, width, height = rect
    if width <= 0 or height <= 0:
        raise ValueError(f"{level_id}: {name} tiene dimensiones no positivas: {rect!r}")
    if x < 0 or y < 0:
        raise ValueError(f"{level_id}: {name} tiene coordenadas negativas: {rect!r}")


def validate_level(level: LevelData) -> None:
    """Valida invariantes mínimas de diseño para un nivel."""
    if not isinstance(level, LevelData):
        raise TypeError(f"Nivel inválido: {type(level).__name__}")

    if not level.level_id or not level.name or not level.subtitle:
        raise ValueError(f"{level.level_id}: metadata incompleta")
    if level.width <= 0 or level.height <= 0:
        raise ValueError(f"{level.level_id}: dimensiones inválidas ({level.width}x{level.height})")
    if not level.platforms:
        raise ValueError(f"{level.level_id}: no hay plataformas")

    for platform in level.platforms:
        _ensure_rect(platform, level_id=level.level_id, name="plataforma")
        x, y, width, height = platform
        if x + width > level.width + 20 or y + height > level.height + 20:
            raise ValueError(f"{level.level_id}: plataforma fuera del mapa: {platform!r}")

    for hazard in level.hazards:
        _ensure_rect(hazard, level_id=level.level_id, name="peligro")
        x, y, width, height = hazard
        if x + width > level.width + 20 or y + height > level.height + 20:
            raise ValueError(f"{level.level_id}: peligro fuera del mapa: {hazard!r}")

    if level.shards_required < 0 or level.shards_required != len(level.shards):
        raise ValueError(
            f"{level.level_id}: shards_required={level.shards_required} debe coincidir exactamente con {len(level.shards)} shards disponibles"
        )

    shard_ids = [shard[0] for shard in level.shards]
    enemy_ids = [enemy[0] for enemy in level.enemies]
    checkpoint_ids = [checkpoint[0] for checkpoint in level.checkpoints]
    object_ids = shard_ids + enemy_ids + checkpoint_ids
    if len(object_ids) != len(set(object_ids)):
        raise ValueError(f"{level.level_id}: hay IDs duplicadas entre shards, enemigos y checkpoints")

    for shard_id, x, y in level.shards:
        if not shard_id:
            raise ValueError(f"{level.level_id}: shard sin identificador")
        if x < 0 or y < 0 or x >= level.width or y >= level.height:
            raise ValueError(f"{level.level_id}: shard fuera del mapa: {shard_id!r} -> ({x}, {y})")

    for enemy_id, x, y, min_x, max_x in level.enemies:
        if not enemy_id:
            raise ValueError(f"{level.level_id}: enemigo sin identificador")
        if min_x >= max_x:
            raise ValueError(f"{level.level_id}: patrol del enemigo {enemy_id} inválido ({min_x}, {max_x})")
        if min_x < 0 or max_x > level.width:
            raise ValueError(f"{level.level_id}: enemigo {enemy_id} fuera del mapa")

    for checkpoint_id, x, y, spawn_x, spawn_y in level.checkpoints:
        if not checkpoint_id:
            raise ValueError(f"{level.level_id}: checkpoint sin identificador")
        if x < 0 or y < 0 or spawn_x < 0 or spawn_y < 0:
            raise ValueError(f"{level.level_id}: checkpoint {checkpoint_id} tiene coordenadas negativas")
        if x >= level.width or y >= level.height or spawn_x >= level.width or spawn_y >= level.height:
            raise ValueError(f"{level.level_id}: checkpoint {checkpoint_id} fuera del mapa")

    _ensure_rect(level.exit_gate, level_id=level.level_id, name="puerta de salida")
    gate_x, gate_y, gate_w, gate_h = level.exit_gate
    if gate_x + gate_w > level.width + 50 or gate_y + gate_h > level.height + 50:
        raise ValueError(f"{level.level_id}: puerta de salida fuera del mapa: {level.exit_gate!r}")

    spawn_x, spawn_y = level.spawn
    if spawn_x < 0 or spawn_y < 0 or spawn_x >= level.width or spawn_y >= level.height:
        raise ValueError(f"{level.level_id}: spawn fuera del mapa: {level.spawn!r}")


def validate_levels(levels: tuple[LevelData, ...]) -> tuple[LevelData, ...]:
    """Valida cada nivel del conjunto y lanza un ValueError si hay inconsistencias."""
    seen: set[str] = set()
    for level in levels:
        if level.level_id in seen:
            raise ValueError(f"Duplicado de level_id: {level.level_id}")
        seen.add(level.level_id)
        validate_level(level)
    return levels
