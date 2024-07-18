import pygame
from random import randint
pygame.init()

# make an Enemy class
class Enemy:
    def __init__(self, image, x, y, vel, scale) -> None:
        width, height = image.get_width(), image.get_height()
        self.x = x
        self.y = y
        self.vel = vel
        self.image = pygame.transform.scale(image, (int(scale * width), int(scale * height)))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        self.x += self.vel
        if self.x >= surface.get_size()[0] - self.width - 10 or self.x <= 10:
            self.y += randint(30, 50)
            self.vel *= -1
        surface.blit(self.image, (self.x, self.y))
