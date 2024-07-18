import pygame
pygame.init()

# make a Button class
class Bullet:
    def __init__(self, image, ship, scale) -> None:
        width, height = image.get_width(), image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = ship.x + ship.width // 2 - self.width // 2
        self.y = ship.y + ship.height // 2 - self.height // 2
        self.mask = pygame.mask.from_surface(self.image)
        self.triger = True
        self.dead = False

    def draw(self, surface, vel):
        if self.triger is True:
            self.triger = False
        if self.triger is False and self.dead is not True:
            self.y += vel
            surface.blit(self.image, (self.x, self.y))
        if self.y >= surface.get_size()[1]:
            self.dead = True