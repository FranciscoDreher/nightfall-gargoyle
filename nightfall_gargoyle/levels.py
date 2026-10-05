"""Datos de niveles. Todo se dibuja con primitivas para evitar assets externos."""

from __future__ import annotations

from dataclasses import dataclass

RectDef = tuple[int, int, int, int]
EnemyDef = tuple[str, int, int, int, int]
ShardDef = tuple[str, int, int]
CheckpointDef = tuple[str, int, int, int, int]


@dataclass(frozen=True, slots=True)
class LevelData:
    level_id: str
    name: str
    subtitle: str
    width: int
    height: int
    spawn: tuple[float, float]
    shards_required: int
    platforms: tuple[RectDef, ...]
    hazards: tuple[RectDef, ...]
    shards: tuple[ShardDef, ...]
    enemies: tuple[EnemyDef, ...]
    checkpoints: tuple[CheckpointDef, ...]
    exit_gate: RectDef


LEVELS: tuple[LevelData, ...] = (
    LevelData(
        level_id="umbra_rooftops",
        name="Tejados de Umbra",
        subtitle="Aprende a saltar entre azoteas y recolecta fragmentos lunares.",
        width=3200,
        height=820,
        spawn=(120.0, 660.0),
        shards_required=5,
        platforms=(
            (0, 740, 3200, 90),
            (250, 650, 260, 26),
            (610, 590, 230, 26),
            (955, 530, 220, 26),
            (1280, 650, 320, 26),
            (1700, 600, 240, 26),
            (2050, 540, 240, 26),
            (2380, 650, 270, 26),
            (2780, 600, 260, 26),
        ),
        hazards=(
            (1120, 724, 150, 16),
            (1970, 724, 170, 16),
        ),
        shards=(
            ("umbra_rooftops:shard_01", 340, 610),
            ("umbra_rooftops:shard_02", 695, 550),
            ("umbra_rooftops:shard_03", 1045, 490),
            ("umbra_rooftops:shard_04", 1810, 560),
            ("umbra_rooftops:shard_05", 2155, 500),
            ("umbra_rooftops:shard_06", 2895, 560),
        ),
        enemies=(
            ("umbra_rooftops:bat_01", 720, 548, 610, 820),
            ("umbra_rooftops:imp_01", 1420, 608, 1290, 1580),
            ("umbra_rooftops:bat_02", 2480, 608, 2390, 2630),
        ),
        checkpoints=(
            ("umbra_rooftops:checkpoint_01", 1510, 596, 1440, 590),
        ),
        exit_gate=(3025, 638, 72, 102),
    ),
    LevelData(
        level_id="clocktower_garden",
        name="Jardín de la Torre",
        subtitle="Usa el doble salto para superar ruinas, picos y guardianes.",
        width=3600,
        height=880,
        spawn=(105.0, 700.0),
        shards_required=6,
        platforms=(
            (0, 780, 3600, 100),
            (210, 690, 200, 26),
            (530, 625, 210, 26),
            (860, 560, 220, 26),
            (1190, 665, 260, 26),
            (1570, 610, 240, 26),
            (1910, 545, 250, 26),
            (2260, 675, 270, 26),
            (2660, 610, 260, 26),
            (3070, 545, 260, 26),
        ),
        hazards=(
            (430, 764, 120, 16),
            (1460, 764, 140, 16),
            (2530, 764, 140, 16),
        ),
        shards=(
            ("clocktower_garden:shard_01", 290, 650),
            ("clocktower_garden:shard_02", 620, 585),
            ("clocktower_garden:shard_03", 960, 520),
            ("clocktower_garden:shard_04", 2025, 505),
            ("clocktower_garden:shard_05", 2765, 570),
            ("clocktower_garden:shard_06", 3175, 505),
            ("clocktower_garden:shard_07", 3360, 735),
        ),
        enemies=(
            ("clocktower_garden:imp_01", 610, 583, 535, 735),
            ("clocktower_garden:bat_01", 1290, 623, 1200, 1440),
            ("clocktower_garden:imp_02", 2350, 633, 2265, 2515),
            ("clocktower_garden:bat_02", 3175, 503, 3080, 3320),
        ),
        checkpoints=(
            ("clocktower_garden:checkpoint_01", 1680, 556, 1640, 550),
            ("clocktower_garden:checkpoint_02", 2850, 556, 2810, 550),
        ),
        exit_gate=(3460, 678, 76, 102),
    ),
)
