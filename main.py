from pathlib import Path
import pygame
BASE_DIR = Path(__file__).resolve().parent
VB_DIR = BASE_DIR / "VB" #dossier des sprites du joueur :D (VB = "Victor Blackwell", le nom du personnage principal)

# ============= PARAMETRES GLOBAUX ============= #

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("28days_soundtrack.ogg")
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1) #musique de fond en boucle
click_sound = pygame.mixer.Sound("click_sound.ogg")
click_sound.set_volume(1) #clic sonore


screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("menu + jeu + info")

scale = 3

font = pygame.font.Font(None, 50)

# ============= FONCTIONS + CLASSES ================ #

# INVENTAIRE (2 cases) (Hiep)

INV_SLOTS = 2
inv_selected = 0
inv_items = [None] * INV_SLOTS  # ex: ["Key", "Med", None, None, "Badge"]

#-------- fonction pour ajouter un item dans l'inventaire --------

def inv_add(item_name):
    """Ajoute l'objet dans la première case vide, return True si OK."""
    global inv_items
    for i in range(INV_SLOTS):
        if inv_items[i] is None:
            inv_items[i] = item_name
            return True
    return False

#-------- dessine l'inventaire dans le jeu --------

def inv_draw(screen, w, h):
    global inv_selected, inv_items
    bar_h = 80
    slot_w, slot_h = 56, 56
    gap = 8

    total_w = INV_SLOTS * slot_w + (INV_SLOTS - 1) * gap
    start_x = (w - total_w) // 2
    start_y = h - bar_h + (bar_h - slot_h) // 2

#-------- inventory slots --------

    for i in range(INV_SLOTS):
        x = start_x + i * (slot_w + gap)
        y = start_y
        rect = pygame.Rect(x, y, slot_w, slot_h)

        # FOND OPAQUE (cache le jeu derrière)
        pygame.draw.rect(screen, (0, 0, 0, 180), rect)


        # contour dde la case (plus épais si sélectionnée)
        if i == inv_selected:
            pygame.draw.rect(screen, (230, 230, 230), rect, 3)
        else:
            pygame.draw.rect(screen, (120, 120, 120), rect, 2)

# ==========================================================

# ---------- fonction qui assombrit une image ----------

def darken_image(image, amount=90):
    dark = image.copy()
    dark.fill((amount, amount, amount), special_flags=pygame.BLEND_RGB_SUB) #malgré alpha qd mm mettre RBG pas RGBA
    return dark

# ---------- class (= blueprint) du joueur ----------

class Player:
    def __init__(self, x, y, width, height, speed, screen_width, screen_height): #pour les limites de l'écran
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load and scale frames

        def load(name):
            img = pygame.image.load(VB_DIR / name).convert_alpha()
            return pygame.transform.scale(img, (img.get_width()*2, img.get_height()*2))

        # Animations (4 images pour chaque direction)
        self.walk_front = [load("F.png"), load("FLF.png"), load("F.png"), load("FRF.png")] #F = front, L = left, R = right, B = back, LF = left foot, RF = right foot
        self.walk_back  = [load("B.png"), load("BLF.png"), load("B.png"), load("BRF.png")]
        self.walk_left  = [load("L.png"), load("LLF.png"), load("L.png"), load("LRF.png")]
        self.walk_right = [load("R.png"), load("RLF.png"), load("R.png"), load("RRF.png")]

        # Animation state
        self.frame_index = 0
        self.animation_speed = 0.02
        self.current_anim = self.walk_front
        self.image = self.walk_front[0]

        self.x = float(x)
        self.y = float(y)

    def move(self, keys, obstacles):
        moving = False
        old_x = self.x #au cas ou il y a une collision, on garde la position avant le mouvement!!
        old_y = self.y

        # Mouvements avec les touches (Q/A = gauche, D = droite, Z/W = haut, S = bas, pour AZERTY et QWERTY)

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

        # Update rect temporarily

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Check collision after movement

        if self.collision(obstacles):

            # repousser le joueur à sa position avant le mouvement

            self.x = old_x #on le remet à old x/y, comme ecrit avant. 
            self.y = old_y
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        # Animation update
        if moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.current_anim):
                self.frame_index = 0
            self.image = self.current_anim[int(self.frame_index)]
        else:
            self.frame_index = 0
            self.image = self.current_anim[0]

        # Screen limits (after collision check)

        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.x
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width   #limies de l'écran pour le joueur
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

    def collision(self, obstacles):
        for obj in obstacles:
            if self.rect.colliderect(obj):
                return True
        return False

# classe pour tous les futurs boutons images

# classe pour tous les boutons images 
class ImageButton:
    def __init__(self, image, pos, scale_hover=1.08):
        # image de base + version assombrie
        self.image = image
        self.image_dark = darken_image(image)

        # zone de collision
        self.rect = self.image.get_rect(topleft=pos)

        # --- images agrandies ---
        w, h = image.get_size()

        self.image_hover = pygame.transform.smoothscale(
            self.image, (int(w * scale_hover), int(h * scale_hover))
        )

        self.image_dark_hover = darken_image(self.image_hover)

        # rect centrée (pour éviter le saut)
        self.rect_hover = self.image_hover.get_rect(center=self.rect.center)

    # fonction pour dessiner le bouton
    def draw(self, screen):
        # applique l'effet hover si la souris est dessus
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(self.image_dark_hover, self.rect_hover)
        else:
            screen.blit(self.image, self.rect)

    # fonction pour vérifier si le bouton est cliqué
    def is_clicked(self, event):
        # clic gauche dans la zone du bouton
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ECRAN MENU

