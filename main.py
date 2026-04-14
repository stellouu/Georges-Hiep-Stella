from pathlib import Path
import math
import pygame

# =========================
# Chemins et paramètres globaux
# =========================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMG_DIR = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"
VB_DIR = BASE_DIR / "VB"  # sprites du joueur

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# =========================
# Gameplay
# =========================

HEALTH_MAX = 100
HEALTH_DECAY_PER_SEC = 1
HEALTH_BAR_POS = (10, 10)
HEALTH_BAR_SIZE = (200, 18)
MED_HEAL_AMOUNT = 25

ATTACK_KEY = pygame.K_SPACE
ATTACK_RADIUS = 50
ATTACK_COOLDOWN = 300  # ms entre deux attaques

ENEMY_DAMAGE = 20
ZOMBIE_DAMAGE = 35

INV_SLOTS = 2
PICKUP_KEY = pygame.K_e
PICKUP_RADIUS = 65

intro_lines = [
    "Ou... ou suis-je ?",
    "Quelque chose rode dans les couloirs.",
    "Je dois sortir d'ici. Maintenant."
]

CLARE_TEXT = [
    "Les monstres... Ils sont partout. Fais attention, et sois pret a te defendre. Un couteau, un bout de verre... (E)",
    "Si tu te sens faible, cherche un endroit pour te soigner, comme la chambre d'a cote. (E)",
    "Apres tout, ce serait bete qu'un hopital n'ait pas de trousse de secours... (E)",
    "Il y a des petits monstres, moins forts que les zombies. Tu peux les tuer avec un bout de verre. (E)",
    "Les zombies sont plus forts, mais tu peux les tuer avec un couteau. (E)",
    "Si tu les tues tous, on pourra peut-etre s'echapper...",
]
CLARE_READ_RADIUS = 60
CLARE_POS = (350, 3)
CLARE_BOX_POS = (70, 430)
CLARE_BOX_SIZE = (SCREEN_WIDTH - 140, 120)
CLARE_SIZE = (100, 140)

# =========================
# Inventaire global
# =========================

inv_selected = 0
inv_items = [None] * INV_SLOTS


# =========================
# UI
# =========================

def intro_overlay(screen, font, lines, delay=2500):
    """
    Affiche un écran noir avec quelques lignes d'introduction.
    Le joueur peut attendre ou appuyer sur une touche pour continuer.
    """
    start_time = pygame.time.get_ticks()
    small_font = pygame.font.Font(font.path if hasattr(font, "path") else None, 28)

    while True:
        screen.fill((0, 0, 0))

        total_height = len(lines) * 50
        start_y = (SCREEN_HEIGHT - total_height) // 2

        for i, line in enumerate(lines):
            label = font.render(line, True, (230, 230, 230))
            rect = label.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 50))
            screen.blit(label, rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return None

        if pygame.time.get_ticks() - start_time >= delay:
            return None

        pygame.display.update()

def draw_darkness_overlay(screen, player_rect, radius=140):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    light_pos = (player_rect.centerx + 20, player_rect.bottom - 10)

    for r in range(radius, 0, -10):
        alpha = int(175 * (r / radius))
        pygame.draw.circle(
            overlay,
            (0, 0, 0, alpha),
            light_pos,
            r
        )

    screen.blit(overlay, (0, 0))

def draw_health_bar(screen, current, max_value, pos, size):
    """Dessine une barre de vie simple."""
    x, y = pos
    w, h = size
    ratio = max(0, min(1, current / max_value)) if max_value > 0 else 0
    fill_w = int(w * ratio)

    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, (220, 40, 40), (x, y, fill_w, h))
    pygame.draw.rect(screen, (230, 230, 230), (x, y, w, h), 2)


def draw_prompt(screen, font, text, x, y, bg_color=(0, 0, 0), alpha=160):
    """Affiche un petit message avec fond semi-transparent."""
    label = font.render(text, True, (230, 230, 230))
    bg = pygame.Surface((label.get_width() + 12, label.get_height() + 8))
    bg.set_alpha(alpha)
    bg.fill(bg_color)
    screen.blit(bg, (x, y))
    screen.blit(label, (x + 6, y + 4))


