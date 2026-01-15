
import pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("28days_soundtrack.ogg")
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1) #musique de fond en boucle
click_sound = pygame.mixer.Sound("click_sound.ogg")
click_sound.set_volume(0.5) #clic sonore


screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("menu + jeu + info")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
scale = 3

font = pygame.font.Font(None, 50)

#fonction qui assombrit une image
def darken_image(image, amount=90):
    dark = image.copy()
    dark.fill((amount, amount, amount), special_flags=pygame.BLEND_RGB_SUB) #malgré alpha qd mm mettre RBG pas RGBA
    return dark

class Player:
    def __init__(self, x, y, width, height, speed, screen_width, screen_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        #load sprite

        self.img_front = pygame.image.load("front.png").convert_alpha()
        self.img_back = pygame.image.load("back.png").convert_alpha()
        self.img_left = pygame.image.load("left.png").convert_alpha()
        self.img_right = pygame.image.load("right.png").convert_alpha()

        self.img_front = pygame.transform.scale(self.img_front, (self.img_front.get_width()*scale, self.img_front.get_height()*scale))
        self.img_back = pygame.transform.scale(self.img_back, (self.img_back.get_width()*scale, self.img_back.get_height()*scale))
        self.img_left = pygame.transform.scale(self.img_left, (self.img_left.get_width()*scale, self.img_left.get_height()*scale))
        self.img_right = pygame.transform.scale(self.img_right, (self.img_right.get_width()*scale, self.img_right.get_height()*scale))

        #perso au debut face a nous
        self.image = self.img_front
        self.x = float(x)
        self.y = float(y)

    def move(self, keys):
        if keys[pygame.K_q]:
            self.x -= self.speed
            self.image = self.img_left
        if keys[pygame.K_d]:
            self.x += self.speed
            self.image = self.img_right
        if keys[pygame.K_z]:
            self.y -= self.speed
            self.image = self.img_back
        if keys[pygame.K_s]:
            self.y += self.speed
            self.image = self.img_front

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        #limites ecran
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height

    def update(self, keys):
        self.move(keys)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# classe pour tous les futurs boutons images
class ImageButton:
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

    # fonction pour dessiner le bouton
    def draw(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(self.image_dark_hover, self.rect_hover)
        else:
            screen.blit(self.image, self.rect)

    # fonction pour vérifier si le bouton est cliqué
    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


#ECRAN MENU

state = "menu"

def menu_screen():

    
    #SECTION BOUTON JEU

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
        background = pygame.image.load("menu.png").convert()
        screen.blit(background, (0, 0))

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

    #bouton retour
    screen_width, screen_height = 800, 600
    retour_img = pygame.image.load("retour.png").convert_alpha()
    retour_img = pygame.transform.scale(retour_img, (80, 40))

    retour_rect = retour_img.get_rect(topright=(screen_width - 10, 10))
    retour_button = ImageButton(retour_img, retour_rect.topleft)

    player = Player(375, 275, 64, 64, speed=0.1, screen_width =800, screen_height=600)
    run = True

    while run:
        screen.fill(BLACK)
        keys = pygame.key.get_pressed()
        player.update(keys)
        player.draw(screen)
        retour_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if retour_button.is_clicked(event):
                click_sound.play()
                return "menu"  # Retour au menu

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l: #appuyer sur L pour tester l'écran de fin
                    click_sound.play()
                    return "fin"  # GAMEOVER screeen
  

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
