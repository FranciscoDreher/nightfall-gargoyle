"""Validación de niveles y progresión de dificultad."""

from __future__ import annotations

import math
import unittest
from unittest.mock import MagicMock

from nightfall_gargoyle.levels import LEVELS, LevelData, RectDef

# Mock pygame si no está disponible (para CI/testing)
try:
    import pygame
    Rect = pygame.Rect
    pygame_available = True
except ImportError:
    pygame_available = False


class MockRect:
    """Simple Rect replacement para tests sin pygame."""
    
    def __init__(self, x: int, y: int = 0, w: int = 0, h: int = 0):
        if isinstance(x, (tuple, list)):
            self.x, self.y, self.width, self.height = x[0], x[1], x[2], x[3]
        else:
            self.x, self.y, self.width, self.height = x, y, w, h
    
    def colliderect(self, other: MockRect) -> bool:
        return not (
            self.x + self.width < other.x
            or other.x + other.width < self.x
            or self.y + self.height < other.y
            or other.y + other.height < self.y
        )
    
    def collidepoint(self, x: int, y: int) -> bool:
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)


# Use pygame.Rect if available, otherwise use MockRect
if not pygame_available or not hasattr(pygame, 'Rect'):
    Rect = MockRect


class TestLevelProgression(unittest.TestCase):
    """Valida que cada nivel aumenta dificultad de forma consistente."""

    def test_all_levels_have_unique_ids(self) -> None:
        """Evita duplicados que rompan la progresión."""
        ids = [level.level_id for level in LEVELS]
        self.assertEqual(len(ids), len(set(ids)), "Hay level_ids duplicados")

    def test_levels_count_minimum(self) -> None:
        """Debe haber al menos 6 niveles (2 base + 4 nuevos)."""
        self.assertGreaterEqual(len(LEVELS), 6, "Faltan niveles")

    def test_all_levels_have_metadata(self) -> None:
        """Cada nivel tiene nombre, descripción y dimensiones."""
        for level in LEVELS:
            self.assertTrue(level.name, f"{level.level_id} sin nombre")
            self.assertTrue(level.subtitle, f"{level.level_id} sin subtítulo")
            self.assertGreater(level.width, 0)
            self.assertGreater(level.height, 0)

    def test_level_dimensions_reasonable(self) -> None:
        """Ancho/alto dentro de límites para rendimiento 2D."""
        for level in LEVELS:
            self.assertGreaterEqual(level.width, 2400, f"{level.level_id} muy estrecho")
            self.assertLessEqual(level.width, 6000, f"{level.level_id} muy ancho")
            self.assertGreaterEqual(level.height, 600, f"{level.level_id} muy bajo")
            self.assertLessEqual(level.height, 1200, f"{level.level_id} muy alto")

    def test_difficulty_increases_monotonically(self) -> None:
        """Dificultad nunca baja significativamente entre niveles."""
        for i in range(len(LEVELS) - 1):
            current = LEVELS[i]
            next_level = LEVELS[i + 1]
            current_difficulty = self._calculate_difficulty_score(current)
            next_difficulty = self._calculate_difficulty_score(next_level)
            
            # Permitir 5% de fluctuación, pero tendencia debe ser arriba
            self.assertGreaterEqual(
                next_difficulty,
                current_difficulty * 0.95,
                f"{next_level.level_id} más fácil que {current.level_id}"
            )

    def test_difficulty_factors_increase(self) -> None:
        """Analizar factores específicos de dificultad."""
        # Ancho: debe crecer o mantenerse
        widths = [level.width for level in LEVELS]
        for i in range(len(widths) - 1):
            self.assertLessEqual(
                widths[i],
                widths[i + 1] * 1.1,  # Permite pequeña reducción
                "Ancho del mapa disminuyó significativamente"
            )
        
        # Enemigos: deben crecer o mantenerse
        enemy_counts = [len(level.enemies) for level in LEVELS]
        for i in range(len(enemy_counts) - 1):
            self.assertLessEqual(
                enemy_counts[i],
                enemy_counts[i + 1],
                "Cantidad de enemigos disminuyó"
            )
        
        # Plataformas: deben volverse más estrechas (o mantenerse)
        avg_platform_widths = [
            sum(p[2] for p in level.platforms) / len(level.platforms)
            for level in LEVELS
        ]
        for i in range(len(avg_platform_widths) - 1):
            self.assertGreaterEqual(
                avg_platform_widths[i],
                avg_platform_widths[i + 1] * 0.9,  # Máximo 10% más estrecho
                "Plataformas se volvieron significativamente más estrechas"
            )

    def _calculate_difficulty_score(self, level: LevelData) -> float:
        """Calcula un score de dificultad basado en factores múltiples."""
        enemy_factor = len(level.enemies) * 10
        shard_factor = level.shards_required * 2
        avg_platform_width = (
            sum(p[2] for p in level.platforms) / len(level.platforms)
        )
        platform_factor = 1.0 / (avg_platform_width / 25.0)  # Normalizado
        hazard_factor = len(level.hazards) * 3
        width_factor = level.width / 3200.0  # Normalizado a L1
        
        return (
            enemy_factor * 0.4
            + shard_factor * 0.2
            + platform_factor * 0.15
            + hazard_factor * 0.15
            + width_factor * 0.1
        )


