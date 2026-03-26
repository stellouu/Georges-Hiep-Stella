from pathlib import Path
import pygame
import math

# =========================
# Chemins et paramètres globaux
# =========================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMG_DIR = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"
VB_DIR = BASE_DIR / "VB"  # sprites du joueur (VB = "Victor Blackwell")

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

FONT_SIZE = 50

# ================== BARRE DE VIE =========
HEALTH_MAX = 100
HEALTH_DECAY_PER_SEC = 1
HEALTH_BAR_POS = (10, 10)
HEALTH_BAR_SIZE = (200, 18)
MED_HEAL_AMOUNT = 25  # quantité de vie rendue par les medcaments

# ================== INVENTAIRE ========
INV_SLOTS = 2
inv_selected = 0
inv_items = [None] * INV_SLOTS  # pour les objets dans l'inv

# ================== PICKUPS =========
# ================== CLARE PNG =========
PICKUP_KEY = pygame.K_e
PICKUP_RADIUS = 40
CLARE_TEXT = ["Les monstres...Ils sont partout. Fais attention, et sois pret a te défendre. Un couteau, un bout de verre... (E) ",
              "Si tu te sens faible, cherche un endroit pour te soigner, comme la chambre d'a coté. (E)",
              "Apres tout, ce serait bete qu'un hopital n'ait pas de trousse de secours..."]
CLARE_READ_RADIUS = 60
CLARE_POS = (350, 3)
CLARE_BOX_POS = (70, 430)
CLARE_BOX_SIZE = (SCREEN_WIDTH - 140, 120)
CLARE_SIZE = (100, 140) # taille du sprite du journal dans la salle 2


# =========================
# pour UI (user interface)
# =========================

def draw_health_bar(screen, current, max_value, pos, size):
    """Dessine une barre de vie simple (fond + vie + contour)."""
    x, y = pos
    w, h = size
    ratio = max(0, min(1, current / max_value)) if max_value > 0 else 0
    fill_w = int(w * ratio)

    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))          # fond
    pygame.draw.rect(screen, (220, 40, 40), (x, y, fill_w, h))    # vie
    pygame.draw.rect(screen, (230, 230, 230), (x, y, w, h), 2)    # contour


def draw_prompt(screen, font, text, x, y):  # affiche un texte avec un fond semi-transparent
    """"Affiche un texte avec un fond semi-transparent"""
    label = font.render(text, True, (230, 230, 230))
    bg = pygame.Surface((label.get_width() + 12, label.get_height() + 8))
    bg.set_alpha(160)
    bg.fill((0, 0, 0))
    screen.blit(bg, (x, y))
    screen.blit(label, (x + 6, y + 4))


def draw_text_box(screen, font, text, box_rect, padding=12):
    """Affiche un texte multi-lignes dans une boite semi-transparente."""
    box = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    box.fill((0, 0, 0, 180))
    screen.blit(box, box_rect.topleft)

    words = text.split()
    lines = []
    current = ""
    max_w = box_rect.width - 2 * padding

    for word in words:
        test = word if not current else f"{current} {word}"
        if font.size(test)[0] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if not lines:
        lines = [text]

    y = box_rect.top + padding
    for line in lines:
        label = font.render(line, True, (230, 230, 230))
        if y + label.get_height() > box_rect.bottom - padding:
            break
        screen.blit(label, (box_rect.left + padding, y))
        y += label.get_height() + 4


def darken_image(image, amount=90):
    """Assombrit une image en soustrayant une valeur RGB (garde l'alpha)."""
    dark = image.copy()
    dark.fill((amount, amount, amount), special_flags=pygame.BLEND_RGB_SUB)
    return dark


# =========================
# Inventaire
# =========================

def inv_add(item_img):
    """Ajoute l'objet dans la première case vide, return True si OK."""
    global inv_items
    for i in range(INV_SLOTS):
        if inv_items[i] is None:
            inv_items[i] = item_img
            return True
    return False


