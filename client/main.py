import ctypes
import socket
from threading import Thread
import json
import pygame
import os
from ctypes import windll
from pyautogui import prompt

# Конфиг
# Пользователь
user32 = windll.user32
# Ставим размер окна под разрешение монитора пользователя
user_monitor = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
WIDTH, HEIGHT = user_monitor[0], user_monitor[1]  # 1920, 1080
isFullScreen = False

pygame.init()
pygame.display.set_caption('Subbiz')
clock = pygame.time.Clock()
main_font = pygame.font.Font(None, 40)
screen = pygame.display.set_mode((WIDTH, HEIGHT), (pygame.FULLSCREEN if isFullScreen else pygame.NOFRAME))
if isFullScreen:
    WIDTH, HEIGHT = screen.get_size()


# Загрузчик изображений
def loader_image(path):
    if not os.path.exists(path):
        raise FileNotFoundError
    return pygame.image.load(path)


class Button(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0), func=None, scale=1):
        super(ButtonEdit, self).__init__()
        self.image = None
        self.rect = self.active.get_rect()
        self.scale = scale
        self.func = func

    def image_change(self, class_image):
        self.image = pygame.transform.scale(class_image, (class_image.get_size()[0] * self.scale,
                                                          class_image.get_size()[1] * self.scale))


class ButtonEdit(pygame.sprite.Sprite):
    def __init__(self, display, pos=(0, 0), func=None, scale=1):
        super(ButtonEdit, self).__init__()
        self.screen = display
        self.image = None
        self.rect = None

        self.position = pos
        self.active = loader_image('data/UI/button_edit.png')
        self.inactive = loader_image('data/UI/button_edit_false.png')
        self.scale = scale

        self.image_change(self.inactive)
        self.func = func

    def image_change(self, class_image):
        self.image = pygame.transform.scale(class_image, (class_image.get_size()[0] * self.scale,
                                                          class_image.get_size()[1] * self.scale))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]

    def draw(self):
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        self.screen.blit(self.image, self.position)

    def update(self, events):
        pos = pygame.mouse.get_pos()
        hit = self.rect.collidepoint(pos)
        if hit:
            self.image_change(self.active)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and self.func:
                    self.func()
        else:
            self.image_change(self.inactive)


class InputBox(pygame.sprite.Sprite):
    def __init__(self, display, pos=(0, 0), scale=1, text='', color=(255, 255, 255), text_dialog='Введите значение'):
        super().__init__()
        self.screen = display
        self.image = None
        self.rect = None
        self.button_edit = None

        self.position = pos
        self.scale = scale
        self.update_model()

        self.text = text
        self.color = color
        self.text_dialog = text_dialog

    def update_model(self):
        img = loader_image('data/UI/input_box.png')
        self.image = pygame.transform.scale(img, (img.get_size()[0] * self.scale * 1.5,
                                                  img.get_size()[1] * self.scale))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]

        self.button_edit = ButtonEdit(self.screen, scale=self.scale * 0.4,
                                      pos=(self.rect.x + self.image.get_size()[0] + 10,
                                           self.rect.y + self.image.get_size()[1]//4), func=self.edit_text)

    def edit_text(self):
        code = prompt(text=self.text_dialog, title='')
        if code:
            self.text = code

    def get_rect(self):
        return self.rect

    def get_size(self):
        return self.image.get_size()

    def get_image(self):
        return self.image

    def get_text(self):
        return self.text

    def update(self, events):
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        self.button_edit.position = (self.rect.x + self.image.get_size()[0] + 10,
                                    self.rect.y + self.image.get_size()[1]//4)

        self.button_edit.draw()
        self.button_edit.update(events)
        self.screen.blit(main_font.render(self.text, False, self.color),
                         (self.position[0] + self.image.get_size()[0] // 10,
                          self.position[1] + self.image.get_size()[1] // 2.3))


# Главное меню
def start_screen():
    # Ассеты
    background = loader_image('data/UI/menu.jpg')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    input_box = InputBox(screen, text='ttttttttgdsa')

    #rect_start_button = (WIDTH//2 - image_start_button.get_size()[0]//2,
                         #HEIGHT//1.2 - image_start_button.get_size()[1]//2 + 20)
    rect_input_box = (WIDTH // 2 - input_box.get_size()[0] // 2,
                       HEIGHT // 1.7 - input_box.get_size()[1] // 2)
    input_box.position = rect_input_box

    sprites = pygame.sprite.Group()
    sprites.add(input_box)

    run = True
    while run:
        screen.blit(background, (0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        sprites.draw(screen)
        sprites.update(events)
        pygame.display.flip()


start_screen()