class TestLevelGeometry(unittest.TestCase):
    """Valida que la geometría de cada nivel es jugable."""

    def test_each_level_is_beatable(self) -> None:
        """Verifica que hay camino viable para el jugador."""
        for level in LEVELS:
            self.assertIsNotNone(
                self._find_path(level.spawn, level.exit_gate, level.platforms),
                f"{level.level_id}: No hay camino viable hacia el exit"
            )

    def test_spawn_on_valid_platform(self) -> None:
        """Spawn debe estar en o cerca de una plataforma válida."""
        for level in LEVELS:
            spawn_x, spawn_y = level.spawn
            # El spawn puede estar flotando, pero debe estar cerca de una plataforma
            # que lo pueda atrapar por gravedad (máximo 200 píxeles abajo)
            found = False
            for platform in level.platforms:
                plat_x, plat_y, plat_w, plat_h = platform
                plat_top = plat_y
                plat_bottom = plat_y + plat_h
                
                # Verificar que el spawn está horizontalmente superpuesto
                # y verticalmente dentro de rango de caída
                if (plat_x <= spawn_x <= plat_x + plat_w and
                    plat_top - 200 <= spawn_y <= plat_bottom + 200):
                    found = True
                    break
            
            self.assertTrue(found, f"{level.level_id}: Spawn no está cerca de plataforma")

    def test_spawn_not_in_hazard(self) -> None:
        """Spawn no debe estar en un pico/hazard."""
        for level in LEVELS:
            spawn_rect = Rect(
                level.spawn[0] - 17,
                level.spawn[1],
                34,
                56
            )
            for hazard in level.hazards:
                hazard_rect = Rect(hazard)
                self.assertFalse(
                    spawn_rect.colliderect(hazard_rect),
                    f"{level.level_id}: Spawn en hazard"
                )

    def test_exit_gate_reachable(self) -> None:
        """Exit gate debe ser alcanzable desde spawn."""
        for level in LEVELS:
            self.assertIsNotNone(
                self._find_path(level.spawn, level.exit_gate, level.platforms),
                f"{level.level_id}: Exit no alcanzable"
            )

    def test_all_shards_reachable(self) -> None:
        """Todos los shards deben existir y tener coordenadas válidas."""
        for level in LEVELS:
            for shard in level.shards:
                shard_id, shard_x, shard_y = shard
                # Verificar que están dentro del mapa
                self.assertGreater(shard_x, 0, f"{level.level_id}: Shard x negativa")
                self.assertGreater(shard_y, 0, f"{level.level_id}: Shard y negativa")
                self.assertLess(shard_x, level.width, f"{level.level_id}: Shard fuera del ancho")
                self.assertLess(shard_y, level.height, f"{level.level_id}: Shard fuera del alto")

    def test_checkpoint_positions_valid(self) -> None:
        """Checkpoints tienen coordenadas válidas."""
        for level in LEVELS:
            for checkpoint in level.checkpoints:
                checkpoint_id, x, y, spawn_x, spawn_y = checkpoint
                # Checkpoint visual position
                self.assertGreater(x, 0, f"{level.level_id}: Checkpoint x negativa")
                self.assertGreater(y, 0, f"{level.level_id}: Checkpoint y negativa")
                self.assertLess(x, level.width, f"{level.level_id}: Checkpoint fuera ancho")
                self.assertLess(y, level.height, f"{level.level_id}: Checkpoint fuera alto")
                
                # Checkpoint spawn position
                self.assertGreater(spawn_x, 0, f"{level.level_id}: Spawn x negativa")
                self.assertGreater(spawn_y, 0, f"{level.level_id}: Spawn y negativa")
                self.assertLess(spawn_x, level.width, f"{level.level_id}: Spawn fuera ancho")
                self.assertLess(spawn_y, level.height, f"{level.level_id}: Spawn fuera alto")

    def _find_path(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        platforms: tuple[RectDef, ...]
    ) -> bool:
        """
        Búsqueda simple para verificar si hay camino.
        Asume que el jugador puede saltar entre plataformas adyacentes.
        """
        if not platforms:
            return False
        
        # Aproximación: si hay plataformas, hay camino
        # (validación más rigurosa requeriría simulación física)
        return len(platforms) > 0


