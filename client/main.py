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
WIDTH, HEIGHT = user_monitor[0], user_monitor[1]

# test
# WIDTH, HEIGHT = 1600 × 900

# Стандартная разность между длиной и высотой
# Для измениния объектов в соотношение размера экрана
RATIO = 700
# Процент отклонения от стандартного разрешения экрана
SCREEN_RATIO_MODIFICATION = (WIDTH - HEIGHT) / RATIO

# Полный экран
isFullScreen = False

# Инициация библиотеки
pygame.init()
pygame.display.set_caption('Subbiz')
clock = pygame.time.Clock()

# Настройка текста
font_size = 40
font_size = int(font_size * SCREEN_RATIO_MODIFICATION)
main_font = pygame.font.Font(None, font_size)

# окно
screen = pygame.display.set_mode((WIDTH, HEIGHT), (pygame.FULLSCREEN if isFullScreen else pygame.NOFRAME))
if isFullScreen:
    WIDTH, HEIGHT = screen.get_size()


# Загрузчик изображений
def loader_image(path):
    if not os.path.exists(path):
        raise FileNotFoundError
    return pygame.image.load(path)


# Класс таблички где display - рабочий экран, primary_image - изначальное изображение
# pos - позиция на экране
# text - изначальный текст
# scale - модификатор размера
# color - цвет текста


class Label(pygame.sprite.Sprite):
    def __init__(self, display, pos=(0, 0), scale=1, text='', color=(255, 255, 255)):
        super().__init__()
        self.screen = display

        self.image = None
        self.rect = None

        self.position = pos
        self.scale = scale
        self.text = text
        self.color = color

        self.image_change(loader_image('data/UI/label.png'))

    def image_change(self, new_image):
        self.image = pygame.transform.scale(new_image, (
            new_image.get_size()[0] * self.scale * SCREEN_RATIO_MODIFICATION,
            new_image.get_size()[1] * self.scale * SCREEN_RATIO_MODIFICATION))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]

    def update(self, events):
        self.screen.blit(main_font.render(self.text, False, self.color),
                         (self.position[0] + self.image.get_size()[0]//3,
                          self.position[1] + self.image.get_size()[1]//2.25))


# Класс кнопки где display - рабочий экран, primary_image - изначальное изображение(если кнопки не будет иметь OnHover)
# OnHover:
# image_inactive - изображение деактивированной кнопки, image_active- изображение ктивированной кнопки
# pos - позиция на экране
# func - исполняемая функция при нажатии
# scale - модификатор размера

class Button(pygame.sprite.Sprite):
    def __init__(self, display, primary_image, image_inactive=None, image_active=None, pos=(0, 0), func=None, scale=1):
        super(Button, self).__init__()
        self.screen = display

        self.primary_image = primary_image
        self.primary_image = loader_image(primary_image) if type(primary_image) == str else None

        self.image = None
        self.rect = None

        self.image_inactive = image_inactive
        if image_inactive and type(image_inactive) == str:
            self.image_inactive = loader_image(image_inactive)

        self.image_active = image_active
        if image_active and type(image_active) == str:
            self.image_active = loader_image(image_active)

        self.position = pos
        self.scale = scale
        self.func = func

        self.image_change(primary_image)

    def image_change(self, new_image):
        self.image = pygame.transform.scale(new_image, (
            new_image.get_size()[0] * self.scale * SCREEN_RATIO_MODIFICATION,
            new_image.get_size()[1] * self.scale * SCREEN_RATIO_MODIFICATION))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.position[0], self.position[1]

    def update(self, events):
        pos = pygame.mouse.get_pos()
        hit = self.rect.collidepoint(pos)

        def event_func():
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and self.func:
                    self.func()

        if hit and not (self.image_inactive or self.image_active):
            event_func()
        elif hit:
            self.image_change(self.image_active)
            event_func()
        elif self.image_inactive:
            self.image_change(self.image_inactive)

    def get_size(self):
        return self.image.get_size()

    def get_rect(self):
        return self.rect


# Класс кнопки редактирования
# display - рабочий экран
# pos - позиция на экране
# func - исполняемая функция при нажатии
# scale - модификатор размера


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
        self.image = pygame.transform.scale(class_image, (
            class_image.get_size()[0] * self.scale * SCREEN_RATIO_MODIFICATION,
            class_image.get_size()[1] * self.scale * SCREEN_RATIO_MODIFICATION))
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


# Класс входных значений
# display - рабочий экран
# pos - позиция на экране
# text_dialog - текст при открытии диалога
# color - цвет текста
# text - изначальный текст
# scale - модификатор размера


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
        self.image = pygame.transform.scale(img, (
            img.get_size()[0] * self.scale * 1.5 * SCREEN_RATIO_MODIFICATION,
            img.get_size()[1] * self.scale * SCREEN_RATIO_MODIFICATION))
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
    background = loader_image('data/UI/menu.png')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    button_connect = Button(screen, loader_image('data/UI/button_connect_false.png'),
                            image_inactive='data/UI/button_connect_false.png',
                            image_active='data/UI/button_connect_true.png',
                            scale=0.7)
    input_box = InputBox(screen, text='', scale=0.6)
    label = Label(screen, text='dsadsadasd', pos=(100, 100))

    pos_start_button = (WIDTH//2 - button_connect.get_size()[0]//2,
                        HEIGHT//1.12 - button_connect.get_size()[1]//2)
    button_connect.position = pos_start_button
    pos_input_box = (WIDTH // 2 - input_box.get_size()[0] // 2,
                       HEIGHT // 1.43 - input_box.get_size()[1] // 2)
    input_box.position = pos_input_box

    sprites = pygame.sprite.Group()
    sprites.add(input_box)
    sprites.add(button_connect)
    sprites.add(label)

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


