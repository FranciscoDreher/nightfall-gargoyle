"""Definición declarativa de los niveles del juego."""

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
        shards_required=6,
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
        shards_required=7,
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
    LevelData(
        level_id="ashcrypt_vault",
        name="Cripta de Ceniza",
        subtitle="Las estructuras se estrechan. Recorre la bóveda subterránea con cuidado.",
        width=3800,
        height=900,
        spawn=(100.0, 720.0),
        shards_required=6,
        platforms=(
            (0, 800, 3800, 100),
            (180, 710, 190, 20),
            (520, 650, 200, 20),
            (900, 585, 195, 20),
            (1260, 715, 210, 20),
            (1650, 655, 190, 20),
            (2030, 590, 200, 20),
            (2410, 720, 200, 20),
            (2810, 660, 190, 20),
            (3220, 595, 190, 20),
        ),
        hazards=(
            (350, 784, 140, 16),
            (1090, 784, 150, 16),
            (1900, 784, 160, 16),
            (2650, 784, 145, 16),
            (3450, 784, 150, 16),
        ),
        shards=(
            ("ashcrypt_vault:shard_01", 250, 670),
            ("ashcrypt_vault:shard_02", 600, 610),
            ("ashcrypt_vault:shard_03", 985, 545),
            ("ashcrypt_vault:shard_04", 1735, 615),
            ("ashcrypt_vault:shard_05", 2490, 620),
            ("ashcrypt_vault:shard_06", 3305, 555),
        ),
        enemies=(
            ("ashcrypt_vault:bat_01", 680, 630, 520, 880),
            ("ashcrypt_vault:imp_01", 1420, 665, 1260, 1640),
            ("ashcrypt_vault:bat_02", 2100, 650, 2030, 2380),
            ("ashcrypt_vault:imp_02", 2950, 635, 2810, 3220),
            ("ashcrypt_vault:imp_03", 3500, 585, 3220, 3800),
        ),
        checkpoints=(
            ("ashcrypt_vault:checkpoint_01", 1260, 695, 1250, 700),
            ("ashcrypt_vault:checkpoint_02", 2030, 670, 2020, 665),
            ("ashcrypt_vault:checkpoint_03", 2810, 640, 2800, 650),
        ),
        exit_gate=(3560, 658, 72, 102),
    ),
    LevelData(
        level_id="night_spire",
        name="Torreon Nocturno",
        subtitle="Las plataformas se separan. El ascenso se vuelve crítico.",
        width=4200,
        height=920,
        spawn=(95.0, 740.0),
        shards_required=7,
        platforms=(
            (0, 820, 4200, 100),
            (160, 720, 180, 18),
            (520, 650, 190, 18),
            (920, 575, 185, 18),
            (1300, 730, 200, 18),
            (1720, 670, 185, 18),
            (2130, 600, 190, 18),
            (2540, 745, 195, 18),
            (2980, 690, 180, 18),
            (3420, 615, 190, 18),
            (3850, 740, 190, 18),
        ),
        hazards=(
            (350, 804, 140, 16),
            (1100, 804, 150, 16),
            (1900, 804, 155, 16),
            (2700, 804, 160, 16),
            (3600, 804, 150, 16),
        ),
        shards=(
            ("night_spire:shard_01", 230, 680),
            ("night_spire:shard_02", 615, 610),
            ("night_spire:shard_03", 1010, 535),
            ("night_spire:shard_04", 1810, 630),
            ("night_spire:shard_05", 2630, 630),
            ("night_spire:shard_06", 3510, 575),
            ("night_spire:shard_07", 3950, 700),
        ),
        enemies=(
            ("night_spire:bat_01", 650, 610, 520, 920),
            ("night_spire:imp_01", 1420, 665, 1300, 1720),
            ("night_spire:bat_02", 2100, 660, 1920, 2360),
            ("night_spire:imp_02", 2850, 645, 2540, 3100),
            ("night_spire:bat_03", 3500, 640, 3420, 3850),
            ("night_spire:imp_03", 3950, 710, 3850, 4200),
        ),
        checkpoints=(
            ("night_spire:checkpoint_01", 1300, 710, 1290, 720),
            ("night_spire:checkpoint_02", 2540, 735, 2530, 745),
        ),
        exit_gate=(4050, 688, 72, 102),
    ),
    LevelData(
        level_id="sleeping_sphinxes",
        name="Esfinges Dormidas",
        subtitle="Las grietas se multiplican. Solo los más ágiles avanzan.",
        width=4500,
        height=950,
        spawn=(90.0, 760.0),
        shards_required=9,
        platforms=(
            (0, 850, 4500, 100),
            (150, 730, 175, 16),
            (500, 655, 180, 16),
            (920, 575, 175, 16),
            (1320, 750, 190, 16),
            (1760, 680, 175, 16),
            (2200, 600, 185, 16),
            (2660, 760, 180, 16),
            (3120, 700, 175, 16),
            (3580, 615, 185, 16),
            (4050, 760, 185, 16),
        ),
        hazards=(
            (340, 834, 140, 16),
            (1120, 834, 150, 16),
            (1980, 834, 160, 16),
            (2900, 834, 155, 16),
            (3800, 834, 165, 16),
        ),
        shards=(
            ("sleeping_sphinxes:shard_01", 220, 690),
            ("sleeping_sphinxes:shard_02", 610, 615),
            ("sleeping_sphinxes:shard_03", 1010, 535),
            ("sleeping_sphinxes:shard_04", 1850, 640),
            ("sleeping_sphinxes:shard_05", 2750, 660),
            ("sleeping_sphinxes:shard_06", 3210, 660),
            ("sleeping_sphinxes:shard_07", 3680, 575),
            ("sleeping_sphinxes:shard_08", 4140, 720),
            ("sleeping_sphinxes:shard_09", 4350, 600),
        ),
        enemies=(
            ("sleeping_sphinxes:bat_01", 640, 615, 500, 920),
            ("sleeping_sphinxes:imp_01", 1420, 680, 1320, 1760),
            ("sleeping_sphinxes:bat_02", 2100, 680, 1920, 2360),
            ("sleeping_sphinxes:imp_02", 2860, 675, 2660, 3120),
            ("sleeping_sphinxes:bat_03", 3500, 670, 3400, 3850),
            ("sleeping_sphinxes:imp_03", 4050, 730, 3900, 4300),
            ("sleeping_sphinxes:imp_04", 4350, 620, 4200, 4500),
        ),
        checkpoints=(
            ("sleeping_sphinxes:checkpoint_01", 1320, 730, 1310, 740),
            ("sleeping_sphinxes:checkpoint_02", 2660, 740, 2650, 750),
        ),
        exit_gate=(4380, 698, 72, 102),
    ),
    LevelData(
        level_id="shadows_crown",
        name="Corona de Sombra",
        subtitle="El último desafío. Enfrenta la oscuridad absoluta.",
        width=5000,
        height=1000,
        spawn=(85.0, 780.0),
        shards_required=11,
        platforms=(
            (0, 900, 5000, 100),
            (140, 750, 170, 14),
            (480, 670, 175, 14),
            (900, 590, 170, 14),
            (1320, 770, 185, 14),
            (1800, 700, 170, 14),
            (2280, 615, 180, 14),
            (2780, 780, 175, 14),
            (3280, 720, 170, 14),
            (3800, 635, 180, 14),
            (4350, 780, 180, 14),
            (4750, 650, 175, 14),
        ),
        hazards=(
            (330, 884, 140, 16),
            (1120, 884, 150, 16),
            (2020, 884, 160, 16),
            (2980, 884, 160, 16),
            (4050, 884, 170, 16),
        ),
        shards=(
            ("shadows_crown:shard_01", 210, 710),
            ("shadows_crown:shard_02", 590, 630),
            ("shadows_crown:shard_03", 1000, 550),
            ("shadows_crown:shard_04", 1900, 660),
            ("shadows_crown:shard_05", 2380, 575),
            ("shadows_crown:shard_06", 2880, 680),
            ("shadows_crown:shard_07", 3380, 680),
            ("shadows_crown:shard_08", 3910, 595),
            ("shadows_crown:shard_09", 4450, 740),
            ("shadows_crown:shard_10", 4850, 610),
            ("shadows_crown:shard_11", 4950, 750),
        ),
        enemies=(
            ("shadows_crown:bat_01", 630, 630, 480, 900),
            ("shadows_crown:imp_01", 1420, 700, 1320, 1800),
            ("shadows_crown:bat_02", 2100, 710, 1920, 2360),
            ("shadows_crown:imp_02", 2860, 710, 2780, 3280),
            ("shadows_crown:bat_03", 3500, 710, 3400, 3900),
            ("shadows_crown:imp_03", 4050, 790, 3950, 4400),
            ("shadows_crown:bat_04", 4650, 670, 4550, 4850),
            ("shadows_crown:imp_04", 4950, 680, 4850, 5000),
        ),
        checkpoints=(
            ("shadows_crown:checkpoint_01", 1320, 750, 1310, 760),
        ),
        exit_gate=(4880, 728, 72, 102),
    ),
)