def inv_draw(screen, w, h, font):
    """
    Dessine l'inventaire (2 cases) en bas de l'écran.
    Note : version minimale, affiche juste le nom des items.
    """
    global inv_selected, inv_items

    bar_h = 80
    slot_w, slot_h = 56, 56
    gap = 8

    total_w = INV_SLOTS * slot_w + (INV_SLOTS - 1) * gap
    start_x = (w - total_w) // 2
    start_y = h - bar_h + (bar_h - slot_h) // 2

    # --- inventory slots ---
    for i in range(INV_SLOTS):
        x = start_x + i * (slot_w + gap)
        y = start_y
        rect = pygame.Rect(x, y, slot_w, slot_h)

        # FOND OPAQUE (cache le jeu derrière)
        pygame.draw.rect(screen, (0, 0, 0), rect)

        # contour de la case (plus épais si sélectionnée)
        if i == inv_selected:
            pygame.draw.rect(screen, (230, 230, 230), rect, 3)
        else:
            pygame.draw.rect(screen, (120, 120, 120), rect, 2)

        # Afficher le texte de l'item (si présent)
        item = inv_items[i]
        
        if item is None:
            continue

        if isinstance(item, pygame.Surface):
            icon = item
            padding = 6
            max_w = rect.width - 2 * padding
            max_h = rect.height - 2 * padding

            iw, ih = icon.get_size()
            scale = min(max_w / iw, max_h / ih)
            new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))

            icon_scaled = pygame.transform.smoothscale(icon, new_size)
            icon_rect = icon_scaled.get_rect(center=rect.center)
            screen.blit(icon_scaled, icon_rect)
        else:
            # fallback: draw text if someone stored a string by mistake
            label = font.render(str(item), True, (230, 230, 230))
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)


# =========================
# Classes de jeu
# =========================

class Enemy:
    def __init__(self, x, y, width, height, speed, screen_width, screen_height, image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = image

    def collision(self, obstacles):
        for obj in obstacles:
            if self.rect.colliderect(obj):
                return True
        return False

    def can_see_player(self, player_rect, radius=220):
        ex, ey = self.rect.center
        px, py = player_rect.center
        dx = px - ex
        dy = py - ey
        return (dx * dx + dy * dy) <= radius * radius

    def update(self, player_rect, obstacles):
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

        # move X separately
        old_x = self.x
        self.x += dir_x * self.speed
        self.rect.x = int(self.x)
        if self.collision(obstacles):
            self.x = old_x
            self.rect.x = int(self.x)

        # move Y separately
        old_y = self.y
        self.y += dir_y * self.speed
        self.rect.y = int(self.y)
        if self.collision(obstacles):
            self.y = old_y
            self.rect.y = int(self.y)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (180, 50, 50), self.rect)

class Player:
    """Joueur avec animations ds 4 directions+collisions+limites écran."""

    def __init__(self, x, y, width, height, speed, screen_width, screen_height, sprites):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Animations (4 images pour chaque direction)
        self.walk_front = sprites["walk_front"]
        self.walk_back = sprites["walk_back"]
        self.walk_left = sprites["walk_left"]
        self.walk_right = sprites["walk_right"]

        # Animation state
        self.frame_index = 0.0
        self.animation_speed = 0.1
        self.current_anim = self.walk_front
        self.image = self.walk_front[0]

        # positions float (déplacements fluides)
        self.x = float(x)
        self.y = float(y)

    def collision(self, obstacles):
        """Retourne True si collision rect avec un obstacle."""
        for obj in obstacles:
            if self.rect.colliderect(obj):
                return True
        return False

    def move(self, keys, obstacles):
        """
        Déplacements :
        - Q/A = gauche
        - D = droite
        - Z/W = haut
        - S = bas
        Support AZERTY et QWERTY.
        """
        moving = False
        old_x, old_y = self.x, self.y  # sauvegarde pour annuler en cas de collision

        # Mouvement (une direction à la fois, comme ton code initial avec elif)
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

        # update rect temporaire
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # collisions
        if self.collision(obstacles):
            self.x, self.y = old_x, old_y
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        # animation
        if moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.current_anim):
                self.frame_index = 0
            self.image = self.current_anim[int(self.frame_index)]
        else:
            self.frame_index = 0
            self.image = self.current_anim[0]

        # limites écran
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
    """Bouton image avec effet hover (assombri + léger zoom) + détection clic."""

    def __init__(self, image, pos, scale_hover=1.08):
        self.image = image
        self.image_dark = darken_image(image)

        self.rect = self.image.get_rect(topleft=pos)

        # --- images agrandies ---
        w, h = image.get_size()
        self.image_hover = pygame.transform.smoothscale(
            self.image, (int(w * scale_hover), int(h * scale_hover))
        )
        self.image_dark_hover = darken_image(self.image_hover)

        # rect centrée (pour éviter le saut)
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
    """Object ramassable (ex: couteau)"""
    def __init__(self, name, rect, image=None):
        self.name = name
        self.rect = pygame.Rect(rect)  # (x, y, w, h)
        self.image = image

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # si pas d'image, dessiner rect jaune
            pygame.draw.rect(screen, (200, 200, 60), self.rect)

    def can_pickup(self, player_rect, radius=40):
        """Vrai si joueur assez proche pr ramasser"""
        px, py = player_rect.center  # centre du joueur
        ix, iy = self.rect.center    # centre de l'objet
        dx, dy = px - ix, py - iy    # distance entre les centres
        return (dx * dx + dy * dy) <= radius * radius  # distance² <= radius²