def draw_enemy_counter(screen, font, text, x, y):
    """Affiche le nombre d'ennemis restants."""
    draw_prompt(screen, font, text, x, y, bg_color=(120, 17, 17), alpha=190)


def draw_text_box(screen, font, text, box_rect, padding=12):
    """Affiche un texte multi-lignes dans une boîte semi-transparente."""
    box = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    box.fill((0, 0, 0, 180))
    screen.blit(box, box_rect.topleft)

    words = text.split()
    lines = []
    current_line = ""
    max_w = box_rect.width - 2 * padding

    for word in words:
        test_line = word if not current_line else f"{current_line} {word}"
        if font.size(test_line)[0] <= max_w:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    y = box_rect.top + padding
    for line in lines:
        label = font.render(line, True, (230, 230, 230))
        if y + label.get_height() > box_rect.bottom - padding:
            break
        screen.blit(label, (box_rect.left + padding, y))
        y += label.get_height() + 4


def darken_image(image, amount=90):
    """Assombrit une image en conservant son alpha."""
    dark = image.copy()
    dark.fill((amount, amount, amount), special_flags=pygame.BLEND_RGB_SUB)
    return dark


# =========================
# Inventaire
# =========================

def inv_add(item_img):
    """Ajoute un objet dans la première case vide."""
    global inv_items
    for i in range(INV_SLOTS):
        if inv_items[i] is None:
            inv_items[i] = item_img
            return True
    return False


def inv_reset():
    """Vide l'inventaire et remet la sélection sur la première case."""
    global inv_items, inv_selected
    inv_items = [None] * INV_SLOTS
    inv_selected = 0


def inv_draw(screen, width, height, font):
    """Dessine l'inventaire en bas de l'écran."""
    global inv_selected, inv_items

    bar_h = 80
    slot_w, slot_h = 56, 56
    gap = 8

    total_w = INV_SLOTS * slot_w + (INV_SLOTS - 1) * gap
    start_x = (width - total_w) // 2
    start_y = height - bar_h + (bar_h - slot_h) // 2

    for i in range(INV_SLOTS):
        x = start_x + i * (slot_w + gap)
        y = start_y
        rect = pygame.Rect(x, y, slot_w, slot_h)

        pygame.draw.rect(screen, (0, 0, 0), rect)
        border_color = (230, 230, 230) if i == inv_selected else (120, 120, 120)
        border_width = 3 if i == inv_selected else 2
        pygame.draw.rect(screen, border_color, rect, border_width)

        item = inv_items[i]
        if item is None:
            continue

        if isinstance(item, pygame.Surface):
            padding = 6
            max_w = rect.width - 2 * padding
            max_h = rect.height - 2 * padding
            iw, ih = item.get_size()
            scale = min(max_w / iw, max_h / ih)
            new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
            icon_scaled = pygame.transform.smoothscale(item, new_size)
            icon_rect = icon_scaled.get_rect(center=rect.center)
            screen.blit(icon_scaled, icon_rect)
        else:
            label = font.render(str(item), True, (230, 230, 230))
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)


# =========================
# Classes
# =========================