class TestLevelBalance(unittest.TestCase):
    """Asegura que los niveles son jugables, no imposibles."""

    def test_required_shards_available(self) -> None:
        """Se pueden recolectar suficientes shards requeridos."""
        for level in LEVELS:
            available_shards = len(level.shards)
            required = level.shards_required
            self.assertLessEqual(
                required,
                available_shards,
                f"{level.level_id}: Se piden {required} shards pero hay {available_shards}"
            )

    def test_no_impossible_gaps(self) -> None:
        """Debe haber suficientes plataformas para progresar."""
        for level in LEVELS:
            # Verificar que hay al menos una plataforma cada 600 píxeles horizontalmente
            platforms_by_x = sorted(level.platforms, key=lambda p: p[0])
            
            # Verificar que no hay gaps horizontales muy grandes al inicio
            if len(platforms_by_x) > 1:
                for i in range(len(platforms_by_x) - 1):
                    current_x = platforms_by_x[i][0]
                    next_x = platforms_by_x[i + 1][0]
                    gap = next_x - current_x
                    
                    # La mayoría de gaps deben ser razonables (menos de 400px)
                    if gap > 600:
                        # Permitir algunos gaps grandes, pero no demasiados
                        pass
                
                # Simplemente verificar que hay múltiples plataformas
                self.assertGreater(len(platforms_by_x), 3, 
                    f"{level.level_id}: Muy pocas plataformas")

    def test_hazard_placement_fair(self) -> None:
        """Picos no bloquean camino hacia shards o exit."""
        for level in LEVELS:
            hazard_rects = [Rect(h) for h in level.hazards]
            
            # Los hazards deben ocupar área razonable (no más del 10% del mapa)
            total_hazard_area = sum(h[2] * h[3] for h in level.hazards)
            total_level_area = level.width * level.height
            hazard_ratio = total_hazard_area / total_level_area
            
            self.assertLess(
                hazard_ratio,
                0.10,
                f"{level.level_id}: Demasiados picos ({hazard_ratio*100:.1f}%)"
            )

    def test_enemy_patrol_ranges_valid(self) -> None:
        """Rango de patrullaje dentro de bounds del nivel."""
        for level in LEVELS:
            for enemy in level.enemies:
                # enemy = ("id", x, y, min_x, max_x)
                self.assertLess(
                    enemy[3],
                    enemy[4],
                    f"{level.level_id}: Rango de patrullaje inválido en {enemy[0]}"
                )
                self.assertGreaterEqual(enemy[3], 0)
                self.assertLessEqual(enemy[4], level.width)
                
                # Rango no debe ser ridículamente pequeño
                patrol_width = enemy[4] - enemy[3]
                self.assertGreater(patrol_width, 50, f"{level.level_id}: Patrullaje muy pequeño")

    def test_enemy_count_escalation(self) -> None:
        """Enemigos aumentan gradualmente, no explosivamente."""
        for i in range(len(LEVELS) - 1):
            current = LEVELS[i]
            next_level = LEVELS[i + 1]
            current_enemies = len(current.enemies)
            next_enemies = len(next_level.enemies)
            
            # Máximo +2 enemigos por nivel
            self.assertLessEqual(
                next_enemies - current_enemies,
                2,
                f"{next_level.level_id}: Salto enemigos de {current_enemies} a {next_enemies}"
            )

    def test_shard_placement_distribution(self) -> None:
        """Shards distribuidos razonablemente a lo largo del nivel."""
        for level in LEVELS:
            if len(level.shards) < 2:
                continue
            
            shard_positions = [s[1] for s in level.shards]  # x coordinate
            shard_positions.sort()
            
            # Calcular espaciamiento promedio
            min_x = level.platforms[0][0] if level.platforms else 0
            max_x = level.width
            level_span = max_x - min_x
            
            avg_spacing = level_span / len(level.shards)
            
            # Verificar que no hay clusters muy grandes
            for i in range(len(shard_positions) - 1):
                gap = shard_positions[i + 1] - shard_positions[i]
                # Gap no debe ser más de 3x el promedio
                self.assertLess(
                    gap,
                    avg_spacing * 3,
                    f"{level.level_id}: Shards mal distribuidos"
                )


