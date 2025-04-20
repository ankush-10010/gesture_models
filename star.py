import pygame
from random import randint
class Star(pygame.sprite.Sprite):
    def __init__(self,groups,surf,screen_width,screen_height):
        super().__init__(groups)
        self.image=surf
        self.screen_width=screen_width
        self.rect=self.image.get_frect(center=(randint(0,screen_width),randint(0,screen_height)))
        self.screen_height=screen_height

        