class Enemy:
    def __init__(self, x, y, width, height, speed, image=None, enemy_type="enemy"):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.image = image
        self.enemy_type = enemy_type
        self.hit_flash_timer = 0

        if enemy_type == "enemy":
            self.max_health = 2
            self.health = 2
            self.damage_to_player = ENEMY_DAMAGE
        elif enemy_type == "zombie":
            self.max_health = 4
            self.health = 4
            self.damage_to_player = ZOMBIE_DAMAGE
        else:
            self.max_health = 1
            self.health = 1
            self.damage_to_player = ENEMY_DAMAGE

    def collision(self, obstacles):
        return any(self.rect.colliderect(obj) for obj in obstacles)

    def can_see_player(self, player_rect, radius=220):
        ex, ey = self.rect.center
        px, py = player_rect.center
        dx = px - ex
        dy = py - ey
        return (dx * dx + dy * dy) <= radius ** 2

    def update(self, player_rect, obstacles, dt_ms):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt_ms

        if not self.can_see_player(player_rect):
            return

        ex, ey = self.rect.center
        px, py = player_rect.center
        dx = px - ex
        dy = py - ey
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        dir_x = dx / dist
        dir_y = dy / dist

        # Déplacement séparé sur X puis Y pour éviter de traverser les obstacles.
        old_x = self.x
        self.x += dir_x * self.speed
        self.rect.x = int(self.x)
        if self.collision(obstacles):
            self.x = old_x
            self.rect.x = int(self.x)

        old_y = self.y
        self.y += dir_y * self.speed
        self.rect.y = int(self.y)
        if self.collision(obstacles):
            self.y = old_y
            self.rect.y = int(self.y)

    def take_damage(self, weapon_name):
        """Applique des dégâts seulement si l'arme est adaptée au type d'ennemi."""
        damage_applied = False

        if self.enemy_type == "enemy" and weapon_name == "glass":
            self.health -= 1
            damage_applied = True
        elif self.enemy_type == "zombie" and weapon_name == "knife":
            self.health -= 2
            damage_applied = True

        if damage_applied:
            self.hit_flash_timer = 200

        return self.health <= 0

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
            if self.hit_flash_timer > 0:
                flash = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                flash.fill((255, 0, 0, 120))
                screen.blit(flash, self.rect.topleft)
        else:
            color = (255, 0, 0) if self.hit_flash_timer > 0 else (180, 50, 50)
            pygame.draw.rect(screen, color, self.rect)


