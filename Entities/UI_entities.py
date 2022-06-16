import pygame

class TextBox(pygame.sprite.Sprite):
    def __init__(self, x, y, font, text, textColor):
        super().__init__()

        self.image = font.render(text, 0, textColor)
        self.textColor = textColor
        self.font = font

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def updateText(self, text):
        self.image = self.font.render(text, 0, self.textColor)

class Image(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width=30, height=32) :
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image = pygame.transform.scale(self.image, (width, height)) 

class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()


        self.MouseinButton = None
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def OnClick(self, buttonPressed):
        if buttonPressed == pygame.mouse.get_pressed()[0] and self.MouseinButton:
            return True
    
    def CursorDetect(self, cursor, image1, image2):
        if cursor.colliderect(self.rect):
            self.image = image1
            self.MouseinButton = True
        else:
            self.image = image2
            self.MouseinButton = False

class Cursor(pygame.Rect):
    def __init__(self):
        super().__init__(0,0,1,1)
    
    def update(self):
        self.left, self.top = pygame.mouse.get_pos()

