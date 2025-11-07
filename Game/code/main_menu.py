import pygame
import sys
import os
import random
import math
from pathlib import Path
import importlib.util

CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.append(str(PARENT_DIR))

main_path = PARENT_DIR / "code" / "main.py"
spec = importlib.util.spec_from_file_location("main", main_path)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
run_game = main_module.run_game

from support import audio_importer

# SCREEN SETTINGS
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 360
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MYCOMON - Main Menu")
clock = pygame.time.Clock()
FPS = 60

# PATH SETUP
BASE_DIR = Path(__file__).resolve().parent.parent
MENU_DIR = BASE_DIR / "graphics" / "Main Menu"
AUDIO_DIR = BASE_DIR / "audio"

# LOAD ANIMATION FRAMES
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

# BUTTON AREAS
START_BUTTON_RECT = pygame.Rect(190, 300, 270, 50)
QUIT_BUTTON_RECT = pygame.Rect(520, 300, 100, 50)

# LEAF PARTICLE CLASS
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
            (255, 200, 100, 180),
            (255, 150, 50, 180),
            (200, 255, 150, 160),
            (255, 255, 180, 140),
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
        stem_color = (50, 50, 50, 100)
        mid_y = self.size // 2
        pygame.draw.line(leaf_surf, stem_color, (0, mid_y), (self.size * 2, mid_y), 1)
        rotated = pygame.transform.rotate(leaf_surf, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

# CREATE PARTICLES
leaves = [LeafParticle() for _ in range(25)]

# AUDIO
pygame.mixer.init()
audio = audio_importer(AUDIO_DIR)

# Background music
if "hopeful" in audio:
    audio["hopeful"].play(-1)
else:
    print("'hopeful' music not found in audio folder!")

# Load typing sound
typing_sound_path = AUDIO_DIR / "TypingSound.mp3"
typing_sound = pygame.mixer.Sound(str(typing_sound_path)) if typing_sound_path.exists() else None

# STORY INTRO FUNCTION
pygame.init()

def wrap_text(text, font, max_width):
    """Splits text into multiple lines that fit the given width."""
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())
    return lines

def story_intro():
    font = pygame.font.Font(str(BASE_DIR / "graphics" / "fonts" / "PixeloidSans.ttf"), 22)
    story_lines = [
        "10 years ago",
        "Nuclear Fallout decimated the world",
        "The remaining humans settled down on a remote island far away from the war",
        "but life will never be the same...",
        "Life on Myco Island mutated from the...",
        "residue radiation caused by nuclear bombs",
        "Mushrooms evolved into sentient beings",
        "and the yearly event known as the...",
        "Mycomon Tournament began..."
    ]

    screen.fill("black")
    pygame.display.update()

    typing_speed = 40  # ms between characters
    line_delay = 1000  # delay after each line
    max_text_width = SCREEN_WIDTH - 80

    for idx, line in enumerate(story_lines):
        wrapped_lines = wrap_text(line, font, max_text_width)

        # Center vertically
        total_height = len(wrapped_lines) * 30
        start_y = (SCREEN_HEIGHT - total_height) // 2

        for i, wrapped_line in enumerate(wrapped_lines):
            typed_text = ""
            last_type_time = pygame.time.get_ticks()
            char_index = 0
            done_line = False

            while not done_line:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        done_line = True
                        break

                current_time = pygame.time.get_ticks()
                if current_time - last_type_time > typing_speed and char_index < len(wrapped_line):
                    typed_text += wrapped_line[char_index]
                    char_index += 1
                    last_type_time = current_time

                    if typing_sound and not pygame.mixer.get_busy():
                        typing_sound.play()

                if char_index >= len(wrapped_line):
                    pygame.mixer.stop()

                screen.fill("black")
                text_surface = font.render(typed_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 30))
                screen.blit(text_surface, text_rect)
                pygame.display.flip()
                clock.tick(FPS)

            pygame.time.delay(line_delay)

        if idx == len(story_lines) - 1:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        pygame.mixer.stop()
                        pygame.quit()
                        run_game() 
                        return

                # Display final text while waiting for space
                screen.fill("black")
                for i, line in enumerate(wrapped_lines):
                    text_surface = font.render(line, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 30))
                    screen.blit(text_surface, text_rect)
                prompt_text = font.render("Press SPACE to continue...", True, (180, 180, 180))
                screen.blit(prompt_text, (SCREEN_WIDTH // 2 - 130, 320))
                pygame.display.flip()
                clock.tick(FPS)

# MAIN MENU LOOP
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
                    pygame.mixer.stop()
                    story_intro()
                    return
                if QUIT_BUTTON_RECT.collidepoint(x, y):
                    print("🚪 Exiting game...")
                    pygame.quit()
                    sys.exit()

        screen.blit(frames[current_frame], (0, 0))
        for leaf in leaves:
            leaf.update()
            leaf.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main_menu()