# =========================
# Chargement assets
# =========================

def load_image(path, size=None, alpha=True):
    """Charge une image et (optionnellement) la redimensionne."""
    img = pygame.image.load(path)
    img = img.convert_alpha() if alpha else img.convert()
    if size is not None:
        img = pygame.transform.scale(img, size)
    return img


def load_player_sprites(scale=2):
    """Charge et scale les sprites du joueur."""
    def load(Victor):
        img = pygame.image.load(VB_DIR / Victor).convert_alpha()
        return pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
    return {
        "walk_front": [load("F.png"), load("FLF.png"), load("F.png"), load("FRF.png")],
        "walk_back":  [load("B.png"), load("BLF.png"), load("B.png"), load("BRF.png")],
        "walk_left":  [load("L.png"), load("LLF.png"), load("L.png"), load("LRF.png")],
        "walk_right": [load("R.png"), load("RLF.png"), load("R.png"), load("RRF.png")],
    }


def load_assets():
    """Centralise tous les chargements (images + audio) pour éviter de recharger en boucle."""
    assets = {}

    # --- Images écrans ---
    assets["menu_bg"] = load_image(IMG_DIR / "menu.png", alpha=False)
    assets["game_bg"] = load_image(IMG_DIR / "game_bg.png", alpha=False)
    assets["game_bg2"] = load_image(IMG_DIR / "game_bg2.png", alpha=False)
    assets["game_bg3"] = load_image(IMG_DIR / "game_bg3.png", alpha=False)
    assets["info_bg"] = load_image(IMG_DIR / "INFO_page.png", alpha=False)
    assets["fin_bg"] = load_image(IMG_DIR / "FIN_page.png", alpha=False)

    # --- Boutons ---
    assets["btn_play"] = load_image(IMG_DIR / "JOUER_bouton.png", size=(200, 80))
    assets["btn_info"] = load_image(IMG_DIR / "INFO_bouton.png", size=(200, 80))
    assets["btn_quit"] = load_image(IMG_DIR / "QUITTER_bouton.png", size=(200, 80))
    assets["btn_replay"] = load_image(IMG_DIR / "REJOUER_bouton.png", size=(200, 80))
    assets["btn_back"] = load_image(IMG_DIR / "retour.png", size=(80, 40))

    # --- Décors ---
    lit = load_image(IMG_DIR / "lit.png")
    table = load_image(IMG_DIR / "table.png")
    assets["lit"] = pygame.transform.scale(lit, (int(lit.get_width() * 0.5), int(lit.get_height() * 0.5)))
    assets["table"] = pygame.transform.scale(table, (int(table.get_width() * 0.5), int(table.get_height() * 0.45)))

    # --- Pickups/PNGs ---
    assets["glass"] = load_image(IMG_DIR / "glass.png", size=(50, 50))  # choose size you want
    clare_path = IMG_DIR / "clare.png"
    if clare_path.exists():
        assets["clare"] = load_image(clare_path, size=CLARE_SIZE)
    else:
        fallback = pygame.Surface(CLARE_SIZE, pygame.SRCALPHA)
        fallback.fill((150, 110, 70))
        pygame.draw.rect(fallback, (230, 220, 180), fallback.get_rect(), 2)
        assets["clare"] = fallback
    


    # --- Joueur ---
    assets["player_sprites"] = load_player_sprites(scale=2.5)

    # --- Audio ---
    pygame.mixer.music.load(str(AUDIO_DIR / "28days_soundtrack.ogg"))
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)  # musique de fond en boucle

    assets["click_sound"] = pygame.mixer.Sound(str(AUDIO_DIR / "click_sound.ogg"))
    assets["click_sound"].set_volume(0.2)

    assets["heal"] = pygame.mixer.Sound(str(AUDIO_DIR / "heal.ogg"))
    assets["heal"].set_volume(0.2)

    return assets


