from pathlib import Path
import pygame


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
HEALTH_DECAY_PER_SEC = 10  # hiep quand tu fais les ennemis modifie cette valeur pour accélérer/ralentir la perte
HEALTH_BAR_POS = (10, 10)
HEALTH_BAR_SIZE = (200, 18)
MED_HEAL_AMOUNT = 25  # quantité de vie rendue par les medcaments

# ================== INVENTAIRE ========
INV_SLOTS = 2
inv_selected = 0
inv_items = [None] * INV_SLOTS #pour les objets dans l'inv


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


def darken_image(image, amount=90):
    """Assombrit une image en soustrayant une valeur RGB (garde l'alpha)."""
    dark = image.copy()
    dark.fill((amount, amount, amount), special_flags=pygame.BLEND_RGB_SUB)
    return dark


# =========================
# Inventaire
# =========================

def inv_add(item_name):
    """Ajoute l'objet dans la première case vide, return True si OK."""
    global inv_items
    for i in range(INV_SLOTS):
        if inv_items[i] is None:
            inv_items[i] = item_name
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

        #FOND OPAQUE (cache le jeu derrière)
        pygame.draw.rect(screen, (0, 0, 0), rect)

        #contour de la case (plus épais si sélectionnée)
        if i == inv_selected:
            pygame.draw.rect(screen, (230, 230, 230), rect, 3)
        else:
            pygame.draw.rect(screen, (120, 120, 120), rect, 2)

        #Afficher le texte de l'item (si présent)
        item = inv_items[i]
        if item:
            label = font.render(str(item), True, (230, 230, 230))
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)


# =========================
# Classes de jeu
# =========================

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

    # Bouton retour
    retour_rect = assets["btn_back"].get_rect(topright=(SCREEN_WIDTH - 10, 10))
    retour_button = ImageButton(assets["btn_back"], retour_rect.topleft)

    # Décor + obstacles
    lit_rect = assets["lit"].get_rect(topleft=(20, 55))
    table_rect = assets["table"].get_rect(topleft=(30, 350))
    obstacles = [lit_rect, table_rect]

    # Joueur (NE PAS CHANGER LA VITESSE -> 2.0 comme dans ton code final)
    player = Player(
        x=375, y=275, width=64, height=64,
        speed=4.0,
        screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
        sprites=assets["player_sprites"]
    )

    player_health = HEALTH_MAX
    
    clock = pygame.time.Clock()

    
    darkness_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)


    while True:
        dt = clock.tick(FPS) / 1000.0  # secondes depuis la dernière frame

        # diminution de la vie
        player_health = max(0, player_health - HEALTH_DECAY_PER_SEC * dt)
        if player_health <= 0:
            return "fin"

        screen.blit(assets["game_bg"], (0, 0))
        screen.blit(assets["lit"], lit_rect)
        screen.blit(assets["table"], table_rect)

        # update joueur
        keys = pygame.key.get_pressed()
        player.update(keys, obstacles)
        player.draw(screen)

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
                if table_rect.collidepoint(event.pos):
                    assets["heal"].play()
                    player_health = min(HEALTH_MAX, player_health + MED_HEAL_AMOUNT)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    inv_selected = 0
                elif event.key == pygame.K_2:
                    inv_selected = 1

                if event.key == pygame.K_t:
                    inv_add("Item")

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

    font = pygame.font.Font(None, FONT_SIZE)
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
        else: #si on sait pas l'état du jeu on quitte au cas ou => risque de bugs
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
