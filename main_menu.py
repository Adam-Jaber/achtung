import _thread
import socket
import pygame
from server import run_new_server
from client import Game_client

SCREEN_SIZE = (800, 600)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)

def main_loop():
    header_font = pygame.font.Font('freesansbold.ttf', 32)
    text = header_font.render('Press C to create a game or J to join a game', True, (200, 200, 200), (50, 50, 50))

    choosing = True

    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    _thread.start_new_thread(run_new_server, tuple())
                    host = get_public_ip()
                    Game_client(host, screen)
                elif event.key == pygame.K_j:
                    choosing = False
                    enter_game()

        textRect = text.get_rect()
        textRect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        screen.blit(text, textRect)
        pygame.display.update()


def enter_game():
    header_font = pygame.font.Font('freesansbold.ttf', 32)
    text = header_font.render('Enter game code', True, (200, 200, 200), (50, 50, 50))

    input_box = pygame.Rect(SCREEN_SIZE[0] // 2 - 100, SCREEN_SIZE[1] // 2 + 100, 140, 32)
    color_inactive = pygame.Color(255, 255, 255)
    color_active = pygame.Color('dodgerblue2')
    input_color = color_inactive
    active = False
    input_text = ''

    entering = True
    while entering:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                input_color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:  # add typed characters to the input box (except of a backspace)
                    if event.key == pygame.K_RETURN:
                        try:
                            Game_client(input_text, screen)
                            entering = False
                        except:
                            input_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

        input_txt_surface = header_font.render(input_text, True, (200, 200, 200), (50, 50, 50))
        input_box.w = max(200, input_txt_surface.get_width() + 10)
        screen.blit(input_txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, input_color, input_box, 2)

        textRect = text.get_rect()
        textRect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        screen.blit(text, textRect)
        pygame.display.update()


def get_public_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    return local_ip

if __name__ == '__main__':
    main_loop()