class Player:
    """Joueur avec animations, collisions et limites écran."""

    def __init__(self, x, y, width, height, speed, screen_width, screen_height, sprites):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.walk_front = sprites["walk_front"]
        self.walk_back = sprites["walk_back"]
        self.walk_left = sprites["walk_left"]
        self.walk_right = sprites["walk_right"]

        self.frame_index = 0.0
        self.animation_speed = 0.1
        self.current_anim = self.walk_front
        self.image = self.walk_front[0]

        self.x = float(x)
        self.y = float(y)

    def collision(self, obstacles):
        return any(self.rect.colliderect(obj) for obj in obstacles)

    def move(self, keys, obstacles):
        moving = False
        old_x, old_y = self.x, self.y

        # Une seule direction à la fois, comme dans ton comportement d'origine.
        if keys[pygame.K_q] or keys[pygame.K_a]:
            self.x -= self.speed
            self.current_anim = self.walk_left
            moving = True
        elif keys[pygame.K_d]:
            self.x += self.speed
            self.current_anim = self.walk_right
            moving = True
        elif keys[pygame.K_z] or keys[pygame.K_w]:
            self.y -= self.speed
            self.current_anim = self.walk_back
            moving = True
        elif keys[pygame.K_s]:
            self.y += self.speed
            self.current_anim = self.walk_front
            moving = True

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.collision(obstacles):
            self.x, self.y = old_x, old_y
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        if moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.current_anim):
                self.frame_index = 0
            self.image = self.current_anim[int(self.frame_index)]
        else:
            self.frame_index = 0
            self.image = self.current_anim[0]

        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.x
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
            self.x = self.rect.x
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.y
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
            self.y = self.rect.y

    def update(self, keys, obstacles):
        self.move(keys, obstacles)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class ImageButton:
    """Bouton image avec hover visuel + détection du clic."""

    def __init__(self, image, pos, scale_hover=1.08):
        self.image = image
        self.image_dark = darken_image(image)
        self.rect = self.image.get_rect(topleft=pos)

        w, h = image.get_size()
        self.image_hover = pygame.transform.smoothscale(
            self.image, (int(w * scale_hover), int(h * scale_hover))
        )
        self.image_dark_hover = darken_image(self.image_hover)
        self.rect_hover = self.image_hover.get_rect(center=self.rect.center)

    def draw(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(self.image_dark_hover, self.rect_hover)
        else:
            screen.blit(self.image, self.rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class Pickup:
    """Objet ramassable."""

    def __init__(self, name, rect, image=None):
        self.name = name
        self.rect = pygame.Rect(rect)
        self.image = image

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (200, 200, 60), self.rect)

    def can_pickup(self, player_rect, radius=PICKUP_RADIUS):
        px, py = player_rect.midbottom
        ix, iy = self.rect.center
        dx, dy = px - ix, py - iy
        return (dx * dx + dy * dy) <= radius * radius


# =========================
# Chargement assets
# =========================

def load_image(path, size=None, alpha=True):
    """Charge une image et la redimensionne si besoin."""
    img = pygame.image.load(path)
    img = img.convert_alpha() if alpha else img.convert()
    if size is not None:
        img = pygame.transform.scale(img, size)
    return img


def load_player_sprites(scale=2):
    """Charge les sprites du joueur."""
    def load(filename):
        img = pygame.image.load(VB_DIR / filename).convert_alpha()
        return pygame.transform.scale(
            img,
            (int(img.get_width() * scale), int(img.get_height() * scale))
        )

    return {
        "walk_front": [load("F.png"), load("FLF.png"), load("F.png"), load("FRF.png")],
        "walk_back":  [load("B.png"), load("BLF.png"), load("B.png"), load("BRF.png")],
        "walk_left":  [load("L.png"), load("LLF.png"), load("L.png"), load("LRF.png")],
        "walk_right": [load("R.png"), load("RLF.png"), load("R.png"), load("RRF.png")],
    }


def load_assets():
    """Centralise tous les chargements d'assets."""
    assets = {}

    assets["menu_bg"] = load_image(IMG_DIR / "menu.png", alpha=False)
    assets["game_bg"] = load_image(IMG_DIR / "game_bg.png", alpha=False)
    assets["game_bg2"] = load_image(IMG_DIR / "game_bg2.png", alpha=False)
    assets["game_bg3"] = load_image(IMG_DIR / "game_bg2.png", alpha=False)
    assets["game_bg4"] = load_image(IMG_DIR / "game_bg2.png", alpha=False)
    assets["game_bg5"] = load_image(IMG_DIR / "game_bg2.png", alpha=False)
    assets["info_bg"] = load_image(IMG_DIR / "INFO_page.png", alpha=False)
    assets["fin_bg"] = load_image(IMG_DIR / "FIN_page.png", alpha=False)
    assets["win_bg"] = load_image(IMG_DIR / "WIN_page.png", size=(SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False)

    assets["btn_play"] = load_image(IMG_DIR / "JOUER_bouton.png", size=(200, 80))
    assets["btn_info"] = load_image(IMG_DIR / "INFO_bouton.png", size=(200, 80))
    assets["btn_quit"] = load_image(IMG_DIR / "QUITTER_bouton.png", size=(200, 80))
    assets["btn_replay"] = load_image(IMG_DIR / "REJOUER_bouton.png", size=(200, 80))
    assets["btn_back"] = load_image(IMG_DIR / "retour.png", size=(80, 40))

    lit = load_image(IMG_DIR / "lit.png")
    table = load_image(IMG_DIR / "table.png")
    assets["lit"] = pygame.transform.scale(
        lit, (int(lit.get_width() * 0.5), int(lit.get_height() * 0.5))
    )
    assets["table"] = pygame.transform.scale(
        table, (int(table.get_width() * 0.5), int(table.get_height() * 0.45))
    )

    assets["glass"] = load_image(IMG_DIR / "glass.png", size=(50, 50))
    assets["knife"] = load_image(IMG_DIR / "knife.png", size=(70, 70))
    assets["enemy"] = load_image(IMG_DIR / "enemy.png", size=(80, 80))
    assets["zombie"] = load_image(IMG_DIR / "zombie.png", size=(140, 140))
    assets["player_sprites"] = load_player_sprites(scale=2.5)

    clare_path = IMG_DIR / "clare.png"
    if clare_path.exists():
        assets["clare"] = load_image(clare_path, size=CLARE_SIZE)
    else:
        fallback = pygame.Surface(CLARE_SIZE, pygame.SRCALPHA)
        fallback.fill((150, 110, 70))
        pygame.draw.rect(fallback, (230, 220, 180), fallback.get_rect(), 2)
        assets["clare"] = fallback

    pygame.mixer.music.load(str(AUDIO_DIR / "28days_soundtrack.ogg"))
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)

    assets["click_sound"] = pygame.mixer.Sound(str(AUDIO_DIR / "click_sound.ogg"))
    assets["click_sound"].set_volume(0.2)

    assets["kill_sound"] = pygame.mixer.Sound(str(AUDIO_DIR / "kill_sound.ogg"))
    assets["kill_sound"].set_volume(0.3)

    assets["heal"] = pygame.mixer.Sound(str(AUDIO_DIR / "heal.ogg"))
    assets["heal"].set_volume(0.2)

    return assets


# =========================
# Écrans
# =========================

def menu_screen(screen, assets):
    play_rect = assets["btn_play"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    info_rect = assets["btn_info"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

    play_button = ImageButton(assets["btn_play"], play_rect.topleft)
    info_button = ImageButton(assets["btn_info"], info_rect.topleft)

    while True:
        screen.blit(assets["menu_bg"], (0, 0))
        play_button.draw(screen)
        info_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if play_button.is_clicked(event):
                assets["click_sound"].play()
                return "game"
            if info_button.is_clicked(event):
                assets["click_sound"].play()
                return "info"

        pygame.display.update()


def info_screen(screen, assets):
    retour_rect = assets["btn_back"].get_rect(topright=(SCREEN_WIDTH - 10, 10))
    retour_button = ImageButton(assets["btn_back"], retour_rect.topleft)

    while True:
        screen.blit(assets["info_bg"], (0, 0))
        retour_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if retour_button.is_clicked(event):
                assets["click_sound"].play()
                return "menu"

        pygame.display.update()


def fin_screen(screen, assets):
    quitter_rect = assets["btn_quit"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    rejouer_rect = assets["btn_replay"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

    quitter_button = ImageButton(assets["btn_quit"], quitter_rect.topleft)
    rejouer_button = ImageButton(assets["btn_replay"], rejouer_rect.topleft)

    while True:
        screen.blit(assets["fin_bg"], (0, 0))
        quitter_button.draw(screen)
        rejouer_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if rejouer_button.is_clicked(event):
                assets["click_sound"].play()
                return "menu"
            if quitter_button.is_clicked(event):
                return "quit"

        pygame.display.update()

def win_screen(screen, assets):
    """Ecran de victoire : rejouer / quitter."""
    quitter_rect = assets["btn_quit"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    rejouer_rect = assets["btn_replay"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

    quitter_button = ImageButton(assets["btn_quit"], quitter_rect.topleft)
    rejouer_button = ImageButton(assets["btn_replay"], rejouer_rect.topleft)

    while True:
        screen.blit(assets["win_bg"], (0, 0))
        quitter_button.draw(screen)
        rejouer_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if rejouer_button.is_clicked(event):
                assets["click_sound"].play()
                return "menu"

            if quitter_button.is_clicked(event):
                return "quit"

        pygame.display.update()


def game_screen(screen, assets, font):
    global inv_selected

    inv_reset()
    result = intro_overlay(screen, font, intro_lines, delay=5000)

    if result == "quit":
        return "quit"
    
    clare_open = False
    clare_index = 0

    retour_rect = assets["btn_back"].get_rect(topright=(SCREEN_WIDTH - 10, 10))
    retour_button = ImageButton(assets["btn_back"], retour_rect.topleft)

    # =========================
    # Rooms / décors / obstacles
    # =========================

    room1_lit_rect = assets["lit"].get_rect(topleft=(20, 55))
    room1_table_rect = assets["table"].get_rect(topleft=(30, 350))
    room1_decors = [(assets["lit"], room1_lit_rect), (assets["table"], room1_table_rect)]
    room1_obstacles = [room1_lit_rect, room1_table_rect]

    clare_img = assets["clare"]
    clare_rect = clare_img.get_rect(topleft=CLARE_POS)
    clare_box_rect = pygame.Rect(CLARE_BOX_POS, CLARE_BOX_SIZE)
    room2_decors = [(clare_img, clare_rect)]
    room2_obstacles = [clare_rect]

    room3_lit_rect = assets["lit"].get_rect(topleft=(400, 55))
    room3_decors = [(assets["lit"], room3_lit_rect)]
    room3_obstacles = [room3_lit_rect]

    room_decors = {
        1: room1_decors,
        2: room2_decors,
        3: room3_decors,
        4: [],
        5: [],
    }

    room_obstacles = {
        1: room1_obstacles,
        2: room2_obstacles,
        3: room3_obstacles,
        4: [],
        5: [],
    }

    room_backgrounds = {
        1: assets["game_bg"],
        2: assets["game_bg2"],
        3: assets["game_bg3"],
        4: assets["game_bg4"],
        5: assets["game_bg5"],
    }

    # =========================
    # Pickups
    # =========================

    glass_img = assets["glass"]
    knife_img = assets["knife"]

    room_pickups = {
        1: [Pickup("Verre", (500, 420, glass_img.get_width(), glass_img.get_height()), image=glass_img)],
        2: [Pickup("Couteau", (500, 300, knife_img.get_width(), knife_img.get_height()), image=knife_img)],
        3: [],
        4: [],
        5: [],
    }

    # =========================
    # Ennemis
    # =========================

    room_enemies = {
        1: [],
        2: [],
        3: [
            Enemy(300, 220, 70, 70, 2.0, image=assets["enemy"], enemy_type="enemy"),
            Enemy(650, 400, 40, 40, 1.0, image=assets["enemy"], enemy_type="enemy"),
        ],
        4: [
            Enemy(300, 220, 70, 70, 2.0, image=assets["zombie"], enemy_type="zombie"),
        ],
        5: [
            Enemy(550, 50, 40, 40, 3.0, image=assets["enemy"], enemy_type="enemy"),
            Enemy(650, 400, 40, 40, 4.0, image=assets["zombie"], enemy_type="zombie"),
        ],
    }

    total_enemies = sum(len(enemies) for enemies in room_enemies.values())

    # =========================
    # Joueur
    # =========================

    player = Player(
        x=375,
        y=275,
        width=64,
        height=64,
        speed=9.0,
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        sprites=assets["player_sprites"],
    )

    player_health = HEALTH_MAX
    current_room = 1
    last_attack_time = 0
    clock = pygame.time.Clock()

    def draw_room(room_id):
        screen.blit(room_backgrounds[room_id], (0, 0))
        for img, rect in room_decors[room_id]:
            screen.blit(img, rect)
        for pickup in room_pickups[room_id]:
            pickup.draw(screen)

    while True:

        dt = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks()
        
        player_health = max(0, player_health - HEALTH_DECAY_PER_SEC * dt)
        if player_health <= 0:
            return "fin"

        keys = pygame.key.get_pressed()
        current_obstacles = room_obstacles[current_room]
        current_pickups = room_pickups[current_room]
        current_enemies = room_enemies[current_room]

        player.update(keys, current_obstacles)

        for enemy in current_enemies:
            enemy.update(player.rect, current_obstacles, dt * 1000)
            if player.rect.colliderect(enemy.rect):
                player_health = max(0, player_health - enemy.damage_to_player * dt)

        # Passage entre salles.
        if current_room == 1 and player.rect.right >= SCREEN_WIDTH:
            current_room = 2
            player.rect.left = 10
            player.x = float(player.rect.x)
        elif current_room == 2 and player.rect.left <= 0:
            current_room = 1
            player.rect.right = SCREEN_WIDTH - 10
            player.x = float(player.rect.x)
        elif current_room == 2 and player.rect.right >= SCREEN_WIDTH:
            current_room = 3
            player.rect.left = 10
            player.x = float(player.rect.x)
        elif current_room == 3 and player.rect.left <= 0:
            current_room = 2
            player.rect.right = SCREEN_WIDTH - 10
            player.x = float(player.rect.x)
        elif current_room == 3 and player.rect.right >= SCREEN_WIDTH:
            current_room = 4
            player.rect.left = 10
            player.x = float(player.rect.x)
        elif current_room == 4 and player.rect.left <= 0:
            current_room = 3
            player.rect.right = SCREEN_WIDTH - 10
            player.x = float(player.rect.x)
        elif current_room == 4 and player.rect.right >= SCREEN_WIDTH:
            current_room = 5
            player.rect.left = 10
            player.x = float(player.rect.x)
        elif current_room == 5 and player.rect.left <= 0:
            current_room = 4
            player.rect.right = SCREEN_WIDTH - 10
            player.x = float(player.rect.x)

        clare_near = (
            current_room == 2
            and player.rect.inflate(CLARE_READ_RADIUS * 2, CLARE_READ_RADIUS * 2).colliderect(clare_rect)
        )

        if not clare_near:
            clare_open = False

        pickup_target = next(
            (pickup for pickup in current_pickups if pickup.can_pickup(player.rect)),
            None
        )

        heal_table_near = (
            current_room == 1
            and player.rect.colliderect(room1_table_rect.inflate(100, 100))
        )

        # =========================
        # Draw
        # =========================

        draw_room(current_room)
        

        for enemy in current_enemies:
            enemy.draw(screen)

        player.draw(screen)
        draw_darkness_overlay(screen, player.rect, radius=140)
        draw_enemy_counter(screen, font, f"il reste {total_enemies} ennemis a tuer", 400, 25)
        
        if pickup_target:
            draw_prompt(screen, font, "appuyer sur E pour ramasser", 10, 40)
        elif heal_table_near:
            draw_prompt(screen, font, "appuyer sur E pour se soigner", 10, 40)

        if clare_near and not clare_open:
            draw_prompt(screen, font, "appuyer sur E pour parler", 10, 40)

        if clare_open:
            draw_text_box(screen, font, CLARE_TEXT[clare_index], clare_box_rect)

        weapon = inv_items[inv_selected]
        if weapon is not None:
            for enemy in current_enemies:
                px, py = player.rect.center
                ex, ey = enemy.rect.center
                dx, dy = px - ex, py - ey
                if dx * dx + dy * dy <= ATTACK_RADIUS ** 2:
                    draw_prompt(screen, font, "appuyer sur espace pour attaquer", 10, 70)
                    break

        inv_draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT, font)
        draw_health_bar(screen, player_health, HEALTH_MAX, HEALTH_BAR_POS, HEALTH_BAR_SIZE)

        # =========================
        # Events
        # =========================

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    inv_selected = 0
                elif event.key == pygame.K_2:
                    inv_selected = 1

                elif event.key == ATTACK_KEY:
                    weapon = inv_items[inv_selected]

                    if weapon is not None and now - last_attack_time >= ATTACK_COOLDOWN:
                        last_attack_time = now

                        if weapon == assets["glass"]:
                            weapon_name = "glass"
                        elif weapon == assets["knife"]:
                            weapon_name = "knife"
                        else:
                            weapon_name = None

                        if weapon_name is not None:
                            px, py = player.rect.center

                            for enemy in current_enemies[:]:
                                ex, ey = enemy.rect.center
                                dx, dy = px - ex, py - ey

                                if dx * dx + dy * dy <= ATTACK_RADIUS ** 2:
                                    dead = enemy.take_damage(weapon_name)
                                    if dead:
                                        current_enemies.remove(enemy)
                                        total_enemies = max(0, total_enemies - 1)
                                        assets["kill_sound"].play()

                                        if total_enemies == 0:
                                            return "win"
                                    break
                                

                elif event.key == PICKUP_KEY:
                    # Une seule interaction à la fois avec la touche E.
                    if pickup_target:
                        if inv_add(pickup_target.image):
                            assets["click_sound"].play()
                            current_pickups.remove(pickup_target)
                        else:
                            assets["click_sound"].play()
                    elif heal_table_near:
                        assets["heal"].play()
                        player_health = min(HEALTH_MAX, player_health + MED_HEAL_AMOUNT)
                    elif clare_near:
                        if not clare_open:
                            clare_open = True
                            clare_index = 0
                        else:
                            clare_index += 1
                            if clare_index >= len(CLARE_TEXT):
                                clare_open = False
                                clare_index = 0

                elif event.key == pygame.K_l:
                    assets["click_sound"].play()
                    return "fin"

        pygame.display.update()


# =========================
# Main
# =========================

def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("menu + jeu + info")

    font = pygame.font.Font(str(ASSETS_DIR / "fonts" / "pixel.ttf"), 40)
    assets = load_assets()

    state = "menu"
    running = True

    while running:
        if state == "menu":
            state = menu_screen(screen, assets)
        elif state == "game":
            state = game_screen(screen, assets, font)
        elif state == "info":
            state = info_screen(screen, assets)
        elif state == "fin":
            state = fin_screen(screen, assets)
        elif state == "win":
            state = win_screen(screen, assets)
        elif state == "quit":
            running = False
        else:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
