import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Menu + Jeu")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

font = pygame.font.Font(None, 50)

# --- Fonctions d'écran ---
def menu_screen():
    run = True
    while run:
        background = pygame.image.load("Menu.jpg").convert()

        screen.blit(background, (0, 0))

        play_text = font.render("Appuie sur ENTER pour jouer", True, WHITE)

        play_warning = font.render("Jeu fait par Stella, Georges et Hiep", True, WHITE)

        screen.blit(play_text, (150, 300))
        screen.blit(play_warning, (100, 350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    run = False  # Quitte le menu pour lancer le jeu

        pygame.display.update()


def game_screen():
    player = pygame.Rect(375, 275, 50, 50)
    run = True

    while run:
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, player)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            player.x -= 1
        if keys[pygame.K_d]:
            player.x += 1
        if keys[pygame.K_z]:
            player.y -= 1
        if keys[pygame.K_s]:
            player.y += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False  

        pygame.display.update()



menu_screen()
game_screen()
menu_screen()  