# =========================
# Ecrans / States
# =========================

def menu_screen(screen, assets):
    """Ecran menu : boutons Jouer / Info."""
    screen_width, screen_height = SCREEN_WIDTH, SCREEN_HEIGHT

    play_rect = assets["btn_play"].get_rect(center=(screen_width // 2, screen_height // 2))
    play_button = ImageButton(assets["btn_play"], play_rect.topleft)

    info_rect = assets["btn_info"].get_rect(center=(screen_width // 2, screen_height // 2 + 100))
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
    """Ecran info avec bouton retour."""
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
    """Ecran de fin : rejouer / quitter."""
    quitter_rect = assets["btn_quit"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    quitter_button = ImageButton(assets["btn_quit"], quitter_rect.topleft)

    rejouer_rect = assets["btn_replay"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
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


def game_screen(screen, assets, font):

    """Boucle du jeu : décor, obstacles, joueur, inventaire, vie, retour menu."""
    global inv_selected

    clare_open = False
    clare_index = 0

    # Bouton retour
    retour_rect = assets["btn_back"].get_rect(topright=(SCREEN_WIDTH - 10, 10))
    retour_button = ImageButton(assets["btn_back"], retour_rect.topleft)

    # Room 1: décor + obstacles
    room1_lit_rect = assets["lit"].get_rect(topleft=(20, 55))
    room1_table_rect = assets["table"].get_rect(topleft=(30, 350))
    room1_obstacles = [room1_lit_rect, room1_table_rect]
    room1_decors = [(assets["lit"], room1_lit_rect), (assets["table"], room1_table_rect)]

    # Room 2: vide (aucun décor / obstacle)
    # Room 2: Clare is visible AND collideable
    room2_decors = []

    clare_img = assets["clare"]
    clare_rect = clare_img.get_rect(topleft=CLARE_POS)
    clare_box_rect = pygame.Rect(CLARE_BOX_POS, CLARE_BOX_SIZE)
    clare_open = False

    room2_obstacles = [clare_rect]
    clare_box_rect = pygame.Rect(CLARE_BOX_POS, CLARE_BOX_SIZE)
    clare_open = False

    # Pickups (ramassables) par room
    glass_img = assets["glass"]
    pickups_room1 = [Pickup("Verre",
                        rect=(500, 420, 
                        glass_img.get_width(), glass_img.get_height()), image=glass_img)]
    pickups_room2 = []
    pickups_room3 = []

    # Room 3: vide
    room3_decors = []
    room3_obstacles = []

    room_obstacles = {1: room1_obstacles, 2: room2_obstacles, 3: room3_obstacles}
    room_pickups = {1: pickups_room1, 2: pickups_room2, 3: pickups_room3}

    #ENNEMIES
    
        # Enemies by room
    enemies_room1 = [
        Enemy(x=600, y=120, width=40, height=40, speed=1.5,
              screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
    ]

    enemies_room2 = [
        Enemy(x=500, y=300, width=40, height=40, speed=1.2,
              screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
    ]

    enemies_room3 = [
        Enemy(x=300, y=220, width=40, height=40, speed=2.0,
              screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT),
        Enemy(x=650, y=400, width=40, height=40, speed=1.0,
              screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
    ]

    room_enemies = {
        1: enemies_room1,
        2: enemies_room2,
        3: enemies_room3,
    }

    # Joueur
    player = Player(
        x=375, y=275, width=64, height=64,
        speed=4.0,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
        sprites=assets["player_sprites"]
    )

    player_health = HEALTH_MAX
    clock = pygame.time.Clock()
    current_room = 1

    def draw_pickups(pickups):
        for p in pickups:
            if p.image:
                screen.blit(p.image, p.rect)
            else:
                pygame.draw.rect(screen, (200, 200, 60), p.rect)

    def draw_room(room_id):
        if room_id == 1:
            screen.blit(assets["game_bg"], (0, 0))
            for img, rect in room1_decors:
                screen.blit(img, rect)
            draw_pickups(pickups_room1)
        elif room_id == 2:
            screen.blit(assets["game_bg2"], (0, 0))
            for img, rect in room2_decors:
                screen.blit(img, rect)
            draw_pickups(pickups_room2)
            screen.blit(clare_img, clare_rect)
        else:
            screen.blit(assets["game_bg3"], (0, 0))
            for img, rect in room3_decors:
                screen.blit(img, rect)
            draw_pickups(pickups_room3)

    while True:
        dt = clock.tick(FPS) / 1000.0  # secondes depuis la dernière frame
        
        # diminution de la vie
        player_health = max(0, player_health - HEALTH_DECAY_PER_SEC * dt)
        if player_health <= 0:
            return "fin"

        # update joueur
        keys = pygame.key.get_pressed()
        current_obstacles = room_obstacles[current_room]
        player.update(keys, current_obstacles)

        current_enemies = room_enemies[current_room]

        for enemy in current_enemies:
            enemy.update(player.rect, current_obstacles)

            if player.rect.colliderect(enemy.rect):
                player_health = max(0, player_health - 20 * dt)

        # Changement instantane de salle sur les bords
        if current_room == 1 and player.rect.right >= SCREEN_WIDTH:
            current_room = 2
            player.rect.left = 10
            player.x = player.rect.x
        elif current_room == 2 and player.rect.left <= 0:
            current_room = 1
            player.rect.right = SCREEN_WIDTH - 10
            player.x = player.rect.x
        elif current_room == 2 and player.rect.right >= SCREEN_WIDTH:
            current_room = 3
            player.rect.left = 10
            player.x = player.rect.x
        elif current_room == 3 and player.rect.left <= 0:
            current_room = 2
            player.rect.right = SCREEN_WIDTH - 10
            player.x = player.rect.x

        current_pickups = room_pickups[current_room]
        clare_near = (
        current_room == 2
        and player.rect.inflate(CLARE_READ_RADIUS * 2, CLARE_READ_RADIUS * 2).colliderect(clare_rect)
)
        if not clare_near:
            clare_open = False

        # --- draw world ---

        draw_room(current_room)

        for enemy in current_enemies:
            enemy.draw(screen)

        screen.blit(player.image, player.rect)

        # --- pickup in range? ---
        pickup_target = None
        for p in current_pickups:
            if p.can_pickup(player.rect, radius=PICKUP_RADIUS):
                pickup_target = p
                break

        if pickup_target:
            draw_prompt(screen, font, "appuyer sur E pour ramasser", 10, 40)

        if clare_near and not clare_open:
            draw_prompt(screen, font, "appuyer sur E pour parler", 10, 40)

        if clare_open:

            draw_text_box(screen, font, CLARE_TEXT[clare_index], clare_box_rect)
            

        # UI
        inv_draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT, font)
        draw_health_bar(screen, player_health, HEALTH_MAX, HEALTH_BAR_POS, HEALTH_BAR_SIZE)

        retour_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if retour_button.is_clicked(event):
                assets["click_sound"].play()
                return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if (
                    current_room == 1
                    and room1_table_rect.collidepoint(event.pos)
                    and player.rect.colliderect(room1_table_rect.inflate(250, 250))
                ):
                    assets["heal"].play()
                    player_health = min(HEALTH_MAX, player_health + MED_HEAL_AMOUNT)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    inv_selected = 0
                elif event.key == pygame.K_2:
                    inv_selected = 1

                if event.key == pygame.K_t:
                    inv_add(assets["glass"])

                # --- PICKUP ---
                if event.key == PICKUP_KEY and pickup_target:
                    if inv_add(pickup_target.image):
                        assets["click_sound"].play()
                        current_pickups.remove(pickup_target)
                    else:
                        # inventory full feedback
                        assets["click_sound"].play()

                # --- CLARE ---
                if event.key == PICKUP_KEY and clare_near:

                    if not clare_open:
                        clare_open = True
                        clare_index = 0
                    else:
                        clare_index += 1

                    if clare_index >= len(CLARE_TEXT):
                        clare_open = False

                if event.key == pygame.K_l:
                    assets["click_sound"].play()
                    return "fin"

        pygame.display.update()


# =========================
# Main (machine à états)
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
        elif state == "quit":
            running = False
        else:  # si on sait pas l'état du jeu on quitte au cas ou => risque de bugs
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