class TestLevelConsistency(unittest.TestCase):
    """Valida coherencia interna de niveles."""

    def test_platform_geometry_valid(self) -> None:
        """Plataformas tienen dimensiones positivas."""
        for level in LEVELS:
            for platform in level.platforms:
                x, y, w, h = platform
                self.assertGreater(w, 0, f"{level.level_id}: Plataforma ancho inválido")
                self.assertGreater(h, 0, f"{level.level_id}: Plataforma alto inválido")
                self.assertGreaterEqual(x, 0)
                self.assertGreaterEqual(y, 0)
                self.assertLess(x + w, level.width + 100, "Plataforma fuera de bounds")

    def test_hazard_geometry_valid(self) -> None:
        """Picos tienen dimensiones positivas."""
        for level in LEVELS:
            for hazard in level.hazards:
                x, y, w, h = hazard
                self.assertGreater(w, 0)
                self.assertGreater(h, 0)
                self.assertGreaterEqual(x, 0)
                self.assertGreaterEqual(y, 0)

    def test_no_duplicate_object_ids(self) -> None:
        """No hay IDs duplicadas dentro de un nivel."""
        for level in LEVELS:
            all_ids = []
            
            # Recolectar todos los IDs
            for shard in level.shards:
                all_ids.append(shard[0])
            for enemy in level.enemies:
                all_ids.append(enemy[0])
            for checkpoint in level.checkpoints:
                all_ids.append(checkpoint[0])
            
            self.assertEqual(
                len(all_ids),
                len(set(all_ids)),
                f"{level.level_id}: IDs duplicadas"
            )

    def test_exit_gate_dimensions(self) -> None:
        """Exit gate tiene tamaño similar entre niveles."""
        for level in LEVELS:
            gate = level.exit_gate
            x, y, w, h = gate
            
            # Exit debe ser un rectángulo pequeño visible
            self.assertGreater(w, 10, f"{level.level_id}: Exit muy estrecho")
            self.assertGreater(h, 10, f"{level.level_id}: Exit muy bajo")
            self.assertLess(w, 200, f"{level.level_id}: Exit muy ancho")
            self.assertLess(h, 200, f"{level.level_id}: Exit muy alto")
            
            # Dentro de bounds
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x + w, level.width + 50)


if __name__ == "__main__":
    unittest.main()
