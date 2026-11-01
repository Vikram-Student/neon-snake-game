#from __future__ import annotations

import random
import sys
from pathlib import Path

import pygame

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 680
CELL = 20
PLAY_LEFT, PLAY_TOP = 30, 112
PLAY_WIDTH, PLAY_HEIGHT = 840, 520
COLS, ROWS = PLAY_WIDTH // CELL, PLAY_HEIGHT // CELL
FPS = 60
BASE_MOVE_DELAY = 125  # milliseconds between moves
ROOT = Path(__file__).resolve().parent
HIGH_SCORE_FILE = ROOT / "high_score.txt"

TEAM_MEMBERS = [
    "PEDADA VIKRAM",
    "MEMBER 2",
    "MEMBER 3",
    "MEMBER 4",
    "MEMBER 5"
]

BG = (7, 10, 24)
PANEL = (13, 19, 39)
GRID = (20, 35, 58)
CYAN = (45, 238, 255)
NEON_GREEN = (80, 255, 154)
PINK = (255, 65, 170)
PURPLE = (164, 100, 255)
WHITE = (232, 245, 255)
MUTED = (126, 151, 180)

pygame.init()
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON SNAKE | Python Arcade")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 20, bold=True)
SMALL = pygame.font.SysFont("consolas", 15)
MEDIUM = pygame.font.SysFont("consolas", 27, bold=True)
LARGE = pygame.font.SysFont("consolas", 54, bold=True)


def load_sound(filename: str):
    if not AUDIO_AVAILABLE:
        return None
    try:
        return pygame.mixer.Sound(str(filename))
    except (pygame.error, OSError):
        return None


eat_sound = load_sound(ROOT / "assets" / "hiss-86052.mp3")
gameover_sound = load_sound(ROOT / "assets" / "game-fail-90322.mp3")


def play_sound(sound) -> None:
    if sound is not None:
        try:
            sound.play()
        except pygame.error:
            pass


def load_high_score() -> int:
    try:
        return max(0, int(HIGH_SCORE_FILE.read_text(encoding="utf-8").strip()))
    except (OSError, ValueError):
        return 0


def save_high_score(value: int) -> None:
    try:
        HIGH_SCORE_FILE.write_text(f"{value}\n", encoding="utf-8")
    except OSError:
        # The game remains playable if the folder is read-only.
        pass


high_score = load_high_score()


def draw_text(text: str, font, color, center, glow=False) -> None:
    if glow:
        shadow = font.render(text, True, color)
        shadow.set_alpha(65)
        for offset in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            screen.blit(shadow, shadow.get_rect(center=(center[0] + offset[0], center[1] + offset[1])))
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))


def draw_background() -> None:
    screen.fill(BG)
    pygame.draw.rect(screen, PANEL, (PLAY_LEFT, PLAY_TOP, PLAY_WIDTH, PLAY_HEIGHT), border_radius=12)
    for x in range(PLAY_LEFT, PLAY_LEFT + PLAY_WIDTH + 1, CELL):
        pygame.draw.line(screen, GRID, (x, PLAY_TOP), (x, PLAY_TOP + PLAY_HEIGHT), 1)
    for y in range(PLAY_TOP, PLAY_TOP + PLAY_HEIGHT + 1, CELL):
        pygame.draw.line(screen, GRID, (PLAY_LEFT, y), (PLAY_LEFT + PLAY_WIDTH, y), 1)
    pygame.draw.rect(screen, CYAN, (PLAY_LEFT, PLAY_TOP, PLAY_WIDTH, PLAY_HEIGHT), 2, border_radius=12)


def draw_header(score: int) -> None:
    draw_text("NEON SNAKE", MEDIUM, CYAN, (175, 43), glow=True)
    draw_text(f"SCORE  {score:04d}", FONT, WHITE, (570, 42))
    draw_text(f"BEST  {high_score:04d}", FONT, PINK, (770, 42))
    pygame.draw.line(screen, (31, 57, 83), (30, 78), (870, 78), 2)


def grid_position(cell_pos):
    return PLAY_LEFT + cell_pos[0] * CELL, PLAY_TOP + cell_pos[1] * CELL


def random_food(snake):
    free_cells = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in snake]
    return random.choice(free_cells) if free_cells else None


