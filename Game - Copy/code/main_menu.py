import pygame
import sys
import os
import random
import math   # ✅ for sin() and radians()
from pathlib import Path

# --- Fix import path properly ---
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.append(str(PARENT_DIR))

# ✅ Import main.py dynamically
import importlib.util
main_path = PARENT_DIR / "code" / "main.py"
spec = importlib.util.spec_from_file_location("main", main_path)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
run_game = main_module.run_game

# ✅ Import the same audio importer from support.py
from support import audio_importer

# =============================
# SCREEN SETTINGS
# =============================
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 360
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MYCOMON - Main Menu")
clock = pygame.time.Clock()
FPS = 60

# =============================
# PATH SETUP
# =============================
BASE_DIR = Path(__file__).resolve().parent.parent
MENU_DIR = BASE_DIR / "graphics" / "Main Menu"

# =============================
# LOAD ANIMATION FRAMES
# =============================
frames = []
for i in range(1, 13):
    frame_path = MENU_DIR / f"MainMenu{i}.png"
    if frame_path.exists():
        img = pygame.image.load(str(frame_path)).convert()
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frames.append(img)
    else:
        print(f"Missing frame: {frame_path}")

if not frames:
    print("No menu frames found! Check your folder path or filenames.")
    pygame.quit()
    sys.exit()

current_frame = 0
frame_timer = 0
frame_delay = 100

# =============================
# BUTTON AREAS
# =============================
START_BUTTON_RECT = pygame.Rect(190, 300, 270, 50)
QUIT_BUTTON_RECT = pygame.Rect(520, 300, 100, 50)

# =============================
# LEAF PARTICLE CLASS
# =============================
class LeafParticle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300)
        self.y = random.randint(-200, SCREEN_HEIGHT // 2)
        self.speed_x = random.uniform(1.5, 3.5)
        self.speed_y = random.uniform(0.8, 2.0)
        self.size = random.randint(6, 12)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-2, 2)
        self.color = random.choice([
            (255, 200, 100, 180),  # golden
            (255, 150, 50, 180),   # orange
            (200, 255, 150, 160),  # light green
            (255, 255, 180, 140),  # pale yellow
        ])
        self.float_phase = random.uniform(0, 360)

    def update(self):
        self.float_phase += 5
        sway = 0.5 * math.sin(math.radians(self.float_phase))
        self.x -= self.speed_x
        self.y += self.speed_y + sway
        self.angle = (self.angle + self.spin) % 360
        if self.x < -50 or self.y > SCREEN_HEIGHT + 50:
            self.reset()

    def draw(self, surface):
        leaf_surf = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf_surf, self.color, (0, 0, self.size * 2, self.size))

        # stem
        stem_color = (50, 50, 50, 100)
        mid_y = self.size // 2
        pygame.draw.line(leaf_surf, stem_color, (0, mid_y), (self.size * 2, mid_y), 1)

        # veins
        vein_color = (60, 60, 60, 80)
        num_veins = 3
        spacing = self.size * 2 // (num_veins + 1)
        for i in range(1, num_veins + 1):
            x = i * spacing
            pygame.draw.line(leaf_surf, vein_color, (x, mid_y), (x - 3, mid_y - 3), 1)
            pygame.draw.line(leaf_surf, vein_color, (x, mid_y), (x - 3, mid_y + 3), 1)

        rotated = pygame.transform.rotate(leaf_surf, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)


# =============================
# CREATE PARTICLES
# =============================
leaves = [LeafParticle() for _ in range(25)]

# =============================
# LOAD AUDIO (same as main.py)
# =============================
pygame.mixer.init()
audio = audio_importer(BASE_DIR / "audio")

# ✅ Play the overworld theme
if "overworld" in audio:
    audio["overworld"].play(-1)
else:
    print("⚠️ 'overworld' music not found in audio folder!")

# =============================
# MAIN MENU LOOP
# =============================
def main_menu():
    global current_frame, frame_timer

    while True:
        dt = clock.tick(FPS)
        frame_timer += dt

        if frame_timer >= frame_delay:
            current_frame = (current_frame + 1) % len(frames)
            frame_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if START_BUTTON_RECT.collidepoint(x, y):
                    print("▶ Starting game...")
                    pygame.mixer.stop()  # Stop menu music
                    pygame.quit()
                    run_game()
                    return
                if QUIT_BUTTON_RECT.collidepoint(x, y):
                    print("🚪 Exiting game...")
                    pygame.quit()
                    sys.exit()

        # Draw background and leaves
        screen.blit(frames[current_frame], (0, 0))
        for leaf in leaves:
            leaf.update()
            leaf.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
