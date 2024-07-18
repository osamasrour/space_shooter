import pygame
pygame.init()

# make a Player class
class Player:
    def __init__(self, image, x, y, scale) -> None:
        width, height = image.get_width(), image.get_height()
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(image, (int(scale * width), int(scale * height)))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.shoot = False
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface, vel):
        width = surface.get_size()[0]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and self.x <= width - self.width:
            self.x += vel
        if keys[pygame.K_LEFT] and self.x >= 0:
            self.x -= vel
        surface.blit(self.image, (self.x, self.y))