state = "menu"

def menu_screen():

    
    # SECTION BOUTON JEU

        # --- Bouton JOUER ---
    play_img = pygame.image.load("JOUER_bouton.png").convert_alpha()
    play_img = pygame.transform.scale(play_img, (200, 80))

    screen_width, screen_height = 800, 600
    play_rect = play_img.get_rect(center=(screen_width // 2, screen_height // 2))
    play_button = ImageButton(play_img, play_rect.topleft)

        # --- Bouton INFO ---
    info_img = pygame.image.load("INFO_bouton.png").convert_alpha()
    info_img = pygame.transform.scale(info_img, (200, 80))

    info_rect = info_img.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    info_button = ImageButton(info_img, info_rect.topleft)

    run = True
    while run:
        # fond du menu
        background = pygame.image.load("menu.png").convert()
        screen.blit(background, (0, 0))

        # dessin des boutons
        play_button.draw(screen)
        info_button.draw(screen)
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if play_button.is_clicked(event):
                click_sound.play()
                return "game"  # Quitte le menu pour lancer le jeu

            if info_button.is_clicked(event):
                click_sound.play()
                return "info"  # Affiche l'écran d'info
          


        pygame.display.update()


def game_screen():
    global inv_selected, inv_items  # <-- INVENTAIRE

    # bouton retour
    screen_width, screen_height = 800, 600
    retour_img = pygame.image.load("retour.png").convert_alpha()
    retour_img = pygame.transform.scale(retour_img, (80, 40))

    retour_rect = retour_img.get_rect(topright=(screen_width - 10, 10))
    retour_button = ImageButton(retour_img, retour_rect.topleft)

    # joueur
    player = Player(375, 275, 64, 64, speed=0.75, screen_width=800, screen_height=600)

    run = True
    while run:
        # fond du jeu
        screen.fill(BLACK)

        # mouvement + rendu du joueur
        keys = pygame.key.get_pressed()
        player.update(keys)
        player.draw(screen)

        # ------- INVENTAIRE (draw) -------
        inv_draw(screen, screen_width, screen_height)
        # --------------------------------

        # bouton retour en haut à droite
        retour_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if retour_button.is_clicked(event):
                click_sound.play()
                return "menu"

            if event.type == pygame.KEYDOWN:

                # ------- INVENTAIRE (1..5) -------
                if event.key == pygame.K_1: inv_selected = 0
                if event.key == pygame.K_2: inv_selected = 1
                if event.key == pygame.K_3: inv_selected = 2
                if event.key == pygame.K_4: inv_selected = 3
                if event.key == pygame.K_5: inv_selected = 4

                # (optionnel) T = ajouter un item test
                if event.key == pygame.K_t:
                    inv_add("Item")
                # ---------------------------------

                if event.key == pygame.K_l:
                    click_sound.play()
                    return "fin"

        pygame.display.update()

def info_screen():

    screen_width, screen_height = 800, 600
    retour_img = pygame.image.load("retour.png").convert_alpha()
    retour_img = pygame.transform.scale(retour_img, (80, 40))

    retour_rect = retour_img.get_rect(topright=(screen_width - 10, 10))
    retour_button = ImageButton(retour_img, retour_rect.topleft)

    info_image = pygame.image.load("INFO_page.png").convert()

    run = True
    while run:
        
        screen.blit(info_image, (0, 0))
        retour_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if retour_button.is_clicked(event):
                click_sound.play()
                return "menu"  # Retour au menu # Retour au menu

        pygame.display.update()

def fin_screen():

    screen_width, screen_height = 800, 600
     # --- Bouton QUITTER ---
    quitter_img = pygame.image.load("QUITTER_bouton.png").convert_alpha()
    quitter_img = pygame.transform.scale(quitter_img, (200, 80))

    quitter_rect = quitter_img.get_rect(center=(screen_width // 2, screen_height // 2))
    quitter_button = ImageButton(quitter_img, quitter_rect.topleft)

        # --- Bouton REJOUER ---
    rejouer_img = pygame.image.load("REJOUER_bouton.png").convert_alpha()
    rejouer_img = pygame.transform.scale(rejouer_img, (200, 80))

    rejouer_rect = rejouer_img.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
    rejouer_button = ImageButton(rejouer_img, rejouer_rect.topleft)
    run = True

    fin_image = pygame.image.load("FIN_page.png").convert()

    while run:
        
        screen.blit(fin_image, (0, 0))

        quitter_button.draw(screen)
        rejouer_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if rejouer_button.is_clicked(event):
                click_sound.play()
                return "menu"  # Revenir au menu
            
            if quitter_button.is_clicked(event):
                pygame.quit()
                exit()
                
        pygame.display.update()


# Boucle principale
while True:
    if state == "menu":
            state = menu_screen()
    elif state == "game":
            state = game_screen()        
    elif state == "info":
            state = info_screen()
    elif state == "fin":
            state = fin_screen()


