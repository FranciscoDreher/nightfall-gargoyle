"""Juego principal de plataformas 2D/2.5D inspirado en clásicos góticos de mascota."""

from __future__ import annotations

from dataclasses import dataclass
import math
import sys
from typing import Iterable

try:
    import pygame
except ImportError as exc:  # pragma: no cover - mensaje útil en máquinas sin dependencia
    raise SystemExit(
        "Pygame no está instalado. Ejecuta: python -m pip install -e ."
    ) from exc

from .levels import LEVELS, CheckpointDef, EnemyDef, LevelData, RectDef, ShardDef
from .persistence import MAX_HEALTH, SaveState, load_save, new_save, reset_save, write_save
from .settings import (
    APP_NAME,
    FPS,
    LOGICAL_HEIGHT,
    LOGICAL_SIZE,
    LOGICAL_WIDTH,
    RESOLUTION_PRESETS,
    GameConfig,
    load_config,
    save_config,
)

Vec2 = pygame.Vector2

SKY_TOP = (19, 18, 42)
SKY_BOTTOM = (50, 31, 76)
INK = (18, 18, 28)
STONE = (80, 76, 92)
STONE_LIGHT = (116, 109, 130)
STONE_DARK = (40, 37, 52)
MOON = (238, 230, 188)
GOLD = (255, 206, 92)
CYAN = (91, 220, 255)
PINK = (245, 97, 170)
GREEN = (98, 222, 132)
RED = (235, 80, 88)
WHITE = (244, 240, 232)
MUTED = (170, 164, 184)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def format_time(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def level_prefix(level: LevelData) -> str:
    return f"{level.level_id}:"


def inflate_rect(rect: pygame.Rect, amount: int) -> pygame.Rect:
    return rect.inflate(amount, amount)


@dataclass(slots=True)
class Toast:
    text: str
    timer: float
    color: tuple[int, int, int] = GOLD


class Player:
    WIDTH = 34
    HEIGHT = 56
    ACCEL = 0.72
    MAX_SPEED = 5.6
    FRICTION = 0.82
    GRAVITY = 0.62
    MAX_FALL = 15.5
    JUMP = -12.4
    DOUBLE_JUMP = -11.2

    def __init__(self, spawn: tuple[float, float], health: int = MAX_HEALTH, lives: int = 3) -> None:
        self.pos = Vec2(spawn)
        self.vel = Vec2(0, 0)
        self.rect = pygame.Rect(round(spawn[0]), round(spawn[1]), self.WIDTH, self.HEIGHT)
        self.health = health
        self.lives = lives
        self.facing = 1
        self.on_ground = False
        self.double_jump_ready = True
        self.attack_timer = 0.0
        self.attack_cooldown = 0.0
        self.invulnerable_timer = 0.0
        self.step_phase = 0.0

    def update(
        self,
        dt: float,
        keys: pygame.key.ScancodeWrapper,
        jump_pressed: bool,
        attack_pressed: bool,
        platforms: Iterable[pygame.Rect],
    ) -> None:
        frame = dt * FPS
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        if left and not right:
            self.vel.x -= self.ACCEL * frame
            self.facing = -1
        elif right and not left:
            self.vel.x += self.ACCEL * frame
            self.facing = 1
        else:
            self.vel.x *= self.FRICTION ** frame
            if abs(self.vel.x) < 0.05:
                self.vel.x = 0

        self.vel.x = clamp(self.vel.x, -self.MAX_SPEED, self.MAX_SPEED)

        if jump_pressed:
            if self.on_ground:
                self.vel.y = self.JUMP
                self.on_ground = False
                self.double_jump_ready = True
            elif self.double_jump_ready:
                self.vel.y = self.DOUBLE_JUMP
                self.double_jump_ready = False

        if attack_pressed and self.attack_cooldown <= 0:
            self.attack_timer = 0.2
            self.attack_cooldown = 0.42

        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        self.vel.y = min(self.MAX_FALL, self.vel.y + self.GRAVITY * frame)
        self._move_and_collide(frame, list(platforms))
        if self.on_ground and abs(self.vel.x) > 0.15:
            self.step_phase += abs(self.vel.x) * dt * 6

    def _move_and_collide(self, frame: float, platforms: list[pygame.Rect]) -> None:
        self.pos.x += self.vel.x * frame
        self.rect.x = round(self.pos.x)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.x > 0:
                    self.rect.right = platform.left
                elif self.vel.x < 0:
                    self.rect.left = platform.right
                self.pos.x = self.rect.x
                self.vel.x = 0

        self.pos.y += self.vel.y * frame
        self.rect.y = round(self.pos.y)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.y > 0:
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.double_jump_ready = True
                elif self.vel.y < 0:
                    self.rect.top = platform.bottom
                self.pos.y = self.rect.y
                self.vel.y = 0

    def attack_rect(self) -> pygame.Rect:
        if self.attack_timer <= 0:
            return pygame.Rect(0, 0, 0, 0)
        if self.facing > 0:
            return pygame.Rect(self.rect.right - 2, self.rect.y + 12, 42, 28)
        return pygame.Rect(self.rect.left - 40, self.rect.y + 12, 42, 28)

    def damage(self, source_x: float) -> bool:
        if self.invulnerable_timer > 0:
            return False
        self.health -= 1
        self.invulnerable_timer = 1.15
        self.vel.x = -6.0 if source_x > self.rect.centerx else 6.0
        self.vel.y = -8.0
        return True

    def draw(self, surface: pygame.Surface, camera: Vec2) -> None:
        r = self.rect.move(-camera.x, -camera.y)
        blink = self.invulnerable_timer > 0 and int(self.invulnerable_timer * 16) % 2 == 0
        if blink:
            return

        shadow = pygame.Rect(r.centerx - 21, r.bottom - 6, 42, 10)
        pygame.draw.ellipse(surface, (0, 0, 0, 80), shadow)

        wing_wave = math.sin(self.step_phase) * 4
        left_wing = [(r.centerx, r.y + 18), (r.x - 20, r.y + 16 + wing_wave), (r.x + 4, r.y + 35)]
        right_wing = [(r.centerx, r.y + 18), (r.right + 20, r.y + 16 - wing_wave), (r.right - 4, r.y + 35)]
        pygame.draw.polygon(surface, (54, 44, 78), left_wing)
        pygame.draw.polygon(surface, (54, 44, 78), right_wing)

        body = pygame.Rect(r.x + 5, r.y + 12, r.w - 10, r.h - 8)
        pygame.draw.rect(surface, (101, 83, 142), body, border_radius=11)
        pygame.draw.rect(surface, (48, 39, 72), body, 2, border_radius=11)
        head = pygame.Rect(r.x + 2, r.y + 2, r.w - 4, 28)
        pygame.draw.ellipse(surface, (124, 102, 170), head)
        pygame.draw.polygon(surface, (124, 102, 170), [(r.x + 7, r.y + 8), (r.x + 2, r.y - 6), (r.x + 16, r.y + 3)])
        pygame.draw.polygon(surface, (124, 102, 170), [(r.right - 7, r.y + 8), (r.right - 2, r.y - 6), (r.right - 16, r.y + 3)])
        eye_y = r.y + 14
        if self.facing > 0:
            pygame.draw.circle(surface, GOLD, (r.x + 22, eye_y), 3)
            pygame.draw.circle(surface, GOLD, (r.x + 29, eye_y), 3)
        else:
            pygame.draw.circle(surface, GOLD, (r.x + 6, eye_y), 3)
            pygame.draw.circle(surface, GOLD, (r.x + 13, eye_y), 3)

        if self.attack_timer > 0:
            slash = self.attack_rect().move(-camera.x, -camera.y)
            pygame.draw.ellipse(surface, (255, 225, 120), slash, 3)
            pygame.draw.ellipse(surface, (255, 255, 225), slash.inflate(-8, -10), 1)


class Enemy:
    def __init__(self, data: EnemyDef) -> None:
        self.enemy_id, x, y, left, right = data
        self.rect = pygame.Rect(x, y, 38, 40)
        self.min_x = left
        self.max_x = right
        self.direction = 1
        self.speed = 1.35
        self.alive = True
        self.phase = 0.0

    def update(self, dt: float) -> None:
        frame = dt * FPS
        self.phase += dt * 5
        self.rect.x += round(self.direction * self.speed * frame)
        if self.rect.left < self.min_x:
            self.rect.left = self.min_x
            self.direction = 1
        elif self.rect.right > self.max_x:
            self.rect.right = self.max_x
            self.direction = -1

    def draw(self, surface: pygame.Surface, camera: Vec2) -> None:
        r = self.rect.move(-camera.x, -camera.y)
        bob = int(math.sin(self.phase) * 3)
        body = pygame.Rect(r.x, r.y + bob, r.w, r.h)
        color = (112, 48, 92) if "imp" in self.enemy_id else (70, 75, 132)
        pygame.draw.ellipse(surface, color, body)
        pygame.draw.ellipse(surface, (35, 26, 48), body, 2)
        pygame.draw.polygon(surface, color, [(body.x + 7, body.y + 8), (body.x + 1, body.y - 8), (body.x + 16, body.y + 3)])
        pygame.draw.polygon(surface, color, [(body.right - 7, body.y + 8), (body.right - 1, body.y - 8), (body.right - 16, body.y + 3)])
        pygame.draw.circle(surface, RED, (body.x + 13, body.y + 18), 3)
        pygame.draw.circle(surface, RED, (body.x + 25, body.y + 18), 3)


class Shard:
    def __init__(self, data: ShardDef) -> None:
        self.shard_id, x, y = data
        self.rect = pygame.Rect(x, y, 24, 24)
        self.phase = (x + y) * 0.02

    def draw(self, surface: pygame.Surface, camera: Vec2, time_value: float) -> None:
        r = self.rect.move(-camera.x, -camera.y)
        y = r.y + int(math.sin(time_value * 4 + self.phase) * 5)
        cx, cy = r.centerx, y + 12
        points = [(cx, cy - 16), (cx + 12, cy), (cx, cy + 16), (cx - 12, cy)]
        pygame.draw.polygon(surface, CYAN, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
        pygame.draw.circle(surface, (118, 255, 255), (cx, cy), 5)


class Checkpoint:
    def __init__(self, data: CheckpointDef) -> None:
        self.checkpoint_id, x, y, spawn_x, spawn_y = data
        self.rect = pygame.Rect(x, y, 34, 84)
        self.spawn = (float(spawn_x), float(spawn_y))

    def draw(self, surface: pygame.Surface, camera: Vec2, active: bool, time_value: float) -> None:
        r = self.rect.move(-camera.x, -camera.y)
        pygame.draw.rect(surface, (50, 43, 62), (r.centerx - 4, r.y + 22, 8, 62), border_radius=3)
        pygame.draw.circle(surface, GOLD if active else MUTED, (r.centerx, r.y + 22), 11)
        glow = 16 + int(math.sin(time_value * 5) * 4)
        if active:
            pygame.draw.circle(surface, (255, 214, 112), (r.centerx, r.y + 22), glow, 2)
        pygame.draw.rect(surface, STONE_DARK, (r.centerx - 15, r.bottom - 5, 30, 8), border_radius=4)


class Gate:
    def __init__(self, rect_def: RectDef) -> None:
        self.rect = pygame.Rect(rect_def)

    def draw(self, surface: pygame.Surface, camera: Vec2, open_gate: bool, time_value: float) -> None:
        r = self.rect.move(-camera.x, -camera.y)
        frame_color = GOLD if open_gate else STONE_LIGHT
        pygame.draw.rect(surface, frame_color, r.inflate(12, 10), border_radius=18)
        pygame.draw.rect(surface, STONE_DARK, r.inflate(4, 2), border_radius=14)
        inner = r.inflate(-10, -10)
        portal_color = (80, 220, 255) if open_gate else (74, 58, 90)
        pygame.draw.ellipse(surface, portal_color, inner)
        if open_gate:
            for index in range(3):
                radius = 18 + index * 12 + int(math.sin(time_value * 3 + index) * 4)
                pygame.draw.ellipse(surface, WHITE, inner.inflate(-radius, -radius), 1)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(APP_NAME)
        self.config = load_config()
        self.window = self._create_window()
        self.surface = pygame.Surface(LOGICAL_SIZE).convert_alpha()
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font(None, 70)
        self.font_medium = pygame.font.Font(None, 38)
        self.font_small = pygame.font.Font(None, 25)
        self.font_tiny = pygame.font.Font(None, 20)

        self.running = True
        self.state = "menu"
        self.menu_index = 0
        self.pause_index = 0
        self.options_index = 0
        self.options_return_state = "menu"
        self.resolution_index = self._resolution_index()
        self.toasts: list[Toast] = []
        self.time_value = 0.0

        self.save_state: SaveState = load_save() or new_save(checkpoint=LEVELS[0].spawn)
        self.level_index = clamp(self.save_state.current_level, 0, len(LEVELS) - 1)
        self.level = LEVELS[int(self.level_index)]
        self.player = Player(self.level.spawn)
        self.platforms: list[pygame.Rect] = []
        self.hazards: list[pygame.Rect] = []
        self.shards: list[Shard] = []
        self.enemies: list[Enemy] = []
        self.checkpoints: list[Checkpoint] = []
        self.gate = Gate(self.level.exit_gate)
        self.camera = Vec2(0, 0)
        self.load_level(int(self.level_index), self.save_state.checkpoint)

    def _create_window(self) -> pygame.Surface:
        flags = pygame.FULLSCREEN if self.config.fullscreen else pygame.RESIZABLE
        try:
            return pygame.display.set_mode(self.config.window_size, flags, vsync=1 if self.config.vsync else 0)
        except TypeError:  # pygame antiguo sin argumento vsync
            return pygame.display.set_mode(self.config.window_size, flags)

    def _resolution_index(self) -> int:
        size = self.config.window_size
        if size in RESOLUTION_PRESETS:
            return RESOLUTION_PRESETS.index(size)
        return 1

    def run(self) -> None:
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self.time_value += dt
            actions = {"jump": False, "attack": False}
            for event in pygame.event.get():
                self.handle_event(event, actions)

            self.update(dt, actions)
            self.draw()
            self.present()

        pygame.quit()

    def handle_event(self, event: pygame.event.Event, actions: dict[str, bool]) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.VIDEORESIZE and not self.config.fullscreen:
            self.config.width = max(640, event.w)
            self.config.height = max(360, event.h)
            save_config(self.config)
            return
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_F11:
            self.config.fullscreen = not self.config.fullscreen
            save_config(self.config)
            self.window = self._create_window()
            return

        if self.state == "menu":
            self.handle_menu_key(event.key)
        elif self.state == "options":
            self.handle_options_key(event.key)
        elif self.state == "playing":
            self.handle_playing_key(event.key, actions)
        elif self.state == "pause":
            self.handle_pause_key(event.key)
        elif self.state in {"game_over", "victory"}:
            self.handle_end_key(event.key)

    def handle_menu_key(self, key: int) -> None:
        items = self.menu_items()
        if key in {pygame.K_DOWN, pygame.K_s}:
            self.menu_index = (self.menu_index + 1) % len(items)
        elif key in {pygame.K_UP, pygame.K_w}:
            self.menu_index = (self.menu_index - 1) % len(items)
        elif key in {pygame.K_RETURN, pygame.K_SPACE}:
            selected = items[self.menu_index]
            if selected == "Nueva partida":
                self.start_new_game()
            elif selected == "Continuar":
                self.continue_game()
            elif selected == "Opciones":
                self.options_return_state = "menu"
                self.state = "options"
            elif selected == "Salir":
                self.running = False

    def handle_options_key(self, key: int) -> None:
        items_count = 5
        if key in {pygame.K_ESCAPE, pygame.K_BACKSPACE}:
            self.state = self.options_return_state
            return
        if key in {pygame.K_DOWN, pygame.K_s}:
            self.options_index = (self.options_index + 1) % items_count
        elif key in {pygame.K_UP, pygame.K_w}:
            self.options_index = (self.options_index - 1) % items_count
        elif key in {pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a, pygame.K_RETURN, pygame.K_SPACE}:
            direction = -1 if key in {pygame.K_LEFT, pygame.K_a} else 1
            if self.options_index == 0:
                self.resolution_index = (self.resolution_index + direction) % len(RESOLUTION_PRESETS)
                self.config.width, self.config.height = RESOLUTION_PRESETS[self.resolution_index]
                save_config(self.config)
                self.window = self._create_window()
            elif self.options_index == 1:
                self.config.fullscreen = not self.config.fullscreen
                save_config(self.config)
                self.window = self._create_window()
            elif self.options_index == 2:
                self.config.master_volume = clamp(self.config.master_volume + 0.1 * direction, 0.0, 1.0)
                save_config(self.config)
            elif self.options_index == 3 and key in {pygame.K_RETURN, pygame.K_SPACE}:
                reset_save()
                self.save_state = new_save(checkpoint=LEVELS[0].spawn)
                self.load_level(0, LEVELS[0].spawn)
                self.options_return_state = "menu"
                self.add_toast("Partida guardada borrada", RED)
            elif self.options_index == 4:
                self.state = self.options_return_state

    def handle_playing_key(self, key: int, actions: dict[str, bool]) -> None:
        if key in {pygame.K_ESCAPE, pygame.K_p}:
            self.state = "pause"
            return
        if key in {pygame.K_SPACE, pygame.K_UP, pygame.K_w}:
            actions["jump"] = True
        elif key in {pygame.K_e, pygame.K_j, pygame.K_LCTRL, pygame.K_RCTRL}:
            actions["attack"] = True
        elif key == pygame.K_F5:
            self.save_progress("Partida guardada")
        elif key == pygame.K_F9:
            self.continue_game()

    def handle_pause_key(self, key: int) -> None:
        items = ["Continuar", "Guardar partida", "Opciones", "Menú principal"]
        if key in {pygame.K_ESCAPE, pygame.K_p}:
            self.state = "playing"
        elif key in {pygame.K_DOWN, pygame.K_s}:
            self.pause_index = (self.pause_index + 1) % len(items)
        elif key in {pygame.K_UP, pygame.K_w}:
            self.pause_index = (self.pause_index - 1) % len(items)
        elif key in {pygame.K_RETURN, pygame.K_SPACE}:
            selected = items[self.pause_index]
            if selected == "Continuar":
                self.state = "playing"
            elif selected == "Guardar partida":
                self.save_progress("Partida guardada")
                self.state = "playing"
            elif selected == "Opciones":
                self.options_return_state = "pause"
                self.state = "options"
            elif selected == "Menú principal":
                self.save_progress("Partida guardada")
                self.state = "menu"

    def handle_end_key(self, key: int) -> None:
        if key in {pygame.K_RETURN, pygame.K_SPACE}:
            self.start_new_game()
        elif key == pygame.K_ESCAPE:
            self.state = "menu"

    def update(self, dt: float, actions: dict[str, bool]) -> None:
        for toast in self.toasts:
            toast.timer -= dt
        self.toasts = [toast for toast in self.toasts if toast.timer > 0]

        if self.state != "playing":
            return

        self.save_state.play_time_seconds += dt
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, actions["jump"], actions["attack"], self.platforms)
        self.update_enemies(dt)
        self.collect_shards()
        self.update_checkpoints()
        self.update_gate()
        self.update_hazards()
        self.update_camera(dt)

        if self.player.rect.top > self.level.height + 260:
            self.lose_life("Caíste al vacío")

    def update_enemies(self, dt: float) -> None:
        attack = self.player.attack_rect()
        for enemy in list(self.enemies):
            enemy.update(dt)
            if attack.width and attack.colliderect(enemy.rect):
                self.defeat_enemy(enemy)
                continue
            stomping = self.player.vel.y > 0 and self.player.rect.bottom - enemy.rect.top < 18
            if self.player.rect.colliderect(enemy.rect):
                if stomping:
                    self.defeat_enemy(enemy)
                    self.player.vel.y = -8.5
                elif self.player.damage(enemy.rect.centerx):
                    self.add_toast("¡Te golpearon!", RED)
                    if self.player.health <= 0:
                        self.lose_life("Sin energía")

    def defeat_enemy(self, enemy: Enemy) -> None:
        if enemy.enemy_id not in self.save_state.defeated_enemies:
            self.save_state.defeated_enemies.append(enemy.enemy_id)
        self.enemies.remove(enemy)
        self.add_toast("Guardián derrotado", GREEN)

    def collect_shards(self) -> None:
        for shard in list(self.shards):
            if inflate_rect(self.player.rect, 8).colliderect(shard.rect):
                if shard.shard_id not in self.save_state.collected_shards:
                    self.save_state.collected_shards.append(shard.shard_id)
                self.shards.remove(shard)
                self.add_toast("Fragmento lunar +1", CYAN)

    def update_checkpoints(self) -> None:
        for checkpoint in self.checkpoints:
            if self.player.rect.colliderect(checkpoint.rect):
                changed = checkpoint.checkpoint_id not in self.save_state.reached_checkpoints
                if checkpoint.checkpoint_id not in self.save_state.reached_checkpoints:
                    self.save_state.reached_checkpoints.append(checkpoint.checkpoint_id)
                    self.add_toast("Punto de control activado", GOLD)
                if self.save_state.checkpoint != checkpoint.spawn:
                    changed = True
                self.save_state.checkpoint = checkpoint.spawn
                self.save_state.health = self.player.health
                self.save_state.lives = self.player.lives
                self.save_state.current_level = int(self.level_index)
                if changed:
                    write_save(self.save_state)

    def update_hazards(self) -> None:
        for hazard in self.hazards:
            if self.player.rect.colliderect(hazard) and self.player.damage(hazard.centerx):
                self.add_toast("¡Cuidado con los picos!", RED)
                if self.player.health <= 0:
                    self.lose_life("Sin energía")

    def update_gate(self) -> None:
        if not self.player.rect.colliderect(self.gate.rect):
            return
        collected_here = self.level_shards_collected()
        if collected_here < self.level.shards_required:
            missing = self.level.shards_required - collected_here
            self.add_toast(f"Faltan {missing} fragmentos para abrir el portal", GOLD)
            return

        next_level = int(self.level_index) + 1
        if next_level >= len(LEVELS):
            self.save_progress("Reino salvado")
            self.state = "victory"
            return

        self.save_state.current_level = next_level
        self.save_state.unlocked_levels = max(self.save_state.unlocked_levels, next_level + 1)
        self.save_state.checkpoint = LEVELS[next_level].spawn
        self.save_state.health = MAX_HEALTH
        self.save_state.lives = self.player.lives
        write_save(self.save_state)
        self.load_level(next_level, LEVELS[next_level].spawn)
        self.add_toast("Nuevo distrito desbloqueado", GREEN)

    def update_camera(self, dt: float) -> None:
        target_x = self.player.rect.centerx - LOGICAL_WIDTH * 0.45
        target_y = self.player.rect.centery - LOGICAL_HEIGHT * 0.58
        max_x = max(0, self.level.width - LOGICAL_WIDTH)
        max_y = max(0, self.level.height - LOGICAL_HEIGHT)
        target_x = clamp(target_x, 0, max_x)
        target_y = clamp(target_y, 0, max_y)
        follow = min(1.0, dt * 7.5)
        self.camera.x += (target_x - self.camera.x) * follow
        self.camera.y += (target_y - self.camera.y) * follow

    def start_new_game(self) -> None:
        reset_save()
        self.save_state = new_save(checkpoint=LEVELS[0].spawn)
        write_save(self.save_state)
        self.load_level(0, LEVELS[0].spawn)
        self.state = "playing"
        self.add_toast("Nueva partida iniciada", GREEN)

    def continue_game(self) -> None:
        loaded = load_save()
        if not loaded:
            self.add_toast("No hay partida guardada; empezando una nueva", GOLD)
            self.start_new_game()
            return
        self.save_state = loaded
        level_index = int(clamp(self.save_state.current_level, 0, len(LEVELS) - 1))
        self.load_level(level_index, self.save_state.checkpoint)
        if self.save_state.lives <= 0:
            self.state = "game_over"
            self.add_toast("La partida guardada no tiene vidas", RED)
            return
        self.state = "playing"
        self.add_toast("Partida cargada", GREEN)

    def save_progress(self, message: str) -> None:
        self.save_state.current_level = int(self.level_index)
        self.save_state.health = self.player.health
        self.save_state.lives = self.player.lives
        write_save(self.save_state)
        self.add_toast(message, GREEN)

    def lose_life(self, reason: str) -> None:
        self.player.lives -= 1
        self.save_state.lives = self.player.lives
        if self.player.lives <= 0:
            self.state = "game_over"
            write_save(self.save_state)
            return
        self.save_state.health = MAX_HEALTH
        write_save(self.save_state)
        self.load_level(int(self.level_index), self.save_state.checkpoint)
        self.add_toast(f"{reason}. Vidas restantes: {self.save_state.lives}", RED)

    def load_level(self, level_index: int, spawn: tuple[float, float] | None = None) -> None:
        self.level_index = int(clamp(level_index, 0, len(LEVELS) - 1))
        self.level = LEVELS[self.level_index]
        start = spawn or self.level.spawn
        self.platforms = [pygame.Rect(rect) for rect in self.level.platforms]
        self.hazards = [pygame.Rect(rect) for rect in self.level.hazards]
        self.shards = [Shard(data) for data in self.level.shards if data[0] not in self.save_state.collected_shards]
        self.enemies = [Enemy(data) for data in self.level.enemies if data[0] not in self.save_state.defeated_enemies]
        self.checkpoints = [Checkpoint(data) for data in self.level.checkpoints]
        self.gate = Gate(self.level.exit_gate)
        self.player = Player(start, health=self.save_state.health, lives=self.save_state.lives)
        self.camera = Vec2(
            clamp(self.player.rect.centerx - LOGICAL_WIDTH * 0.45, 0, max(0, self.level.width - LOGICAL_WIDTH)),
            clamp(self.player.rect.centery - LOGICAL_HEIGHT * 0.58, 0, max(0, self.level.height - LOGICAL_HEIGHT)),
        )

    def level_shards_collected(self) -> int:
        prefix = level_prefix(self.level)
        return sum(1 for shard_id in self.save_state.collected_shards if shard_id.startswith(prefix))

    def add_toast(self, text: str, color: tuple[int, int, int] = GOLD) -> None:
        if self.toasts and self.toasts[-1].text == text:
            self.toasts[-1].timer = 1.8
            return
        self.toasts.append(Toast(text, 1.8, color))
        self.toasts = self.toasts[-4:]

    def menu_items(self) -> list[str]:
        return ["Nueva partida", "Continuar", "Opciones", "Salir"]

    def draw(self) -> None:
        self.surface.fill(SKY_TOP)
        if self.state in {"playing", "pause"}:
            self.draw_world()
            self.draw_hud()
        elif self.state == "menu":
            self.draw_main_menu()
        elif self.state == "options":
            self.draw_options()
        elif self.state == "game_over":
            self.draw_world()
            self.draw_overlay("Fin de partida", "Enter: nueva partida  ·  Esc: menú", RED)
        elif self.state == "victory":
            self.draw_world()
            self.draw_overlay("¡Umbra está a salvo!", "Enter: jugar otra vez  ·  Esc: menú", GREEN)

        if self.state == "pause":
            self.draw_pause()
        self.draw_toasts()

    def draw_world(self) -> None:
        self.draw_background()
        self.draw_platforms()
        self.draw_hazards()
        for shard in self.shards:
            if self.is_visible(shard.rect):
                shard.draw(self.surface, self.camera, self.time_value)
        for checkpoint in self.checkpoints:
            active = checkpoint.checkpoint_id in self.save_state.reached_checkpoints
            if self.is_visible(checkpoint.rect):
                checkpoint.draw(self.surface, self.camera, active, self.time_value)
        self.gate.draw(self.surface, self.camera, self.level_shards_collected() >= self.level.shards_required, self.time_value)
        for enemy in self.enemies:
            if self.is_visible(enemy.rect):
                enemy.draw(self.surface, self.camera)
        self.player.draw(self.surface, self.camera)

    def draw_background(self) -> None:
        for y in range(LOGICAL_HEIGHT):
            ratio = y / LOGICAL_HEIGHT
            color = tuple(round(SKY_TOP[i] * (1 - ratio) + SKY_BOTTOM[i] * ratio) for i in range(3))
            pygame.draw.line(self.surface, color, (0, y), (LOGICAL_WIDTH, y))

        moon_x = int(760 - self.camera.x * 0.04)
        moon_y = 80
        pygame.draw.circle(self.surface, MOON, (moon_x, moon_y), 42)
        pygame.draw.circle(self.surface, SKY_TOP, (moon_x + 15, moon_y - 8), 40)

        for layer, color, speed, base_y, width in (
            (0, (29, 28, 50), 0.12, 365, 130),
            (1, (22, 22, 38), 0.22, 405, 105),
            (2, (15, 16, 30), 0.36, 448, 82),
        ):
            offset = int(-self.camera.x * speed) % width
            for x in range(-width, LOGICAL_WIDTH + width, width):
                bx = x + offset
                h = 80 + (x + layer * 37) % 70
                pygame.draw.rect(self.surface, color, (bx, base_y - h, width - 18, h))
                pygame.draw.polygon(
                    self.surface,
                    color,
                    [(bx + 12, base_y - h), (bx + 36, base_y - h - 36), (bx + 62, base_y - h)],
                )
                pygame.draw.rect(self.surface, (248, 196, 94), (bx + 28, base_y - h + 34, 8, 12))

    def draw_platforms(self) -> None:
        for platform in self.platforms:
            if not self.is_visible(platform):
                continue
            r = platform.move(-self.camera.x, -self.camera.y)
            pygame.draw.rect(self.surface, STONE_DARK, r.inflate(0, 7), border_radius=5)
            pygame.draw.rect(self.surface, STONE, r, border_radius=5)
            pygame.draw.rect(self.surface, STONE_LIGHT, (r.x, r.y, r.w, 7), border_radius=4)
            for x in range(r.x + 12, r.right, 42):
                pygame.draw.line(self.surface, STONE_DARK, (x, r.y + 8), (x - 18, r.bottom - 5), 1)

    def draw_hazards(self) -> None:
        for hazard in self.hazards:
            if not self.is_visible(hazard):
                continue
            r = hazard.move(-self.camera.x, -self.camera.y)
            pygame.draw.rect(self.surface, (72, 30, 42), r)
            for x in range(r.x, r.right, 18):
                pygame.draw.polygon(self.surface, RED, [(x, r.bottom), (x + 9, r.y - 18), (x + 18, r.bottom)])

    def draw_hud(self) -> None:
        pygame.draw.rect(self.surface, (14, 13, 25), (12, 12, 350, 78), border_radius=14)
        pygame.draw.rect(self.surface, (93, 82, 122), (12, 12, 350, 78), 2, border_radius=14)
        for index in range(MAX_HEALTH):
            x = 30 + index * 27
            color = RED if index < self.player.health else (64, 56, 72)
            pygame.draw.circle(self.surface, color, (x, 34), 9)
            pygame.draw.circle(self.surface, color, (x + 10, 34), 9)
            pygame.draw.polygon(self.surface, color, [(x - 8, 39), (x + 18, 39), (x + 5, 55)])

        shards_text = f"Fragmentos: {self.level_shards_collected()}/{self.level.shards_required}  ·  Total: {self.save_state.total_shards}"
        self.text(shards_text, (28, 62), self.font_small, CYAN)
        self.text(f"Vidas: {self.player.lives}", (235, 30), self.font_small, WHITE)

        title = f"{self.level.name}"
        self.text(title, (LOGICAL_WIDTH - 26, 22), self.font_small, WHITE, align="topright")
        self.text("F5 guardar · F9 cargar · F11 pantalla", (LOGICAL_WIDTH - 26, 49), self.font_tiny, MUTED, align="topright")

    def draw_main_menu(self) -> None:
        self.draw_menu_background()
        self.text("Nightfall", (LOGICAL_WIDTH // 2, 88), self.font_big, WHITE, align="center")
        self.text("Gargoyle", (LOGICAL_WIDTH // 2, 147), self.font_big, GOLD, align="center")
        self.text(
            "Plataformas gótico original · saltos, ataques, fragmentos y portales",
            (LOGICAL_WIDTH // 2, 205),
            self.font_small,
            MUTED,
            align="center",
        )
        for index, item in enumerate(self.menu_items()):
            y = 278 + index * 50
            selected = index == self.menu_index
            color = GOLD if selected else WHITE
            if selected:
                pygame.draw.rect(self.surface, (70, 57, 94), (LOGICAL_WIDTH // 2 - 155, y - 14, 310, 40), border_radius=13)
            self.text(item, (LOGICAL_WIDTH // 2, y), self.font_medium, color, align="center")
        self.text("W/S o ↑/↓ para navegar · Enter para elegir", (LOGICAL_WIDTH // 2, 500), self.font_small, MUTED, align="center")

    def draw_menu_background(self) -> None:
        self.camera = Vec2(math.sin(self.time_value * 0.25) * 80 + 300, 140)
        self.draw_background()
        for y in range(0, LOGICAL_HEIGHT, 34):
            alpha_color = (30 + y // 20, 25, 48 + y // 18)
            pygame.draw.line(self.surface, alpha_color, (0, y), (LOGICAL_WIDTH, y), 1)

    def draw_options(self) -> None:
        self.draw_menu_background()
        panel = pygame.Rect(LOGICAL_WIDTH // 2 - 250, 94, 500, 350)
        pygame.draw.rect(self.surface, (18, 17, 32), panel, border_radius=18)
        pygame.draw.rect(self.surface, (110, 95, 145), panel, 2, border_radius=18)
        self.text("Opciones", (LOGICAL_WIDTH // 2, 124), self.font_medium, GOLD, align="center")

        fullscreen = "Sí" if self.config.fullscreen else "No"
        options = [
            f"Resolución: {self.config.width} × {self.config.height}",
            f"Pantalla completa: {fullscreen}",
            f"Volumen maestro: {int(self.config.master_volume * 100)}%",
            "Borrar partida guardada",
            "Volver al menú",
        ]
        for index, item in enumerate(options):
            y = 185 + index * 48
            selected = index == self.options_index
            color = GOLD if selected else WHITE
            if selected:
                pygame.draw.rect(self.surface, (67, 54, 90), (panel.x + 35, y - 17, panel.w - 70, 38), border_radius=11)
            self.text(item, (LOGICAL_WIDTH // 2, y), self.font_small, color, align="center")
        self.text("←/→ cambia · Enter confirma · Esc vuelve", (LOGICAL_WIDTH // 2, 462), self.font_small, MUTED, align="center")

    def draw_pause(self) -> None:
        overlay = pygame.Surface(LOGICAL_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        self.surface.blit(overlay, (0, 0))
        panel = pygame.Rect(LOGICAL_WIDTH // 2 - 180, 135, 360, 270)
        pygame.draw.rect(self.surface, (19, 17, 32), panel, border_radius=18)
        pygame.draw.rect(self.surface, (120, 100, 150), panel, 2, border_radius=18)
        self.text("Pausa", (LOGICAL_WIDTH // 2, 171), self.font_medium, GOLD, align="center")
        items = ["Continuar", "Guardar partida", "Opciones", "Menú principal"]
        for index, item in enumerate(items):
            y = 225 + index * 42
            color = GOLD if index == self.pause_index else WHITE
            self.text(item, (LOGICAL_WIDTH // 2, y), self.font_small, color, align="center")

    def draw_overlay(self, title: str, subtitle: str, color: tuple[int, int, int]) -> None:
        overlay = pygame.Surface(LOGICAL_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.surface.blit(overlay, (0, 0))
        self.text(title, (LOGICAL_WIDTH // 2, 210), self.font_big, color, align="center")
        self.text(subtitle, (LOGICAL_WIDTH // 2, 282), self.font_medium, WHITE, align="center")
        self.text(f"Tiempo: {format_time(self.save_state.play_time_seconds)}", (LOGICAL_WIDTH // 2, 336), self.font_small, MUTED, align="center")

    def draw_toasts(self) -> None:
        y = 105
        for toast in reversed(self.toasts):
            alpha = int(255 * min(1.0, toast.timer / 0.35))
            text_surface = self.font_small.render(toast.text, True, toast.color)
            box = text_surface.get_rect(topright=(LOGICAL_WIDTH - 26, y)).inflate(24, 14)
            bubble = pygame.Surface(box.size, pygame.SRCALPHA)
            pygame.draw.rect(bubble, (14, 13, 25, min(220, alpha)), bubble.get_rect(), border_radius=12)
            pygame.draw.rect(bubble, (*toast.color, min(210, alpha)), bubble.get_rect(), 2, border_radius=12)
            self.surface.blit(bubble, box)
            text_surface.set_alpha(alpha)
            self.surface.blit(text_surface, text_surface.get_rect(center=box.center))
            y += 45

    def is_visible(self, rect: pygame.Rect) -> bool:
        view = pygame.Rect(self.camera.x - 80, self.camera.y - 80, LOGICAL_WIDTH + 160, LOGICAL_HEIGHT + 160)
        return view.colliderect(rect)

    def text(
        self,
        value: str,
        pos: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int],
        align: str = "topleft",
    ) -> None:
        rendered = font.render(value, True, color)
        rect = rendered.get_rect()
        setattr(rect, align, pos)
        self.surface.blit(rendered, rect)

    def present(self) -> None:
        window_size = self.window.get_size()
        if window_size == LOGICAL_SIZE:
            self.window.blit(self.surface, (0, 0))
        else:
            pygame.transform.smoothscale(self.surface, window_size, self.window)
        pygame.display.flip()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
