import pygame
import Load_Resources

class coin(pygame.sprite.Sprite):
    def __init__(self, x, y, value=1):
        super().__init__()

        self.value = value
        self.typeObj = "collectable"

        self.image = pygame.image.load(Load_Resources.CoinSpr)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def took(self):
        self.value = 0