def new_game():
    start = (COLS // 2, ROWS // 2)
    snake = [start, (start[0] - 1, start[1]), (start[0] - 2, start[1])]
    return snake, (1, 0), random_food(snake), 0, False


def draw_snake(snake) -> None:
    for index, part in enumerate(snake):
        x, y = grid_position(part)
        rect = pygame.Rect(x + 2, y + 2, CELL - 4, CELL - 4)
        color = NEON_GREEN if index == 0 else (35, max(100, 220 - index * 3), 125)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        if index == 0:
            pygame.draw.circle(screen, BG, (x + 7, y + 7), 2)
            pygame.draw.circle(screen, BG, (x + 13, y + 7), 2)


def draw_food(food) -> None:
    if food is None:
        return
    x, y = grid_position(food)
    center = (x + CELL // 2, y + CELL // 2)
    pygame.draw.circle(screen, PINK, center, 8)
    pygame.draw.circle(screen, (255, 190, 225), (center[0] - 2, center[1] - 3), 2)


def draw_footer() -> None:
    draw_text("MOVE  ARROWS / WASD", SMALL, MUTED, (170, 654))
    draw_text("PAUSE  P", SMALL, MUTED, (430, 654))
    draw_text("QUIT  ESC", SMALL, MUTED, (690, 654))


def draw_overlay(title: str, subtitle: str, hint: str, accent=CYAN) -> None:
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((3, 6, 18, 190))
    screen.blit(shade, (0, 0))

    pygame.draw.rect(
        screen, (17, 27, 52),
        (100, 165, 700, 350),
        border_radius=18
    )

    pygame.draw.rect(
        screen, accent,
        (100, 165, 700, 350),
        2, border_radius=18
    )

    draw_text(title, LARGE, accent, (WIDTH // 2, 225), glow=True)
    draw_text(subtitle, FONT, WHITE, (WIDTH // 2, 280))

    draw_text(
        "DEVELOPED BY",
        FONT,
        CYAN,
        (WIDTH // 2, 335)
    )

    team_font = pygame.font.SysFont("consolas", 15, bold=True)

    for index, name in enumerate(TEAM_MEMBERS):
        draw_text(
            name,
            team_font,
            WHITE,
            (WIDTH // 2, 365 + index * 25)
        )

    draw_text(hint, SMALL, MUTED, (WIDTH // 2, 490))


def main() -> None:
    global high_score
    state = "menu"  # menu, playing, paused, gameover
    snake, direction, food, score, won = new_game()
    next_move = 0
    running = True

    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    snake, direction, food, score, won = new_game()
                    state, next_move = "playing", now
                elif state == "gameover" and event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    snake, direction, food, score, won = new_game()
                    state, next_move = "playing", now
                elif state == "playing":
                    if event.key == pygame.K_p:
                        state = "paused"
                    else:
                        turns = {
                            pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
                            pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
                            pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
                            pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
                        }
                        new_direction = turns.get(event.key)
                        if new_direction and new_direction != (-direction[0], -direction[1]):
                            direction = new_direction
                elif state == "paused" and event.key in (pygame.K_p, pygame.K_RETURN, pygame.K_SPACE):
                    state = "playing"
                    next_move = now

        if state == "playing" and now >= next_move:
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            eating = head == food
            body_to_check = snake if eating else snake[:-1]
            if (not 0 <= head[0] < COLS or not 0 <= head[1] < ROWS or head in body_to_check):
                state = "gameover"
                play_sound(gameover_sound)
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                snake.insert(0, head)
                if eating:
                    score += 1
                    play_sound(eat_sound)
                    food = random_food(snake)
                    if food is None:
                        won, state = True, "gameover"
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                else:
                    snake.pop()
            speed = min(230, BASE_MOVE_DELAY + score * 4)
            next_move = now + max(55, BASE_MOVE_DELAY - score * 3)

        draw_background()
        draw_header(score)
        draw_snake(snake)
        draw_food(food)
        draw_footer()

        if state == "menu":
            draw_overlay("SNAKE", "A classic arcade game with a neon twist", "PRESS ENTER / SPACE TO START")
        elif state == "paused":
            draw_overlay("PAUSED", f"Current score: {score}", "PRESS P / ENTER TO RESUME", PURPLE)
        elif state == "gameover":
            if won:
                title, subtitle = "YOU WIN!", f"Board cleared  |  Score: {score}"
            else:
                title, subtitle = "GAME OVER", f"Score: {score}  |  Best: {high_score}"
            draw_overlay(title, subtitle, "PRESS R / ENTER TO PLAY AGAIN   |   ESC TO QUIT", PINK)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
