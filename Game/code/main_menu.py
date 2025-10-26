import pygame
import sys
import os
from pathlib import Path

# --- Fix the import path issue properly ---
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.append(str(PARENT_DIR))

# ✅ Import main.py using full absolute path
import importlib.util

main_path = PARENT_DIR / "code" / "main.py"
spec = importlib.util.spec_from_file_location("main", main_path)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
run_game = main_module.run_game  # ✅ Assign reference to function

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
for i in range(1, 13):  # Loads MainMenu1.png - MainMenu12.png
    frame_path = MENU_DIR / f"MainMenu{i}.png"
    if frame_path.exists():
        img = pygame.image.load(str(frame_path)).convert()
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frames.append(img)
    else:
        print(f"⚠️ Missing frame: {frame_path}")

if not frames:
    print("❌ No menu frames found! Check your folder path or filenames.")
    pygame.quit()
    sys.exit()

current_frame = 0
frame_timer = 0
frame_delay = 100  # milliseconds per frame

# =============================
# BUTTON AREAS
# =============================
START_BUTTON_RECT = pygame.Rect(190, 300, 270, 50)
QUIT_BUTTON_RECT = pygame.Rect(520, 300, 100, 50)

# =============================
# MAIN MENU LOOP
# =============================
def main_menu():
    global current_frame, frame_timer

    while True:
        dt = clock.tick(FPS)
        frame_timer += dt

        # Loop through frames continuously
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
                    pygame.quit()
                    run_game()
                    return
                if QUIT_BUTTON_RECT.collidepoint(x, y):
                    print("🚪 Exiting game...")
                    pygame.quit()
                    sys.exit()

        # Draw animated background
        screen.blit(frames[current_frame], (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
