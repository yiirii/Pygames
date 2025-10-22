from settings import *
from os.path import join
from os import walk
from pytmx.util_pygame import load_pygame
import pygame # Ensure pygame is imported if not already, as the functions rely on it.

# --- Import Functions ---

def import_image(*path, alpha = True, format = 'png'):
    full_path = join(*path) + f'.{format}'
    # Use pygame.image.load with a check for alpha
    surf = pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
    return surf

def import_folder(*path):
    frames = []
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
            full_path = join(folder_path, image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames.append(surf)
    return frames

def import_folder_dict(*path):
    frames = {}
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image_name in image_names:
            full_path = join(folder_path, image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            
            # FIX: Convert the key to lowercase before adding it to the dictionary
            key = image_name.split('.')[0].lower() 
            frames[key] = surf
            
    return frames

def import_sub_folders(*path):
    frames = {}
    for _, sub_folders, __ in walk(join(*path)):
        if sub_folders:
            for sub_folder in sub_folders:
                frames[sub_folder] = import_folder(*path, sub_folder)
    return frames

def import_tilemap(cols, rows, *path):
    frames = {}
    surf = import_image(*path)
    cell_width, cell_height = surf.get_width() / cols, surf.get_height() / rows
    for col in range(cols):
        for row in range(rows):
            cutout_rect = pygame.Rect(col * cell_width, row * cell_height,cell_width,cell_height)
            cutout_surf = pygame.Surface((cell_width, cell_height))
            cutout_surf.fill('green')
            cutout_surf.set_colorkey('green')
            cutout_surf.blit(surf, (0,0), cutout_rect)
            frames[(col, row)] = cutout_surf
    return frames

def character_importer(cols, rows, *path):
    frame_dict = import_tilemap(cols, rows, *path)
    new_dict = {}
    for row, direction in enumerate(('down', 'left', 'right', 'up')):
        new_dict[direction] = [frame_dict[(col, row)] for col in range(cols)]
        new_dict[f'{direction}_idle'] = [frame_dict[(0, row)]]
    return new_dict

def all_character_import(*path):
    new_dict = {}
    for _, __, image_names in walk(join(*path)):
        for image in image_names:
            image_name = image.split('.')[0]
            print("Found character sprite:", image_name)
            new_dict[image_name] = character_importer(4, 4, *path, image_name)
            print("Final character keys:", new_dict.keys())
    return new_dict

def coast_importer(cols, rows, *path):
    frame_dict = import_tilemap(cols, rows, *path)
    new_dict = {}
    
    terrains = ['grass', 'grass_i', 'sand_i', 'sand', 'rock', 'rock_i', 'ice', 'ice_i']
    
    sides = {
        'topleft': (0,0), 'top': (1,0), 'topright': (2,0),
        'left': (0,1), 'right': (2,1), 'bottomleft': (0,2),
        'bottom': (1,2), 'bottomright': (2,2)}
    
    for index, terrain in enumerate(terrains):
        new_dict[terrain] = {}
        
        terrain_col_offset = index * 3
        
        for key, pos in sides.items():
            
            target_col = pos[0] + terrain_col_offset
            
            # This logic correctly collects frames stepping by 3 rows vertically
            frames = [frame_dict[(target_col, current_row)] 
                      for current_row in range(pos[1], rows, 3) 
                      if (target_col, current_row) in frame_dict] 
            
            # Only assign the key if sprites were actually found
            if frames:
                new_dict[terrain][key] = frames
            
    return new_dict


def tmx_importer(*path):
    tmx_dict = {}
    for folder_path, sub_folders, file_names in walk(join(*path)):
        for file in file_names:
            tmx_dict[file.split('.')[0]] = load_pygame(join(folder_path, file))
        return tmx_dict           

def monster_importer(cols, rows, *path):
    monster_dict = {}
    for folder_path, sub_folders, image_names in walk(join(*path)):
        for image in image_names:
            image_name = image.split('.')[0]
            monster_dict[image_name] = {}
            frame_dict = import_tilemap(cols, rows, *path, image_name)
            for row, key in enumerate(('idle', 'attack')):
                monster_dict[image_name][key] = [frame_dict[(col,row)] for col in range(cols)]
    return monster_dict

def outline_creator(frame_dict, width):
    outline_frame_dict = {}
    for monster, monster_frames in frame_dict.items():
        outline_frame_dict[monster] = {}
        for state, frames in monster_frames.items():
            outline_frame_dict[monster][state] = []
            for frame in frames:
                new_surf = pygame.Surface(vector(frame.get_size()) + vector(width * 2), pygame.SRCALPHA)
                new_surf.fill((0,0,0,0))
                white_frame = pygame.mask.from_surface(frame).to_surface()
                white_frame.set_colorkey('black')

                new_surf.blit(white_frame, (0,0)) 
                new_surf.blit(white_frame, (width,0))
                new_surf.blit(white_frame, (width * 2,0))
                new_surf.blit(white_frame, (width * 2,width))
                new_surf.blit(white_frame, (width * 2,width * 2))
                new_surf.blit(white_frame, (width,width * 2))
                new_surf.blit(white_frame, (0,width * 2))
                new_surf.blit(white_frame, (0,width))
                outline_frame_dict[monster][state].append(new_surf)
    return outline_frame_dict

def attack_importer(*path):
    attack_dict = {}
    for folder_path, _, image_names in walk(join(*path)):
        for image in image_names:
            image_name = image.split('.')[0]
            attack_dict[image_name] = list(import_tilemap(4,1,folder_path, image_name).values())
    return attack_dict

def audio_importer(*path):
    files = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path, file_name)
            files[file_name.split('.')[0]] = pygame.mixer.Sound(full_path)
    return files

# --- Game Functions ---

def draw_bar(surface, rect, value, max_value, color, bg_color, radius = 1):
    ratio = rect.width / max_value
    bg_rect = rect.copy()
    progress = max(0, min(rect.width,value * ratio))
    progress_rect = pygame.FRect(rect.topleft, (progress,rect.height))
    pygame.draw.rect(surface, bg_color, bg_rect, 0, radius)
    pygame.draw.rect(surface, color, progress_rect, 0, radius)

def check_connections(radius, entity, target, tolerance = 30):
    """
    Checks if a target is within a given radius and in front of an entity.
    This definition has 3 required positional arguments, matching the call in entities.py.
    """
    # Use the vector alias from settings.py if it's imported as needed
    try:
        relation = vector(target.rect.center) - vector(entity.rect.center)
    except NameError:
        # Fallback if 'vector' is not defined (assuming it's pygame.math.Vector2)
        relation = pygame.math.Vector2(target.rect.center) - pygame.math.Vector2(entity.rect.center)

    if relation.length() < radius:
        if entity.facing_direction == 'left' and relation.x < 0 and abs(relation.y) < tolerance or\
           entity.facing_direction == 'right' and relation.x > 0 and abs(relation.y) < tolerance or\
           entity.facing_direction == 'up' and relation.y < 0 and abs(relation.x) < tolerance or\
           entity.facing_direction == 'down' and relation.y > 0 and abs(relation.x) < tolerance:
                return True
    return False # Added explicit return False outside the radius check